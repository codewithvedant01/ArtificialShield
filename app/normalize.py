import base64
import html
import re
import unicodedata

# Unicode invisible characters often used for tokenizer evasion
ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E]")
# ASCII control characters excluding newline and tab
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def normalize_text(text: str) -> str:
    """Normalize text against unicode evasion, invisible characters, and whitespace anomalies."""
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Strip zero-width and invisible characters
    text = ZERO_WIDTH_CHARS.sub("", text)
    # Strip dangerous non-printable control characters
    text = CONTROL_CHARS.sub("", text)
    # Canonical Unicode decomposition/composition
    text = unicodedata.normalize("NFKC", text)
    # Unify line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse irregular whitespace
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_encoded_payloads(text: str, max_depth: int = 3, max_size: int = 1024 * 100) -> list[str]:
    """Detect and decode potential Base64 payloads hidden inside text."""
    # Cap size and depth to prevent DoS via recursive/massive decompression
    if max_depth <= 0 or len(text) > max_size:
        return []
        
    candidates: list[str] = []
    # Match potential base64 tokens of at least 16 characters
    tokens = re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", text)
    for token in tokens:
        try:
            raw = base64.b64decode(token).decode("utf-8", errors="ignore").strip()
            # Verify decoded content is meaningful text (at least 6 readable characters)
            if len(raw) >= 6 and all(c.isprintable() or c in "\n\t" for c in raw):
                norm = normalize_text(raw)
                candidates.append(norm)
                # Recursively extract if nested
                nested = extract_encoded_payloads(raw, max_depth=max_depth - 1, max_size=max_size)
                candidates.extend(nested)
        except Exception:
            continue
    return candidates


def segment_text(text: str, max_chars: int = 512, overlap: int = 64) -> list[str]:
    """Split text into segments using an overlapping sliding window to prevent boundary escapes."""
    text = normalize_text(text)
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    segments: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            split_at = text.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        chunk = text[start:end].strip()
        if chunk and (not segments or chunk != segments[-1]):
            segments.append(chunk)
        if end >= len(text):
            break
        # Apply sliding window overlap to catch boundary-spanning attacks
        next_start = end - overlap if (end - overlap) > start else end
        start = next_start

    return segments
