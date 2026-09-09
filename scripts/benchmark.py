"""Run lightweight classifier and baseline benchmarks for the Review 2 report."""

import json
import statistics
import time
from pathlib import Path

from baseline.attack_harness import ATTACKS, BENIGN, run_baseline_attacks
from app.detector import InjectionDetector
from app.normalize import segment_text
from config import settings


def benchmark_latency(samples: list[str], iterations: int = 5) -> dict:
    detector = InjectionDetector()
    latencies: list[float] = []
    for sample in samples:
        segments = segment_text(sample, settings.max_segment_chars)
        for _ in range(iterations):
            start = time.perf_counter()
            detector.score_segments(segments)
            latencies.append((time.perf_counter() - start) * 1000)
    latencies.sort()
    return {
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(latencies[int(len(latencies) * 0.95) - 1], 2),
        "p99_ms": round(latencies[int(len(latencies) * 0.99) - 1], 2),
        "samples": len(latencies),
    }


def evaluate_proxy(samples: list[str], expected_blocked: bool) -> dict:
    detector = InjectionDetector()
    blocked = 0
    for sample in samples:
        segments = segment_text(sample, settings.max_segment_chars)
        _, max_score = detector.score_segments(segments)
        if max_score >= settings.threshold:
            blocked += 1
    total = len(samples)
    rate = blocked / total if total else 0.0
    if expected_blocked:
        return {"blocked": blocked, "total": total, "block_rate": round(rate, 4)}
    return {"false_positives": blocked, "total": total, "fpr": round(rate, 4)}


def main() -> None:
    baseline = run_baseline_attacks()
    attack_texts = [f"{a['context']}\n{a['query']}" for a in ATTACKS]
    latency = benchmark_latency(attack_texts + BENIGN)
    attack_eval = evaluate_proxy(attack_texts, expected_blocked=True)
    benign_eval = evaluate_proxy(BENIGN, expected_blocked=False)

    report = {
        "model": settings.model_name,
        "threshold": settings.threshold,
        "baseline_attack_success_rate": round(
            sum(1 for item in baseline if item["success"]) / len(baseline), 4
        ),
        "proxy_attack_block_rate": attack_eval["block_rate"],
        "benign_false_positive_rate": benign_eval["fpr"],
        "latency": latency,
    }

    out = Path("data/review2_benchmark.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
