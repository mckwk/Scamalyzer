# train_bilstm.py
from utils.config import FINAL_DATASET_PATH
import json
import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import (LSTM, Bidirectional, Dense, Dropout,
                                     Embedding)
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SEED = 42
MAX_LEN = 200
MAX_WORDS = 50000
EMBED_DIM = 100
BATCH_SIZE = 64
EPOCHS = 1

# Load
df = pd.read_csv(FINAL_DATASET_PATH)
df = df.dropna(subset=["message", "label"])
df["label"] = df["label"].astype(int)

# Split
train_df, test_df = train_test_split(
    df, test_size=0.2, stratify=df["label"], random_state=SEED)
train_df, val_df = train_test_split(
    train_df, test_size=0.125, stratify=train_df["label"], random_state=SEED)

# Tokenize
tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<UNK>")
tokenizer.fit_on_texts(train_df["message"])


def prep_texts(texts):
    seqs = tokenizer.texts_to_sequences(texts)
    return pad_sequences(seqs, maxlen=MAX_LEN, padding="post", truncating="post")


X_train = prep_texts(train_df["message"])
X_val = prep_texts(val_df["message"])
X_test = prep_texts(test_df["message"])

y_train, y_val, y_test = train_df["label"].values, val_df["label"].values, test_df["label"].values

# Model
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

# Train
es = EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)
history = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                    batch_size=BATCH_SIZE, epochs=EPOCHS, callbacks=[es])

# Save model
model.save("models/bilstm_model.h5")

# Save tokenizer
tokenizer_json = tokenizer.to_json()
with open("models/bilstm_tokenizer.json", "w", encoding="utf-8") as f:
    f.write(tokenizer_json)
