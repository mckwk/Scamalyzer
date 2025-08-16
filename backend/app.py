from flask import Flask, jsonify
from api.routes import api_blueprint

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/')

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Welcome to the Scamalyzer API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)