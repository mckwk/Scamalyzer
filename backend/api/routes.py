from flask import Blueprint, jsonify, request

from database.database import Message, SessionLocal
from models.bert_model import analyze_message as analyze_bert
from models.bilstm_model import analyze_message as analyze_bilstm
from models.xgboost_model import analyze_message as analyze_xgboost

api_blueprint = Blueprint('api', __name__)


def analyze_with_models(message):
    return {
        'BERT': analyze_bert(message),
        'BiLSTM': analyze_bilstm(message),
        'XGBoost': analyze_xgboost(message),
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
def get_messages():
    db = SessionLocal()
    try:
        messages = db.query(Message).all()
        return jsonify([format_message(msg) for msg in messages])
    finally:
        db.close()


@api_blueprint.route('/verify_message/<int:message_id>', methods=['POST'])
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
