# train_xgboost.py
import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from utils.config import FINAL_DATASET_PATH

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SEED = 42

# Load
df = pd.read_csv(FINAL_DATASET_PATH)
df = df.dropna(subset=["message", "label"])
df["label"] = df["label"].astype(int)

# Split
train_df, test_df = train_test_split(
    df, test_size=0.2, stratify=df["label"], random_state=SEED)
train_df, val_df = train_test_split(
    train_df, test_size=0.125, stratify=train_df["label"], random_state=SEED)

# TF-IDF
tfidf = TfidfVectorizer(
    analyzer="char_wb", ngram_range=(3, 5), max_features=50000)
X_train = tfidf.fit_transform(train_df["message"])
X_val = tfidf.transform(val_df["message"])
X_test = tfidf.transform(test_df["message"])

y_train, y_val, y_test = train_df["label"], val_df["label"], test_df["label"]

# Model
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

# Save
joblib.dump(clf, "models/xgb_model.joblib")
joblib.dump(tfidf, "models/tfidf.joblib")
