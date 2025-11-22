# Scamalyzer

The Scamalyzer project is designed to analyze text messages (such as SMS and emails) for signs of deception and fraud. This application utilizes advanced machine learning techniques, specifically BERT-based models, to classify messages as safe or fraudulent.

## Setup Instructions

### Prerequisites

- Clone the repository:
  ```bash
  git clone https://github.com/mckwk/Scamalyzer.git
  cd Scamalyzer
  ```  
- Copy the .env.example file to .env:
  ```bash
   cp .env.example .env
  ```  
- Update the .env file with the appropriate paths and configuration values.

### Backend

1. Navigate to the `backend` directory.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   flask run
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

## Usage

Once the backend and frontend applications are running, you can access the web interface to input messages for analysis. The application will classify the messages and provide feedback on their safety.
