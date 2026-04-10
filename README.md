# Scamalyzer

Scamalyzer analyzes text messages and emails for scam, phishing, and deceptive content. The backend now supports multilingual inference with separate models for `en`, `es`, and `de` across the BERT, BiLSTM, and XGBoost pipelines.

## Local Setup

### Prerequisites

- Python 3.10+ with `venv`
- Node.js 18+ and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/mckwk/Scamalyzer.git
cd Scamalyzer
```

### 2. Configure environment variables

Copy the example environment file to `.env`:

```bash
copy .env.example .env
```

The local defaults are already set for development. Confirm these values in `.env`:

- `FRONTEND_ADDRESS=localhost`
- `FRONTEND_PORT=3000`
- `BACKEND_ADDRESS=localhost`
- `BACKEND_PORT=5000`
- `DEFAULT_LANGUAGE=en`
- `DB_FILE=backend/database/scamalyzer.db`

The multilingual model templates should point to the trained artifacts under `backend/models/training/`:

- `BERT_MODEL_PATH_TEMPLATE=models/training/DistilBERT/{lang}`
- `BILSTM_MODEL_PATH_TEMPLATE=models/training/bilstm/bilstm_model_{lang}.h5`
- `BILSTM_TOKENIZER_PATH_TEMPLATE=models/training/bilstm/bilstm_tokenizer_{lang}.json`
- `XGBOOST_MODEL_PATH_TEMPLATE=models/training/xgboost/xgb_model_{lang}.joblib`
- `TFIDF_PATH_TEMPLATE=models/training/xgboost/tfidf_{lang}.joblib`

### 3. Run the backend

Open a terminal in `backend` and start the Flask app with the project virtual environment:

```bash
cd backend
D:/Repos/Scamalyzer/venv/Scripts/python.exe app.py
```

The API should be available at `http://localhost:5000`.

### 4. Run the frontend

Open a second terminal in `frontend`:

```bash
cd frontend
npm install
npm start
```

The web app should open at `http://localhost:3000`.

### 5. Verify the app

- Open the frontend in your browser.
- Submit a message on the main analysis page.
- The frontend calls the backend at `http://localhost:5000/analyze`.

## How multilingual inference works

The backend detects the message language and normalizes it to one of:

- `en`
- `es`
- `de`

For each request, all three model families are run using the matching language-specific artifacts:

- BERT loads the model directory for that language.
- BiLSTM loads the matching `.h5` model and tokenizer.
- XGBoost loads the matching model and TF-IDF vectorizer.

If a required artifact is missing, the backend now fails fast instead of silently falling back to a different language or shared model.

## Retraining flow

The backend saves every successful inference to the SQLite database with the per-model outputs.

Retraining uses only messages that are:

- marked as `verified = True`
- not yet marked as `used_for_training = True`

To retrain from the database, run:

```bash
cd backend
D:/Repos/Scamalyzer/venv/Scripts/python.exe models/retraining/retraining.py
```

After retraining, processed rows are marked as used so they are not reused automatically.

## Optional: expose the backend with ngrok

If you want to access a local backend from outside your machine, start the backend locally first and then run:

```bash
ngrok http 5000
```

Update the frontend API endpoint only if you want the web app to use the public ngrok URL instead of localhost.

## Notes

- The frontend is configured for local development and points to `http://localhost:5000`.
- The backend database is SQLite at `backend/database/scamalyzer.db`.
- Some older model artifacts may emit version-compatibility warnings during loading; the app still runs, but retraining/exporting with the current library versions is recommended.
