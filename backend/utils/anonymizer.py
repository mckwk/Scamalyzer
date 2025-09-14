import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from tqdm import tqdm

from backend.utils.config import MERGED_PATH, OUTPUT_FOLDER

print("Loading dataset...")
df = pd.read_csv(MERGED_PATH + "/merged_dataset.csv")

if "message" in df.columns:
    print("Scrubbing 'message' column for PII...")
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    def scrub_text(text):
        if not isinstance(text, str):
            return text
        results = analyzer.analyze(
            text=text,
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
            language='en'
        )
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized.text

    tqdm.pandas(desc="Scrubbing messages")
    df["message"] = df["message"].progress_apply(scrub_text)
else:
    print("No 'message' column found. No text anonymization performed.")

print("Saving anonymized dataset...")
df.to_csv(OUTPUT_FOLDER + "/anonymized_dataset.csv", index=False)
print("Anonymization complete. Saved to anonymized_dataset.csv")
