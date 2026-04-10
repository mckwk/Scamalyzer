from langdetect import DetectorFactory, LangDetectException, detect

from utils.config import DEFAULT_LANGUAGE, normalize_language

# Ensure deterministic language detection behavior.
DetectorFactory.seed = 0


def detect_message_language(message, requested_language=None):
    if requested_language:
        return normalize_language(requested_language)

    if not isinstance(message, str) or not message.strip():
        return DEFAULT_LANGUAGE

    try:
        detected = detect(message)
    except LangDetectException:
        return DEFAULT_LANGUAGE

    return normalize_language(detected)
