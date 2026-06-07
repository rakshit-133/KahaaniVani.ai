import torch
import numpy as np
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset
from torch.utils.data import Dataset
from sklearn.preprocessing import LabelEncoder
import os
import pickle

_model = None
_tokenizer = None
_label_encoder = None
_device = None

MODEL_DIR = "emotion_model"


class EmotionDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def train_emotion_model():
    print("Downloading GoEmotions dataset...")
    dataset = load_dataset("google-research-datasets/go_emotions", "simplified")

    train_data = dataset["train"]
    texts = train_data["text"]
    raw_labels = [item[0] if len(item) > 0 else 0 for item in train_data["labels"]]

    le = LabelEncoder()
    encoded_labels = le.fit_transform(raw_labels)

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)

    split_idx = int(len(texts) * 0.9)
    train_dataset = EmotionDataset(
        {k: v[:split_idx] for k, v in encodings.items()},
        encoded_labels[:split_idx].tolist(),
    )
    eval_dataset = EmotionDataset(
        {k: v[split_idx:] for k, v in encodings.items()},
        encoded_labels[split_idx:].tolist(),
    )

    num_labels = len(le.classes_)
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=num_labels
    )

    training_args = TrainingArguments(
        output_dir=MODEL_DIR,
        num_train_epochs=2,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=64,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=100,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    print("Fine-tuning DistilBERT on GoEmotions (this takes 5-10 mins on CPU)...")
    trainer.train()

    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "wb") as f:
        pickle.dump(le, f)

    print(f"Model saved to {MODEL_DIR}/")


def load_emotion_model():
    global _model, _tokenizer, _label_encoder, _device

    if not os.path.exists(MODEL_DIR):
        print("No trained model found. Starting fine-tuning...")
        train_emotion_model()

    print("Loading fine-tuned emotion model...")
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
    _model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR).to(_device)
    _model.eval()

    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
        _label_encoder = pickle.load(f)

    print(f"Emotion model loaded on {_device}.")


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

    return [
        {
            "label": _label_encoder.inverse_transform([idx])[0],
            "score": float(probs[idx]),
        }
        for idx in top2_indices
    ]