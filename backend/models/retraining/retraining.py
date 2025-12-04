import os
import shutil
import sqlite3
import tempfile

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from datasets import Dataset
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments)
from xgboost import XGBClassifier

load_dotenv()

DB_PATH = os.getenv(
    "DB_FILE", "D:/Repos/Scamalyzer/backend/database/scamalyzer.db")
ABS_PATH = os.getenv("ABS_PATH", os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))
BERT_MODEL_PATH = ABS_PATH + \
    os.getenv("BERT_MODEL_PATH", "models/output/bert_finetuned")
BILSTM_MODEL_PATH = ABS_PATH + \
    os.getenv("BILSTM_MODEL_PATH", "models/output/bilstm_model.h5")
BILSTM_TOKENIZER_PATH = ABS_PATH + \
    os.getenv("BILSTM_TOKENIZER_PATH", "models/output/bilstm_tokenizer.json")
XGBOOST_MODEL_PATH = ABS_PATH + \
    os.getenv("XGBOOST_MODEL_PATH", "models/output/xgb_model.json")
TFIDF_PATH = ABS_PATH + os.getenv("TFIDF_PATH", "models/output/tfidf.joblib")


def connect_to_db():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def fetch_verified_messages():
    conn = connect_to_db()
    if not conn:
        return [], [], []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, content, 
                   bert_label, bert_confidence, 
                   bilstm_label, bilstm_confidence, 
                   xgboost_label, xgboost_confidence
            FROM messages
            WHERE verified = 1 AND used_for_training = 0;
        """)
        rows = cursor.fetchall()
        conn.close()
        print(f"Fetched {len(rows)} verified messages for retraining.")
        return process_message_rows(rows)
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
        return [], [], []


def process_message_rows(rows):
    message_ids = [row[0] for row in rows]
    texts = [row[1] for row in rows]
    labels = [get_highest_confidence_label(row) for row in rows]
    return message_ids, texts, labels


def get_highest_confidence_label(row):
    confidences = {
        "bert": row[3],
        "bilstm": row[5],
        "xgboost": row[7]
    }
    highest_model = max(confidences, key=confidences.get)
    return int(row[2] if highest_model == "bert" else row[4] if highest_model == "bilstm" else row[6])


def mark_messages_as_used(message_ids):
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.executemany("""
            UPDATE messages
            SET used_for_training = 1
            WHERE id = ?;
        """, [(message_id,) for message_id in message_ids])
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error updating the database: {e}")


def retrain_model(model_name, retrain_function, texts, labels):
    if not texts:
        print(f"No new verified messages for {model_name} retraining.")
        return
    retrain_function(texts, labels)
    print(f"{model_name} model retrained successfully.")


def retrain_bert(texts, labels):
    if not os.path.exists(BERT_MODEL_PATH):
        raise FileNotFoundError(
            f"BERT model path '{BERT_MODEL_PATH}' does not exist.")
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_PATH)
    train_ds = prepare_dataset(texts, labels, tokenizer)
    model = AutoModelForSequenceClassification.from_pretrained(
        BERT_MODEL_PATH, num_labels=2)
    args = TrainingArguments(
        output_dir=BERT_MODEL_PATH,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        save_total_limit=2,
    )
    trainer = Trainer(model=model, args=args,
                      train_dataset=train_ds, tokenizer=tokenizer)
    trainer.train()
    save_model_and_tokenizer(trainer, tokenizer, BERT_MODEL_PATH)


def prepare_dataset(texts, labels, tokenizer):
    new_data = pd.DataFrame({"message": texts, "label": labels})
    train_ds = Dataset.from_pandas(new_data).map(lambda batch: tokenizer(
        batch["message"], truncation=True, padding="max_length", max_length=256), batched=True)
    train_ds.set_format(type="torch", columns=[
                        "input_ids", "attention_mask", "label"])
    return train_ds


def save_model_and_tokenizer(trainer, tokenizer, model_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        trainer.save_model(temp_dir)
        tokenizer.save_pretrained(temp_dir)
        if os.path.exists(model_path):
            shutil.rmtree(model_path)
        shutil.move(temp_dir, model_path)


def retrain_bilstm(texts, labels):
    tf.config.run_functions_eagerly(True)
    tokenizer = load_bilstm_tokenizer()
    X_new_train = prepare_bilstm_texts(texts, tokenizer)
    y_new_train = np.array(labels)
    model = load_model(BILSTM_MODEL_PATH)
    model.compile(loss="binary_crossentropy",
                  optimizer="adam", metrics=["accuracy"])
    model.fit(X_new_train, y_new_train, batch_size=64, epochs=2)
    model.save(BILSTM_MODEL_PATH)


def load_bilstm_tokenizer():
    with open(BILSTM_TOKENIZER_PATH, "r") as f:
        tokenizer_json = f.read()
    return tokenizer_from_json(tokenizer_json)


def prepare_bilstm_texts(texts, tokenizer):
    seqs = tokenizer.texts_to_sequences(texts)
    return pad_sequences(seqs, maxlen=200, padding="post", truncating="post")


def retrain_xgboost(texts, labels):
    tfidf = joblib.load(TFIDF_PATH)
    X_new_train, y_new_train = prepare_xgboost_data(texts, labels, tfidf)
    model = joblib.load(XGBOOST_MODEL_PATH)
    model.fit(X_new_train, y_new_train)
    joblib.dump(model, XGBOOST_MODEL_PATH)
    joblib.dump(tfidf, TFIDF_PATH)


def prepare_xgboost_data(texts, labels, tfidf):
    X_new_train = tfidf.transform(texts)
    y_new_train = np.array(labels)
    if len(np.unique(y_new_train)) < 2:
        X_new_train, y_new_train = add_synthetic_data(
            X_new_train, y_new_train, tfidf)
    return X_new_train, y_new_train


def add_synthetic_data(X_new_train, y_new_train, tfidf):
    if 0 not in y_new_train:
        X_synthetic = tfidf.transform(["Synthetic non-fraudulent message"])
        X_new_train = np.vstack([X_new_train.toarray(), X_synthetic.toarray()])
        y_new_train = np.append(y_new_train, 0)
    if 1 not in y_new_train:
        X_synthetic = tfidf.transform(["Synthetic fraudulent message"])
        X_new_train = np.vstack([X_new_train.toarray(), X_synthetic.toarray()])
        y_new_train = np.append(y_new_train, 1)
    return X_new_train, y_new_train


def retrain_all_models():
    message_ids, texts, labels = fetch_verified_messages()
    retrain_model("BERT", retrain_bert, texts, labels)
    retrain_model("BiLSTM", retrain_bilstm, texts, labels)
    retrain_model("XGBoost", retrain_xgboost, texts, labels)
    mark_messages_as_used(message_ids)
    print("All models retrained successfully!")


if __name__ == "__main__":
    retrain_all_models()
