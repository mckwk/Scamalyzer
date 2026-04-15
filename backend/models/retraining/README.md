# Retraining Models

This module is responsible for retraining the machine learning models used in the Scamalyzer project. It fetches verified messages from the database, processes them, and updates the models with new training data.

## Overview
The retraining process involves the following steps:
1. **Fetching Verified Messages**: Retrieves messages marked as verified and not yet used for training from the database. Messages in the database must have the `verified` column set to `True` and the `used_for_training` column set to `False` to be included in the retraining process.
2. **Processing Messages**: Extracts message content and determines the label with the highest confidence from the existing models.
3. **Retraining Models**: Groups verified messages by language (`en`, `es`, `de`) and updates BERT, BiLSTM, and XGBoost artifacts for each language.
4. **Marking Messages as Used**: Marks the processed messages as used for training in the database.

## Models
### BERT
- Uses the Hugging Face `transformers` library.
- Tokenizes language-specific messages and trains the model using the `Trainer` API.
- Saves the updated model and tokenizer to the language artifact path.

### BiLSTM
- Uses TensorFlow/Keras.
- Loads the language-specific tokenizer and model.
- Prepares the language-specific data and retrains the model.
- Saves the updated language-specific model.

### XGBoost
- Uses the `xgboost` library.
- Transforms language-specific messages using the language-specific TF-IDF vectorizer.
- Retrains and saves the language-specific model and vectorizer.

**Sidenote**: For optimal performance, the XGBoost model should ideally be retrained when there is an equal share of positive and negative entries in the training data. If the dataset is imbalanced, synthetic data is added to ensure both classes are represented.

## Usage
To retrain all models, run the script:
```bash
python retraining.py
```

## Environment Variables
- `DB_FILE`: Path to the SQLite database file. Default: `D:/Repos/Scamalyzer/backend/database/scamalyzer.db`
- `ABS_PATH`: Absolute path to the project root. Default: Computed dynamically.

## Dependencies
Ensure the following Python packages are installed:
- `tensorflow`
- `transformers`
- `xgboost`
- `joblib`
- `numpy`
- `pandas`
- `datasets`
- `dotenv`
- `scikit-learn`

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Notes
- The script automatically handles the addition of synthetic data for imbalanced datasets.
- Retraining is strict per language: if a language-specific artifact is missing, retraining fails fast instead of falling back to a shared legacy model.
- Ensure the database is up-to-date and contains verified messages before running the script.