from utils.config import BACKEND_ADDRESS, BACKEND_PORT, FRONTEND_URL
from api.routes import api_blueprint, limiter
from flask_cors import CORS
from flask import Flask, jsonify
import sys
from os.path import abspath, dirname

# Add the backend directory to the Python path
sys.path.append(dirname(abspath(__file__)))


app = Flask(__name__)
limiter.init_app(app)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                FRONTEND_URL,
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                r"https://.*\.vercel\.app",
                "https://scamalyzer.vercel.app",
                "https://pulverable-kaydence-modular.ngrok-free.dev",
            ]
        }
    },
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)
app.register_blueprint(api_blueprint, url_prefix='/')


@app.after_request
def set_security_headers(response):
    # Content Security Policy - restrictive policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self';"
    )
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Force HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Control permissions
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Cross-Origin policies
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    return response


@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Welcome to the Scamalyzer API"})


if __name__ == "__main__":
    app.run(host=BACKEND_ADDRESS, port=int(BACKEND_PORT))
