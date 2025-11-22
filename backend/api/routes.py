from flask import Blueprint, Flask, jsonify, request
from backend.models.bert_model import analyze_message as analyze_bert
from backend.models.bilstm_model import analyze_message as analyze_bilstm
from backend.models.xgboost_model import analyze_message as analyze_xgboost

app = Flask(__name__)
api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    # Analyze message with all models
    bert_result = analyze_bert(message)
    bilstm_result = analyze_bilstm(message)
    xgboost_result = analyze_xgboost(message)

    # Combine results
    results = [
        {'model': 'BERT', 'label': bert_result[0], 'confidence': bert_result[1]},
        {'model': 'BiLSTM', 'label': bilstm_result[0], 'confidence': bilstm_result[1]},
        {'model': 'XGBoost', 'label': xgboost_result[0], 'confidence': xgboost_result[1]},
    ]

    # Pick the best result based on confidence
    best_result = max(results, key=lambda x: x['confidence'])

    return jsonify({'results': results, 'best': best_result})


app.register_blueprint(api_blueprint)
