# AyuNet — Startup Guide

> Step-by-step guide to get AyuNet running from a fresh clone. Follow each step in order.

---

## Prerequisites

Before you begin, install the following:

| Tool | Version | Download |
|------|---------|----------|
| **Docker Desktop** | Latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Python** | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

Verify installations:

```bash
docker --version        # Docker version 24+
python --version        # Python 3.11+
node --version          # v18+
git --version           # git version 2+
```

> **Resource requirements:** Neo4j via Docker needs ~512MB RAM. The full stack (Neo4j + Backend + Frontend) runs comfortably on 2GB.

---

## Step 1: Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/aryanp006/AyuNet.git
cd AyuNet

# Create Python virtual environment
python -m venv venv

# Activate it

# ── Windows CMD:
venv\Scripts\activate

# ── Windows PowerShell:
.\venv\Scripts\Activate.ps1

# ── macOS / Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure API Keys

```bash
# Copy the environment template
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
# Neo4j (default Docker values — no change needed for local dev)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Groq (REQUIRED — get from https://console.groq.com)
GROQ_API_KEY=gsk_your_key_here

# Sarvam AI (needed for voice features — get from https://sarvam.ai)
SARVAM_API_KEY=your_sarvam_key_here

# Twilio (needed for follow-up calls — get from https://twilio.com)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# App URLs
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

### Which keys do I actually need?

| Feature | Required Keys |
|---------|--------------|
| **Diagnose tab** (text input) | `GROQ_API_KEY` only |
| **Voice input/output** | `GROQ_API_KEY` + `SARVAM_API_KEY` |
| **Follow-up phone calls** | All keys (Groq + Sarvam + Twilio) |

> **Tip:** Start with just `GROQ_API_KEY` to test the core diagnosis flow. Add the others later.

### Where to get free API keys

| Service | URL | Free Tier |
|---------|-----|-----------|
| **Groq** | [console.groq.com](https://console.groq.com) | 30 requests/minute |
| **Sarvam AI** | [sarvam.ai](https://www.sarvam.ai) | 500 API calls/day |
| **Twilio** | [twilio.com](https://www.twilio.com) | $15 trial credit + 1 free phone number |

---

## Step 3: Start Neo4j

Make sure Docker Desktop is running, then:

```bash
cd AyuNet

# Pull and start Neo4j container
docker-compose up neo4j -d

# Watch logs until you see "Started."
docker-compose logs -f neo4j
```

### Verify Neo4j is running

```bash
# Check container health
docker-compose ps
# Should show neo4j as "healthy"
```

You can also open the **Neo4j Browser** at [http://localhost:7474](http://localhost:7474):
- **Username:** `neo4j`
- **Password:** `password`
- Run `RETURN 1` to verify connectivity

> **Note:** Neo4j takes 15–30 seconds to fully boot. Wait until `docker-compose ps` shows "healthy" before proceeding.

---

## Step 4: Initialize the Database

With Neo4j running and your venv activated:

```bash
cd backend

# Step 4a: Create constraints and indexes (10 constraints, 11 indexes)
python scripts/setup_graph.py

# Step 4b: Seed demo data (51 symptoms, 22 diseases, 28 drugs, 5 patients, etc.)
python scripts/seed_data.py
```

### Expected output for setup_graph.py:

```
[Setup] Connecting to Neo4j...
[Setup] Connected!

[Step 1] Creating uniqueness constraints...
  [OK] Patient.patient_id unique constraint
  [OK] Symptom.symptom_id unique constraint
  [OK] Disease.disease_id unique constraint
  ...

[Step 2] Creating indexes for lookup performance...
  [OK] Index on Patient.name
  [OK] Index on Symptom.name
  ...

[Step 3] Verifying setup...
  Constraints: 10
  Indexes: 21

[Setup] DONE! Neo4j schema ready.
```

### Expected output for seed_data.py:

```
[Seed] Connecting to Neo4j...
[Seed] Connected!

[Seed] Upserting symptoms...    -> 51 symptoms
[Seed] Upserting diseases...    -> 22 diseases
[Seed] Creating disease-symptom edges... -> 150+ edges
[Seed] Upserting drugs...       -> 28 drugs
...
[Seed] COMPLETE!
```

### Verify data in Neo4j Browser

Open [http://localhost:7474](http://localhost:7474) and run:

```cypher
-- Check patients
MATCH (p:Patient) RETURN p.name, p.language, p.phone LIMIT 5

-- Test multi-hop traversal
MATCH (s:Symptom)<-[:HAS_SYMPTOM]-(d:Disease)-[:REFERS_TO]->(sp:Specialist)
WHERE s.name = 'fever'
RETURN s.name, d.name, sp.name
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Neo4j isn't fully booted. Wait 15s and retry. |
| "Constraint already exists" | Safe to ignore — constraints use `IF NOT EXISTS`. |
| Setup script hangs | Check that `NEO4J_URI` in `.env` matches Docker port `7687`. |

---

## Step 5: Start the Backend

```bash
cd AyuNet/backend

# Make sure venv is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Expected output:

```
[AyuNet] Starting up...
[Neo4j] Warm-up ping successful
[AyuNet] PageRank cached
[AyuNet] Scheduler started
[AyuNet] Ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Verify backend

Open a new terminal and run:

```bash
# Health check
curl http://localhost:8000/health
# -> {"status": "healthy"}

# Root endpoint
curl http://localhost:8000/
# -> {"name": "AyuNet", "status": "running", "version": "1.0.0"}
```

Or simply open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---

## Step 6: Start the Frontend

Open a **new terminal** (keep the backend running):

```bash
cd AyuNet/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Opens at **[http://localhost:5173](http://localhost:5173)**

---

## Step 7: Verify Everything Works

### Test each Dashboard tab:

| Tab | Test Action | Expected Result |
|-----|-------------|-----------------|
| **Diagnose** | Type "I have fever and headache for 2 days" → Click Analyze | Extracted symptoms, top-5 diagnoses, graph visualization |
| **Diagnose** | Click mic → speak in Hindi → stop | Auto-transcription + auto-analysis |
| **Drug Check** | Select Warfarin + Aspirin → Check Interactions | "Severe" interaction with mechanism |
| **Treatment Path** | Select "Dengue Fever" → Find Path | Disease → Specialist → Treatment → Drug pathway |
| **Risk Analysis** | Select "Rahul" → Predict Risk | 4-hop risk predictions with multiplier scores |
| **Follow-ups** | View due patients | Karthik + Priya should appear as due today |

### Check sidebar indicators:

- ✅ **Green dot** = WebSocket connected
- 🔴 **Red dot** = WebSocket disconnected (backend may not be running)

---

## Alternative: Full Docker Setup

To run everything via Docker (Neo4j + Backend + Frontend):

```bash
cd AyuNet

# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# After Neo4j shows "healthy", initialize the database (one-time only):
cd backend
python scripts/setup_graph.py
python scripts/seed_data.py
```

### Service URLs

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:5173](http://localhost:5173) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| Backend Swagger | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Neo4j Browser | [http://localhost:7474](http://localhost:7474) |
| Neo4j Bolt | `bolt://localhost:7687` |

---

## Twilio Setup (for Follow-up Calls)

Follow-up calls require Twilio to reach your backend via a **public URL** (for webhooks).

### For local development:

```bash
# Install ngrok (https://ngrok.com)
ngrok http 8000

# Copy the public URL, e.g., https://abc123.ngrok-free.app
# Update .env:
BASE_URL=https://abc123.ngrok-free.app
```

### For production:

Set `BASE_URL` to your deployed backend URL (e.g., your Railway URL).

---

## Deployment

### Backend → Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Set environment variables
railway variables set NEO4J_URI=bolt://your-neo4j-host:7687
railway variables set NEO4J_USER=neo4j
railway variables set NEO4J_PASSWORD=your_password
railway variables set GROQ_API_KEY=...
railway variables set SARVAM_API_KEY=...
railway variables set TWILIO_ACCOUNT_SID=...
railway variables set TWILIO_AUTH_TOKEN=...
railway variables set TWILIO_PHONE_NUMBER=...
railway variables set BASE_URL=https://your-railway-url.railway.app

# Deploy
railway up
```

The `railway.toml` is pre-configured:
```toml
[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```

### Frontend → Vercel

```bash
cd frontend
npm install -g vercel
vercel

# Set env var in Vercel dashboard:
# VITE_API_URL = https://your-railway-backend-url.railway.app
```

### Neo4j → AuraDB (Production)

For production, replace local Docker with Neo4j AuraDB Free:

1. Go to [neo4j.com/cloud/aura-free](https://neo4j.com/cloud/aura-free/)
2. Create a free instance
3. Note connection URI (`neo4j+s://xxxxx.databases.neo4j.io`), username, password
4. Update `.env`:
   ```env
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_aura_password
   ```
5. Run setup + seed scripts against the cloud instance

---

## Demo Day Checklist

### 10 minutes before demo:

- [ ] Re-run `python scripts/seed_data.py` so follow-ups are due "today"
- [ ] Hit every backend endpoint once (warms Neo4j query cache)
- [ ] Open Dashboard, switch through all 5 tabs
- [ ] Verify WebSocket shows green "connected" dot
- [ ] Pre-dial a test Twilio call to verify it connects

### Backup plan:

- [ ] Pre-record a full Twilio call conversation as video backup
- [ ] Screenshot each Dashboard tab for presentation slides
- [ ] Backend has error handling and cached PageRank — it won't crash if Neo4j hiccups

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Neo4j won't start | Check Docker Desktop is running |
| "Connection refused" on port 7687 | Neo4j still booting — wait 15–30 seconds |
| Setup script fails | Run `python scripts/setup_graph.py` again (idempotent) |
| Groq rate limit (429) | Wait 60 seconds, or reduce concurrent requests |
| Sarvam STT returns empty | Check audio format (webm/wav), verify API key |
| Twilio call not connecting | Need public URL (ngrok) for webhooks |
| Frontend can't reach backend | Check `VITE_API_URL` env var matches backend port |
| PageRank query fails | Normal with empty DB — run `seed_data.py` first |
| WebSocket shows "Disconnected" | Backend must be running before frontend connects |
| `pip install` fails | Make sure venv is activated and Python is 3.11+ |
| `npm install` fails | Delete `node_modules` and `package-lock.json`, retry |
