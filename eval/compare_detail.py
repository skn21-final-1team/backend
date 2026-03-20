"""
baseline.json vs new result를 케이스별로 비교 분석하는 스크립트.

사용법:
    python -m eval.compare_detail eval/results/baseline.json eval/results/new_result.json
"""

import json
import sys


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


def _get_score(detail: dict, metric: str) -> float | None:
    """메트릭 점수를 가져옴. None이면 None 반환 (미평가)."""
    val = detail["metrics"].get(metric)
    return val  # None이면 None, 숫자면 숫자


def _avg(scores: list[float | None]) -> tuple[float, int]:
    """None을 제외한 평균과 유효 개수 반환."""
    valid = [s for s in scores if s is not None]
    if not valid:
        return 0.0, 0
    return sum(valid) / len(valid), len(valid)


def analyze(baseline_path: str, new_path: str):
    bl_details = load_details(baseline_path)
    nw_details = load_details(new_path)

    n = min(len(bl_details), len(nw_details))
    print(f"비교 대상: {n}건\n")

    by_type: dict[str, dict[str, dict[str, list]]] = {}
    degraded_cases = []
    improved_cases = []

    for i in range(n):
        bl = bl_details[i]
        nw = nw_details[i]
        qtype = classify_question(i)

        if qtype not in by_type:
            by_type[qtype] = {m: {"bl": [], "nw": []} for m in METRICS}

        for m in METRICS:
            by_type[qtype][m]["bl"].append(_get_score(bl, m))
            by_type[qtype][m]["nw"].append(_get_score(nw, m))

        faith_bl = _get_score(bl, "Faithfulness")
        faith_nw = _get_score(nw, "Faithfulness")
        ar_bl = _get_score(bl, "Answer Relevancy")
        ar_nw = _get_score(nw, "Answer Relevancy")

        # Faithfulness 크게 하락한 케이스 (둘 다 유효하고 0.2 이상 차이)
        if faith_bl is not None and faith_nw is not None and faith_bl - faith_nw >= 0.2:
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

        # Answer Relevancy 크게 상승한 케이스
        if ar_bl is not None and ar_nw is not None and ar_nw - ar_bl >= 0.2:
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
    print("  전체 메트릭 비교 (null 제외 평균)")
    print("=" * 70)
    print(f"  {'메트릭':<25} {'BASELINE':>10} {'NEW':>10} {'Delta':>10}")
    print(f"  {'-' * 57}")
    for m in METRICS:
        bl_all = [_get_score(bl_details[i], m) for i in range(n)]
        nw_all = [_get_score(nw_details[i], m) for i in range(n)]
        bl_avg, bl_cnt = _avg(bl_all)
        nw_avg, nw_cnt = _avg(nw_all)
        delta = nw_avg - bl_avg
        sign = "+" if delta >= 0 else ""
        marker = " ***" if abs(delta) >= 0.05 else ""
        print(f"  {m:<25} {bl_avg:>10.4f} {nw_avg:>10.4f} {sign}{delta:>9.4f}{marker}")

    # === 2. 질문 유형별 비교 ===
    print(f"\n{'=' * 70}")
    print("  질문 유형별 메트릭 비교 (null 제외)")
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
            bl_avg, bl_cnt = _avg(data[m]["bl"])
            nw_avg, nw_cnt = _avg(data[m]["nw"])
            delta = nw_avg - bl_avg
            sign = "+" if delta >= 0 else ""
            marker = " ***" if abs(delta) >= 0.05 else ""
            cnt_info = f" ({bl_cnt}/{nw_cnt})" if bl_cnt != count or nw_cnt != count else ""
            print(f"  {m:<25} {bl_avg:>10.4f} {nw_avg:>10.4f} {sign}{delta:>9.4f}{marker}{cnt_info}")

    # === 3. Faithfulness 하락 케이스 ===
    print(f"\n{'=' * 70}")
    print(f"  Faithfulness 크게 하락 케이스 (delta <= -0.2): {len(degraded_cases)}건")
    print("=" * 70)
    for c in degraded_cases:
        print(f"  #{c['idx']:02d} [{c['type']}] {c['question']}")
        print(f"       Faith: {c['faith_bl']:.2f} -> {c['faith_nw']:.2f} ({c['delta']:+.2f})")
        print(f"       답변길이: {c['bl_answer_len']} -> {c['nw_answer_len']}, 소스: {c['bl_sources']} -> {c['nw_sources']}")

    # === 4. Answer Relevancy 상승 케이스 ===
    print(f"\n{'=' * 70}")
    print(f"  Answer Relevancy 크게 상승 케이스 (delta >= +0.2): {len(improved_cases)}건")
    print("=" * 70)
    for c in improved_cases:
        print(f"  #{c['idx']:02d} [{c['type']}] {c['question']}")
        print(f"       AR: {c['ar_bl']:.2f} -> {c['ar_nw']:.2f} ({c['delta']:+.2f})")

    # === 5. 케이스별 핵심 지표 ===
    print(f"\n{'=' * 70}")
    print("  케이스별 핵심 지표 (Faithfulness / Answer Relevancy)")
    print("=" * 70)
    print(f"  {'#':>3} {'유형':<20} {'Faith BL':>9} {'Faith NW':>9} {'dFaith':>8} {'AR BL':>7} {'AR NW':>7} {'dAR':>7}")
    print(f"  {'-' * 75}")
    for i in range(n):
        bl = bl_details[i]
        nw = nw_details[i]
        qtype = classify_question(i)
        fb = _get_score(bl, "Faithfulness")
        fn = _get_score(nw, "Faithfulness")
        ab = _get_score(bl, "Answer Relevancy")
        an = _get_score(nw, "Answer Relevancy")

        fb_s = f"{fb:>9.3f}" if fb is not None else "     null"
        fn_s = f"{fn:>9.3f}" if fn is not None else "     null"
        ab_s = f"{ab:>7.3f}" if ab is not None else "   null"
        an_s = f"{an:>7.3f}" if an is not None else "   null"

        df_s = f"{fn - fb:>+8.3f}" if fb is not None and fn is not None else "     n/a"
        da_s = f"{an - ab:>+7.3f}" if ab is not None and an is not None else "    n/a"

        flag = ""
        if fb is not None and fn is not None and fb - fn >= 0.2:
            flag = " <-"
        print(f"  {i+1:>3} {qtype:<20} {fb_s} {fn_s} {df_s} {ab_s} {an_s} {da_s}{flag}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python -m eval.compare_detail <baseline.json> <new_result.json>")
        sys.exit(1)
    analyze(sys.argv[1], sys.argv[2])
