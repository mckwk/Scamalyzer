import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from utils.config import get_language_paths, normalize_language

_model_cache = {}
_tokenizer_cache = {}


def _get_language_artifacts(language):
    language = normalize_language(language)
    if language in _model_cache and language in _tokenizer_cache:
        return _model_cache[language], _tokenizer_cache[language]

    model_path = get_language_paths(language)["bert_model"]
    if not os.path.isdir(model_path):
        raise FileNotFoundError(
            f"Missing BERT model directory for language '{language}': {model_path}"
        )

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    _model_cache[language] = model
    _tokenizer_cache[language] = tokenizer
    return model, tokenizer


def analyze_message(message, language="en"):
    model, tokenizer = _get_language_artifacts(language)
    inputs = tokenizer(message, truncation=True, padding=True,
                       max_length=256, return_tensors="pt")
    # DistilBERT models do not use token_type_ids.
    if "token_type_ids" in inputs:
        inputs.pop("token_type_ids")
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
    label = int(probs[1] > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(probs[label])
    return label, confidence
