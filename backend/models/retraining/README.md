# Retraining Models

This module is responsible for retraining the machine learning models used in the Scamalyzer project. It fetches verified messages from the database, processes them, and updates the models with new training data.

## Overview
The retraining process involves the following steps:
1. **Fetching Verified Messages**: Retrieves messages marked as verified and not yet used for training from the database. Messages in the database must have the `verified` column set to `True` and the `used_for_training` column set to `False` to be included in the retraining process.
2. **Processing Messages**: Extracts message content and determines the label with the highest confidence from the existing models.
3. **Retraining Models**: Updates the BERT, BiLSTM, and XGBoost models with the new data.
4. **Marking Messages as Used**: Marks the processed messages as used for training in the database.

## Models
### BERT
- Uses the Hugging Face `transformers` library.
- Tokenizes the messages and trains the model using the `Trainer` API.
- Saves the updated model and tokenizer.

### BiLSTM
- Uses TensorFlow/Keras.
- Loads the existing tokenizer and model.
- Prepares the data and retrains the model.
- Saves the updated model.

### XGBoost
- Uses the `xgboost` library.
- Transforms the messages using a pre-trained TF-IDF vectorizer.
- Retrains the model and saves the updated model and vectorizer.

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
- Ensure the database is up-to-date and contains verified messages before running the script.