from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json
from utils.config import BILSTM_MODEL_PATH, BILSTM_TOKENIZER_PATH

# Load BiLSTM model and tokenizer
MAX_LEN = 200
model = load_model(BILSTM_MODEL_PATH)

with open(BILSTM_TOKENIZER_PATH, "r") as f:
    tokenizer_json = f.read()
tokenizer = tokenizer_from_json(tokenizer_json)

def analyze_message(message):
    seq = tokenizer.texts_to_sequences([message])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding="post", truncating="post")
    prob = model.predict(padded)[0][0]
    label = int(prob > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(prob if label == 1 else 1 - prob)
    return label, confidence