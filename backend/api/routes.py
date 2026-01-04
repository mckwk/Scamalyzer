from flask import Blueprint, jsonify, request, after_this_request
import os
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from database.database import Message, SessionLocal
from models.bert_model import analyze_message as analyze_bert
from models.bilstm_model import analyze_message as analyze_bilstm
from models.xgboost_model import analyze_message as analyze_xgboost

api_blueprint = Blueprint('api', __name__)

# Rate limiter setup - will be initialized with the app in app.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = os.getenv("ADMIN_API_KEY")
        if not api_key:
            return jsonify({"error": "Server admin key not configured"}), 500
        header_key = request.headers.get("X-API-KEY") or (request.headers.get("Authorization") or "").replace("Bearer ", "")
        if header_key != api_key:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def analyze_with_models(message):
    bert_result = analyze_bert(message)
    bilstm_result = analyze_bilstm(message)
    xgboost_result = analyze_xgboost(message)
    print("Analyzing message:", message)
    print("BERT Result:", bert_result)
    print("BiLSTM Result:", bilstm_result)
    print("XGBoost Result:", xgboost_result)

    return {
        'BERT': bert_result,
        'BiLSTM': bilstm_result,
        'XGBoost': xgboost_result,
    }


def save_analysis_to_db(message, analysis_results):
    db = SessionLocal()
    try:
        existing_message = db.query(Message).filter(
            Message.content == message).first()
        if existing_message:
            return existing_message  # Return the existing message if it's a duplicate

        db_message = Message(
            content=message,
            bert_label=analysis_results['BERT'][0],
            bert_confidence=analysis_results['BERT'][1],
            bilstm_label=analysis_results['BiLSTM'][0],
            bilstm_confidence=analysis_results['BiLSTM'][1],
            xgboost_label=analysis_results['XGBoost'][0],
            xgboost_confidence=analysis_results['XGBoost'][1],
            verified=False,
            used_for_training=False
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    finally:
        db.close()


def format_message(message):
    return {
        'id': message.id,
        'content': message.content,
        'bert_label': message.bert_label,
        'bert_confidence': message.bert_confidence,
        'bilstm_label': message.bilstm_label,
        'bilstm_confidence': message.bilstm_confidence,
        'xgboost_label': message.xgboost_label,
        'xgboost_confidence': message.xgboost_confidence,
        'timestamp': message.timestamp.isoformat(),
        'verified': message.verified,
        'used_for_training': message.used_for_training,
    }


@api_blueprint.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    analysis_results = analyze_with_models(message)
    results = [
        {'model': model, 'label': result[0], 'confidence': result[1]}
        for model, result in analysis_results.items()
    ]
    best_result = max(results, key=lambda x: x['confidence'])
    save_analysis_to_db(message, analysis_results)
    return jsonify({'results': results, 'best': best_result})


@api_blueprint.route('/messages', methods=['GET'])
@limiter.limit("30 per minute")
@require_api_key
def get_messages():
    db = SessionLocal()
    try:
        messages = db.query(Message).all()
        return jsonify([format_message(msg) for msg in messages])
    finally:
        db.close()


@api_blueprint.route('/verify_message/<int:message_id>', methods=['POST'])
@limiter.limit("20 per minute")
@require_api_key
def verify_message(message_id):
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        message.verified = True
        db.commit()
        return jsonify({'message': 'Message verified successfully'})
    finally:
        db.close()
