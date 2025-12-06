import joblib
import xgboost as xgb

from utils.config import TFIDF_PATH, XGBOOST_MODEL_PATH

# Load XGBoost model and TF-IDF vectorizer
model = joblib.load(XGBOOST_MODEL_PATH)
tfidf = joblib.load(TFIDF_PATH)


def analyze_message(message):
    vectorized = tfidf.transform([message])
    dmatrix = xgb.DMatrix(vectorized)
    prob = model.predict(dmatrix)[0]
    label = int(prob > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(prob if label == 1 else 1 - prob)
    return label, confidence
