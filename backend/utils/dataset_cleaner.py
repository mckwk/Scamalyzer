import os
import pandas as pd
import glob
import string

# -----------------------------
# Configuration
# -----------------------------
DATA_FOLDER = ""
OUTPUT_FOLDER = ""
MAX_MESSAGE_LENGTH = 20000
MIN_MESSAGE_LENGTH = 10

TEXT_COLUMNS = [
    'text', 'message', 'content', 'body', 'email', 'email text',
    'text_combined', 'msg_content', 'url'
]
LABEL_COLUMNS = [
    'label', 'class', 'spam', 'is_scam', 'is_spam', 'email type', 'type'
]

LABEL_MAPPING = {
    'spam': 1, 'scam': 1, 'fraud': 1, 'phishing': 1, 'unsafe': 1,
    'ham': 0, 'legit': 0, 'safe email': 0, 'not spam': 0,
    '0': 0, '1': 1, 0: 0, 1: 1
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
    text = str(text).strip().lower()
    text = text.replace('\t', ' ') 
    text = text.replace('"', '') 
    text = text.translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

def filter_messages(df, min_len=MIN_MESSAGE_LENGTH, max_len=MAX_MESSAGE_LENGTH):
    df = df.dropna(subset=["message", "label"])
    df = df[df["message"].str.strip().str.len() >= min_len]
    df = df[df["message"].str.len() <= max_len]
    return df

def report_distribution(df):
    scam_count = (df["label"] == 1).sum()
    non_scam_count = (df["label"] == 0).sum()
    total = scam_count + non_scam_count
    scam_pct = (scam_count / total) * 100 if total else 0
    non_scam_pct = (non_scam_count / total) * 100 if total else 0
    return scam_count, non_scam_count, scam_pct, non_scam_pct

def save_csv(df, path):
    df.to_csv(path, index=False)
    print(f"  [OK] Saved file to: {path}")

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

        df.columns = [c.strip() for c in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.loc[:, [c for c in df.columns if c and any(ch.isalnum() for ch in c)]]
        df.columns = [c.strip().lower() for c in df.columns]

        print(f"  Columns found: {df.columns.tolist()}")

        text_col = find_column(df.columns, TEXT_COLUMNS)
        label_col = find_column(df.columns, LABEL_COLUMNS)

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
        df = filter_messages(df)
        print(f"  Rows after filtering: {len(df)}")
        print(f"  Unique label values (normalized): {list(df['label'].dropna().unique())}")

        output_file = os.path.join(output_folder, os.path.basename(file))
        save_csv(df, output_file)

    print("\n========== Normalization Complete ==========\n")

def merge_and_deduplicate(output_folder, merged_filename="merged/merged.csv"):
    print("\n========== Merging and Deduplicating ==========\n")
    csv_files = glob.glob(os.path.join(output_folder, "*.csv"))
    dfs = []
    for file in csv_files:
        print(f"  Adding {os.path.basename(file)} ({os.path.getsize(file)//1024} KB)")
        df = pd.read_csv(file)
        dfs.append(df)
    merged_df = pd.concat(dfs, ignore_index=True)

    before = len(merged_df)
    print(f"\n  Merged rows: {before}")

    merged_df = filter_messages(merged_df)
    merged_df = merged_df.drop_duplicates(subset=["message", "label"])
    after = len(merged_df)
    print(f"  Rows after deduplication and filtering: {after}")

    # Randomize order
    merged_df = merged_df.sample(frac=1, random_state=42).reset_index(drop=True)

    scam_count, non_scam_count, scam_pct, non_scam_pct = report_distribution(merged_df)
    # Optionally, print a summary line
    print(f"\n  Final distribution: {scam_count} scam, {non_scam_count} non-scam")
    print(f"  Scam percentage: {scam_pct:.2f}%, Non-scam percentage: {non_scam_pct:.2f}%")

    merged_path = os.path.join(output_folder, merged_filename)
    save_csv(merged_df, merged_path)
    print("========== Merge Complete ==========\n")

# -----------------------------
# Run the script
# -----------------------------
if __name__ == "__main__":
    normalize_datasets(DATA_FOLDER, OUTPUT_FOLDER)
    merge_and_deduplicate(OUTPUT_FOLDER)
