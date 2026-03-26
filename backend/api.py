import json
import os
import sys
import subprocess

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.append(os.path.dirname(__file__))

from copilot.copilot_engine import CopilotEngine

app = Flask(__name__)
CORS(app)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Initialize copilot (auto-detects Claude API key)
copilot = CopilotEngine()


# ── Findings & Stats ──────────────────────────────────────────────────────────

@app.route('/api/findings', methods=['GET'])
def get_findings():
    provider = request.args.get('provider', 'aws')
    findings_path = os.path.join(BASE_PATH, 'data', f'findings_{provider}.json')
    
    # Fallback to default findings.json if provider-specific not found
    if not os.path.exists(findings_path):
        findings_path = os.path.join(BASE_PATH, 'data', 'findings.json')
    
    try:
        with open(findings_path, 'r', encoding='utf-8') as f:
            findings = json.load(f)
        return jsonify(findings)
    except FileNotFoundError:
        return jsonify([])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    from copilot.context_builder import ContextBuilder
    cb    = ContextBuilder()
    stats = cb.get_summary_stats()
    # Don't send all findings in the stats response
    stats.pop('findings', None)
    return jsonify(stats)


# ── Copilot ───────────────────────────────────────────────────────────────────

@app.route('/api/copilot', methods=['POST'])
def copilot_query():
    data  = request.json or {}
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    result = copilot.process_query(query)
    return jsonify(result)


# ── Data Generation ───────────────────────────────────────────────────────────

@app.route('/api/generate', methods=['POST'])
def generate_data():
    """
    Trigger a fresh data generation + analysis run.
    Accepts optional JSON body: { "n_resources": 50, "provider": "aws" }
    Returns the new summary stats after generation.
    """
    data       = request.json or {}
    n_resources = int(data.get('n_resources', 50))
    provider    = data.get('provider', 'aws')

    generator_path = os.path.join(BASE_PATH, 'generate_data_multicloud.py')
    result = subprocess.run(
        [sys.executable, generator_path, '--provider', provider, '--count', str(n_resources)],
        capture_output=True, text=True, cwd=BASE_PATH
    )

    if result.returncode != 0:
        return jsonify({
            'success': False,
            'error':   result.stderr[-500:] if result.stderr else 'Unknown error'
        }), 500

    # Reload and return fresh stats
    try:
        from copilot.context_builder import ContextBuilder
        # Re-instantiate to pick up new findings.json
        cb    = ContextBuilder()
        stats = cb.get_summary_stats()
        stats.pop('findings', None)
    except Exception as e:
        stats = {}

    return jsonify({
        'success':     True,
        'n_resources': n_resources,
        'provider':    provider,
        'stats':       stats,
        'message':     f'Generated {n_resources} resources for {provider.upper()} and ran analysis pipeline.'
    })


@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Return list of available cloud providers with data."""
    providers = []
    for p in ['aws', 'azure', 'gcp']:
        findings_path = os.path.join(BASE_PATH, 'data', f'findings_{p}.json')
        if os.path.exists(findings_path):
            try:
                with open(findings_path, 'r', encoding='utf-8') as f:
                    findings = json.load(f)
                providers.append({
                    'id': p,
                    'name': {'aws': 'AWS', 'azure': 'Azure', 'gcp': 'GCP'}[p],
                    'count': len(findings)
                })
            except:
                pass
    return jsonify(providers)


# ── Health ────────────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    gemini_key    = os.environ.get('GEMINI_API_KEY', '').strip()
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()

    if gemini_key:
        genai_mode = 'gemini'
        model      = 'gemini-1.5-flash'
    elif anthropic_key:
        genai_mode = 'claude'
        model      = 'claude-haiku-4-5'
    else:
        genai_mode = 'mock'
        model      = 'rule-based-mock'

    return jsonify({
        'status': 'healthy',
        'genai':  genai_mode,
        'model':  model,
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  GenAI Cloud Security Copilot - API Server")
    print("=" * 50)
    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
    if gemini_key:
        print(f"  GenAI: Gemini AI connected (gemini-1.5-flash)")
    elif anthropic_key:
        print(f"  GenAI: Claude AI connected")
    else:
        print(f"  GenAI: Mock mode (set GEMINI_API_KEY or ANTHROPIC_API_KEY)")
    print(f"  Server: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
