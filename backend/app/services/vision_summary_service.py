"""
AI summary of YOLOv8 object-detection results — a real call to the Anthropic
API (via the official `anthropic` Python SDK) when ANTHROPIC_API_KEY is set,
with an honest template-based fallback otherwise. Same gating pattern as
hedera_service.py: never fake a "real LLM" response when one wasn't made.
"""
import os
from typing import List, Dict

try:
    import anthropic
    _ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    _ANTHROPIC_SDK_AVAILABLE = False


def status() -> dict:
    if not _ANTHROPIC_SDK_AVAILABLE:
        return {"configured": False, "reason": "anthropic package not installed"}
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {"configured": False, "reason": "ANTHROPIC_API_KEY not set — using template summaries"}
    return {"configured": True}


def _template_summary(detections: List[Dict]) -> str:
    if not detections:
        return "No objects were detected above the confidence threshold, so there's nothing to summarize."
    counts: Dict[str, int] = {}
    for d in detections:
        counts[d["label"]] = counts.get(d["label"], 0) + 1
    parts = [f"{n} {label}s" if n > 1 else f"a {label}" for label, n in counts.items()]
    top = max(detections, key=lambda d: d["confidence"])
    return (
        f"This image contains {', '.join(parts)}. The most confident detection is "
        f"\"{top['label']}\" at {top['confidence']*100:.0f}%. "
        f"(Template summary — set ANTHROPIC_API_KEY for a real LLM-written summary.)"
    )


def summarize(detections: List[Dict]) -> dict:
    """Returns {"summary": str, "source": "llm" | "template"}."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not (_ANTHROPIC_SDK_AVAILABLE and api_key):
        return {"summary": _template_summary(detections), "source": "template"}

    if not detections:
        return {"summary": _template_summary(detections), "source": "template"}

    detection_list = "\n".join(
        f"- {d['label']} (confidence {d['confidence']*100:.0f}%)" for d in detections
    )
    prompt = (
        "A general-purpose YOLOv8 object detector (COCO classes — everyday objects, "
        "not a medical image classifier) found the following in a user-uploaded photo:\n\n"
        f"{detection_list}\n\n"
        "Write a 1-2 sentence, plain-language summary of what the image likely shows. "
        "Do not invent details beyond what these labels support, and do not make any "
        "medical or diagnostic claims."
    )
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        return {"summary": text or _template_summary(detections), "source": "llm"}
    except Exception:
        # Never fail the request over a flaky/misconfigured LLM call — degrade honestly.
        return {"summary": _template_summary(detections), "source": "template"}
