import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Safely get environment variables with defaults or raise an error
DATA_FOLDER_MESSAGES = os.getenv(
    "DATA_FOLDER_MESSAGES", "default/messages/path")
DATA_FOLDER_URLS = os.getenv("DATA_FOLDER_URLS", "default/urls/path")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "default/output/path")
MERGED_PATH = os.path.join(OUTPUT_FOLDER, "merged")
FINAL_DATASET_PATH = os.path.join(MERGED_PATH, "anonymized_dataset.csv")

FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "localhost")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "3000")
FRONTEND_URL = f"http://{FRONTEND_ADDRESS}:{FRONTEND_PORT}"

BACKEND_ADDRESS = os.getenv("BACKEND_ADDRESS", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "5000")
BACKEND_URL = f"http://{BACKEND_ADDRESS}:{BACKEND_PORT}"

# Model paths
BERT_MODEL_PATH = os.getenv("BERT_MODEL_PATH", "models/output/bert_finetuned")
BILSTM_MODEL_PATH = os.getenv(
    "BILSTM_MODEL_PATH", "models/output/bilstm_model.h5")
BILSTM_TOKENIZER_PATH = os.getenv(
    "BILSTM_TOKENIZER_PATH", "models/output/bilstm_tokenizer.json")
XGBOOST_MODEL_PATH = os.getenv(
    "XGBOOST_MODEL_PATH", "models/output/xgb_model.joblib")
TFIDF_PATH = os.getenv("TFIDF_PATH", "models/output/tfidf.joblib")
