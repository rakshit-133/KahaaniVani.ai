VAD_MAP = {
    "admiration":     {"v":  0.80, "a":  0.40, "d":  0.30},
    "amusement":      {"v":  0.85, "a":  0.55, "d":  0.20},
    "anger":          {"v": -0.65, "a":  0.85, "d":  0.75},
    "annoyance":      {"v": -0.50, "a":  0.55, "d":  0.35},
    "approval":       {"v":  0.70, "a":  0.20, "d":  0.40},
    "caring":         {"v":  0.75, "a":  0.30, "d":  0.20},
    "confusion":      {"v": -0.20, "a":  0.30, "d": -0.30},
    "curiosity":      {"v":  0.40, "a":  0.60, "d":  0.10},
    "desire":         {"v":  0.60, "a":  0.70, "d":  0.20},
    "disappointment": {"v": -0.65, "a": -0.30, "d": -0.20},
    "disapproval":    {"v": -0.55, "a":  0.40, "d":  0.45},
    "disgust":        {"v": -0.70, "a":  0.45, "d":  0.55},
    "embarrassment":  {"v": -0.45, "a":  0.35, "d": -0.55},
    "excitement":     {"v":  0.80, "a":  0.90, "d":  0.50},
    "fear":           {"v": -0.70, "a":  0.75, "d": -0.65},
    "gratitude":      {"v":  0.85, "a":  0.30, "d":  0.15},
    "grief":          {"v": -0.80, "a": -0.40, "d": -0.50},
    "joy":            {"v":  0.90, "a":  0.65, "d":  0.55},
    "love":           {"v":  0.90, "a":  0.45, "d":  0.25},
    "nervousness":    {"v": -0.40, "a":  0.70, "d": -0.45},
    "neutral":        {"v":  0.00, "a":  0.00, "d":  0.00},
    "optimism":       {"v":  0.75, "a":  0.45, "d":  0.35},
    "pride":          {"v":  0.75, "a":  0.55, "d":  0.70},
    "realization":    {"v":  0.15, "a":  0.30, "d":  0.10},
    "relief":         {"v":  0.70, "a": -0.25, "d":  0.20},
    "remorse":        {"v": -0.70, "a": -0.20, "d": -0.40},
    "sadness":        {"v": -0.75, "a": -0.35, "d": -0.45},
    "surprise":       {"v":  0.20, "a":  0.75, "d": -0.10},
}


def blend_vad(emotions: list[dict]) -> dict:
    total_score = sum(e["score"] for e in emotions)
    if total_score == 0:
        return {"v": 0.0, "a": 0.0, "d": 0.0}

    v = a = d = 0.0
    for e in emotions:
        weight = e["score"] / total_score
        coords = VAD_MAP.get(e["label"].lower(), {"v": 0.0, "a": 0.0, "d": 0.0})
        v += weight * coords["v"]
        a += weight * coords["a"]
        d += weight * coords["d"]

    return {"v": round(v, 3), "a": round(a, 3), "d": round(d, 3)}