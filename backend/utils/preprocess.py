from sklearn.feature_extraction.text import CountVectorizer
import re

def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove digits
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = text.strip()  # Remove leading and trailing whitespace
    return text

def tokenize_text(text):
    vectorizer = CountVectorizer()
    tokens = vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out()

def preprocess_message(message):
    cleaned_message = clean_text(message)
    tokens = tokenize_text(cleaned_message)
    return tokens