"""
data_prep.py
------------
Step 2: Dataset Preparation

Downloads and merges multiple emotion datasets into a single
training-ready CSV file. Run this BEFORE fine-tuning.

Datasets included:
  1. GoEmotions (Google, 58k) — base dataset, all 28 classes
  2. ISEAR (7.6k) — personal event narratives, 7 emotions
  3. Your manual labels (if manual_labels.csv exists)

Output: training/data/combined_train.csv
         training/data/combined_val.csv

Usage (from backend/ folder):
    python training/data_prep.py
"""

import os
import requests
import pandas as pd
import numpy as np
from datasets import load_dataset
from tqdm import tqdm

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

# ── GoEmotions label list (28 classes) ───────────────────────────────────────
GOEMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval",
    "caring", "confusion", "curiosity", "desire", "disappointment",
    "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "neutral",
    "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise"
]
LABEL2IDX = {l: i for i, l in enumerate(GOEMOTION_LABELS)}

# ── ISEAR → GoEmotions label mapping ─────────────────────────────────────────
# ISEAR has 7 basic emotions. We map each to the closest GoEmotions label.
ISEAR_MAP = {
    "joy":     "joy",
    "fear":    "fear",
    "anger":   "anger",
    "sadness": "sadness",
    "disgust": "disgust",
    "shame":   "embarrassment",  # closest GoEmotions equivalent
    "guilt":   "remorse",        # closest GoEmotions equivalent
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. GoEmotions
# ─────────────────────────────────────────────────────────────────────────────
def load_goemotion() -> pd.DataFrame:
    print("\n[1/3] Loading GoEmotions dataset...")
    dataset = load_dataset("google-research-datasets/go_emotions", "simplified")

    rows = []
    for split in ["train", "validation", "test"]:
        for ex in tqdm(dataset[split], desc=f"  {split}"):
            if not ex["labels"]:
                continue
            # Take the first label for single-label training
            label_idx = ex["labels"][0]
            label_name = GOEMOTION_LABELS[label_idx]
            rows.append({
                "text":   ex["text"],
                "label":  label_name,
                "label_idx": label_idx,
                "source": f"goemotion_{split}",
                "split":  "val" if split in ("validation", "test") else "train",
            })

    df = pd.DataFrame(rows)
    print(f"  GoEmotions: {len(df)} examples | "
          f"Train: {(df.split=='train').sum()} | Val: {(df.split=='val').sum()}")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. ISEAR
# ─────────────────────────────────────────────────────────────────────────────
def load_isear() -> pd.DataFrame:
    print("\n[2/3] Downloading ISEAR dataset...")

    # ISEAR is publicly available via this GitHub mirror
    url = "https://raw.githubusercontent.com/sinmaniphel/py_isear_dataset/master/isear.csv"
    cache_path = os.path.join(OUT_DIR, "isear_raw.csv")

    if not os.path.exists(cache_path):
        print("  Downloading from GitHub...")
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            print(f"  WARNING: Could not download ISEAR (status {r.status_code}). Skipping.")
            return pd.DataFrame()
        with open(cache_path, "wb") as f:
            f.write(r.content)
        print("  Downloaded.")
    else:
        print("  Using cached ISEAR file.")

    try:
        raw = pd.read_csv(cache_path, sep="|", on_bad_lines="skip")
        # The ISEAR dataset columns vary by mirror; try to find the right ones
        # Common columns: Field1 (emotion), Field2 (situation text)
        if "Field1" in raw.columns and "Field2" in raw.columns:
            raw = raw.rename(columns={"Field1": "emotion", "Field2": "text"})
        elif "EMOT" in raw.columns and "SIT" in raw.columns:
            raw = raw.rename(columns={"EMOT": "emotion", "SIT": "text"})
        else:
            print(f"  WARNING: Unexpected ISEAR columns: {raw.columns.tolist()}. Skipping.")
            return pd.DataFrame()

        raw["emotion"] = raw["emotion"].astype(str).str.strip().str.lower()
        raw = raw[raw["emotion"].isin(ISEAR_MAP.keys())].copy()
        raw["label"]     = raw["emotion"].map(ISEAR_MAP)
        raw["label_idx"] = raw["label"].map(LABEL2IDX)
        raw["source"]    = "isear"
        raw["split"]     = "train"  # all ISEAR goes to training
        raw = raw[["text", "label", "label_idx", "source", "split"]].dropna()

        print(f"  ISEAR: {len(raw)} examples loaded.")
        return raw

    except Exception as e:
        print(f"  WARNING: Failed to parse ISEAR ({e}). Skipping.")
        return pd.DataFrame()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Manual Labels (your hand-labeled story excerpts)
# ─────────────────────────────────────────────────────────────────────────────
def load_manual_labels() -> pd.DataFrame:
    manual_path = os.path.join(OUT_DIR, "manual_labels.csv")
    if not os.path.exists(manual_path):
        print(f"\n[3/3] No manual_labels.csv found at {manual_path}. Skipping.")
        print("      (Run label_gutenberg.py to create this file.)")
        return pd.DataFrame()

    print(f"\n[3/3] Loading manual labels from {manual_path}...")
    df = pd.read_csv(manual_path)

    # Validate expected columns
    required = {"text", "label"}
    if not required.issubset(df.columns):
        print(f"  WARNING: manual_labels.csv must have columns: {required}. Found: {df.columns.tolist()}")
        return pd.DataFrame()

    df["label"]     = df["label"].str.strip().str.lower()
    df = df[df["label"].isin(GOEMOTION_LABELS)].copy()
    df["label_idx"] = df["label"].map(LABEL2IDX)
    df["source"]    = "manual"
    df["split"]     = "train"
    df = df[["text", "label", "label_idx", "source", "split"]].dropna()

    print(f"  Manual labels: {len(df)} examples loaded.")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("KahaaniVani.ai — Dataset Preparation")
    print("=" * 60)

    # Load all sources
    goemotion_df = load_goemotion()
    isear_df     = load_isear()
    manual_df    = load_manual_labels()

    # Merge
    all_dfs = [df for df in [goemotion_df, isear_df, manual_df] if len(df) > 0]
    combined = pd.concat(all_dfs, ignore_index=True)

    # Shuffle
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    # Split
    train_df = combined[combined["split"] == "train"].reset_index(drop=True)
    val_df   = combined[combined["split"] == "val"].reset_index(drop=True)

    # Stats
    print("\n" + "=" * 60)
    print("COMBINED DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total:      {len(combined):,} examples")
    print(f"  Train:      {len(train_df):,}")
    print(f"  Validation: {len(val_df):,}")
    print(f"\n  Sources:")
    for src, count in combined["source"].value_counts().items():
        print(f"    {src:<25} {count:>6,} examples")

    print(f"\n  Class distribution (train):")
    counts = train_df["label"].value_counts()
    for label in GOEMOTION_LABELS:
        c = counts.get(label, 0)
        bar = "█" * (c // 200)
        print(f"    {label:<20} {c:>5}  {bar}")

    # Save
    train_path = os.path.join(OUT_DIR, "combined_train.csv")
    val_path   = os.path.join(OUT_DIR, "combined_val.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path,   index=False)

    print(f"\nSaved:")
    print(f"  {train_path}")
    print(f"  {val_path}")
    print("\nNext step: Run  python training/label_gutenberg.py  to add story labels.")
    print("Then run:        python training/finetune.py  (or upload to Colab)")


if __name__ == "__main__":
    main()
