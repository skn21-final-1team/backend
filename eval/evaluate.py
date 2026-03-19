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

비교 대상:
    baseline = classify(2분류) → 직접 retrieve → 기존 프롬프트로 generate
    new      = classify(3분류) → rewrite/decompose → retrieve → 개선 프롬프트로 generate
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.environ.setdefault("DEEPEVAL_THROTTLE_VALUE", "15")

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


async def build_test_cases(graph, testset: list[dict], model_name: str, label: str) -> list[LLMTestCase]:
    """테스트셋에 대해 그래프를 실행하고 LLMTestCase 목록을 반환합니다."""
    test_cases = []
    total = len(testset)

    print(f"\n[{label}] 에이전트 실행 ({total}건)")
    print("-" * 60)

    for i, item in enumerate(testset, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]
        notebook_id = item["notebook_id"]

        print(f"  [{i}/{total}] {question[:50]}...")

        try:
            result = await run_graph(graph, question, notebook_id, model_name)
            print(f"    → intent={result['intent']}, sources={len(result['sources'])}건")
        except Exception as e:
            print(f"    → 에러: {e}")
            result = {"answer": "", "sources": []}

        test_case = LLMTestCase(
            input=question,
            actual_output=result["answer"],
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


def print_summary(label: str, results, test_cases: list[LLMTestCase]) -> dict:
    """평가 결과 요약을 출력하고 수집된 결과를 반환합니다."""
    collected = collect_results(label, results, test_cases)

    print(f"\n{'=' * 60}")
    print(f"  [{label}] 평가 결과")
    print(f"{'=' * 60}")

    for name, avg in collected["averages"].items():
        count = sum(1 for d in collected["details"] if d["metrics"].get(name) is not None)
        print(f"  {name}: {avg:.4f} ({count}건)")

    return collected


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


def run_single_model(graph, testset, model_name, label, metrics):
    """단일 모델로 그래프를 실행하고 평가합니다."""
    test_cases = asyncio.run(build_test_cases(graph, testset, model_name, label))
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


def run_compare(testset, models, metrics):
    """baseline vs new 비교를 실행합니다."""
    from agent.graph import graph as new_graph  # noqa: PLC0415
    from eval.baseline_graph import baseline_graph  # noqa: PLC0415

    all_collected = []
    for model_name in models:
        print(f"\n{'#' * 60}")
        print(f"  모델: {model_name}")
        print(f"{'#' * 60}")

        bl = run_single_model(baseline_graph, testset, model_name, f"BASELINE({model_name})", metrics)
        nw = run_single_model(new_graph, testset, model_name, f"NEW({model_name})", metrics)
        comparison = print_comparison(bl["label"], bl["averages"], nw["label"], nw["averages"])
        all_collected.extend([bl, nw, {"label": f"COMPARISON({model_name})", "comparison": comparison}])

    compare_if_multi_model(all_collected, models, prefix="NEW")
    return all_collected


def run_single_pipeline(graph, testset, models, metrics, prefix):
    """단일 파이프라인을 모델별로 실행합니다."""
    all_collected = []
    for model_name in models:
        collected = run_single_model(graph, testset, model_name, f"{prefix}({model_name})", metrics)
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
    args = parser.parse_args()

    testset_path = Path(args.testset)
    if not testset_path.exists():
        print(f"테스트셋 파일을 찾을 수 없습니다: {testset_path}")
        sys.exit(1)

    with open(testset_path, encoding="utf-8") as f:
        testset = json.load(f)

    models = args.model
    model_str = ", ".join(models)
    print(f"테스트셋: {testset_path} ({len(testset)}건)")
    print(f"모델: {model_str}")

    metrics = get_metrics()

    if args.compare:
        all_collected = run_compare(testset, models, metrics)
    elif args.baseline:
        from eval.baseline_graph import baseline_graph  # noqa: PLC0415

        all_collected = run_single_pipeline(baseline_graph, testset, models, metrics, "BASELINE")
    else:
        from agent.graph import graph as new_graph  # noqa: PLC0415

        all_collected = run_single_pipeline(new_graph, testset, models, metrics, "NEW")

    save_and_log(all_collected, model_str, str(testset_path), args.experiment)
    print("\n평가 완료")


if __name__ == "__main__":
    main()
