# train_bilstm.py
import argparse
import os
import shutil
import sys

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import (LSTM, Bidirectional, Dense, Dropout,
                                     Embedding)
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from utils.config import (BILSTM_MODEL_PATH, BILSTM_TOKENIZER_PATH,
                          get_dataset_paths, get_language_paths,
                          normalize_language)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SEED = 42
MAX_LEN = 200
MAX_WORDS = 50000
EMBED_DIM = 100
BATCH_SIZE = 64
EPOCHS = 1

parser = argparse.ArgumentParser()
parser.add_argument("--language", default="all", help="en, es, de, or all")
args = parser.parse_args()


def train_for_language(language, dataset_path):
    print(f"Training BiLSTM for language={language} using {dataset_path}")
    df = pd.read_csv(dataset_path)
    df = df.dropna(subset=["message", "label"])
    df["label"] = df["label"].astype(int)

    train_df, test_df = train_test_split(
        df, test_size=0.2, stratify=df["label"], random_state=SEED)
    train_df, val_df = train_test_split(
        train_df, test_size=0.125, stratify=train_df["label"], random_state=SEED)

    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<UNK>")
    tokenizer.fit_on_texts(train_df["message"])


    def prep_texts(texts):
        seqs = tokenizer.texts_to_sequences(texts)
        return pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")

    X_train = prep_texts(train_df["message"])
    X_val = prep_texts(val_df["message"])

    y_train = train_df["label"].values
    y_val = val_df["label"].values

    model = Sequential([
        Embedding(input_dim=MAX_WORDS, output_dim=EMBED_DIM, input_length=MAX_LEN),
        Bidirectional(LSTM(128, return_sequences=False)),
        Dropout(0.5),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(1, activation="sigmoid")
    ])

    model.compile(loss="binary_crossentropy",
                  optimizer="adam", metrics=["accuracy"])

    es = EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)
    model.fit(X_train, y_train, validation_data=(X_val, y_val),
              batch_size=BATCH_SIZE, epochs=EPOCHS, callbacks=[es])

    output_paths = get_language_paths(language)
    model_path = output_paths["bilstm_model"]
    tokenizer_path = output_paths["bilstm_tokenizer"]
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)

    tokenizer_json = tokenizer.to_json()
    with open(tokenizer_path, "w", encoding="utf-8") as f:
        f.write(tokenizer_json)


dataset_paths = get_dataset_paths()
target_language = normalize_language(args.language) if args.language != "all" else "all"

if target_language == "all":
    for language, path in dataset_paths.items():
        if os.path.exists(path):
            train_for_language(language, path)
else:
    path = dataset_paths.get(target_language)
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found for language: {target_language}")
    train_for_language(target_language, path)

# Save EN fallback artifacts for backward compatibility if EN was trained.
if os.path.exists(get_language_paths("en")["bilstm_model"]):
    en_paths = get_language_paths("en")
    if not os.path.exists(BILSTM_MODEL_PATH):
        shutil.copy2(en_paths["bilstm_model"], BILSTM_MODEL_PATH)
    if not os.path.exists(BILSTM_TOKENIZER_PATH):
        shutil.copy2(en_paths["bilstm_tokenizer"], BILSTM_TOKENIZER_PATH)
