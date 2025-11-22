import sys
from os.path import dirname, abspath

# Add the backend directory to the Python path
sys.path.append(dirname(abspath(__file__)))

from api.routes import api_blueprint
from flask import Flask, jsonify
from flask_cors import CORS
from utils.config import FRONTEND_URL, BACKEND_ADDRESS, BACKEND_PORT

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": FRONTEND_URL}})
app.register_blueprint(api_blueprint, url_prefix='/')


@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Welcome to the Scamalyzer API"})


if __name__ == "__main__":
    app.run(host=BACKEND_ADDRESS, port=int(BACKEND_PORT), debug=True)