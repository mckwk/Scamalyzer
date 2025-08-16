# Scamalyzer

The Scamalyzer project is designed to analyze text messages (such as SMS and emails) for signs of deception and fraud. This application utilizes advanced machine learning techniques, specifically BERT-based models, to classify messages as safe, suspicious, or fraudulent.

## Project Structure

The project is organized into several key components:

- **backend/**: Contains the server-side application, including the model, API routes, and utility functions.
  - **app.py**: Main entry point for the backend application.
  - **requirements.txt**: Lists the Python dependencies required for the backend.
  - **model/**: Contains the implementation of the BERT model for text classification.
  - **api/**: Defines the API routes for analyzing messages.
  - **utils/**: Contains utility functions for preprocessing text data.

- **frontend/**: Contains the client-side application built with React.
  - **src/**: Source files for the React application, including components and styles.
  - **package.json**: Configuration file for npm, listing dependencies and scripts.
  - **README.md**: Documentation specific to the frontend application.

- **database/**: Contains the database models and the SQLite database file.
  - **models.py**: Defines the database schema for storing user submissions and results.
  - **db.sqlite3**: SQLite database file.

## Setup Instructions

### Backend

1. Navigate to the `backend` directory.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   python app.py
   ```

### Frontend

1. Navigate to the `frontend` directory.
2. Install the required npm packages:
   ```
   npm install
   ```
3. Start the frontend application:
   ```
   npm start
   ```

### Database

The database is automatically created and managed by the application. Ensure that the `db.sqlite3` file is present in the `database` directory.

## Usage

Once the backend and frontend applications are running, you can access the web interface to input messages for analysis. The application will classify the messages and provide feedback on their safety.
