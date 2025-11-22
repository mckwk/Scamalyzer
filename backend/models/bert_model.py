from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from utils.config import BERT_MODEL_PATH

# Load BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(BERT_MODEL_PATH)
model.eval()

def analyze_message(message):
    inputs = tokenizer(message, truncation=True, padding=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
    label = int(probs[1] > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(probs[label])
    return label, confidence