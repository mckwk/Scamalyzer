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
from keras.models import load_model
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          Trainer, TrainingArguments)

from utils.config import (BERT_MODEL_PATH, BILSTM_MODEL_PATH,
                          BILSTM_TOKENIZER_PATH, DEFAULT_LANGUAGE,
                          TFIDF_PATH, XGBOOST_MODEL_PATH, get_language_paths,
                          normalize_language)

load_dotenv()

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.getenv("DB_FILE", os.path.join(BACKEND_ROOT, "database", "scamalyzer.db"))


def resolve_path(path):
    if os.path.isabs(path):
        return path
    return os.path.join(BACKEND_ROOT, path)


def connect_to_db():
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def fetch_verified_messages():
    conn = connect_to_db()
    if not conn:
        return []

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, content, language,
                   bert_label, bert_confidence,
                   bilstm_label, bilstm_confidence,
                   xgboost_label, xgboost_confidence
            FROM messages
            WHERE verified = 1 AND used_for_training = 0;
        """)
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} verified messages for retraining.")
        return process_message_rows(rows)
    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")
        return []
    finally:
        conn.close()


def process_message_rows(rows):
    processed = []
    for row in rows:
        processed.append({
            "id": row["id"],
            "text": row["content"],
            "language": normalize_language(row["language"] or DEFAULT_LANGUAGE),
            "label": get_highest_confidence_label(row),
        })
    return processed


def get_highest_confidence_label(row):
    confidences = {
        "bert": row["bert_confidence"] if row["bert_confidence"] is not None else -1,
        "bilstm": row["bilstm_confidence"] if row["bilstm_confidence"] is not None else -1,
        "xgboost": row["xgboost_confidence"] if row["xgboost_confidence"] is not None else -1,
    }
    highest_model = max(confidences, key=confidences.get)

    if highest_model == "bert":
        return int(row["bert_label"])
    if highest_model == "bilstm":
        return int(row["bilstm_label"])
    return int(row["xgboost_label"])


def mark_messages_as_used(message_ids):
    if not message_ids:
        return

    conn = connect_to_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE messages SET used_for_training = 1 WHERE id = ?;",
            [(message_id,) for message_id in message_ids],
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating the database: {e}")
    finally:
        conn.close()


def prepare_dataset(texts, labels, tokenizer):
    new_data = pd.DataFrame({"message": texts, "label": labels})
    train_ds = Dataset.from_pandas(new_data).map(
        lambda batch: tokenizer(
            batch["message"], truncation=True, padding="max_length", max_length=256),
        batched=True,
    )
    train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
    return train_ds


def save_model_and_tokenizer(trainer, tokenizer, model_path):
    model_path = resolve_path(model_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        trainer.save_model(temp_dir)
        tokenizer.save_pretrained(temp_dir)
        if os.path.exists(model_path):
            shutil.rmtree(model_path)
        shutil.move(temp_dir, model_path)


def retrain_bert(entries):
    if not entries:
        return

    texts = [entry["text"] for entry in entries]
    labels = [entry["label"] for entry in entries]

    model_path = resolve_path(BERT_MODEL_PATH)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    train_ds = prepare_dataset(texts, labels, tokenizer)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)

    args = TrainingArguments(
        output_dir=model_path,
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        save_total_limit=2,
    )

    trainer = Trainer(model=model, args=args, train_dataset=train_ds, tokenizer=tokenizer)
    trainer.train()
    save_model_and_tokenizer(trainer, tokenizer, BERT_MODEL_PATH)


def retrain_bilstm(language, entries):
    if not entries:
        return

    paths = get_language_paths(language)
    model_path = resolve_path(paths["bilstm_model"])
    tokenizer_path = resolve_path(paths["bilstm_tokenizer"])

    # Legacy fallback for repositories that only have EN artifacts.
    if not os.path.exists(model_path):
        model_path = resolve_path(BILSTM_MODEL_PATH)
    if not os.path.exists(tokenizer_path):
        tokenizer_path = resolve_path(BILSTM_TOKENIZER_PATH)

    with open(tokenizer_path, "r", encoding="utf-8") as f:
        tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(f.read())

    texts = [entry["text"] for entry in entries]
    labels = np.array([entry["label"] for entry in entries])
    seqs = tokenizer.texts_to_sequences(texts)
    X_new_train = tf.keras.preprocessing.sequence.pad_sequences(
        seqs, maxlen=200, padding="post", truncating="post")

    tf.config.run_functions_eagerly(True)
    model = load_model(model_path)
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.fit(X_new_train, labels, batch_size=64, epochs=2)
    model.save(model_path)


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


def retrain_xgboost(language, entries):
    if not entries:
        return

    paths = get_language_paths(language)
    model_path = resolve_path(paths["xgboost_model"])
    tfidf_path = resolve_path(paths["tfidf"])

    # Legacy fallback for repositories that only have EN artifacts.
    if not os.path.exists(model_path):
        model_path = resolve_path(XGBOOST_MODEL_PATH)
    if not os.path.exists(tfidf_path):
        tfidf_path = resolve_path(TFIDF_PATH)

    tfidf = joblib.load(tfidf_path)
    model = joblib.load(model_path)

    texts = [entry["text"] for entry in entries]
    labels = np.array([entry["label"] for entry in entries])
    X_new_train = tfidf.transform(texts)

    if len(np.unique(labels)) < 2:
        X_new_train, labels = add_synthetic_data(X_new_train, labels, tfidf)

    model.fit(X_new_train, labels)
    joblib.dump(model, model_path)
    joblib.dump(tfidf, tfidf_path)


def group_entries_by_language(entries):
    grouped = {}
    for entry in entries:
        language = normalize_language(entry["language"])
        grouped.setdefault(language, []).append(entry)
    return grouped


def retrain_all_models():
    entries = fetch_verified_messages()
    if not entries:
        print("No new verified messages available for retraining.")
        return

    retrain_bert(entries)
    print("BERT model retrained successfully.")

    by_language = group_entries_by_language(entries)
    for language, lang_entries in by_language.items():
        retrain_bilstm(language, lang_entries)
        print(f"BiLSTM model retrained successfully for {language}.")
        retrain_xgboost(language, lang_entries)
        print(f"XGBoost model retrained successfully for {language}.")

    mark_messages_as_used([entry["id"] for entry in entries])
    print("All models retrained successfully.")


if __name__ == "__main__":
    retrain_all_models()
