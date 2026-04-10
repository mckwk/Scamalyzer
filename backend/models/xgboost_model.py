import os

import joblib
import xgboost as xgb

from utils.config import get_language_paths, normalize_language

_model_cache = {}
_tfidf_cache = {}


def _load_xgboost_model(model_path):
    if model_path.endswith(".json"):
        model = xgb.Booster()
        model.load_model(model_path)
        return model
    return joblib.load(model_path)


def _get_language_artifacts(language):
    language = normalize_language(language)
    if language in _model_cache and language in _tfidf_cache:
        return _model_cache[language], _tfidf_cache[language]

    paths = get_language_paths(language)
    model_path = paths["xgboost_model"]
    tfidf_path = paths["tfidf"]

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Missing XGBoost model for language '{language}': {model_path}"
        )
    if not os.path.exists(tfidf_path):
        raise FileNotFoundError(
            f"Missing TF-IDF vectorizer for language '{language}': {tfidf_path}"
        )

    model = _load_xgboost_model(model_path)
    tfidf = joblib.load(tfidf_path)
    _model_cache[language] = model
    _tfidf_cache[language] = tfidf
    return model, tfidf


def analyze_message(message, language="en"):
    model, tfidf = _get_language_artifacts(language)
    vectorized = tfidf.transform([message])

    if isinstance(model, xgb.Booster):
        dmatrix = xgb.DMatrix(vectorized)
        prob = model.predict(dmatrix)[0]
    else:
        prob = model.predict_proba(vectorized)[0][1]

    label = int(prob > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(prob if label == 1 else 1 - prob)
    return label, confidence
