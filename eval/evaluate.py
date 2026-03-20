"""
RAG 파이프라인 A/B 평가 스크립트 (deepeval)

사용법:
    python -m eval.evaluate                        # new 그래프만 평가
    python -m eval.evaluate --baseline             # baseline 그래프만 평가
    python -m eval.evaluate --compare              # baseline vs new A/B 비교
    python -m eval.evaluate --testset path/to.json # 커스텀 테스트셋
    python -m eval.evaluate --model exaone         # 단일 모델 지정
    python -m eval.evaluate --model gpt-4o-mini exaone  # 멀티 모델 비교
    python -m eval.evaluate --experiment my-exp    # MLflow 실험 이름 지정
    python -m eval.evaluate --batch-size 10        # 10건씩 배치 평가 (rate limit 방지)
    python -m eval.evaluate --batch-delay 120       # 배치 간 대기 시간(초)
    python -m eval.evaluate --baseline --resume    # 중간 저장 파일에서 이어서 평가

비교 대상:
    baseline = classify(2분류) → 직접 retrieve → 기존 프롬프트로 generate
    new      = classify(3분류) → rewrite/decompose → retrieve → 개선 프롬프트로 generate
"""

import argparse
import asyncio
import json
import os
import sys
import time
import traceback
from datetime import UTC, datetime

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("DEEPEVAL_THROTTLE_VALUE", "45")
os.environ.setdefault("DEEPEVAL_MAX_CONCURRENT", "1")
os.environ.setdefault("DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE", "360")

EVAL_JUDGE_MODEL = os.environ.get("DEEPEVAL_TEST_MODEL", "gpt-4o-mini")

from pathlib import Path

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

try:
    import mlflow

    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

RESULTS_DIR = Path(__file__).parent / "results"
MIN_MODELS_FOR_COMPARISON = 2


async def run_graph(graph, question: str, notebook_id: int, model_name: str) -> dict:
    """주어진 그래프를 실행하고 결과를 반환합니다."""
    result = await graph.ainvoke(
        {
            "notebook_id": notebook_id,
            "question": question,
            "chat_history": [],
        },
        config={"configurable": {"model_name": model_name}},
    )
    return {
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "intent": result.get("intent", ""),
        "search_queries": result.get("search_queries", []),
    }


async def build_test_cases(
    graph,
    testset: list[dict],
    model_name: str,
    label: str,
    skip_indices: set[int] | None = None,
    prev_details: list[dict] | None = None,
) -> list[LLMTestCase]:
    """테스트셋에 대해 그래프를 실행하고 LLMTestCase 목록을 반환합니다.

    skip_indices가 주어지면 해당 인덱스는 그래프 실행을 건너뛰고
    prev_details에서 LLMTestCase를 복원합니다.
    """
    test_cases = []
    total = len(testset)
    skip_indices = skip_indices or set()
    run_count = total - len(skip_indices)

    print(f"\n[{label}] 에이전트 실행 ({run_count}/{total}건, {len(skip_indices)}건 스킵)")
    print("-" * 60)

    for i, item in enumerate(testset):
        question = item["question"]
        ground_truth = item["ground_truth"]
        notebook_id = item["notebook_id"]

        # 이미 완료된 테스트 케이스: 저장된 결과에서 복원
        if i in skip_indices and prev_details and i < len(prev_details):
            detail = prev_details[i]
            test_case = LLMTestCase(
                input=detail["input"],
                actual_output=detail["actual_output"],
                expected_output=detail["expected_output"],
                retrieval_context=detail.get("retrieval_context", [""]),
            )
            test_cases.append(test_case)
            print(f"  [{i + 1}/{total}] {question[:50]}... → 캐시 사용")
            continue

        print(f"  [{i + 1}/{total}] {question[:50]}...")

        try:
            result = await run_graph(graph, question, notebook_id, model_name)
            print(f"    → intent={result['intent']}, sources={len(result['sources'])}건")
        except Exception as e:
            print(f"    → 에러: {e}")
            traceback.print_exc()
            result = {"answer": "", "sources": []}

        # deepeval 메트릭은 빈 actual_output을 허용하지 않음
        actual_output = result["answer"] if result["answer"] else "(답변을 생성하지 못했습니다)"

        test_case = LLMTestCase(
            input=question,
            actual_output=actual_output,
            expected_output=ground_truth,
            retrieval_context=result["sources"] if result["sources"] else [""],
        )
        test_cases.append(test_case)

    return test_cases


def get_metrics() -> list:
    return [
        ContextualPrecisionMetric(threshold=0.5, model=EVAL_JUDGE_MODEL),
        ContextualRecallMetric(threshold=0.5, model=EVAL_JUDGE_MODEL),
        ContextualRelevancyMetric(threshold=0.5, model=EVAL_JUDGE_MODEL),
        FaithfulnessMetric(threshold=0.5, model=EVAL_JUDGE_MODEL),
        AnswerRelevancyMetric(threshold=0.5, model=EVAL_JUDGE_MODEL),
    ]


def collect_results(label: str, results, test_cases: list[LLMTestCase]) -> dict:
    """평가 결과를 수집하여 딕셔너리로 반환합니다."""
    scores: dict[str, list[float]] = {}
    details = []

    for tc, result in zip(test_cases, results.test_results, strict=True):
        case_detail = {
            "input": tc.input,
            "actual_output": tc.actual_output,
            "expected_output": tc.expected_output,
            "retrieval_context": tc.retrieval_context,
            "metrics": {},
        }
        for metric_result in result.metrics_data:
            name = metric_result.name
            score = metric_result.score
            if name not in scores:
                scores[name] = []
            if score is not None:
                scores[name].append(score)
            case_detail["metrics"][name] = score
        details.append(case_detail)

    averages = {}
    for name, score_list in scores.items():
        averages[name] = sum(score_list) / len(score_list) if score_list else 0.0

    return {"label": label, "averages": averages, "details": details}


def print_collected_summary(collected: dict):
    """수집된 결과 딕셔너리를 요약 출력합니다."""
    label = collected["label"]
    print(f"\n{'=' * 60}")
    print(f"  [{label}] 평가 결과")
    print(f"{'=' * 60}")

    for name, avg in collected["averages"].items():
        count = sum(1 for d in collected["details"] if d["metrics"].get(name) is not None)
        print(f"  {name}: {avg:.4f} ({count}건)")


def print_summary(label: str, results, test_cases: list[LLMTestCase]) -> dict:
    """평가 결과 요약을 출력하고 수집된 결과를 반환합니다."""
    collected = collect_results(label, results, test_cases)
    print_collected_summary(collected)
    return collected


def _save_partial(label: str, all_details: list, scores: dict[str, list[float]]):
    """배치 중간 결과를 저장합니다. 크래시 시 복구용."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = RESULTS_DIR / f"_partial_{label.lower()}.json"
    averages = {}
    for name, score_list in scores.items():
        averages[name] = sum(score_list) / len(score_list) if score_list else 0.0
    payload = {"label": label, "averages": averages, "details": all_details, "partial": True}
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  → 중간 결과 저장: {filepath}")


def _run_batch_with_retry(batch, metrics, batch_num, total_batches, batch_delay):
    """배치 평가를 최대 1회 시도합니다. 실패 시 None을 반환합니다."""
    max_retries = 1
    for attempt in range(1, max_retries + 1):
        try:
            return evaluate(test_cases=batch, metrics=metrics)
        except Exception as e:
            print(f"\n  ✗ 배치 {batch_num}/{total_batches} 시도 {attempt}/{max_retries} 실패: {type(e).__name__}")
            if attempt < max_retries:
                retry_delay = batch_delay * 2
                print(f"  → {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                print(f"  → 배치 {batch_num} 건너뜀 (재시도 소진)")
    return None


def _load_resume_data(label: str) -> dict | None:
    """중간 저장 파일이 있으면 로드합니다."""
    partial_path = RESULTS_DIR / f"_partial_{label.lower()}.json"
    if not partial_path.exists():
        return None
    with partial_path.open(encoding="utf-8") as f:
        data = json.load(f)
    count = sum(1 for d in data.get("details", []) if not d.get("skipped"))
    print(f"\n  resume: 중간 저장 파일 발견 ({count}건 완료)")
    print(f"  resume: {partial_path}")
    return data


def evaluate_in_batches(
    test_cases: list[LLMTestCase],
    metrics: list,
    label: str,
    batch_size: int,
    batch_delay: int,
    resume: bool = False,
) -> dict:
    """테스트케이스를 배치로 나누어 평가하고 결과를 병합합니다."""
    total_batches = (len(test_cases) + batch_size - 1) // batch_size
    all_details = []
    scores: dict[str, list[float]] = {}
    skipped_batches = []
    start_batch_idx = 0

    # resume: 중간 저장 파일에서 이전 결과 로드
    skipped_batch_indices: set[int] = set()
    if resume:
        resume_data = _load_resume_data(label)
        if resume_data and resume_data.get("details"):
            prev_details = resume_data["details"]
            all_details = list(prev_details)
            # skip된 배치 인덱스 찾기
            for i, detail in enumerate(prev_details):
                if detail.get("skipped"):
                    skipped_batch_indices.add(i // batch_size)
            # 이전 결과에서 scores 복원 (skip 제외)
            for detail in prev_details:
                if detail.get("skipped"):
                    continue
                for name, score in detail.get("metrics", {}).items():
                    if name not in scores:
                        scores[name] = []
                    if score is not None:
                        scores[name].append(score)
            if skipped_batch_indices:
                print(f"  resume: 실패 배치 {sorted(b + 1 for b in skipped_batch_indices)} 재평가")
            else:
                start_batch_idx = len(prev_details)
                done = start_batch_idx // batch_size
                print(f"  resume: 배치 {done}까지 건너뜀 → 배치 {done + 1}부터 재개")

    for batch_idx in range(start_batch_idx, len(test_cases), batch_size):
        batch = test_cases[batch_idx : batch_idx + batch_size]
        batch_num = batch_idx // batch_size + 1

        # resume: 이미 성공한 배치는 건너뜀
        is_retry = batch_num - 1 in skipped_batch_indices
        if resume and all_details and not is_retry and batch_idx + batch_size <= len(all_details):
            continue

        print(f"\n{'─' * 60}")
        retry_tag = " [재시도]" if is_retry else ""
        print(f"  평가 배치 {batch_num}/{total_batches} ({len(batch)}건){retry_tag} — [{label}]")
        print(f"{'─' * 60}")

        results = _run_batch_with_retry(batch, metrics, batch_num, total_batches, batch_delay)

        # 배치 결과를 detail 목록으로 변환
        batch_details = []
        if results is None:
            skipped_batches.append(batch_num)
            for tc in batch:
                batch_details.append(
                    {
                        "input": tc.input,
                        "actual_output": tc.actual_output,
                        "expected_output": tc.expected_output,
                        "retrieval_context": tc.retrieval_context,
                        "metrics": {},
                        "skipped": True,
                    }
                )
            if batch_idx + batch_size < len(test_cases):
                print(f"  → 다음 배치까지 {batch_delay}초 대기...")
                time.sleep(batch_delay)
        else:
            for tc, result in zip(batch, results.test_results, strict=True):
                case_detail = {
                    "input": tc.input,
                    "actual_output": tc.actual_output,
                    "expected_output": tc.expected_output,
                    "retrieval_context": tc.retrieval_context,
                    "metrics": {},
                }
                for metric_result in result.metrics_data:
                    name = metric_result.name
                    score = metric_result.score
                    if name not in scores:
                        scores[name] = []
                    if score is not None:
                        scores[name].append(score)
                    case_detail["metrics"][name] = score
                batch_details.append(case_detail)
            print(f"  ✓ 배치 {batch_num}/{total_batches} 완료")

        # 재시도 배치: 기존 skipped 항목을 교체 / 신규: 추가
        if is_retry:
            all_details[batch_idx : batch_idx + batch_size] = batch_details
        else:
            all_details.extend(batch_details)

        # 매 배치마다 중간 결과 저장
        _save_partial(label, all_details, scores)

        # 다음 배치 전 대기 (마지막 배치 제외)
        if batch_idx + batch_size < len(test_cases):
            print(f"  → 다음 배치까지 {batch_delay}초 대기 (rate limit 방지)...")
            time.sleep(batch_delay)

    # 전체 평균 계산
    averages = {}
    for name, score_list in scores.items():
        averages[name] = sum(score_list) / len(score_list) if score_list else 0.0

    if skipped_batches:
        evaluated = len(test_cases) - len(skipped_batches) * batch_size
        print(f"\n  ⚠ 건너뛴 배치: {skipped_batches} ({evaluated}/{len(test_cases)}건 평가 완료)")

    # 중간 저장 파일 삭제 (완료되었으므로)
    partial_path = RESULTS_DIR / f"_partial_{label.lower()}.json"
    if partial_path.exists():
        partial_path.unlink()

    return {"label": label, "averages": averages, "details": all_details}


def print_comparison(
    label_a: str,
    avg_a: dict[str, float],
    label_b: str,
    avg_b: dict[str, float],
) -> dict[str, dict[str, float]]:
    """두 결과의 비교 테이블을 출력하고 비교 결과를 반환합니다."""
    print(f"\n{'=' * 60}")
    print(f"  비교 결과 ({label_a} vs {label_b})")
    print(f"{'=' * 60}")
    print(f"  {'메트릭':<30} {label_a:>10} {label_b:>10} {'Delta':>10}")
    print(f"  {'-' * 62}")

    comparison = {}
    all_keys = sorted(set(avg_a.keys()) | set(avg_b.keys()))
    for key in all_keys:
        a = avg_a.get(key, 0.0)
        b = avg_b.get(key, 0.0)
        delta = b - a
        sign = "+" if delta >= 0 else ""
        print(f"  {key:<30} {a:>10.4f} {b:>10.4f} {sign}{delta:>9.4f}")
        comparison[key] = {label_a: a, label_b: b, "delta": delta}

    return comparison


def save_results_json(collected: dict | list[dict], model: str, testset_path: str) -> Path:
    """평가 결과를 로컬 JSON 파일로 저장합니다."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")

    label = "compare" if isinstance(collected, list) else collected["label"].lower()

    filename = f"{timestamp}_{label}.json"
    filepath = RESULTS_DIR / filename

    payload = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "model": model,
        "testset": testset_path,
        "results": collected,
    }

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {filepath}")
    return filepath


def log_to_mlflow(
    collected: dict | list[dict],
    model: str,
    testset_path: str,
    experiment_name: str,
    json_path: Path,
):
    """MLflow에 실험 결과를 기록합니다. MLflow 서버 미연결 시 건너뜁니다."""
    if not HAS_MLFLOW:
        print("\nMLflow 미설치 — pip install mlflow 로 설치 후 사용 가능")
        return

    try:
        mlflow.set_experiment(experiment_name)
    except Exception as e:
        print(f"\nMLflow 연결 실패 (로컬 JSON만 저장됨): {e}")
        return

    items = collected if isinstance(collected, list) else [collected]

    for item in items:
        label = item["label"]
        with mlflow.start_run(run_name=f"{label}_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_params({"model": model, "testset": testset_path, "pipeline": label})

            for metric_name, avg_score in item["averages"].items():
                safe_name = metric_name.replace(" ", "_")
                mlflow.log_metric(f"{safe_name}", avg_score)

            mlflow.log_artifact(str(json_path))

    print(f"MLflow 기록 완료 (experiment: {experiment_name})")


def run_single_model(graph, testset, model_name, label, metrics, batch_size=0, batch_delay=60, resume=False):
    """단일 모델로 그래프를 실행하고 평가합니다."""
    skip_indices: set[int] = set()
    prev_details: list[dict] | None = None

    # resume: 이미 완료된 테스트 케이스는 그래프 실행 스킵
    if resume:
        resume_data = _load_resume_data(label)
        if resume_data and resume_data.get("details"):
            prev_details = resume_data["details"]
            for i, detail in enumerate(prev_details):
                if not detail.get("skipped"):
                    skip_indices.add(i)

    test_cases = asyncio.run(build_test_cases(graph, testset, model_name, label, skip_indices, prev_details))

    if batch_size > 0 and batch_size < len(test_cases):
        collected = evaluate_in_batches(test_cases, metrics, label, batch_size, batch_delay, resume)
        print_collected_summary(collected)
        return collected

    print(f"\n평가 중... ({label})")
    results = evaluate(test_cases=test_cases, metrics=metrics)
    return print_summary(label, results, test_cases)


def compare_if_multi_model(all_collected, models, prefix="NEW"):
    """모델이 2개 이상이면 모델 간 비교 테이블을 출력합니다."""
    if len(models) <= 1:
        return
    items = [c for c in all_collected if c["label"].startswith(f"{prefix}(")]
    if len(items) >= MIN_MODELS_FOR_COMPARISON:
        print_comparison(
            items[0]["label"],
            items[0]["averages"],
            items[1]["label"],
            items[1]["averages"],
        )


def save_and_log(all_collected, model_str, testset_path, experiment, json_path=None):
    """결과를 JSON 저장 + MLflow 기록합니다."""
    json_path = save_results_json(all_collected, model_str, str(testset_path))
    loggable = [c for c in all_collected if "averages" in c] if isinstance(all_collected, list) else all_collected
    log_to_mlflow(loggable, model_str, str(testset_path), experiment, json_path)


def run_compare(testset, models, metrics, batch_size=0, batch_delay=60, resume=False):
    """baseline vs new 비교를 실행합니다."""
    from agent.graph import graph as new_graph  # noqa: PLC0415
    from eval.baseline_graph import baseline_graph  # noqa: PLC0415

    all_collected = []
    for model_name in models:
        print(f"\n{'#' * 60}")
        print(f"  모델: {model_name}")
        print(f"{'#' * 60}")

        bl = run_single_model(
            baseline_graph, testset, model_name, f"BASELINE({model_name})", metrics, batch_size, batch_delay, resume
        )
        nw = run_single_model(
            new_graph, testset, model_name, f"NEW({model_name})", metrics, batch_size, batch_delay, resume
        )
        comparison = print_comparison(bl["label"], bl["averages"], nw["label"], nw["averages"])
        all_collected.extend([bl, nw, {"label": f"COMPARISON({model_name})", "comparison": comparison}])

    compare_if_multi_model(all_collected, models, prefix="NEW")
    return all_collected


def run_single_pipeline(graph, testset, models, metrics, prefix, batch_size=0, batch_delay=60, resume=False):
    """단일 파이프라인을 모델별로 실행합니다."""
    all_collected = []
    for model_name in models:
        collected = run_single_model(
            graph, testset, model_name, f"{prefix}({model_name})", metrics, batch_size, batch_delay, resume
        )
        all_collected.append(collected)
    compare_if_multi_model(all_collected, models, prefix=prefix)
    return all_collected


def main():
    parser = argparse.ArgumentParser(description="RAG 파이프라인 A/B 평가")
    parser.add_argument("--testset", type=str, default="agent/testset.json")
    parser.add_argument("--model", type=str, nargs="+", default=["gpt-4o-mini"])
    parser.add_argument("--baseline", action="store_true", help="baseline 그래프만 평가")
    parser.add_argument("--compare", action="store_true", help="baseline vs new A/B 비교")
    parser.add_argument("--experiment", type=str, default="rag-evaluation", help="MLflow 실험 이름")
    parser.add_argument("--batch-size", type=int, default=5, help="배치당 테스트케이스 수 (0=배치 없음, 기본 5)")
    parser.add_argument("--batch-delay", type=int, default=60, help="배치 간 대기 시간(초) (기본 60)")
    parser.add_argument(
        "--no-resume", dest="resume", action="store_false", help="중간 저장 파일 무시하고 처음부터 평가"
    )
    parser.set_defaults(resume=True)
    args = parser.parse_args()

    testset_path = Path(args.testset)
    if not testset_path.exists():
        print(f"테스트셋 파일을 찾을 수 없습니다: {testset_path}")
        sys.exit(1)

    with open(testset_path, encoding="utf-8") as f:
        testset = json.load(f)

    models = args.model
    model_str = ", ".join(models)
    batch_size = args.batch_size
    batch_delay = args.batch_delay

    print(f"테스트셋: {testset_path} ({len(testset)}건)")
    print(f"모델: {model_str}")
    if batch_size > 0:
        total_batches = (len(testset) + batch_size - 1) // batch_size
        print(f"배치: {batch_size}건씩 {total_batches}배치 (배치 간 {batch_delay}초 대기)")

    metrics = get_metrics()

    if args.compare:
        all_collected = run_compare(testset, models, metrics, batch_size, batch_delay, args.resume)
    elif args.baseline:
        from eval.baseline_graph import baseline_graph  # noqa: PLC0415

        all_collected = run_single_pipeline(
            baseline_graph, testset, models, metrics, "BASELINE", batch_size, batch_delay, args.resume
        )
    else:
        from agent.graph import graph as new_graph  # noqa: PLC0415

        all_collected = run_single_pipeline(
            new_graph, testset, models, metrics, "NEW", batch_size, batch_delay, args.resume
        )

    save_and_log(all_collected, model_str, str(testset_path), args.experiment)
    print("\n평가 완료")


if __name__ == "__main__":
    main()
