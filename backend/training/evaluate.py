"""
evaluate.py
-----------
Step 1: Baseline Evaluation

Run this BEFORE any fine-tuning to get your "before" numbers.
This script evaluates your current emotion_model/ against
the GoEmotions test split and prints:
  - Macro F1, Weighted F1, Accuracy
  - Per-class precision, recall, F1
  - Confusion matrix saved as PNG

Usage (from backend/ folder):
    python training/evaluate.py

Usage (from training/ folder):
    python evaluate.py --model_dir ../emotion_model
"""

import argparse
import os
import sys
import numpy as np
import torch
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
)
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from datasets import load_dataset

# ── Label Set ────────────────────────────────────────────────────────────────
GOEMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "neutral",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise"
]


def load_model(model_dir: str):
    print(f"Loading model from: {model_dir}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
    model = DistilBertForSequenceClassification.from_pretrained(model_dir).to(device)
    model.eval()

    label_encoder_path = os.path.join(model_dir, "label_encoder.pkl")
    if os.path.exists(label_encoder_path):
        with open(label_encoder_path, "rb") as f:
            label_encoder = pickle.load(f)
        print(f"Model loaded. Classes: {len(label_encoder.classes_)}")
    else:
        label_encoder = None
        print("Model loaded (no label_encoder.pkl found, using GOEMOTION_LABELS).")

    return model, tokenizer, device, label_encoder


def predict_batch(texts, model, tokenizer, device, batch_size=32):
    all_preds = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Predicting"):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        preds = outputs.logits.argmax(dim=-1).cpu().numpy()
        all_preds.extend(preds.tolist())
    return all_preds


def goemotion_label_to_idx(label_ids: list) -> int:
    """GoEmotions is multi-label. For single-label eval, take the first label."""
    if not label_ids:
        return GOEMOTION_LABELS.index("neutral")
    # label_ids are already integer indices into GOEMOTION_LABELS
    return label_ids[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", "emotion_model"),
        help="Path to emotion_model/ directory",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "eval_results"),
        help="Where to save results",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["test", "validation"],
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Load model
    model, tokenizer, device, label_encoder = load_model(args.model_dir)

    # 2. Load GoEmotions test split
    print(f"\nLoading GoEmotions {args.split} split...")
    dataset = load_dataset("google-research-datasets/go_emotions", "simplified")
    split_data = dataset[args.split]
    print(f"  {len(split_data)} examples loaded.")

    # 3. Extract texts and true labels
    texts = [ex["text"] for ex in split_data]
    # GoEmotions simplified: each example has a list of label indices
    true_labels = [goemotion_label_to_idx(ex["labels"]) for ex in split_data]

    # 4. Run predictions
    print("\nRunning predictions...")
    pred_labels = predict_batch(texts, model, tokenizer, device)

    # 5. Compute metrics
    macro_f1  = f1_score(true_labels, pred_labels, average="macro",    zero_division=0)
    weighted_f1 = f1_score(true_labels, pred_labels, average="weighted", zero_division=0)
    accuracy  = accuracy_score(true_labels, pred_labels)

    print("\n" + "=" * 60)
    print("BASELINE EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Accuracy:     {accuracy:.4f}  ({accuracy*100:.1f}%)")
    print(f"  Macro F1:     {macro_f1:.4f}  ({macro_f1*100:.1f}%)")
    print(f"  Weighted F1:  {weighted_f1:.4f}  ({weighted_f1*100:.1f}%)")
    print("=" * 60)

    # 6. Per-class report
    report = classification_report(
        true_labels,
        pred_labels,
        labels=list(range(len(GOEMOTION_LABELS))),
        target_names=GOEMOTION_LABELS,
        zero_division=0,
    )
    print("\nPer-class Report:")
    print(report)

    # 7. Save report to file
    report_path = os.path.join(args.output_dir, "baseline_report.txt")
    with open(report_path, "w") as f:
        f.write(f"Accuracy:    {accuracy:.4f}\n")
        f.write(f"Macro F1:    {macro_f1:.4f}\n")
        f.write(f"Weighted F1: {weighted_f1:.4f}\n\n")
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # 8. Confusion matrix (top 10 most common classes for readability)
    print("\nGenerating confusion matrix...")
    cm = confusion_matrix(true_labels, pred_labels, labels=list(range(len(GOEMOTION_LABELS))))
    plt.figure(figsize=(16, 14))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=GOEMOTION_LABELS,
        yticklabels=GOEMOTION_LABELS,
    )
    plt.title("Emotion Classifier — Confusion Matrix (Baseline)", fontsize=14)
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    cm_path = os.path.join(args.output_dir, "baseline_confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    print(f"Confusion matrix saved to: {cm_path}")

    # 9. Identify worst performing classes
    per_class_f1 = f1_score(
        true_labels, pred_labels,
        labels=list(range(len(GOEMOTION_LABELS))),
        average=None,
        zero_division=0,
    )
    sorted_classes = sorted(
        zip(GOEMOTION_LABELS, per_class_f1),
        key=lambda x: x[1],
    )
    print("\nWorst performing classes (targets for fine-tuning):")
    for label, score in sorted_classes[:7]:
        print(f"  {label:<20} F1: {score:.3f}")

    print(f"\nSave these numbers! They are your BEFORE scores.")
    print(f"  Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")


if __name__ == "__main__":
    main()
