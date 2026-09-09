from app.normalize import normalize_text, segment_text


def test_normalize_collapses_whitespace():
    assert normalize_text("  hello   world  ") == "hello world"


def test_segment_splits_long_text():
    text = "word " * 200
    segments = segment_text(text, max_chars=100)
    assert len(segments) > 1
    assert all(len(segment) <= 100 for segment in segments)
