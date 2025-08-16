from flask import Flask, Blueprint, request, jsonify
from model.bert_model import analyze_message

app = Flask(__name__)
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    label, confidence = analyze_message(message)
    
    return jsonify({'label': label, 'confidence': confidence})

app.register_blueprint(api_blueprint)