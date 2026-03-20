# GenAI-Powered Cloud Security Copilot

Risk & Cost Optimization Advisor for Cloud Infrastructure

## Project Structure

```
copilot-aws/
├── backend/
│   ├── data/              # Simulated data and findings
│   ├── models/            # Resource and Rule models
│   ├── parser/            # Data parser
│   ├── engine/            # Rule engine, risk scorer, insight generator
│   ├── copilot/           # GenAI copilot layer
│   ├── api.py             # Flask API
│   └── main.py            # Analyzer pipeline
└── frontend/
    └── src/               # React dashboard
```

## Features

### 1. Config-Driven Rule Engine
- Rules stored in JSON
- Dynamic condition matching
- Category-based classification

### 2. Weighted Risk Scoring
- Formula: `(Base + Cost + Usage) × Exposure`
- Category weights (Security: 4x, Compliance: 3x, Cost: 2x)
- Priority thresholds (CRITICAL/HIGH/MEDIUM/LOW)

### 3. Insight Generator
- Template-based messages
- Context-aware summaries
- Actionable recommendations

### 4. GenAI Copilot
- Natural language queries
- Command-based interface
- Intelligent responses

### 5. Interactive Dashboard
- Real-time findings visualization
- Priority filtering
- Detailed resource analysis

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the analyzer:
```bash
python main.py
```

4. Start the API server:
```bash
python api.py
```

The API will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The UI will run on `http://localhost:5173`

## Usage

### Dashboard
- View all security findings
- Filter by priority (Critical, High, Medium, Low)
- Click on findings for detailed analysis
- See risk scores, impacts, and recommendations

### AI Copilot
- Ask natural language questions
- Use quick commands:
  - `show critical` - Display critical findings
  - `explain r3` - Explain specific resource
  - `summary` - Get executive summary
  - `show cost issues` - Display cost optimization opportunities

## Architecture Highlights

### Data Flow
```
resources.json → Parser → Rule Engine → Risk Scorer → Insight Generator → findings.json → Dashboard/Copilot
```

### Risk Scoring Formula
```
Base Score = Σ(rule_risk × category_weight)
Cost Factor = cost / 5
Usage Factor = 5 (if usage < 5%)
Exposure Multiplier = 1.5 (if public)
Final Score = (Base + Cost + Usage) × Exposure
```

## Key Differentiators

1. **Production-Grade Architecture** - Not simple if-else logic
2. **Config-Driven** - Rules and scoring configurable via JSON
3. **Weighted Risk Model** - Industry-standard scoring approach
4. **Template-Based Insights** - Human-readable, actionable outputs
5. **GenAI Integration** - Intelligent copilot for queries

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: React, Vite
- **Architecture**: Modular, scalable design
- **Data**: Simulated cloud resources (50 resources)

## Results

From 50 simulated cloud resources:
- **14 CRITICAL** findings (Score >= 100)
- **2 HIGH** findings (Score >= 60)
- **6 MEDIUM** findings (Score >= 30)
- **13 LOW** findings (Score < 30)
- **$169** total cost at risk
- **$43** potential savings from critical/high priority fixes

## Future Enhancements

- Real cloud provider integration (AWS, Azure, GCP)
- Advanced GenAI models (OpenAI, AWS Bedrock)
- Automated remediation workflows
- Historical trend analysis
- Multi-cloud support
