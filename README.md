# 🚀  - Multi-Cloud Security Copilot

## ⚡ 3 Commands to Get Started

```bash
# 0. Setup Gemini API keys (first time only)
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (see API_KEY_SETUP.md)

# 1. Generate data for all clouds (30 resources each)
cd backend
python generate_data_multicloud.py --provider all --count 30
python main.py --provider azure
python main.py --provider gcp
copy data\findings_*.json ..\frontend\public\

# 2. Start backend (keep running)
python api.py

# 3. Start frontend in new terminal (keep running)
cd ..\frontend
npm run dev
```

**Open browser:** http://localhost:5173

**Click cloud buttons (bottom-right) to switch between AWS, Azure, GCP!**

---

## 🎯 Current Data (Ready to View)

| Cloud | Findings | Critical | High | Cost | Savings |
|-------|----------|----------|------|------|---------|
| **AWS** | 27 | 11 | 12 | $242 | $111 |
| **Azure** | 29 | 9 | 5 | $306 | $125 |
| **GCP** | 28 | 6 | 11 | $268 | $110 |

---

## 🔄 Generate New Data

### In UI (Easiest):
Click **"⟳ Generate Data"** button → Wait → Auto-refresh!

### Command Line:
```bash
python generate_data_multicloud.py --provider aws --count 50
python main.py --provider aws
copy data\findings_aws.json ..\frontend\public\
```

Then: **Ctrl + Shift + R** in browser

---

## 🌐 Cloud Service Names

| Service | AWS | Azure | GCP |
|---------|-----|-------|-----|
| Activity | CloudTrail | Activity Log | Cloud Audit Logs |
| Inventory | Config | Resource Graph | Asset Inventory |
| Cost | Cost Explorer | Cost Management | Cloud Billing |
| Security | Security Hub | Security Center | Security Command Center |
| Metrics | CloudWatch | Azure Monitor | Cloud Monitoring |

---

## 📦 Resource Naming

| Type | AWS | Azure | GCP |
|------|-----|-------|-----|
| Compute | ec2-web-server | vm-web-server | gce-web-server |
| Storage | s3-backup-store | blob-backup-store | gcs-backup-store |
| Database | rds-primary-db | sqldb-primary-db | cloudsql-primary-db |
| Network | alb-public-lb | lb-public-lb | gclb-public-lb |

---

## 🎨 UI Features

- **Cloud Selector**: Bottom-right corner (3 buttons)
- **Generate Button**: Top-right (creates new data)
- **Refresh Button**: Top-right (reloads data)
- **Export CSV**: Top-right (downloads findings)
- **Priority Queue**: Top 5 critical/high findings
- **Charts**: Risk, Cost, Compliance
- **Table**: All findings (sortable, filterable)
- **Drawer**: Click row for details
- **GenAI Copilot**: Multi-cloud AI assistant (AWS/Azure/GCP)
  - Cloud-specific CLI commands
  - Automatic service name translation
  - Context-aware explanations

---

## 🔧 Troubleshooting

### GenAI Copilot not working?
**Setup API keys:**
```bash
cd backend
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
# See API_KEY_SETUP.md for detailed instructions
```

**Multiple keys for high availability:**
```bash
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_1=your_fallback_key_1
GEMINI_API_KEY_2=your_fallback_key_2
```
System will automatically rotate keys on quota exhaustion!

### Not seeing new data?
**Hard refresh:** Ctrl + Shift + R (Windows/Linux) or Cmd + Shift + R (Mac)

### Backend not starting?
```bash
cd backend
pip install -r requirements.txt
python api.py
```

### Frontend not starting?
```bash
cd frontend
npm install
npm run dev
```

### Files not copying?
```bash
cd backend
copy data\findings_aws.json ..\frontend\public\findings_aws.json
copy data\findings_azure.json ..\frontend\public\findings_azure.json
copy data\findings_gcp.json ..\frontend\public\findings_gcp.json
```

---

## 📁 Key Files

```
backend/
├── generate_data_multicloud.py  ← Generate data
├── main.py                      ← Run analysis
├── api.py                       ← Start server
└── data/
    ├── findings_aws.json        ← AWS results
    ├── findings_azure.json      ← Azure results
    └── findings_gcp.json        ← GCP results

frontend/
├── src/
│   ├── App.jsx                  ← Cloud selector
│   └── Dashboard.jsx            ← Main dashboard
└── public/
    ├── findings_aws.json        ← AWS data (UI)
    ├── findings_azure.json      ← Azure data (UI)
    └── findings_gcp.json        ← GCP data (UI)
```

---

## ✅ Verification

### Check backend files:
```bash
cd backend
find /c "resource_id" data\findings_aws.json
find /c "resource_id" data\findings_azure.json
find /c "resource_id" data\findings_gcp.json
```

Should show ~27-30 each!

### Check frontend files:
```bash
find /c "resource_id" ..\frontend\public\findings_aws.json
find /c "resource_id" ..\frontend\public\findings_azure.json
find /c "resource_id" ..\frontend\public\findings_gcp.json
```

Should match backend!

### Check UI:
1. Open http://localhost:5173
2. Look at "Total Findings" tile
3. Should show 27-30 (not 5!)
4. If showing 5: Press Ctrl+Shift+R

---

## 🎯 What Makes This Multi-Cloud?

✅ **Same Code**: One codebase for all clouds
✅ **Cloud-Specific Names**: ec2/vm/gce, CloudTrail/Activity Log/Audit Logs
✅ **Unified Model**: Same data structure across clouds
✅ **Consistent Rules**: 15 rules apply to all
✅ **Easy Switching**: Click button to change cloud
✅ **Independent Data**: Each cloud has separate findings
✅ **GenAI Copilot**: Multi-cloud AI with cloud-specific CLI commands
  - AWS CLI for AWS resources
  - Azure CLI for Azure resources
  - gcloud CLI for GCP resources

---

## 📚 Documentation

- `COMPLETE_DEMO_GUIDE.md` - Full architecture & demo
- `WORKING_STATE.md` - Current state & verification
- `COLLECTOR_NAMES.md` - Service mapping details
- `MULTICLOUD_GUIDE.md` - Implementation guide
- `DATA_VERIFICATION.md` - Data change verification

---

## 🎉 You're Ready!

**Everything is set up and working!**

Just run:
```bash
cd backend && python api.py
cd frontend && npm run dev
```

Open http://localhost:5173 and click the cloud buttons! 🚀
