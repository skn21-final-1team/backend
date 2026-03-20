"""
baseline.json vs new result를 케이스별로 비교 분석하는 스크립트.

사용법:
    python -m eval.compare_detail eval/results/baseline.json eval/results/new_result.json
"""

import json
import sys
from pathlib import Path


METRICS = [
    "Contextual Precision",
    "Contextual Recall",
    "Contextual Relevancy",
    "Faithfulness",
    "Answer Relevancy",
]


def load_details(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    results = data.get("results", data)
    if isinstance(results, list):
        return results[0]["details"]
    return results["details"]


def classify_question(idx: int) -> str:
    """testset 구간에 따라 질문 유형 분류 (1-20 단일, 21-35 복합-비관련, 36-50 복합-관련)"""
    if idx < 20:
        return "single"
    elif idx < 35:
        return "complex-unrelated"
    else:
        return "complex-related"


def analyze(baseline_path: str, new_path: str):
    bl_details = load_details(baseline_path)
    nw_details = load_details(new_path)

    n = min(len(bl_details), len(nw_details))
    print(f"비교 대상: {n}건\n")

    # 케이스별 delta 수집
    deltas = {m: [] for m in METRICS}
    by_type = {}
    degraded_cases = []  # Faithfulness가 크게 떨어진 케이스
    improved_cases = []  # Answer Relevancy가 크게 오른 케이스

    for i in range(n):
        bl = bl_details[i]
        nw = nw_details[i]
        qtype = classify_question(i)

        if qtype not in by_type:
            by_type[qtype] = {m: {"bl": [], "nw": []} for m in METRICS}

        faith_bl = bl["metrics"].get("Faithfulness", 0) or 0
        faith_nw = nw["metrics"].get("Faithfulness", 0) or 0
        ar_bl = bl["metrics"].get("Answer Relevancy", 0) or 0
        ar_nw = nw["metrics"].get("Answer Relevancy", 0) or 0

        for m in METRICS:
            bl_score = bl["metrics"].get(m, 0) or 0
            nw_score = nw["metrics"].get(m, 0) or 0
            deltas[m].append(nw_score - bl_score)
            by_type[qtype][m]["bl"].append(bl_score)
            by_type[qtype][m]["nw"].append(nw_score)

        # Faithfulness 크게 하락한 케이스 (0.2 이상)
        if faith_bl - faith_nw >= 0.2:
            degraded_cases.append({
                "idx": i + 1,
                "type": qtype,
                "question": bl["input"][:80],
                "faith_bl": faith_bl,
                "faith_nw": faith_nw,
                "delta": faith_nw - faith_bl,
                "bl_answer_len": len(bl.get("actual_output", "")),
                "nw_answer_len": len(nw.get("actual_output", "")),
                "bl_sources": len(bl.get("retrieval_context", [])),
                "nw_sources": len(nw.get("retrieval_context", [])),
            })

        # Answer Relevancy 크게 상승한 케이스 (0.2 이상)
        if ar_nw - ar_bl >= 0.2:
            improved_cases.append({
                "idx": i + 1,
                "type": qtype,
                "question": bl["input"][:80],
                "ar_bl": ar_bl,
                "ar_nw": ar_nw,
                "delta": ar_nw - ar_bl,
            })

    # === 1. 전체 요약 ===
    print("=" * 70)
    print("  전체 메트릭 비교")
    print("=" * 70)
    print(f"  {'메트릭':<25} {'BASELINE':>10} {'NEW':>10} {'Delta':>10}")
    print(f"  {'-' * 57}")
    for m in METRICS:
        # recalculate properly
        bl_all = [bl_details[i]["metrics"].get(m, 0) or 0 for i in range(n)]
        nw_all = [nw_details[i]["metrics"].get(m, 0) or 0 for i in range(n)]
        bl_avg = sum(bl_all) / len(bl_all)
        nw_avg = sum(nw_all) / len(nw_all)
        delta = nw_avg - bl_avg
        sign = "+" if delta >= 0 else ""
        marker = " ***" if abs(delta) >= 0.05 else ""
        print(f"  {m:<25} {bl_avg:>10.4f} {nw_avg:>10.4f} {sign}{delta:>9.4f}{marker}")

    # === 2. 질문 유형별 비교 ===
    print(f"\n{'=' * 70}")
    print("  질문 유형별 메트릭 비교")
    print("=" * 70)
    for qtype in ["single", "complex-unrelated", "complex-related"]:
        if qtype not in by_type:
            continue
        data = by_type[qtype]
        count = len(data[METRICS[0]]["bl"])
        print(f"\n  [{qtype}] ({count}건)")
        print(f"  {'메트릭':<25} {'BASELINE':>10} {'NEW':>10} {'Delta':>10}")
        print(f"  {'-' * 57}")
        for m in METRICS:
            bl_avg = sum(data[m]["bl"]) / len(data[m]["bl"]) if data[m]["bl"] else 0
            nw_avg = sum(data[m]["nw"]) / len(data[m]["nw"]) if data[m]["nw"] else 0
            delta = nw_avg - bl_avg
            sign = "+" if delta >= 0 else ""
            marker = " ***" if abs(delta) >= 0.05 else ""
            print(f"  {m:<25} {bl_avg:>10.4f} {nw_avg:>10.4f} {sign}{delta:>9.4f}{marker}")

    # === 3. Faithfulness 하락 케이스 ===
    print(f"\n{'=' * 70}")
    print(f"  Faithfulness 크게 하락 케이스 (delta ≤ -0.2): {len(degraded_cases)}건")
    print("=" * 70)
    for c in degraded_cases:
        print(f"  #{c['idx']:02d} [{c['type']}] {c['question']}")
        print(f"       Faith: {c['faith_bl']:.2f} → {c['faith_nw']:.2f} ({c['delta']:+.2f})")
        print(f"       답변길이: {c['bl_answer_len']} → {c['nw_answer_len']}, 소스: {c['bl_sources']} → {c['nw_sources']}")

    # === 4. Answer Relevancy 상승 케이스 ===
    print(f"\n{'=' * 70}")
    print(f"  Answer Relevancy 크게 상승 케이스 (delta ≥ +0.2): {len(improved_cases)}건")
    print("=" * 70)
    for c in improved_cases:
        print(f"  #{c['idx']:02d} [{c['type']}] {c['question']}")
        print(f"       AR: {c['ar_bl']:.2f} → {c['ar_nw']:.2f} ({c['delta']:+.2f})")

    # === 5. 케이스별 Faithfulness 전체 리스트 ===
    print(f"\n{'=' * 70}")
    print("  케이스별 핵심 지표 (Faithfulness / Answer Relevancy)")
    print("=" * 70)
    print(f"  {'#':>3} {'유형':<20} {'Faith BL':>9} {'Faith NW':>9} {'ΔFaith':>8} {'AR BL':>7} {'AR NW':>7} {'ΔAR':>7}")
    print(f"  {'-' * 75}")
    for i in range(n):
        bl = bl_details[i]
        nw = nw_details[i]
        qtype = classify_question(i)
        fb = bl["metrics"].get("Faithfulness", 0) or 0
        fn = nw["metrics"].get("Faithfulness", 0) or 0
        ab = bl["metrics"].get("Answer Relevancy", 0) or 0
        an = nw["metrics"].get("Answer Relevancy", 0) or 0
        df = fn - fb
        da = an - ab
        flag = " ←" if df <= -0.2 else ""
        print(f"  {i+1:>3} {qtype:<20} {fb:>9.3f} {fn:>9.3f} {df:>+8.3f} {ab:>7.3f} {an:>7.3f} {da:>+7.3f}{flag}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python -m eval.compare_detail <baseline.json> <new_result.json>")
        sys.exit(1)
    analyze(sys.argv[1], sys.argv[2])
