# AyuNet — Detailed Project Overview

> A graph-powered, multilingual health intelligence platform that diagnoses patients in their native Indian language, predicts comorbidity risks through 4-hop graph traversals, and autonomously follows up with patients via voice calls — alerting doctors in real-time when risk flags trigger.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [System Architecture](#system-architecture)
- [Graph Data Model](#graph-data-model)
- [Core Graph Queries (Q1–Q8)](#core-graph-queries-q1q8)
- [Indic Voice AI Pipeline](#indic-voice-ai-pipeline)
- [Real-time Voice AI (LiveKit)](#real-time-voice-ai-livekit)
- [Automated Follow-up Call Engine](#automated-follow-up-call-engine)
- [Direct Phone Calling](#direct-phone-calling)
- [Frontend Dashboard](#frontend-dashboard)
- [API Endpoints](#api-endpoints)
- [Data Pipeline](#data-pipeline)
- [Tech Stack Deep Dive](#tech-stack-deep-dive)
- [Performance Characteristics](#performance-characteristics)
- [Future Roadmap](#future-roadmap)

---

## Problem Statement

**800 million Indians** cannot describe their medical symptoms in English. Rural and semi-urban patients often:

- Misdiagnose themselves or delay treatment due to language barriers
- Cannot read English prescriptions or lab reports
- Miss follow-up appointments because reminders come via text in English
- Fall through the cracks of the healthcare system because no one tracks their comorbidity risks

Traditional SQL databases can match symptoms to a single disease. But real healthcare is **multi-hop** — a patient's existing diabetes, combined with their current medications, their family history, and the subtle interaction between two drugs they're taking, can point to a completely different diagnosis than a simple symptom lookup would suggest.

---

## Solution Overview

AyuNet is a **graph-powered multilingual health intelligence platform** that:

1. **Listens** in the patient's native language (Hindi, Tamil, Telugu, Bengali, Kannada, Marathi, English)
2. **Traverses** a medical knowledge graph (Neo4j) to diagnose, check drug interactions, find treatment pathways, detect rare diseases, and predict comorbidity risks — all through multi-hop Cypher queries
3. **Speaks** the diagnosis back in the patient's language
4. **Calls** patients automatically for follow-ups — asking personalized questions generated from their graph context
5. **Alerts** doctors in real-time via WebSockets when risk flags trigger during calls
6. **Converses** in real-time via browser-based Voice AI using LiveKit sessions with Sarvam STT/TTS
7. **Dials** any phone number directly for ad-hoc patient follow-ups (not limited to registered patients)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Vite)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐  │
│  │  DiagnoseTab │ │ DrugCheckTab│ │TreatmentPath│ │  RiskAnalysis   │  │
│  │  (Voice+Text)│ │             │ │    Tab      │ │     Tab         │  │
│  └──────┬───────┘ └──────┬──────┘ └──────┬──────┘ └───────┬─────────┘  │
│         │                │               │                │            │
│  ┌──────┴────────────────┴───────────────┴────────────────┴─────────┐  │
│  │                    Cytoscape.js GraphView                        │  │
│  │              (hop-by-hop traversal animation)                    │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │ REST + WebSocket                         │
│  ┌──────────────────────┐  ┌┴─────────────────────────────────────┐   │
│  │  LiveKitVoice (Voice │  │  FollowupsTab  ◄── WebSocket Alerts  │   │
│  │  AI Tab — real-time) │  │  + Quick Call (dial any number)      │   │
│  └──────────┬───────────┘  └──────────────────────────────────────┘   │
└─────────────┼───────────────────┬───────────────────────────────────────┘
              │                   │
┌─────────────▼───────────────────▼─────────────┐
│           BACKEND (FastAPI)                    │
│                                               │
│  routers/                                     │
│   ├─ diagnosis.py                             │
│   ├─ voice.py                                 │
│   ├─ calls.py (+ /call-number)                │
│   ├─ livekit.py (token, respond, greeting)    │
│   └─ alerts.py (WS)                           │
│                                               │
│  services/                                    │
│   ├─ graph.py (Q1-Q8)                         │
│   ├─ nlp.py (Groq LLM)                       │
│   ├─ voice.py (Sarvam AI — pavithra speaker)  │
│   ├─ caller.py (Twilio + direct call)         │
│   ├─ livekit_agent.py (session manager)       │
│   └─ followup.py                              │
└─────┬────┬────┬────┬─────────────────┘
      │    │    │    │
  ┌───┘    │    │    └────────────┐
  ▼        ▼    ▼                ▼
┌──────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│Neo4j │ │Groq API│ │Sarvam AI │ │ LiveKit  │
│(Graph│ │(LLaMA 3│ │(STT/TTS) │ │(WebRTC)  │
│ DB)  │ │ 70B)   │ │          │ │          │
└──────┘ └────────┘ └─────┬────┘ └──────────┘
                          │
                    ┌─────▼─────┐
                    │  Twilio   │
                    │  (Calls)  │
                    └───────────┘
```

---

## Graph Data Model

### Vertex Types (10)

| Vertex | Key Properties | Description |
|--------|---------------|-------------|
| **Patient** | patient_id, name, phone, language, age, gender | Individual patient record |
| **Symptom** | symptom_id, name, category | Medical symptom (e.g., fever, headache) |
| **Disease** | disease_id, name, icd_code, prevalence, description | Medical condition with ICD coding |
| **Drug** | drug_id, name, drug_class | Pharmaceutical agent |
| **Specialist** | specialist_id, name, specialization | Medical specialist type |
| **Treatment** | treatment_id, name, treatment_type, cost_tier | Treatment protocol |
| **RiskFactor** | risk_factor_id, name, category | Clinical risk factor |
| **LabTest** | lab_test_id, name, test_type | Diagnostic lab test |
| **Protocol** | protocol_id, name, followup_days | Follow-up scheduling protocol |
| **FollowUp** | followup_id, status, scheduled_date, pain_score | Individual follow-up record |

### Edge Types (15)

| Edge | From → To | Key Properties | Used In |
|------|-----------|---------------|---------|
| **HAS_SYMPTOM** | Disease → Symptom | weight | Q1, Q4 |
| **INTERACTS_WITH** | Drug ↔ Drug | severity, mechanism, clinical_note | Q2 |
| **TREATED_BY** | Disease → Treatment | success_rate, accessibility_score | Q3 |
| **PRESCRIBED** | Treatment → Drug | dosage, duration | Q3 |
| **REFERS_TO** | Disease → Specialist | — | Q3, Q4 |
| **REQUIRES_TEST** | Disease → LabTest | — | Q4, Q5 |
| **HAS_CONDITION** | Patient → Disease | status, diagnosed_date | Q5, Q7 |
| **RISK_INCREASES** | Disease → RiskFactor | — | Q5 |
| **ELEVATES** | RiskFactor → Disease | multiplier | Q5 |
| **HAS_COMPLETED_TEST** | Patient → LabTest | — | Q5 |
| **TAKES_MEDICATION** | Patient → Drug | dosage | Q7 |
| **PRESENTS_WITH** | Patient → Symptom | — | Q7 |
| **HAS_FOLLOWUP** | Patient → FollowUp | linked_disease | Q7, Q8 |
| **HAS_PROTOCOL** | Disease → Protocol | — | Q7 |
| **FOLLOWS_PROTOCOL** | FollowUp → Protocol | — | Q8 |

### Seeded Data Summary

| Entity | Count |
|--------|-------|
| Symptoms | 51 |
| Diseases | 22 |
| Drugs | 28 |
| Specialists | 12 |
| Treatments | 12 |
| Risk Factors | 10 |
| Lab Tests | 14 |
| Protocols | 3 |
| Patients | 10 |
| Total Edges | 350+ |

---

## Core Graph Queries (Q1–Q8)

All queries are implemented in `backend/services/graph.py` as Cypher queries executed via the Neo4j Python driver.

### Q1: Symptom-to-Diagnosis Multi-hop Traversal

```
run_diagnose(symptoms: list[str])
```

**What it does:** Takes an array of extracted symptoms, traverses `Symptom ←[HAS_SYMPTOM]— Disease`, ranks by match count and edge weight, returns top-5 diagnoses with confidence scores.

**Why a graph:** A SQL `JOIN` would require pre-defined symptom-disease mappings in a flat table. The graph traversal dynamically weights multi-symptom matches and returns confidence scores based on how many symptoms connect to each disease node — all in a single query.

**Cypher pattern:**
```cypher
UNWIND $symptoms AS symptom_name
MATCH (s:Symptom)<-[r:HAS_SYMPTOM]-(d:Disease)
WHERE toLower(s.name) = toLower(symptom_name)
WITH d, count(DISTINCT s) AS matched_count, sum(r.weight) AS total_weight
RETURN d.name, matched_count, confidence_score
ORDER BY confidence_score DESC
LIMIT 5
```

---

### Q2: Drug Interaction Check

```
run_drug_interactions(drugs: list[str])
```

**What it does:** Pattern matches `INTERACTS_WITH` edges between selected drugs, returns severity (mild/moderate/severe), mechanism, and clinical notes. Ordered by severity.

**Why a graph:** Drug interactions are inherently a **graph problem** — each drug can interact with any other drug in a set. The graph finds all interaction paths in a single traversal, something that requires N² self-joins in SQL.

---

### Q3: Treatment Pathway

```
run_treatment_path(disease_name: str)
```

**What it does:** Traverses `Disease →[TREATED_BY]→ Treatment →[PRESCRIBED]→ Drug` with optional `Disease →[REFERS_TO]→ Specialist`. Returns full pathway with success rates, cost tiers, and dosages.

**Why a graph:** The *pathway* from disease to treatment to drug to specialist is a natural directed graph. The query returns it as a single traversal — no multi-table joins needed.

---

### Q4: Rare Disease Detection (4-hop)

```
run_rare_diseases(symptoms: list[str])
```

**What it does:** Same symptom matching as Q1, but filters to `prevalence < 0.05` (rare diseases). Also traverses to recommended specialists and lab tests. Returns ICD codes.

**Why a graph:** Rare diseases share atypical symptoms with common diseases. The graph traversal surfaces these connections that a simple SQL lookup would miss — especially when the rare disease shares only 1–2 symptoms with the patient's profile.

---

### Q5: Comorbidity Risk Prediction (4-hop)

```
run_comorbidity_risk(patient_id: str)
```

**What it does:** The most complex query — 4 hops deep:

| Hop | Traversal | Purpose |
|-----|-----------|---------|
| 1 | Patient → Disease (HAS_CONDITION) | Current diagnoses |
| 2 | Disease → RiskFactor (RISK_INCREASES) | Risk factors from conditions |
| 3 | RiskFactor → Disease (ELEVATES) | Predicted future diseases |
| 4 | Disease → LabTest (REQUIRES_TEST) | Tests patient hasn't taken |

Returns risk multiplier scores. Threshold > 1.5 triggers automatic doctor alert.

**Why a graph:** This is **impossible in SQL** without 4 nested joins across 5 tables. Neo4j does it in a single traversal, accumulating multiplier scores along the way.

---

### Q6: Disease PageRank (Degree Centrality)

```
run_pagerank()
```

**What it does:** Ranks all diseases by total graph connectivity — symptom links + treatment links + risk links + specialist links. Used to weight differential diagnosis (highly connected diseases ranked higher).

**Why a graph:** Centrality analysis is a **native graph algorithm**. The query counts all relationship types per disease node to produce a network-aware ranking.

---

### Q7: Patient Context (Multi-hop Read)

```
run_patient_context(patient_id: str)
```

**What it does:** Aggregates everything about a patient in a single query — conditions, medications, symptoms, follow-ups, protocols. Used by the follow-up call engine to generate personalized scripts.

**Why a graph:** A patient's full clinical context spans 6 entity types. The graph retrieves it in one traversal instead of 6 SQL queries.

---

### Q8: Due Follow-ups

```
run_due_followups()
```

**What it does:** Finds all patients with `FollowUp` nodes where `status = 'pending'` and `scheduled_date <= today`. Traverses to their conditions for context.

---

## Indic Voice AI Pipeline

### Speech-to-Text (STT)

- **Engine:** Sarvam AI `saarika:v2`
- **Languages:** Hindi, Tamil, Telugu, Bengali, Kannada, Marathi (+ English via Web Speech API fallback)
- **Flow:** MediaRecorder captures audio (WebM format) → Send to `/api/stt` → Sarvam transcribes → Text returned to frontend → Auto-triggers analysis

### Text-to-Speech (TTS)

- **Engine:** Sarvam AI `bulbul:v1`
- **Flow:** Diagnosis result text → Send to `/api/tts` with language code → Sarvam generates audio → Plays in browser
- **Use in calls:** Same TTS engine generates the voice for automated Twilio follow-up calls

### Language Detection

- **Engine:** Groq LLM (LLaMA 3 70B)
- **Method:** The LLM auto-detects the language from the transcribed text during symptom extraction — no manual language selection needed by the user

---

## Real-time Voice AI (LiveKit)

AyuNet includes a browser-based real-time Voice AI interface powered by LiveKit sessions.

### How It Works

```
1. User clicks "Start Voice Chat" in the Voice AI tab
         │
         ▼
2. Backend creates a LiveKit session (room + token)
         │
         ▼
3. User speaks into the browser microphone
   MediaRecorder captures audio (WebM) →
   Sarvam STT transcribes in the detected language
         │
         ▼
4. Groq LLM generates a contextual healthcare response
   (language-aware, using conversation history)
         │
         ▼
5. Sarvam TTS (bulbul:v1, pavithra speaker) converts response to audio
         │
         ▼
6. Audio plays back in the browser — full duplex conversation loop
```

### Key Features

- **Session management** — each conversation gets a unique room with full history
- **Language auto-detection** — detects Hindi, Tamil, Telugu, Bengali, etc. from the first utterance
- **Structured data extraction** — continuously extracts pain scores, medication adherence, and new symptoms from conversation
- **Risk flagging** — flags high-risk responses (pain > 7, critical new symptoms) in real-time
- **Chat-bubble transcript** — visual display of the full conversation with extracted metadata badges

---

## Automated Follow-up Call Engine

This is AyuNet's most distinctive feature — the graph database doesn't just diagnose, it **calls patients back**.

### How It Works

```
1. APScheduler fires daily at 9:00 AM
         │
         ▼
2. Q8 (run_due_followups) → finds patients due today
         │
         ▼
3. For each patient:
   a. Q7 (run_patient_context) → full clinical context
   b. Groq LLM → generates personalized, empathetic follow-up script
      (in patient's language, referencing their specific conditions)
   c. Sarvam TTS → converts script to speech audio
   d. Twilio → places actual phone call to patient's phone number
         │
         ▼
4. Patient responds (voice) →
   Sarvam STT transcribes → Groq extracts structured data:
   {pain_score, took_medication, new_symptoms}
         │
         ▼
5. Data written back to Neo4j FollowUp node
   If pain_score > 7 or critical new symptoms:
         │
         ▼
6. WebSocket alert → Doctor Dashboard (real-time)
```

### What Makes It Special

- **The AI doesn't read a generic script.** Q7 gives it *everything* about the patient — conditions, medications, drug side effects, risk factors, overdue tests, past follow-up responses. Groq uses this to generate hyper-specific, empathetic questions.
- **The patient feels like they're talking to someone who truly knows them** — because the graph *does* know them.
- **Structured data collection:** Patient voice responses are transcribed, parsed into structured JSON, and written back to Neo4j — closing the feedback loop.

---

## Direct Phone Calling

AyuNet's Follow-ups tab includes a **Quick Call** feature that lets doctors call any phone number directly — not limited to registered patients in Neo4j.

### How It Works

1. Doctor enters a phone number, patient name, and language in the Quick Call card
2. Backend creates a minimal patient context (no Neo4j lookup required)
3. Groq generates a personalized greeting in the selected language
4. Sarvam TTS converts the greeting to speech audio
5. Twilio places the call with the same dynamic conversation engine used for scheduled follow-ups
6. Doctor can end the call from the dashboard at any time

This enables ad-hoc follow-ups, new patient intake calls, and emergency outreach to any phone number.

---

## Frontend Dashboard

The dashboard is a 6-tab clinical interface built with React 19, TypeScript, Tailwind CSS v4, and Cytoscape.js.

### Tabs

| Tab | Component | Features |
|-----|-----------|----------|
| **Diagnose** | `DiagnoseTab.tsx` | Voice/text input, symptom extraction, top-5 diagnoses, TTS playback, live graph |
| **Drug Check** | `DrugCheckTab.tsx` | Multi-drug selector, interaction severity cards, graph visualization |
| **Treatment Path** | `TreatmentPathTab.tsx` | Disease selector, pathway cards, directed graph flow |
| **Risk Analysis** | `RiskAnalysisTab.tsx` | Patient selector, 4-hop risk prediction, concentric ring graph |
| **Follow-ups** | `FollowupsTab.tsx` | Quick Call (any number), due patient list, call initiation, demo trigger, live transcript |
| **Voice AI** | `LiveKitVoice.tsx` | Real-time browser voice chat, STT/TTS pipeline, risk flagging, chat transcript |

### Additional UI Features

- **Dark / Light mode** with system preference detection
- **WebSocket connection indicator** (green/red dot in sidebar)
- **Real-time risk alert toasts** when risk flags trigger during calls
- **Responsive layout** with sidebar navigation

---

## API Endpoints

### Diagnosis & Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Full pipeline: text → LLM extract → graph diagnose → return results |
| POST | `/api/diagnose` | Direct graph diagnosis from symptom array |
| POST | `/api/drug-check` | Check drug interactions |
| POST | `/api/treatment-path` | Find treatment pathway for a disease |
| POST | `/api/rare-diseases` | Detect rare diseases from symptoms |
| POST | `/api/comorbidity-risk/{patient_id}` | 4-hop comorbidity risk prediction |
| GET | `/api/pagerank` | Disease network rankings |

### Voice

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/stt` | Sarvam AI speech-to-text |
| POST | `/api/tts` | Sarvam AI text-to-speech |

### Calls & Follow-ups

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/call/initiate` | Initiate a follow-up call to a patient |
| POST | `/api/calls/call-number` | Call any phone number directly |
| GET | `/api/call/due` | List patients with due follow-ups |
| POST | `/api/calls/webhook/start` | Twilio webhook for call script |
| POST | `/api/calls/webhook/{call_sid}/respond` | Twilio webhook for response collection |
| POST | `/api/calls/end/{call_sid}` | End an active call |
| POST | `/api/calls/demo-trigger` | One-click demo call trigger |

### LiveKit Voice AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/livekit/token` | Generate LiveKit session token |
| POST | `/api/livekit/greeting` | Generate session greeting audio |
| POST | `/api/livekit/respond` | Process speech and return AI response |
| POST | `/api/livekit/end` | End a LiveKit session |
| GET | `/api/livekit/status` | Check session status |

### WebSocket

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | `/ws/alerts` | Real-time doctor alerts (risk flags) |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |

---

## Data Pipeline

### Graph Initialization

```bash
# Step 1: Create schema (constraints + indexes)
cd backend && python scripts/setup_graph.py

# Step 2: Populate with demo data
python scripts/seed_data.py
```

**`setup_graph.py`** creates:
- 10 uniqueness constraints (one per vertex type)
- 11 lookup indexes (on frequently queried properties)

**`seed_data.py`** populates:
- 51 symptoms across 8 categories
- 22 diseases with ICD codes, prevalence scores, and descriptions
- 28 drugs with drug classes
- 150+ disease-symptom edges with weights
- 12 drug interaction edges with severity ratings
- 12 specialists, 12 treatments, 10 risk factors, 14 lab tests
- 3 follow-up protocols, 5 demo patients, 2 pending follow-ups

### Data Flow During Operation

```
Voice Input → Sarvam STT → Groq LLM (extract) → Neo4j (traverse) → Frontend (visualize)
                                                        │
                                                        ▼
                                                   Groq LLM (script) → Sarvam TTS → Twilio (call)
                                                                                         │
                                                                                         ▼
                                                   Sarvam STT (response) → Groq (parse) → Neo4j (write back)
                                                                                              │
                                                                                              ▼
                                                                                    WebSocket → Doctor Alert
```

---

## Tech Stack Deep Dive

### Neo4j (Graph Database)

- **Version:** 5.16.0 (via Docker)
- **Driver:** `neo4j` Python driver (Bolt protocol)
- **Features used:** Cypher queries, UNWIND, pattern matching, uniqueness constraints, schema indexes, date functions
- **Deployment:** Docker locally, Neo4j AuraDB Free for production
- **Connection:** Singleton driver pattern with startup warm-up ping

### FastAPI (Backend)

- **Version:** Latest (async)
- **Features:** Async lifespan management, CORS middleware, APScheduler for cron jobs, Pydantic v2 models
- **Scheduler:** `AsyncIOScheduler` fires daily at 9:00 AM for follow-up checks
- **WebSocket:** Native FastAPI WebSocket for real-time doctor alerts

### React + Vite (Frontend)

- **React:** v19.2 with TypeScript
- **Vite:** v8 with `@vitejs/plugin-react`
- **Tailwind CSS:** v4.2 with `@tailwindcss/vite` plugin
- **Cytoscape.js:** v3.33 via `react-cytoscapejs` wrapper + `cytoscape-cola` layout
- **Animations:** Framer Motion for component transitions
- **Icons:** Lucide React
- **Routing:** React Router v7

### Groq (LLM)

- **Model:** LLaMA 3.3 70B (`llama-3.3-70b-versatile`)
- **Usage 1:** Symptom extraction — structured JSON output from natural language
- **Usage 2:** Follow-up script generation — empathetic, language-aware scripts from patient context
- **Usage 3:** Response parsing — extract structured data (pain score, medication adherence, new symptoms) from voice responses
- **Usage 4:** Real-time voice AI conversation — contextual healthcare responses during LiveKit sessions

### Sarvam AI (Voice)

- **STT Model:** `saarika:v2` — Indic language speech recognition
- **TTS Model:** `bulbul:v1` — Indic language speech synthesis (speaker: `pavithra`, soft feminine voice)
- **Languages:** Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Bengali (`bn`), Kannada (`kn`), Marathi (`mr`)
- **Free tier:** 500 API calls/day

### LiveKit (Real-time Voice)

- **Usage:** Browser-based real-time voice AI conversations
- **Session management:** In-memory session store with conversation history, extracted data accumulation
- **Pipeline:** Browser mic → Sarvam STT → Groq LLM → Sarvam TTS → Browser audio playback
- **Features:** Language auto-detection, risk flagging, structured data extraction per turn

### Twilio (Calls)

- **Usage:** Automated outbound voice calls for patient follow-ups
- **Webhook pattern:** FastAPI generates TwiML (Twilio Markup Language) for call scripts
- **Requirement:** Public URL (ngrok for dev, deployed URL for production) for webhooks

---

## Performance Characteristics

| Operation | Expected Latency | Notes |
|-----------|------------------|-------|
| Neo4j Cypher query | 50–200ms | After warm-up; first query may take ~1s |
| Groq LLM inference | 500ms–2s | Depends on prompt length |
| Sarvam STT | 1–3s | Based on audio duration |
| Sarvam TTS | 1–2s | Based on text length |
| Full diagnosis pipeline | 3–5s | STT + LLM + Graph + Response |
| PageRank computation | 100–500ms | Cached on startup, refreshed periodically |
| WebSocket alert delivery | < 100ms | Real-time push |

---

## Future Roadmap

| Feature | Description |
|---------|-------------|
| **Multilingual Audio OCR** | Scan prescriptions/bills → extract text → read aloud in regional language |
| **Doctor Availability Graph** | Specialist scheduling via graph traversal of availability slots |
| **Socio-Cultural Diet Pathways** | Regional Indic diet recommendations mapped to treatment pathways |
| **Health Reminder System** | Automated medication reminders via voice in patient's language |
| **Patient-Reported Data Dashboard** | Analytics on structured follow-up response data |
| **Offline Mode** | Cached graph responses for areas with poor connectivity |
| **LiveKit SIP Trunking** | Replace Twilio webhooks with LiveKit SIP for lower-latency phone calls |
