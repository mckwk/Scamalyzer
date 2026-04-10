# train_bert.py
import os
import sys

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          EarlyStoppingCallback, Trainer, TrainingArguments)

from utils.config import (BERT_MODEL_PATH, MULTILINGUAL_BERT_MODEL_NAME,
                          MULTILINGUAL_DATASET_PATH, get_dataset_paths)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SEED = 42
MODEL_NAME = MULTILINGUAL_BERT_MODEL_NAME
MAX_LEN = 256
BATCH_SIZE = 16
EPOCHS = 4
OUTPUT_DIR = BERT_MODEL_PATH


def load_multilingual_dataset():
    if os.path.exists(MULTILINGUAL_DATASET_PATH):
        df = pd.read_csv(MULTILINGUAL_DATASET_PATH)
        if "language" not in df.columns:
            df["language"] = "en"
        return df

    frames = []
    for language, dataset_path in get_dataset_paths().items():
        if not os.path.exists(dataset_path):
            continue
        data = pd.read_csv(dataset_path)
        data["language"] = language
        frames.append(data)

    if not frames:
        raise FileNotFoundError("No multilingual dataset files were found.")

    merged = pd.concat(frames, ignore_index=True)
    os.makedirs(os.path.dirname(MULTILINGUAL_DATASET_PATH), exist_ok=True)
    merged.to_csv(MULTILINGUAL_DATASET_PATH, index=False)
    return merged


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
    }


df = load_multilingual_dataset()
df = df.dropna(subset=["message", "label"])
df["label"] = df["label"].astype(int)
df["language"] = df["language"].fillna("en").astype(str)
df["stratify_key"] = df["label"].astype(str) + "_" + df["language"]

# Split data
train_df, test_df = train_test_split(
    df, test_size=0.2, stratify=df["stratify_key"], random_state=SEED)
train_df, val_df = train_test_split(
    train_df, test_size=0.125, stratify=train_df["stratify_key"], random_state=SEED)

# Tokenization
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def preprocess(batch):
    return tokenizer(batch["message"], truncation=True, padding="max_length", max_length=MAX_LEN)


train_ds = Dataset.from_pandas(train_df).map(preprocess, batched=True)
val_ds = Dataset.from_pandas(val_df).map(preprocess, batched=True)
test_ds = Dataset.from_pandas(test_df).map(preprocess, batched=True)

cols = ["input_ids", "attention_mask", "label"]
train_ds.set_format(type="torch", columns=cols)
val_ds.set_format(type="torch", columns=cols)
test_ds.set_format(type="torch", columns=cols)

# Model
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2)

# Training
args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    learning_rate=2e-5,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    metric_for_best_model="f1",
    save_total_limit=2,
    seed=SEED,
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
)

trainer.train()
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
