"""
finetune.py
-----------
Step 3: Fine-Tuning DistilBERT on Narrative Emotion Data

Designed to run on Google Colab (T4 GPU) or Kaggle (P100).
Also works locally on CPU (will be slow — ~8hrs for 3 epochs).

Before running:
  1. Run data_prep.py to generate combined_train.csv and combined_val.csv
  2. (Optional) Run label_gutenberg.py to add your manual story labels

Usage on Colab/Kaggle:
  - Upload this file + the data/ folder
  - pip install -r requirements_train.txt
  - python finetune.py

Usage locally (from backend/ folder):
  python training/finetune.py

Output:
  training/output/emotion_model/   ← drop-in replacement for backend/emotion_model/
"""

import os
import pickle
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
DATA_DIR  = os.path.join(BASE_DIR, "data")
OUT_DIR   = os.path.join(BASE_DIR, "output", "emotion_model")

CONFIG = {
    # Starting checkpoint — we continue fine-tuning from the GoEmotions model
    # This is the HuggingFace ID of the same architecture as your current model
    "base_model":     "bhadresh-savani/distilbert-base-uncased-emotion",

    "num_labels":     28,
    "max_length":     128,
    "batch_size":     32,       # Use 16 if you get OOM errors on GPU
    "learning_rate":  5e-5,     # Aggressive LR for fast learning
    "epochs":         4,        # Shorter run to prevent overfitting with high LR
    "warmup_ratio":   0.1,      # Standard 10% warmup
    "weight_decay":   0.01,
    "use_weighted_loss": False, # Disabled to maximize overall Macro average
    "seed":           42,

    # Paths
    "train_csv":  os.path.join(DATA_DIR, "combined_train.csv"),
    "val_csv":    os.path.join(DATA_DIR, "combined_val.csv"),
    "output_dir": OUT_DIR,
}

GOEMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "neutral",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise"
]


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────
class EmotionDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_length: int):
        self.texts  = df["text"].tolist()
        self.labels = df["label_idx"].tolist()
        self.tokenizer  = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Compute class weights (to handle GoEmotions imbalance)
# ─────────────────────────────────────────────────────────────────────────────
def compute_class_weights(df: pd.DataFrame, num_classes: int) -> torch.Tensor:
    counts = df["label_idx"].value_counts().sort_index()
    counts = counts.reindex(range(num_classes), fill_value=1)  # avoid div/0
    total  = counts.sum()
    # Inverse frequency, normalised
    weights = total / (num_classes * counts.values)
    weights = torch.tensor(weights, dtype=torch.float32)
    # Clip to avoid extreme weights for very rare classes
    weights = torch.clamp(weights, max=10.0)
    return weights


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation helper
# ─────────────────────────────────────────────────────────────────────────────
def evaluate(model, dataloader, device, desc="Val"):
    model.eval()
    all_preds, all_labels = [], []
    total_loss = 0.0

    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc=f"  {desc}", leave=False):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss    = criterion(outputs.logits, labels)
            total_loss += loss.item()

            preds = outputs.logits.argmax(dim=-1).cpu().numpy()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.cpu().numpy().tolist())

    macro_f1    = f1_score(all_labels, all_preds, average="macro",    zero_division=0)
    weighted_f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
    accuracy    = accuracy_score(all_labels, all_preds)
    avg_loss    = total_loss / len(dataloader)

    return {
        "loss":        avg_loss,
        "accuracy":    accuracy,
        "macro_f1":    macro_f1,
        "weighted_f1": weighted_f1,
        "preds":       all_preds,
        "labels":      all_labels,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main Training Loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    torch.manual_seed(CONFIG["seed"])
    np.random.seed(CONFIG["seed"])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("=" * 60)
    print("KahaaniVani.ai — DistilBERT Fine-Tuning")
    print("=" * 60)
    print(f"  Device:       {device}")
    if device == "cuda":
        print(f"  GPU:          {torch.cuda.get_device_name(0)}")
        print(f"  VRAM:         {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    print(f"  Base model:   {CONFIG['base_model']}")
    print(f"  Epochs:       {CONFIG['epochs']}")
    print(f"  Batch size:   {CONFIG['batch_size']}")
    print(f"  Learning rate:{CONFIG['learning_rate']}")
    num_gpus = torch.cuda.device_count() if device == "cuda" else 0
    if num_gpus > 1:
        print(f"  GPUs:         {num_gpus} x {torch.cuda.get_device_name(0)} (DataParallel)")

    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    # ── Load Data ──────────────────────────────────────────────────────────
    print("\nLoading datasets...")
    if not os.path.exists(CONFIG["train_csv"]):
        raise FileNotFoundError(
            f"Training data not found: {CONFIG['train_csv']}\n"
            "Run data_prep.py first!"
        )

    train_df = pd.read_csv(CONFIG["train_csv"])
    val_df   = pd.read_csv(CONFIG["val_csv"])

    print(f"  Train: {len(train_df):,} examples")
    print(f"  Val:   {len(val_df):,}   examples")

    # Build label encoder (maps label_name → index, same as your current model)
    le = LabelEncoder()
    le.classes_ = np.array(GOEMOTION_LABELS)

    # ── Load Tokenizer & Model ─────────────────────────────────────────────
    print(f"\nLoading base model: {CONFIG['base_model']}...")
    tokenizer = DistilBertTokenizerFast.from_pretrained(CONFIG["base_model"])
    model = DistilBertForSequenceClassification.from_pretrained(
        CONFIG["base_model"],
        num_labels=CONFIG["num_labels"],
        ignore_mismatched_sizes=True,  # In case the base model has different num_labels
    ).to(device)

    # ── Multi-GPU: wrap in DataParallel if 2x T4 available ─────────────────
    num_gpus = torch.cuda.device_count() if device == "cuda" else 1
    if num_gpus > 1:
        model = nn.DataParallel(model)
        # Double the batch size to fully utilize both GPUs
        CONFIG["batch_size"] = CONFIG["batch_size"] * num_gpus
        print(f"  DataParallel enabled across {num_gpus} GPUs — batch size -> {CONFIG['batch_size']}")
    print("  Model loaded.")

    # ── DataLoaders ────────────────────────────────────────────────────────
    train_dataset = EmotionDataset(train_df, tokenizer, CONFIG["max_length"])
    val_dataset   = EmotionDataset(val_df,   tokenizer, CONFIG["max_length"])

    train_loader = DataLoader(
        train_dataset, batch_size=CONFIG["batch_size"], shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        val_dataset, batch_size=CONFIG["batch_size"] * 2, shuffle=False, num_workers=0
    )

    # ── Class Weights ──────────────────────────────────────────────────────
    if CONFIG["use_weighted_loss"]:
        class_weights = compute_class_weights(train_df, CONFIG["num_labels"]).to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weights)
        print(f"\nUsing weighted cross-entropy loss (max weight: {class_weights.max():.2f})")
    else:
        criterion = nn.CrossEntropyLoss()

    # ── Optimizer & Scheduler ─────────────────────────────────────────────
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=CONFIG["learning_rate"],
        weight_decay=CONFIG["weight_decay"],
    )
    total_steps   = len(train_loader) * CONFIG["epochs"]
    warmup_steps  = int(total_steps * CONFIG["warmup_ratio"])
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    # ── Training ───────────────────────────────────────────────────────────
    best_macro_f1  = 0.0
    best_epoch     = 0
    history        = []

    print(f"\nStarting training for {CONFIG['epochs']} epochs...")
    print(f"  Total steps:  {total_steps:,}")
    print(f"  Warmup steps: {warmup_steps:,}")
    print("─" * 60)

    for epoch in range(1, CONFIG["epochs"] + 1):
        model.train()
        epoch_loss = 0.0
        t0 = time.time()

        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{CONFIG['epochs']} [Train]")
        for batch in pbar:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss    = criterion(outputs.logits, labels)
            loss.backward()

            # Gradient clipping (prevents exploding gradients)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_train_loss = epoch_loss / len(train_loader)
        elapsed = time.time() - t0

        # Validate
        val_metrics = evaluate(model, val_loader, device)

        history.append({
            "epoch":        epoch,
            "train_loss":   avg_train_loss,
            "val_loss":     val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "macro_f1":     val_metrics["macro_f1"],
            "weighted_f1":  val_metrics["weighted_f1"],
        })

        print(f"\nEpoch {epoch}/{CONFIG['epochs']}  ({elapsed:.0f}s)")
        print(f"  Train loss:   {avg_train_loss:.4f}")
        print(f"  Val loss:     {val_metrics['loss']:.4f}")
        print(f"  Val accuracy: {val_metrics['accuracy']:.4f}")
        print(f"  Macro F1:     {val_metrics['macro_f1']:.4f}  ← key metric")
        print(f"  Weighted F1:  {val_metrics['weighted_f1']:.4f}")

        # Save best model (unwrap DataParallel if needed)
        if val_metrics["macro_f1"] > best_macro_f1:
            best_macro_f1 = val_metrics["macro_f1"]
            best_epoch = epoch
            save_model = model.module if isinstance(model, nn.DataParallel) else model
            save_model.save_pretrained(CONFIG["output_dir"])
            tokenizer.save_pretrained(CONFIG["output_dir"])
            # Save label encoder (required by emotion.py)
            with open(os.path.join(CONFIG["output_dir"], "label_encoder.pkl"), "wb") as f:
                pickle.dump(le, f)
            print(f"  ✓ New best! Saved to {CONFIG['output_dir']}")

    # ── Final Report ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"  Best epoch:   {best_epoch}")
    print(f"  Best Macro F1:{best_macro_f1:.4f}")
    print(f"\nTraining history:")
    print(f"  {'Epoch':<8} {'Train Loss':<12} {'Val Loss':<12} {'Macro F1':<12} {'Weighted F1'}")
    for h in history:
        print(f"  {h['epoch']:<8} {h['train_loss']:<12.4f} {h['val_loss']:<12.4f} "
              f"{h['macro_f1']:<12.4f} {h['weighted_f1']:.4f}")

    # Final per-class report using best model
    print("\nRunning final evaluation with best model...")
    best_model = DistilBertForSequenceClassification.from_pretrained(CONFIG["output_dir"]).to(device)
    final_metrics = evaluate(best_model, val_loader, device, desc="Final Eval")
    report = classification_report(
        final_metrics["labels"],
        final_metrics["preds"],
        labels=list(range(len(GOEMOTION_LABELS))),
        target_names=GOEMOTION_LABELS,
        zero_division=0,
    )
    print(report)

    # Save report
    report_path = os.path.join(BASE_DIR, "output", "finetuned_report.txt")
    with open(report_path, "w") as f:
        f.write(f"Best Epoch:    {best_epoch}\n")
        f.write(f"Macro F1:      {best_macro_f1:.4f}\n")
        f.write(f"Weighted F1:   {final_metrics['weighted_f1']:.4f}\n")
        f.write(f"Accuracy:      {final_metrics['accuracy']:.4f}\n\n")
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"  1. Download the folder: {CONFIG['output_dir']}")
    print(f"  2. Replace backend/emotion_model/ with it")
    print(f"  3. Restart the backend server")
    print(f"  4. Run evaluate.py again to compare before/after numbers")


if __name__ == "__main__":
    main()
