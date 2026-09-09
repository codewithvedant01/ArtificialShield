from dataclasses import dataclass
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
        self.model = AutoModelForSequenceClassification.from_pretrained(settings.model_name)
        self.model.eval()
        torch.set_num_threads(max(1, torch.get_num_threads()))

    def score_segment(self, text: str) -> SegmentScore:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        start = time.perf_counter()
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0]
        _ = (time.perf_counter() - start) * 1000

        injection_idx = 1 if self.model.config.num_labels == 2 else 0
        score = float(probs[injection_idx])
        label = "INJECTION" if score >= settings.threshold else "BENIGN"
        return SegmentScore(text=text, score=score, label=label)

    def score_segments(self, segments: list[str]) -> tuple[list[SegmentScore], float]:
        if not segments:
            return [], 0.0
        results = [self.score_segment(segment) for segment in segments]
        max_score = max(item.score for item in results)
        return results, max_score
