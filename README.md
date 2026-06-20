# 🛡️ VendorGuard

**AI-Powered Supply Chain Risk Agent for SME Manufacturers**

> Kaggle AI Agents Capstone 2026 | Agents for Business Track

VendorGuard is a multi-agent AI system that monitors vendor risk in real time for small and medium-sized manufacturers in India's auto-ancillary sector. It fuses the manufacturer's own vendor records with live external signals (weather, news, fuel prices, commodity trends) to predict supply chain disruptions and auto-generate procurement actions.

---

## 🏗️ Architecture

```
Vendor Google Sheet (MCP)
        ↓
[Ingest Agent]  →  Structured vendor objects
        ↓  (parallel fan-out per vendor)
[Risk Monitor Agent]  ←  Weather / News / Prices / Logistics
        ↓  Risk scores + evidence
[Prediction Agent]  →  Unified risk assessment
        ↓  (if risk score > threshold)
[Procurement Agent]  →  Draft PO / Alternate supplier / Alert
        ↓
Dashboard UI  +  WhatsApp alert (stretch)
```

**4 Specialized Agents** built on Google ADK + Gemini 1.5 Pro:
- **Ingest Agent** — Reads vendor data via Google Drive MCP
- **Risk Monitor Agent** — Fetches weather, news, commodity, fuel signals
- **Prediction Agent** — Computes composite risk scores (0–100)
- **Procurement Agent** — Generates PO drafts for high-risk vendors

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+ (for frontend)
- API Keys: Gemini, OpenWeatherMap, Newscatcher

### Setup

```bash
# Clone the repo
git clone https://github.com/sarthak11234/VendorGuard.git
cd VendorGuard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
python main.py
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scan` | Start a new risk scan |
| `GET` | `/api/scan/{scan_id}` | Poll scan status |
| `GET` | `/api/vendors` | Get all vendor risk assessments |
| `GET` | `/api/vendors/{id}` | Get single vendor details |
| `GET` | `/api/alerts` | Get HIGH-risk vendor alerts |
| `GET` | `/api/health` | Health check |

### CLI Mode

```bash
vendorguard scan --vendor-sheet <SHEET_URL> --output report.json
```

---

## 📁 Project Structure

```
vendorguard/
├── agents/              # ADK agent definitions
│   ├── __init__.py
│   ├── coordinator.py   # Pipeline orchestrator
│   ├── ingest.py        # Vendor data ingestion
│   ├── risk_monitor.py  # External risk signals
│   ├── prediction.py    # Risk scoring
│   └── procurement.py   # PO draft generation
├── api/                 # FastAPI backend
│   ├── __init__.py
│   ├── models.py        # Pydantic data models
│   └── routes.py        # API endpoint handlers
├── frontend/            # React dashboard
├── tools/               # Custom tools & integrations
│   ├── __init__.py
│   ├── weather.py       # OpenWeatherMap client
│   ├── news.py          # Newscatcher client
│   ├── trends.py        # pytrends wrapper
│   └── ppac.py          # PPAC fuel price scraper
├── data/                # Synthetic demo data
│   └── vendors_synthetic.csv
├── tests/               # Test suite
├── config.py            # Configuration from env vars
├── main.py              # FastAPI entry point
├── Dockerfile           # Multi-stage Docker build
├── requirements.txt     # Python dependencies (pinned)
├── .env.example         # Environment variable template
└── README.md
```

---

## 🎨 Risk Color Coding

| Band | Score | Color | Action |
|------|-------|-------|--------|
| 🟢 LOW | 0–40 | Green `#16A34A` | Monitor only |
| 🟡 MEDIUM | 41–65 | Amber `#D97706` | Flag on dashboard |
| 🔴 HIGH | 66–100 | Red `#DC2626` | Auto-trigger procurement |

---

## 🔒 Security

- Vendor data **never persisted** — read from user's Drive, held in-memory only
- All API keys via **environment variables**, never in code
- All external API calls are **read-only**
- No authentication for MVP (hackathon demo)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | Google ADK (Python) |
| LLM | Gemini 1.5 Pro |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Tailwind CSS |
| Deployment | Google Cloud Run |

---

## 📄 License

This project is built for the Kaggle AI Agents Capstone 2026 hackathon.
