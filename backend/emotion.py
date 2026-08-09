print("EMOTION MODULE LOADED WITH FIX")

import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import pickle
import os

GOEMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "neutral",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise"
]

_model = None
_tokenizer = None
_label_encoder = None
_device = None

MODEL_DIR = "emotion_model"


def load_emotion_model():
    global _model, _tokenizer, _label_encoder, _device

    if not os.path.exists(MODEL_DIR):
        raise RuntimeError("emotion_model/ folder not found in backend/.")

    print("Loading fine-tuned emotion model...")
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
    _model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR).to(_device)
    _model.eval()

    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
        _label_encoder = pickle.load(f)

    print(f"Emotion model loaded on {_device}. Classes: {len(_label_encoder.classes_)}")


def classify_emotion(embedding: np.ndarray, text: str) -> list[dict]:
    if _model is None:
        raise RuntimeError("Emotion model not loaded. Call load_emotion_model() first.")

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128,
    )
    inputs = {k: v.to(_device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = _model(**inputs)

    probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
    top2_indices = probs.argsort()[-2:][::-1]

    print(f"DEBUG - label 0: {GOEMOTION_LABELS[int(top2_indices[0])]}, label 1: {GOEMOTION_LABELS[int(top2_indices[1])]}")

    return [
        {
            "label": GOEMOTION_LABELS[int(idx)],
            "score": float(probs[idx]),
        }
        for idx in top2_indices
    ]
