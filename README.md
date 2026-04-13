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

### iOS App (Capacitor)

To build and export the iOS app, you must use a macOS device with Xcode installed.

1. Navigate to the `frontend` directory.
2. Install npm dependencies:
   ```
   npm install
   ```
3. Build the web app assets:
   ```
   npm run build
   ```
4. Sync assets and native configuration to iOS:
   ```
   npx cap sync ios
   ```
5. Open the iOS project in Xcode:
   ```
   npx cap open ios
   ```
6. In Xcode, choose an iOS device/simulator and archive/export the app.

## Usage

Once the backend and frontend applications are running, you can access the web interface to input messages for analysis. The application will classify the messages and provide feedback on their safety.
