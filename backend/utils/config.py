import os

from dotenv import load_dotenv

# Load environment variables from .env file and override inherited shell values.
# This prevents stale global vars from breaking local runs.
load_dotenv(override=True)

# Safely get environment variables with defaults or raise an error
DATA_FOLDER_MESSAGES = os.getenv(
    "DATA_FOLDER_MESSAGES", "default/messages/path")
DATA_FOLDER_URLS = os.getenv("DATA_FOLDER_URLS", "default/urls/path")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "default/output/path")
MERGED_PATH = os.path.join(OUTPUT_FOLDER, "merged")
FINAL_DATASET_PATH = os.path.join(MERGED_PATH, "anonymized_dataset.csv")

FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "localhost")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "3000")

BACKEND_ADDRESS = os.getenv("BACKEND_ADDRESS", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "5000")


def _build_url(address, port):
    address = (address or "").strip()
    if address.startswith("http://") or address.startswith("https://"):
        return address.rstrip("/")
    return f"http://{address}:{port}"


FRONTEND_URL = _build_url(FRONTEND_ADDRESS, FRONTEND_PORT)
BACKEND_URL = _build_url(BACKEND_ADDRESS, BACKEND_PORT)

# Model paths (legacy single-path settings kept for backward compatibility)
BERT_MODEL_PATH = os.getenv("BERT_MODEL_PATH", "models/output/bert_finetuned")
BILSTM_MODEL_PATH = os.getenv(
    "BILSTM_MODEL_PATH", "models/output/bilstm_model.h5")
BILSTM_TOKENIZER_PATH = os.getenv(
    "BILSTM_TOKENIZER_PATH", "models/output/bilstm_tokenizer.json")
XGBOOST_MODEL_PATH = os.getenv(
    "XGBOOST_MODEL_PATH", "models/output/xgb_model.joblib")
TFIDF_PATH = os.getenv("TFIDF_PATH", "models/output/tfidf.joblib")

# Multilingual settings
SUPPORTED_LANGUAGES = ("en", "es", "de")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en").lower()
MULTILINGUAL_BERT_MODEL_NAME = os.getenv(
    "MULTILINGUAL_BERT_MODEL_NAME", "xlm-roberta-base")

# Language-specific model path templates
BERT_MODEL_PATH_TEMPLATE = os.getenv(
    "BERT_MODEL_PATH_TEMPLATE", "models/training/DistilBERT/{lang}")
BILSTM_MODEL_PATH_TEMPLATE = os.getenv(
    "BILSTM_MODEL_PATH_TEMPLATE", "models/training/bilstm/bilstm_model_{lang}.h5")
BILSTM_TOKENIZER_PATH_TEMPLATE = os.getenv(
    "BILSTM_TOKENIZER_PATH_TEMPLATE", "models/training/bilstm/bilstm_tokenizer_{lang}.json")
XGBOOST_MODEL_PATH_TEMPLATE = os.getenv(
    "XGBOOST_MODEL_PATH_TEMPLATE", "models/training/xgboost/xgb_model_{lang}.joblib")
TFIDF_PATH_TEMPLATE = os.getenv(
    "TFIDF_PATH_TEMPLATE", "models/training/xgboost/tfidf_{lang}.joblib")

# Dataset paths
DATASET_EN_PATH = os.getenv(
    "DATASET_EN_PATH", "models/data/anonymized_dataset.csv")
DATASET_ES_PATH = os.getenv(
    "DATASET_ES_PATH", "models/data/anonymized_dataset_es.csv")
DATASET_DE_PATH = os.getenv(
    "DATASET_DE_PATH", "models/data/anonymized_dataset_de.csv")
MULTILINGUAL_DATASET_PATH = os.getenv(
    "MULTILINGUAL_DATASET_PATH", "models/data/anonymized_dataset_multilingual.csv")


def normalize_language(language):
    if not language:
        return DEFAULT_LANGUAGE
    language = str(language).strip().lower()
    if language in SUPPORTED_LANGUAGES:
        return language
    if language.startswith("es"):
        return "es"
    if language.startswith("de"):
        return "de"
    if language.startswith("en"):
        return "en"
    return DEFAULT_LANGUAGE


def get_language_paths(language):
    lang = normalize_language(language)
    return {
        "bert_model": BERT_MODEL_PATH_TEMPLATE.format(lang=lang),
        "bilstm_model": BILSTM_MODEL_PATH_TEMPLATE.format(lang=lang),
        "bilstm_tokenizer": BILSTM_TOKENIZER_PATH_TEMPLATE.format(lang=lang),
        "xgboost_model": XGBOOST_MODEL_PATH_TEMPLATE.format(lang=lang),
        "tfidf": TFIDF_PATH_TEMPLATE.format(lang=lang),
    }


def get_dataset_paths():
    return {
        "en": DATASET_EN_PATH,
        "es": DATASET_ES_PATH,
        "de": DATASET_DE_PATH,
    }
