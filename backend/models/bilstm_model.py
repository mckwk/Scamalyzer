import os

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from utils.config import get_language_paths, normalize_language

MAX_LEN = 200

_model_cache = {}
_tokenizer_cache = {}


class _CompatEmbedding(tf.keras.layers.Embedding):
    def __init__(self, *args, quantization_config=None, **kwargs):
        # Ignore unknown config fields present in some saved models.
        super().__init__(*args, **kwargs)


class _CompatDense(tf.keras.layers.Dense):
    def __init__(self, *args, quantization_config=None, **kwargs):
        super().__init__(*args, **kwargs)


def _get_language_artifacts(language):
    language = normalize_language(language)
    if language in _model_cache and language in _tokenizer_cache:
        return _model_cache[language], _tokenizer_cache[language]

    paths = get_language_paths(language)
    model_path = paths["bilstm_model"]
    tokenizer_path = paths["bilstm_tokenizer"]

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Missing BiLSTM model for language '{language}': {model_path}"
        )
    if not os.path.exists(tokenizer_path):
        raise FileNotFoundError(
            f"Missing BiLSTM tokenizer for language '{language}': {tokenizer_path}"
        )

    model = load_model(
        model_path,
        compile=False,
        custom_objects={
            "Embedding": _CompatEmbedding,
            "Dense": _CompatDense,
        },
    )
    with open(tokenizer_path, "r", encoding="utf-8") as f:
        tokenizer_json = f.read()
    tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_json)

    _model_cache[language] = model
    _tokenizer_cache[language] = tokenizer
    return model, tokenizer

def analyze_message(message, language="en"):
    model, tokenizer = _get_language_artifacts(language)
    seq = tokenizer.texts_to_sequences([message])
    padded = pad_sequences(seq, maxlen=MAX_LEN,
                           padding="post", truncating="post")
    prob = model.predict(padded)[0][0]
    label = int(prob > 0.5)  # 1 for fraud, 0 for legit
    confidence = float(prob if label == 1 else 1 - prob)
    return label, confidence
