from transformers import BertTokenizer, BertForSequenceClassification
import torch

class BERTModel:
    def __init__(self, model_name='bert-base-uncased', num_labels=3):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    def preprocess(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        return inputs

    def predict(self, text):
        self.model.eval()
        inputs = self.preprocess(text)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        return predicted_class, confidence

    def load_model(self, model_path):
        self.model = BertForSequenceClassification.from_pretrained(model_path)

# Create a global model instance (so it's loaded only once)
bert_model_instance = BERTModel()

def analyze_message(text):
    label, confidence = bert_model_instance.predict(text)
    return label, confidence