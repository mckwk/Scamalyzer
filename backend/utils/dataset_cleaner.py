import os
import pandas as pd
import glob
import string
import csv

# -----------------------------
# Configuration
# -----------------------------
DATA_FOLDER = "D:\\Repos\\datasets"
OUTPUT_FOLDER = "D:\\Repos\\datasets\\normalized"

TEXT_COLUMNS = [
    'text', 'message', 'content', 'body', 'email', 'email text',
    'text_combined', 'msg_content'
]
LABEL_COLUMNS = [
    'label', 'class', 'spam', 'is_scam', 'is_spam', 'email type'
]

LABEL_MAPPING = {
    'spam': 1,
    'scam': 1,
    'fraud': 1,
    'phishing': 1,
    'unsafe': 1,
    'ham': 0,
    'legit': 0,
    'safe email': 0,
    'not spam': 0,
    '0': 0,
    '1': 1,
    0: 0,
    1: 1
}

# -----------------------------
# Helper functions
# -----------------------------
def find_column(columns, candidates):
    columns_lower = [c.lower().strip() for c in columns]
    for candidate in candidates:
        candidate = candidate.lower().strip()
        for idx, col in enumerate(columns_lower):
            if col.startswith(candidate):
                return columns[idx]
    return None

def normalize_label(value):
    """Normalize labels to 0 or 1 as integers, including float values like 0.0/1.0."""
    if pd.isnull(value):
        return None
    try:
        num = int(float(value))
        if num in [0, 1]:
            return num
    except Exception:
        pass
    value_str = str(value).strip().lower()
    mapped = LABEL_MAPPING.get(value_str, None)
    if mapped is not None:
        return int(mapped)
    return None

def clean_text(text):
    """Basic text cleaning: remove punctuation, lowercase, strip extra spaces."""
    if pd.isnull(text):
        return ""
    text = str(text).strip()
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = " ".join(text.split())
    return text

# -----------------------------
# Main processing
# -----------------------------
def normalize_datasets(data_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    all_files = glob.glob(os.path.join(data_folder, "*.csv"))

    print("\n========== Scamalyzer Dataset Normalizer ==========\n")
    print(f"Input folder: {data_folder}")
    print(f"Output folder: {output_folder}\n")
    print(f"Text column candidates: {TEXT_COLUMNS}")
    print(f"Label column candidates: {LABEL_COLUMNS}\n")

    for file in all_files:
        print(f"\n--- Normalizing: {os.path.basename(file)} ---")
        try:
            df = pd.read_csv(file, sep=",", encoding='utf-8-sig', on_bad_lines='skip')
        except Exception as e:
            print(f"  [ERROR] Could not read file: {e}")
            continue

        # Clean up columns
        df.columns = [c.strip() for c in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.loc[:, [c for c in df.columns if c and any(ch.isalnum() for ch in c)]]
        df.columns = [c.strip().lower() for c in df.columns]

        print(f"  Columns found: {df.columns.tolist()}")

        text_col = find_column(df.columns, [c.lower() for c in TEXT_COLUMNS])
        label_col = find_column(df.columns, [c.lower() for c in LABEL_COLUMNS])

        if text_col is None or label_col is None:
            print("  [WARNING] Required columns not found. Skipping file.")
            continue

        print(f"  Using text column: '{text_col}', label column: '{label_col}'")
        print(f"  Unique label values (raw): {df[label_col].unique()}")

        df = df[[text_col, label_col]].copy()
        df.columns = ['message', 'label']

        df['message'] = df['message'].apply(clean_text)
        df['label'] = df['label'].apply(normalize_label).astype('Int64')

        print(f"  Rows before dropna: {len(df)}")
        df = df.dropna(subset=['message', 'label'])
        print(f"  Rows after dropna: {len(df)}")
        print(f"  Unique label values (normalized): {list(df['label'].dropna().unique())}")

        output_file = os.path.join(output_folder, os.path.basename(file))
        df.to_csv(output_file, index=False)
        print(f"  [OK] Saved normalized file to: {output_file}")

    print("\n========== Normalization Complete ==========\n")

def merge_and_deduplicate(output_folder, merged_filename="merged.csv"):
    print("\n========== Merging and Deduplicating ==========\n")
    csv_files = glob.glob(os.path.join(output_folder, "*.csv"))
    dfs = []
    for file in csv_files:
        print(f"  Adding {os.path.basename(file)} ({os.path.getsize(file)//1024} KB)")
        df = pd.read_csv(file)
        dfs.append(df)
    merged_df = pd.concat(dfs, ignore_index=True)

    # Remove broken lines: message is null, empty, or too long
    before = len(merged_df)
    merged_df = merged_df.dropna(subset=["message", "label"])
    merged_df = merged_df[merged_df["message"].str.len() < 20000]

    merged_df = merged_df.drop_duplicates(subset=["message", "label"])
    after = len(merged_df)
    print(f"\n  Merged rows: {before}")
    print(f"  Rows after deduplication and filtering: {after}")
    merged_path = os.path.join(output_folder, merged_filename)
    merged_df.to_csv(merged_path, index=False)
    print(f"  [OK] Saved merged file to: {merged_path}\n")
    print("========== Merge Complete ==========\n")

# -----------------------------
# Run the script
# -----------------------------
if __name__ == "__main__":
    normalize_datasets(DATA_FOLDER, OUTPUT_FOLDER)
    merge_and_deduplicate(OUTPUT_FOLDER)
