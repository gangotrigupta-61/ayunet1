<p align="center">
  <img src="https://img.shields.io/badge/Neo4j-4581C3?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="TailwindCSS" />
  <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white" alt="Twilio" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

# 🩺 AyuNet — Graph-Powered Multilingual Health Intelligence

> **800 million Indians can't describe symptoms in English.** AyuNet lets them speak in their mother tongue — and a graph database does in milliseconds what no SQL database can: multi-hop traversals across symptoms, diseases, drugs, and risk factors to deliver precise, life-saving diagnoses. Then it *calls* the patient back, speaks to them in their language, and alerts the doctor in real-time.

---

## 🏗️ Architecture

```
Patient Voice (Hindi / Tamil / Telugu / Bengali / Kannada / Marathi / English)
     │
     ▼
Sarvam AI STT ──► Groq LLM (extract symptoms)
                       │
                       ▼
                 ┌─────────────┐
                 │    Neo4j    │
                 │ Q1: Diagnose│──►  Cytoscape.js
                 │ Q2: Drug    │    Visualization
                 │ Q3: Treat   │
                 │ Q4: Rare    │──►  Diagnosis Cards
                 │ Q5: Risk    │
                 │ Q6: PageRank│──►  Risk Alerts
                 │ Q7: Context │         │
                 │ Q8: FollowUp│         ▼
                 └──────┬──────┘   WebSocket ──► Doctor Dashboard
                        │
                        ▼
                 Groq LLM (generate caring script)
                        │
                        ▼
                 Sarvam AI TTS
                        │
                        ▼
                 Twilio Voice Call ──► Patient's Phone
```

---

## ❓ Why a Graph Database?

A SQL database can look up a disease from symptoms. Neo4j traverses **4 hops deep** — from a patient's existing conditions, through risk factors, to diseases they don't even know they're developing, to lab tests they haven't taken yet — in **milliseconds**.

It doesn't just diagnose. It **predicts**. And then it **calls** the patient and asks them the exact right questions, because the graph *told* it what to ask.

| Feature | Neo4j Capability | Query |
|---------|------------------|-------|
| Symptom → Diagnosis | Multi-hop traversal (MATCH + UNWIND) | Q1 |
| Drug Interaction Check | Pattern matching (INTERACTS_WITH) | Q2 |
| Treatment Pathway | Directed traversal (Disease → Treatment → Drug) | Q3 |
| Rare Disease Detection | Low-prevalence filter + 4-hop deep traversal | Q4 |
| Comorbidity Risk | 4-hop + multiplier accumulation | Q5 |
| Disease Ranking | Degree centrality (connectivity analysis) | Q6 |
| Patient Context (Calls) | Multi-hop context aggregation | Q7 |
| Follow-up Scheduling | Date filter + graph traversal | Q8 |

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | 🎙️ **Multilingual Voice Diagnosis** | Speak symptoms in Hindi, Tamil, Telugu, Bengali, Kannada, or Marathi — get diagnosed |
| 2 | 💊 **Drug Interaction Checker** | Pattern matching across drug combinations with severity ratings |
| 3 | 🛤️ **Treatment Pathway Finder** | Shortest path from disease to specialist to treatment to drug |
| 4 | 🧬 **Rare Disease Detection** | 4-hop deep traversal catches uncommon conditions from atypical symptoms |
| 5 | 🫀 **Comorbidity Risk Predictor** | 4-hop risk accumulation with automatic alert threshold |
| 6 | 📈 **Graph-Native PageRank** | Disease network analysis for weighted differential diagnosis |
| 7 | 📞 **Automated Follow-up Calls** | Graph-driven, empathetic, multilingual phone calls via Twilio |
| 8 | 🔔 **Real-time Doctor Alerts** | WebSocket alerts when risk flags trigger during patient calls |
| 9 | 📊 **Live Graph Visualization** | Hop-by-hop Cytoscape.js animation proving multi-hop traversals |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Graph Database** | Neo4j (Cypher queries, graph models, 10 vertex types, 15 edge types) |
| **Backend** | FastAPI (async), WebSockets, APScheduler |
| **Frontend** | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| **LLM** | Groq (LLaMA 3 70B) — symptom extraction + script generation |
| **Voice** | Sarvam AI (saarika:v2 STT + bulbul:v1 TTS) — 7 Indic languages |
| **Calls** | Twilio — automated follow-up phone calls |
| **Visualization** | Cytoscape.js with hop-by-hop traversal animation |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/aryanp006/AyuNet.git
cd AyuNet

# 2. Start Neo4j
docker-compose up neo4j -d

# 3. Setup backend
python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env                               # Fill in API keys

# 4. Initialize database
cd backend
python scripts/setup_graph.py
python scripts/seed_data.py

# 5. Start backend
uvicorn main:app --reload --port 8000

# 6. Start frontend (new terminal)
cd frontend
npm install && npm run dev
```

Or run everything with Docker:
```bash
docker-compose up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Neo4j Browser | http://localhost:7474 |

> 📖 **Detailed setup instructions:** See [STARTUP_GUIDE.md](./STARTUP_GUIDE.md)
>
> 📋 **Full project overview:** See [OVERVIEW.md](./OVERVIEW.md)

---

## 🧪 Demo Patients

| Name | Language | Conditions | Demo Purpose |
|------|----------|-----------|--------------|
| Priya | Hindi | Dengue + Diabetes | Drug interaction + comorbidity risk |
| Karthik | Tamil | Post-surgery | Twilio follow-up call demo |
| Ananya | Telugu | Unusual symptoms | Rare disease detection |
| Rahul | English | Multiple chronic | 4-hop risk prediction |
| Meera | Bengali | New patient | Full symptom-to-diagnosis flow |

---

## 🔑 API Keys

| Key | Source | Free Tier |
|-----|--------|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | 30 req/min |
| `SARVAM_API_KEY` | [sarvam.ai](https://www.sarvam.ai) | 500 calls/day |
| `TWILIO_ACCOUNT_SID` | [twilio.com](https://www.twilio.com) | $15 trial credit |
| `TWILIO_AUTH_TOKEN` | Twilio dashboard | Included |
| `TWILIO_PHONE_NUMBER` | Twilio → Buy a number | 1 free with trial |

> **Minimum to run:** Only `GROQ_API_KEY` is required for the Diagnose tab. Voice features need `SARVAM_API_KEY`. Follow-up calls need all Twilio keys.

---

## 📁 Project Structure

```
AyuNet/
├── backend/
│   ├── main.py                  # FastAPI app + lifespan + scheduler
│   ├── config.py                # Environment variable loading
│   ├── routers/
│   │   ├── diagnosis.py         # /api/analyze, /api/diagnose, /api/drug-check, etc.
│   │   ├── voice.py             # /api/stt, /api/tts (Sarvam AI)
│   │   ├── calls.py             # /api/call/initiate, Twilio webhooks
│   │   └── alerts.py            # WebSocket /ws/alerts
│   ├── services/
│   │   ├── graph.py             # Neo4j driver + all 8 Cypher queries
│   │   ├── nlp.py               # Groq LLM symptom extraction + script gen
│   │   ├── voice.py             # Sarvam STT/TTS integration
│   │   ├── caller.py            # Twilio call orchestration
│   │   └── followup.py          # Daily follow-up scheduler logic
│   ├── schemas/
│   │   └── models.py            # Pydantic request/response models
│   └── scripts/
│       ├── setup_graph.py       # Create Neo4j constraints + indexes
│       └── seed_data.py         # Populate graph with demo data
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Landing page
│   │   ├── pages/
│   │   │   └── Dashboard.tsx    # 5-tab clinical dashboard
│   │   ├── components/
│   │   │   ├── DiagnoseTab.tsx   # Voice/text symptom analysis
│   │   │   ├── DrugCheckTab.tsx  # Drug interaction checker
│   │   │   ├── TreatmentPathTab.tsx
│   │   │   ├── RiskAnalysisTab.tsx
│   │   │   ├── FollowupsTab.tsx  # Follow-up call management
│   │   │   └── GraphView.tsx    # Cytoscape.js visualization
│   │   └── hooks/
│   │       └── useWebSocket.ts  # Real-time alert hook
│   └── package.json
├── docker-compose.yml           # Neo4j + Backend + Frontend
├── Dockerfile                   # Backend container (Python 3.11)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── railway.toml                 # Railway deployment config
```

---

## 📄 License

MIT
