# evaluate_models.py
import os
import sys
import time

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import tokenizer_from_json
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from utils.config import FINAL_DATASET_PATH

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SEED = 42
df = pd.read_csv(FINAL_DATASET_PATH)
df = df.dropna(subset=["message", "label"])
df["label"] = df["label"].astype(int)

# Ensure same split strategy as training
train_df, test_df = train_test_split(
    df, test_size=0.2, stratify=df["label"], random_state=SEED)
_, val_df = train_test_split(
    train_df, test_size=0.125, stratify=train_df["label"], random_state=SEED)

X_test = test_df["message"].tolist()
y_test = test_df["label"].values

# Take a smaller subset for faster evaluation
N = 500  # or any number you want
X_test = X_test[:N]
y_test = y_test[:N]


results = {}

# ----------------
# 1. Evaluate BERT
# ----------------

print("Loading and evaluating BERT model...")
bert_path = "./models/bert_finetuned"
bert_tokenizer = AutoTokenizer.from_pretrained(bert_path)
bert_model = AutoModelForSequenceClassification.from_pretrained(bert_path)
bert_model.eval()


def bert_predict(texts, batch_size=32):
    preds = []
    for i in range(0, len(texts), batch_size):
        print(
            f"BERT: Predicting batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        batch_texts = texts[i:i+batch_size]
        inputs = bert_tokenizer(
            batch_texts, truncation=True, padding=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            outputs = bert_model(**inputs)
        batch_preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
        preds.extend(batch_preds)
    return np.array(preds)


start = time.time()
bert_preds = bert_predict(X_test)
bert_infer_time = time.time() - start
results["BERT"] = {
    "accuracy": accuracy_score(y_test, bert_preds),
    "precision": precision_score(y_test, bert_preds),
    "recall": recall_score(y_test, bert_preds),
    "f1": f1_score(y_test, bert_preds),
    "inference_time_sec": bert_infer_time
}
print(f"\nBERT inference time: {bert_infer_time:.2f} seconds")
for k, v in results["BERT"].items():
    if k != "inference_time_sec":
        print(f"{k}: {v:.4f}")

# ----------------
# 2. Evaluate XGBoost
# ----------------
print("\nLoading and evaluating XGBoost model...")
xgb_model = joblib.load("./models/xgb_model.joblib")
tfidf = joblib.load("./models/tfidf.joblib")

X_test_tfidf = tfidf.transform(X_test)
start = time.time()
xgb_preds = xgb_model.predict(X_test_tfidf)
xgb_infer_time = time.time() - start
results["XGBoost"] = {
    "accuracy": accuracy_score(y_test, xgb_preds),
    "precision": precision_score(y_test, xgb_preds),
    "recall": recall_score(y_test, xgb_preds),
    "f1": f1_score(y_test, xgb_preds),
    "inference_time_sec": xgb_infer_time
}
print(f"\nXGBoost inference time: {xgb_infer_time:.2f} seconds")
for k, v in results["XGBoost"].items():
    if k != "inference_time_sec":
        print(f"{k}: {v:.4f}")

# ----------------
# 3. Evaluate BiLSTM
# ----------------
print("\nLoading and evaluating BiLSTM model...")
bilstm_model = load_model("./models/bilstm_model.h5")

# Reload tokenizer from JSON
with open("./models/bilstm_tokenizer.json") as f:
    tokenizer_json = f.read()
bilstm_tokenizer = tokenizer_from_json(tokenizer_json)

MAX_LEN = 200
X_test_seq = bilstm_tokenizer.texts_to_sequences(X_test)
X_test_pad = pad_sequences(X_test_seq, maxlen=MAX_LEN,
                           padding="post", truncating="post")

print("BiLSTM: Predicting...")
start = time.time()
bilstm_probs = bilstm_model.predict(X_test_pad)
bilstm_infer_time = time.time() - start
bilstm_preds = (bilstm_probs > 0.5).astype(int).reshape(-1)
results["BiLSTM"] = {
    "accuracy": accuracy_score(y_test, bilstm_preds),
    "precision": precision_score(y_test, bilstm_preds),
    "recall": recall_score(y_test, bilstm_preds),
    "f1": f1_score(y_test, bilstm_preds),
    "inference_time_sec": bilstm_infer_time
}
print(f"\nBiLSTM inference time: {bilstm_infer_time:.2f} seconds")
for k, v in results["BiLSTM"].items():
    if k != "inference_time_sec":
        print(f"{k}: {v:.4f}")

# ----------------
# Print comparison
# ----------------
print("\nModel Comparison (including inference time):\n")
df_results = pd.DataFrame(results).T
print(df_results)

# ----------------
# Plot confusion matrices
# ----------------


def plot_cm(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Legit (0)", "Fraud (1)"],
                yticklabels=["Legit (0)", "Fraud (1)"])
    plt.title(title)
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.show()


plot_cm(y_test, bert_preds, "BERT Confusion Matrix")
plot_cm(y_test, xgb_preds, "XGBoost Confusion Matrix")
plot_cm(y_test, bilstm_preds, "BiLSTM Confusion Matrix")
