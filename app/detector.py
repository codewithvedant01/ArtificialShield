from dataclasses import dataclass
import gc
import time

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from config import settings


@dataclass
class SegmentScore:
    text: str
    score: float
    label: str


class InjectionDetector:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            settings.model_name,
            low_cpu_mem_usage=True,
        )
        self.model.eval()
        torch.set_num_threads(1)
        gc.collect()

    def score_segment(self, text: str) -> SegmentScore:
        scored, _ = self.score_segments([text])
        return scored[0]

    def score_segments(self, segments: list[str]) -> tuple[list[SegmentScore], float]:
        if not segments:
            return [], 0.0

        # Batch tokenization for high-throughput parallel inference
        inputs = self.tokenizer(
            segments,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)

        injection_idx = 1 if self.model.config.num_labels == 2 else 0
        results: list[SegmentScore] = []
        for i, segment in enumerate(segments):
            score = float(probs[i, injection_idx])
            label = "INJECTION" if score >= settings.threshold else "BENIGN"
            results.append(SegmentScore(text=segment, score=score, label=label))

        max_score = max(item.score for item in results) if results else 0.0
        return results, max_score
