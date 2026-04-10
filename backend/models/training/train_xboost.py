# train_xgboost.py
import argparse
import os
import shutil
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from utils.config import (TFIDF_PATH, XGBOOST_MODEL_PATH, get_dataset_paths,
                          get_language_paths, normalize_language)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SEED = 42

parser = argparse.ArgumentParser()
parser.add_argument("--language", default="all", help="en, es, de, or all")
args = parser.parse_args()


def train_for_language(language, dataset_path):
    print(f"Training XGBoost for language={language} using {dataset_path}")
    df = pd.read_csv(dataset_path)
    df = df.dropna(subset=["message", "label"])
    df["label"] = df["label"].astype(int)

    train_df, test_df = train_test_split(
        df, test_size=0.2, stratify=df["label"], random_state=SEED)
    train_df, val_df = train_test_split(
        train_df, test_size=0.125, stratify=train_df["label"], random_state=SEED)

    tfidf = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5), max_features=50000)
    X_train = tfidf.fit_transform(train_df["message"])
    X_val = tfidf.transform(val_df["message"])

    y_train, y_val = train_df["label"], val_df["label"]

    clf = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=25,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=SEED,
        n_jobs=-1
    )

    clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=True)

    output_paths = get_language_paths(language)
    model_path = output_paths["xgboost_model"]
    tfidf_path = output_paths["tfidf"]
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    joblib.dump(clf, model_path)
    joblib.dump(tfidf, tfidf_path)

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
if os.path.exists(get_language_paths("en")["xgboost_model"]):
    en_paths = get_language_paths("en")
    if not os.path.exists(XGBOOST_MODEL_PATH):
        shutil.copy2(en_paths["xgboost_model"], XGBOOST_MODEL_PATH)
    if not os.path.exists(TFIDF_PATH):
        shutil.copy2(en_paths["tfidf"], TFIDF_PATH)
