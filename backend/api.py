from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.dirname(__file__))

from copilot.copilot_engine import CopilotEngine

app = Flask(__name__)
CORS(app)

copilot = CopilotEngine()

@app.route('/api/findings', methods=['GET'])
def get_findings():
    findings_path = os.path.join(os.path.dirname(__file__), 'data', 'findings.json')
    
    import json
    with open(findings_path, 'r', encoding='utf-8') as f:
        findings = json.load(f)
    
    return jsonify(findings)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    from copilot.context_builder import ContextBuilder
    context_builder = ContextBuilder()
    stats = context_builder.get_summary_stats()
    return jsonify(stats)

@app.route('/api/copilot', methods=['POST'])
def copilot_query():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    result = copilot.process_query(query)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
