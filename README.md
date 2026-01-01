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


### Exposing the Backend with ngrok

To make the Flask backend accessible over the internet, you can use ngrok. Follow these steps:

1. [Download ngrok](https://ngrok.com/download) and install it on your system.
2. Start the Flask backend as described in the "Backend" section.
3. Open a new terminal and run the following command to expose the Flask server:
   ```bash
   ngrok http 5000
   ```
4. Copy the public URL provided by ngrok (e.g., `https://<random-subdomain>.ngrok.io`) and use it to access the backend API from the internet. Paste this URL into `API_ENDPOINT` in `frontend\src\constants\Config.ts` file.

Note: Ensure that the `BACKEND_ADDRESS` in your `.env` file is set to `localhost` and the `BACKEND_PORT` is set to `5000` for this to work.

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
