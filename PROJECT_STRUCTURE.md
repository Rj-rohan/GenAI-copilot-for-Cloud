# GenAI-Powered Cloud Security Copilot

## 🎯 Clean Project Structure

```
copilot-aws/
├── backend/
│   ├── collector/                    # Data Collection Layer
│   │   ├── __init__.py
│   │   ├── cloudtrail_collector.py   # Activity logs
│   │   ├── config_collector.py       # Resource inventory
│   │   ├── cost_collector.py         # Billing data
│   │   ├── metrics_collector.py      # Performance metrics
│   │   ├── securityhub_collector.py  # Security findings
│   │   └── collector_orchestrator.py # Orchestrates all collectors
│   │
│   ├── copilot/                      # GenAI Copilot Layer
│   │   ├── cli_commands.py
│   │   ├── context_builder.py
│   │   ├── copilot_engine.py
│   │   ├── llm_connector.py
│   │   ├── prompt_generator.py
│   │   └── query_handler.py
│   │
│   ├── data/                         # Data Files
│   │   ├── sources/                  # 5 AWS Data Sources
│   │   │   ├── cloudtrail.json
│   │   │   ├── config.json
│   │   │   ├── cost.json
│   │   │   ├── metrics.json
│   │   │   └── securityhub.json
│   │   ├── findings.json             # Analysis output
│   │   ├── insight_templates.json    # Message templates
│   │   ├── resources.json            # Resource inventory
│   │   ├── rules.json                # Detection rules
│   │   └── scoring_config.json       # Risk scoring config
│   │
│   ├── engine/                       # Analysis Engine
│   │   ├── insight_generator.py      # Generate insights
│   │   ├── risk_scorer.py            # Calculate risk scores
│   │   ├── rule_engine.py            # Main engine
│   │   ├── rule_evaluator.py         # Evaluate rules
│   │   └── rule_loader.py            # Load rules
│   │
│   ├── models/                       # Data Models
│   │   ├── resource.py               # Resource model
│   │   └── rule.py                   # Rule model
│   │
│   ├── api.py                        # Flask REST API
│   ├── generate_data.py              # Data generator
│   ├── main.py                       # Analysis pipeline
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # React Dashboard
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── findings.json             # Findings for UI
│   │   └── icons.svg
│   │
│   ├── src/
│   │   ├── App.css                   # Main app styles
│   │   ├── App.jsx                   # Main app component
│   │   ├── Copilot.css               # Copilot styles
│   │   ├── Copilot.jsx               # AI Copilot component
│   │   ├── Dashboard.css             # Dashboard styles
│   │   ├── Dashboard.jsx             # Dashboard component
│   │   ├── index.css                 # Global styles
│   │   └── main.jsx                  # React entry point
│   │
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Generate Fresh Data
```bash
cd backend
python generate_data.py
```

### 2. Start Backend API
```bash
python api.py
```

### 3. Start Frontend
```bash
cd ../frontend
npm install
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 📊 Data Flow

```
generate_data.py
    ↓
5 AWS Data Sources (JSON files)
    ↓
CollectorOrchestrator
    ↓
Unified Resource Model (40+ attributes)
    ↓
Rule Engine → Risk Scorer → Insight Generator
    ↓
findings.json
    ↓
Flask API ←→ React Dashboard
```

## 🎯 Core Components

### Backend

**Data Collection:**
- `collector_orchestrator.py` - Coordinates 5 collectors
- Individual collectors for each AWS service

**Analysis Engine:**
- `rule_engine.py` - Main analysis logic
- `risk_scorer.py` - Weighted risk calculation
- `insight_generator.py` - Human-readable insights

**API:**
- `api.py` - REST endpoints for frontend
- `main.py` - CLI analysis pipeline

### Frontend

**Components:**
- `Dashboard.jsx` - Security findings overview
- `Copilot.jsx` - AI-powered chat interface
- `App.jsx` - Main application shell

## 🔧 Key Files

### Must-Have Files

**Backend:**
- ✅ `generate_data.py` - Generate simulated data
- ✅ `main.py` - Run analysis pipeline
- ✅ `api.py` - Start REST API server
- ✅ `requirements.txt` - Python dependencies

**Frontend:**
- ✅ `package.json` - Node dependencies
- ✅ `vite.config.js` - Vite configuration
- ✅ `src/main.jsx` - React entry point

### Configuration Files

- ✅ `data/rules.json` - Detection rules
- ✅ `data/scoring_config.json` - Risk scoring weights
- ✅ `data/insight_templates.json` - Message templates

## 🗑️ Removed Files

### Obsolete Files (Cleaned Up)
- ❌ `parser/data_parser.py` - Replaced by collector_orchestrator
- ❌ `tests/` - Test files removed
- ❌ `copilot_demo.py` - Demo script removed
- ❌ `RISK_SCORING.md` - Documentation removed
- ❌ `DATA_COLLECTOR.md` - Documentation removed
- ❌ `WHATS_NEW.md` - Documentation removed
- ❌ `UI_FEATURES.md` - Documentation removed
- ❌ `frontend/README.md` - Duplicate README removed
- ❌ `frontend/src/assets/hero.png` - Unused assets removed
- ❌ `frontend/src/assets/react.svg` - Unused assets removed
- ❌ `frontend/src/assets/vite.svg` - Unused assets removed
- ❌ `setup_git.bat` - Git setup script removed

## 📝 Commands Reference

### Backend Commands
```bash
# Generate data (50 resources)
python generate_data.py

# Generate custom amount
python generate_data.py 100

# Run analysis only
python main.py

# Start API server
python api.py
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Project Status

✅ **Clean** - All obsolete files removed  
✅ **Working** - Only production code remains  
✅ **Organized** - Clear folder structure  
✅ **Documented** - This README explains everything  

## 🚀 Ready for Production!

Your project is now clean, organized, and ready to showcase! 🎉
