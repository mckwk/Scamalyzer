#!/usr/bin/env python3
"""
Local evaluation script for multilingual scam detection models.
Loads trained models and evaluates on test datasets with confusion matrices.
"""

import os
import json
import time
import gc
import random
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
import torch
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from transformers import AutoTokenizer, AutoModelForSequenceClassification, PreTrainedTokenizerFast

# ============================================================================
# CONFIGURATION
# ============================================================================

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
RESULTS_DIR = os.path.join(BASE_DIR, "evaluation_results")

os.makedirs(RESULTS_DIR, exist_ok=True)

DATASET_PATHS = {
    "en": os.path.join(DATASET_DIR, "anonymized_dataset.csv"),
    "es": os.path.join(DATASET_DIR, "anonymized_dataset_es.csv"),
    "de": os.path.join(DATASET_DIR, "anonymized_dataset_de.csv"),
}

BERT_OUTPUT_DIR = os.path.join(BASE_DIR, "DistilBERT")
BILSTM_DIR = os.path.join(BASE_DIR, "bilstm")
XGBOOST_DIR = os.path.join(BASE_DIR, "xgboost")

BASE_TOKENIZER_BY_LANG = {
    "en": "distilbert-base-uncased",
    "es": "dccuchile/distilbert-base-spanish-uncased",
    "de": "distilbert-base-german-cased",
}

BERT_BATCH_SIZE_EVAL = 64

# ============================================================================
# UTILITIES
# ============================================================================


def log_step(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)

def plot_cm_and_save(cm, title, filename):
    """Plot and save confusion matrix as image."""
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Legit (0)", "Fraud (1)"],
        yticklabels=["Legit (0)", "Fraud (1)"],
    )
    plt.title(title, fontsize=14, fontweight="bold")
    plt.ylabel("True Label", fontsize=12)
    plt.xlabel("Predicted Label", fontsize=12)
    plt.tight_layout()
    
    filepath = os.path.join(RESULTS_DIR, filename)
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    print(f"  Saved: {filepath}")
    plt.close()


def load_distilbert_tokenizer(model_path, lang):
    """Load tokenizer from local tokenizer.json first, then fallback to base checkpoint."""
    tokenizer_json_path = os.path.join(model_path, "tokenizer.json")
    try:
        if os.path.exists(tokenizer_json_path):
            return PreTrainedTokenizerFast(
                tokenizer_file=tokenizer_json_path,
                unk_token="[UNK]",
                sep_token="[SEP]",
                pad_token="[PAD]",
                cls_token="[CLS]",
                mask_token="[MASK]",
            )
        return AutoTokenizer.from_pretrained(model_path, use_fast=True, local_files_only=True)
    except Exception as e:
        print(f"  Warning: local tokenizer load failed for {lang} ({e})")
        fallback_name = BASE_TOKENIZER_BY_LANG[lang]
        print(f"  Falling back to base tokenizer: {fallback_name}")
        return AutoTokenizer.from_pretrained(fallback_name, use_fast=True)


def predict_distilbert_batched(model, tokenizer, texts, batch_size=BERT_BATCH_SIZE_EVAL):
    """Run DistilBERT prediction in batches to keep memory usage stable."""
    all_preds = []
    total = len(texts)
    n_batches = (total + batch_size - 1) // batch_size
    log_step(f"Running DistilBERT inference in {n_batches} batches (batch_size={batch_size})")

    for batch_idx, i in enumerate(range(0, total, batch_size), start=1):
        batch_texts = texts[i : i + batch_size]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
        if "token_type_ids" in inputs:
            del inputs["token_type_ids"]
        with torch.no_grad():
            outputs = model(**inputs)
        batch_preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
        all_preds.extend(batch_preds.tolist())

        if batch_idx % 5 == 0 or batch_idx == n_batches:
            done = min(batch_idx * batch_size, total)
            pct = (done / total) * 100
            log_step(f"DistilBERT batches: {batch_idx}/{n_batches} ({done}/{total}, {pct:.1f}%)")

    return np.array(all_preds)


class CompatibleEmbedding(tf.keras.layers.Embedding):
    @classmethod
    def from_config(cls, config):
        config = dict(config)
        config.pop("quantization_config", None)
        return cls(**config)


class CompatibleDense(tf.keras.layers.Dense):
    @classmethod
    def from_config(cls, config):
        config = dict(config)
        config.pop("quantization_config", None)
        return cls(**config)

# ============================================================================
# LOAD TEST DATA
# ============================================================================

print("\n" + "=" * 80)
print("LOADING TEST DATA")
print("=" * 80)

test_data_by_lang = {}
for lang in ["en", "es", "de"]:
    if not os.path.exists(DATASET_PATHS[lang]):
        print(f"  WARNING: Missing dataset: {DATASET_PATHS[lang]}")
        continue
    
    df = pd.read_csv(DATASET_PATHS[lang])
    df = df.dropna(subset=["message", "label"]).copy()
    df["label"] = df["label"].astype(int)
    df["language"] = lang
    
    # Use up to 2000 samples for evaluation
    test_sample = df.sample(n=min(2000, len(df)), random_state=SEED)
    test_data_by_lang[lang] = {
        "texts": test_sample["message"].tolist(),
        "labels": test_sample["label"].values,
    }
    print(f"  ✓ {lang.upper()}: Loaded {len(test_sample)} samples")

# ============================================================================
# DISTILBERT EVALUATION
# ============================================================================

print("\n" + "=" * 80)
print("DISTILBERT INFERENCE TIMES & CONFUSION MATRICES")
print("=" * 80)

bert_inference_times = {}
bert_results = {}

for lang in ["en", "es", "de"]:
    model_path = os.path.join(BERT_OUTPUT_DIR, lang)
    
    if not os.path.exists(model_path):
        print(f"  WARNING: Skipping {lang}: model not found at {model_path}")
        continue
    
    if lang not in test_data_by_lang:
        print(f"  WARNING: Skipping {lang}: no test data")
        continue

    lang_start = time.time()
    model = None
    tokenizer = None
    try:
        print(f"\n  Loading DistilBERT for {lang.upper()}...")
        log_step(f"[{lang.upper()}][DistilBERT] Loading model from disk")
        t0 = time.time()
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        log_step(f"[{lang.upper()}][DistilBERT] Model loaded in {time.time() - t0:.2f}s")

        log_step(f"[{lang.upper()}][DistilBERT] Loading tokenizer")
        t0 = time.time()
        tokenizer = load_distilbert_tokenizer(model_path, lang)
        log_step(f"[{lang.upper()}][DistilBERT] Tokenizer loaded in {time.time() - t0:.2f}s")
        model.eval()

        texts = test_data_by_lang[lang]["texts"]
        true_labels = test_data_by_lang[lang]["labels"]

        # Inference timing
        start_time = time.time()
        preds = predict_distilbert_batched(model, tokenizer, texts)
        inference_time = time.time() - start_time

        bert_inference_times[lang] = inference_time / len(texts)

        cm = confusion_matrix(true_labels, preds)
        acc = accuracy_score(true_labels, preds)
        prec = precision_score(true_labels, preds, zero_division=0)
        rec = recall_score(true_labels, preds, zero_division=0)
        f1_val = f1_score(true_labels, preds, zero_division=0)

        bert_results[lang] = {
            "samples": len(texts),
            "inference_time_per_sample": bert_inference_times[lang],
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1_val,
        }

        print(f"  Samples: {len(texts)}")
        print(f"  Avg inference time: {bert_inference_times[lang]:.6f}s per sample")
        print(f"  Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1_val:.4f}")

        # Save confusion matrix image
        plot_cm_and_save(cm, f"DistilBERT - {lang.upper()}", f"distilbert_{lang}_cm.png")
        log_step(f"[{lang.upper()}][DistilBERT] Completed in {time.time() - lang_start:.2f}s")
    except Exception as e:
        print(f"  ERROR: DistilBERT evaluation failed for {lang.upper()}: {e}")
    finally:
        del model, tokenizer
        gc.collect()

# ============================================================================
# BILSTM EVALUATION
# ============================================================================

print("\n" + "=" * 80)
print("BILSTM INFERENCE TIMES & CONFUSION MATRICES")
print("=" * 80)

bilstm_inference_times = {}
bilstm_results = {}

for lang in ["en", "es", "de"]:
    model_path = os.path.join(BILSTM_DIR, f"bilstm_model_{lang}.h5")
    tokenizer_path = os.path.join(BILSTM_DIR, f"bilstm_tokenizer_{lang}.json")
    
    if not os.path.exists(model_path) or not os.path.exists(tokenizer_path):
        print(f"  WARNING: Skipping {lang}: model/tokenizer not found")
        continue
    
    if lang not in test_data_by_lang:
        print(f"  WARNING: Skipping {lang}: no test data")
        continue

    lang_start = time.time()
    model = None
    tokenizer = None
    try:
        print(f"\n  Loading BiLSTM for {lang.upper()}...")
        log_step(f"[{lang.upper()}][BiLSTM] Loading model")
        t0 = time.time()
        model = tf.keras.models.load_model(
            model_path,
            compile=False,
            custom_objects={"Embedding": CompatibleEmbedding, "Dense": CompatibleDense},
        )
        log_step(f"[{lang.upper()}][BiLSTM] Model loaded in {time.time() - t0:.2f}s")
        log_step(f"[{lang.upper()}][BiLSTM] Loading tokenizer")
        t0 = time.time()
        with open(tokenizer_path, "r", encoding="utf-8") as f:
            tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(f.read())
        log_step(f"[{lang.upper()}][BiLSTM] Tokenizer loaded in {time.time() - t0:.2f}s")

        texts = test_data_by_lang[lang]["texts"]
        true_labels = test_data_by_lang[lang]["labels"]

        # Preprocess
        seqs = tokenizer.texts_to_sequences(texts)
        X = tf.keras.preprocessing.sequence.pad_sequences(seqs, maxlen=200, padding="post", truncating="post")

        # Inference timing
        start_time = time.time()
        probs = model.predict(X, verbose=0).reshape(-1)
        inference_time = time.time() - start_time
        preds = (probs > 0.5).astype(int)

        bilstm_inference_times[lang] = inference_time / len(texts)

        cm = confusion_matrix(true_labels, preds)
        acc = accuracy_score(true_labels, preds)
        prec = precision_score(true_labels, preds, zero_division=0)
        rec = recall_score(true_labels, preds, zero_division=0)
        f1_val = f1_score(true_labels, preds, zero_division=0)

        bilstm_results[lang] = {
            "samples": len(texts),
            "inference_time_per_sample": bilstm_inference_times[lang],
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1_val,
        }

        print(f"  Samples: {len(texts)}")
        print(f"  Avg inference time: {bilstm_inference_times[lang]:.6f}s per sample")
        print(f"  Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1_val:.4f}")

        # Save confusion matrix image
        plot_cm_and_save(cm, f"BiLSTM - {lang.upper()}", f"bilstm_{lang}_cm.png")
        log_step(f"[{lang.upper()}][BiLSTM] Completed in {time.time() - lang_start:.2f}s")
    except Exception as e:
        print(f"  ERROR: BiLSTM evaluation failed for {lang.upper()}: {e}")
    finally:
        del model, tokenizer
        gc.collect()

# ============================================================================
# XGBOOST EVALUATION
# ============================================================================

print("\n" + "=" * 80)
print("XGBOOST INFERENCE TIMES & CONFUSION MATRICES")
print("=" * 80)

xgb_inference_times = {}
xgb_results = {}

for lang in ["en", "es", "de"]:
    model_path = os.path.join(XGBOOST_DIR, f"xgb_model_{lang}.joblib")
    tfidf_path = os.path.join(XGBOOST_DIR, f"tfidf_{lang}.joblib")
    
    if not os.path.exists(model_path) or not os.path.exists(tfidf_path):
        print(f"  WARNING: Skipping {lang}: model/tfidf not found")
        continue
    
    if lang not in test_data_by_lang:
        print(f"  WARNING: Skipping {lang}: no test data")
        continue

    lang_start = time.time()
    clf = None
    tfidf = None
    try:
        print(f"\n  Loading XGBoost for {lang.upper()}...")
        log_step(f"[{lang.upper()}][XGBoost] Loading model and vectorizer")
        t0 = time.time()
        clf = joblib.load(model_path)
        tfidf = joblib.load(tfidf_path)
        log_step(f"[{lang.upper()}][XGBoost] Artifacts loaded in {time.time() - t0:.2f}s")

        texts = test_data_by_lang[lang]["texts"]
        true_labels = test_data_by_lang[lang]["labels"]

        # Inference timing
        start_time = time.time()
        X = tfidf.transform(texts)
        probs = clf.predict_proba(X)[:, 1]
        inference_time = time.time() - start_time
        preds = (probs > 0.5).astype(int)

        xgb_inference_times[lang] = inference_time / len(texts)

        cm = confusion_matrix(true_labels, preds)
        acc = accuracy_score(true_labels, preds)
        prec = precision_score(true_labels, preds, zero_division=0)
        rec = recall_score(true_labels, preds, zero_division=0)
        f1_val = f1_score(true_labels, preds, zero_division=0)

        xgb_results[lang] = {
            "samples": len(texts),
            "inference_time_per_sample": xgb_inference_times[lang],
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1_val,
        }

        print(f"  Samples: {len(texts)}")
        print(f"  Avg inference time: {xgb_inference_times[lang]:.6f}s per sample")
        print(f"  Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1_val:.4f}")

        # Save confusion matrix image
        plot_cm_and_save(cm, f"XGBoost - {lang.upper()}", f"xgboost_{lang}_cm.png")
        log_step(f"[{lang.upper()}][XGBoost] Completed in {time.time() - lang_start:.2f}s")
    except Exception as e:
        print(f"  ERROR: XGBoost evaluation failed for {lang.upper()}: {e}")
    finally:
        del clf, tfidf
        gc.collect()

# ============================================================================
# SUMMARY TABLE
# ============================================================================

print("\n" + "=" * 80)
print("INFERENCE TIME SUMMARY (seconds per sample)")
print("=" * 80)

summary_data = {}
for lang in ["en", "es", "de"]:
    summary_data[lang] = {
        "DistilBERT": bert_inference_times.get(lang, None),
        "BiLSTM": bilstm_inference_times.get(lang, None),
        "XGBoost": xgb_inference_times.get(lang, None),
    }

summary_df = pd.DataFrame(summary_data).T
print(summary_df.to_string())

print("\nFastest model per language:")
for lang in ["en", "es", "de"]:
    if lang in summary_df.index:
        row = summary_df.loc[lang]
        valid = row.dropna()
        if len(valid) > 0:
            fastest = valid.idxmin()
            fastest_time = valid.min()
            print(f"  {lang.upper()}: {fastest} ({fastest_time:.6f}s)")

# ============================================================================
# SAVE RESULTS TO JSON
# ============================================================================

results = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "distilbert": bert_results,
    "bilstm": bilstm_results,
    "xgboost": xgb_results,
}

results_file = os.path.join(RESULTS_DIR, "evaluation_results.json")
with open(results_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"\n✓ Results saved to: {results_file}")

print("\n" + "=" * 80)
print("EVALUATION COMPLETE")
print("=" * 80)
print(f"Confusion matrix images saved to: {RESULTS_DIR}")
print(f"Results JSON saved to: {results_file}")
