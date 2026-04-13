# AyuNet — Demo Guide & PPT Flow

> Use this document to walk judges through a live demo of AyuNet.
> Each section tells you exactly which feature to show, what data to use, and what to highlight.

---

## Pre-Demo Setup

### 1. Start Services (3 terminals)

```bash
# Terminal 1 — Backend
cd C:\Users\aryan\Downloads\projects\AyuNet\backend
C:\Users\aryan\Downloads\projects\AyuNet\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd C:\Users\aryan\Downloads\projects\AyuNet\frontend
npm run dev

# Terminal 3 — Ngrok (for Twilio webhooks)
ngrok http 8000
```

### 2. Update BASE_URL
After starting ngrok, copy the `https://xxxx.ngrok-free.app` URL and update `backend/.env`:
```
BASE_URL=https://xxxx.ngrok-free.app
```
Then restart the backend.

### 3. Verify
- Open `http://localhost:5173` in the browser
- Check that the sidebar shows a green "Connected" dot (WebSocket active)

---

## PPT Slide Flow

### Slide 1: Problem Statement
- 800M Indians can't describe symptoms in English
- Rural patients miss follow-ups, get generic treatment
- Comorbidity risks are invisible without multi-hop analysis
- No existing system combines graph intelligence + multilingual voice

### Slide 2: Solution — AyuNet
- Graph-powered multilingual health intelligence platform
- Neo4j knowledge graph with 10 vertex types, 15 edge types, 350+ edges
- 7 Indian languages supported (Hindi, Tamil, Telugu, Bengali, Kannada, Marathi, English)
- Real-time voice AI + automated phone follow-ups + doctor alerts

### Slide 3: Architecture
- Show the system architecture diagram from OVERVIEW.md
- Highlight: Neo4j → Groq LLM → Sarvam AI → Twilio/LiveKit pipeline

### Slide 4-9: Live Demo (see below)

### Slide 10: Tech Stack
- Neo4j (graph DB), FastAPI (backend), React + Vite (frontend)
- Groq (LLaMA 3.3 70B), Sarvam AI (STT/TTS), Twilio (calls), LiveKit (real-time voice)
- Cytoscape.js (graph visualization), WebSocket (real-time alerts)

### Slide 11: Future Roadmap
- Multilingual Audio OCR, LiveKit SIP trunking, diet pathways, offline mode

---

## Live Demo Script

### Demo 1: Diagnose Tab (Graph Query Q1)

**What to show:** Multilingual symptom analysis with graph traversal visualization.

**Steps:**
1. Go to **Diagnose** tab
2. Type (or speak in Hindi): `mujhe do din se bukhar hai, sar mein dard hai, jodo mein dard hai aur thakan lag rahi hai`
   - Translation: "I've had fever for 2 days, headache, joint pain, and fatigue"
3. Click **Analyze**
4. **Highlight:**
   - Extracted symptoms panel: shows detected language (Hindi) and parsed symptoms
   - Top diagnoses: Dengue Fever should rank high (fever + headache + joint pain + fatigue)
   - Confidence scores with progress bars
   - Graph view: symptoms (blue) → diseases (red) with weighted edges

**What judges should notice:**
- The AI understood Hindi text and extracted medical symptoms
- Graph traversal shows Symptom → Disease paths with confidence weights
- Hop-by-hop animation reveals how the graph is walked

**Alternative voice demo:** Click the mic button, speak in Hindi, watch auto-transcription → auto-analysis

---

### Demo 2: Drug Check Tab (Graph Query Q2)

**What to show:** Drug interaction detection via graph relationships.

**Best drug combinations to demo:**

| Drugs to Select | Expected Result |
|-----------------|----------------|
| **Warfarin + Aspirin** | SEVERE — increased bleeding risk |
| **Warfarin + Ibuprofen** | SEVERE — NSAID + anticoagulant danger |
| **Warfarin + Rifampicin** | SEVERE — CYP enzyme induction reduces Warfarin efficacy |
| **Fluoxetine + Sertraline** | SEVERE — serotonin syndrome risk (dual SSRIs) |
| **Simvastatin + Amlodipine** | MODERATE — myopathy risk |
| **Metformin + Prednisolone** | MODERATE — corticosteroids increase blood glucose |

**Steps:**
1. Go to **Drug Check** tab
2. Select **Warfarin**, **Aspirin**, and **Ibuprofen** (3 drugs)
3. Click **Check Interactions**
4. **Highlight:**
   - Two SEVERE interactions detected
   - Mechanism explanations and clinical notes
   - Graph visualization: drug nodes with red edges for severe, yellow for moderate

**What judges should notice:**
- N-drug interaction check in a single graph traversal (not N² SQL joins)
- Clinical-grade severity ratings with actionable recommendations

---

### Demo 3: Treatment Path Tab (Graph Query Q3)

**What to show:** Disease → Specialist → Treatment → Drug pathway discovery.

**Best diseases to demo:**

| Disease | What You'll See |
|---------|----------------|
| **Dengue Fever** | Dr. General Physician → Antiviral Supportive Care → Paracetamol |
| **Type 2 Diabetes** | Dr. Endocrinologist → Oral Hypoglycemic + Insulin pathways |
| **Coronary Artery Disease** | Dr. Cardiologist → Antihypertensive Therapy + Coronary Stenting |
| **Tuberculosis** | Dr. Pulmonologist → DOTS TB Treatment → Isoniazid + Rifampicin |

**Steps:**
1. Go to **Treatment Path** tab
2. Select **Type 2 Diabetes**
3. Click **Find Treatment Path**
4. **Highlight:**
   - Multiple treatment pathways (Oral Hypoglycemic 80% success vs Insulin 85% success)
   - Cost tiers (low vs medium)
   - Graph: Disease (red) → Specialist (purple) → Treatment (orange) → Drug (green)

**What judges should notice:**
- Full treatment pathway from a single graph traversal
- Success rates, cost tiers, and dosages — all from graph edge properties

---

### Demo 4: Risk Analysis Tab (Graph Query Q5 — 4-hop!)

**What to show:** Comorbidity risk prediction through 4-hop graph traversal.

**Best patients to demo:**

| Patient | Conditions | Why It's Interesting |
|---------|-----------|---------------------|
| **Rahul** | Hypertension + Diabetes + CAD | 3 conditions = many overlapping risk factors, high-scoring predictions |
| **Suresh** | Diabetes + CKD + Hypertension | Complex chronic with renal involvement |
| **Priya** | Dengue + Diabetes | Active infection + chronic condition crossover |
| **Meera** | Hypothyroid + Depression + Anemia | Multi-system comorbidity |

**Steps:**
1. Go to **Risk Analysis** tab
2. Select **Rahul** (has 3 conditions — most dramatic results)
3. Click **Predict Risk**
4. **Highlight:**
   - Hop pills: H1 (3 existing diseases) → H2 (risk factors) → H3 (predicted diseases) → H4 (tests needed)
   - Risk score cards with severity coloring (red > 2x, amber > 1.5x, green < 1.5x)
   - "Via risk factor" shows the causal chain
   - Required tests with completion status
   - Graph view: concentric ring layout showing the 4-hop traversal

**What judges should notice:**
- This is the **impossible-in-SQL** query — 4 hops across 5 tables in a single Neo4j traversal
- Risk multiplier scores are accumulated along the graph path
- Tests the patient hasn't taken are surfaced automatically

---

### Demo 5: Follow-ups Tab + Voice Call (THE MAIN EVENT)

**What to show:** AI-powered automated patient follow-up via real phone call.

**Steps:**
1. Go to **Follow-ups** tab
2. Show the **Quick Call** card — enter a real phone number, name, and language
3. Click **Call Number** — this dials the actual phone
4. **OR** use the scheduled follow-up list:
   - Click **Demo Trigger** to auto-select the first due patient and call
5. **During the call:**
   - Show the live transcript appearing on the right panel
   - Extracted data badges (pain score, medication adherence, new symptoms)
   - If risk flags trigger (pain > 7 or critical symptoms), show the red alert toast
6. Click **End Call** when done

**What judges should notice:**
- The AI speaks in the patient's language (not a generic English script)
- Questions are generated from the patient's actual graph context (conditions, medications, follow-up day)
- Structured data is extracted in real-time from voice responses
- Risk alerts push to the doctor dashboard instantly via WebSocket
- The entire conversation is dynamic — no pre-recorded scripts

**Phone call demo tips:**
- Use your own phone number for the most convincing demo
- Speak in Hindi to show multilingual capability
- Say something like "dard bahut zyada hai, 8 number ka" (pain is very high, 8 out of 10) to trigger a risk alert

---

### Demo 6: Voice AI Tab (Real-time Browser Voice)

**What to show:** Real-time voice conversation directly in the browser.

**Steps:**
1. Go to **Voice AI** tab
2. Click **Start Voice Chat**
3. Speak in Hindi (or any supported language): "Mujhe sir mein dard hai aur bukhar bhi aa raha hai"
4. Wait for the AI to respond with audio in the same language
5. Continue the conversation for 2-3 turns
6. **Highlight:**
   - Chat bubbles showing the full conversation
   - Extracted metadata (pain score, symptoms) in badges
   - Risk flag indicator if triggered
7. Click **End Session**

**What judges should notice:**
- Full real-time voice AI in the browser — no phone needed
- Same Sarvam STT → Groq LLM → Sarvam TTS pipeline as phone calls
- Language is auto-detected from the first utterance
- Conversational context is maintained across turns

---

## Seeded Data Quick Reference

### Patients (10)

| ID | Name | Language | Conditions | Best For Demo |
|----|------|----------|-----------|---------------|
| aryan | Aryan | Hindi | Dengue (Active) | Diagnose, Follow-up call |
| priya | Priya | Hindi | Dengue + Diabetes | Risk Analysis (acute + chronic) |
| karthik | Karthik | Tamil | CAD + Hypertension | Risk Analysis, Treatment Path |
| ananya | Ananya | Telugu | Lupus + Anemia | Risk Analysis (autoimmune) |
| rahul | Rahul | English | Hypertension + Diabetes + CAD | Risk Analysis (most dramatic) |
| meera | Meera | Bengali | Hypothyroid + Depression + Anemia | Risk Analysis (multi-system) |
| suresh | Suresh | Hindi | Diabetes + CKD + Hypertension | Risk Analysis (complex chronic) |
| lakshmi | Lakshmi | Tamil | Asthma + Gastritis | Treatment Path |
| dev | Dev | English | Typhoid (Active) | Follow-up call, Treatment Path |
| fatima | Fatima | Hindi | RA + Migraine | Drug Check (on methotrexate + diclofenac) |

### Drug Interactions (best combos for demo)

| Combination | Severity | Why |
|-------------|----------|-----|
| Warfarin + Aspirin + Ibuprofen | 2x SEVERE | Bleeding cascade |
| Fluoxetine + Sertraline | SEVERE | Serotonin syndrome |
| Simvastatin + Amlodipine | MODERATE | Myopathy risk |
| Warfarin + Rifampicin | SEVERE | CYP induction |

### Diseases (for Treatment Path)

| Disease | Interesting Because |
|---------|-------------------|
| Type 2 Diabetes | Multiple treatment pathways (oral vs insulin) |
| Coronary Artery Disease | High-cost stenting vs low-cost medication |
| Tuberculosis | DOTS protocol with multiple drugs |
| Dengue Fever | Simple supportive care pathway |

### Diagnose Tab (symptom inputs)

| Input (Hindi) | Translation | Expected Top Diagnosis |
|--------------|-------------|----------------------|
| bukhar, sar dard, jodo mein dard, thakan | fever, headache, joint pain, fatigue | Dengue Fever |
| seene mein dard, sans lene mein taklif, chakkar | chest pain, shortness of breath, dizziness | CAD / Hypertension |
| khansi, bukhar, raat ko pasina | cough, fever, night sweats | Tuberculosis |
| pet mein dard, jee machlana, ulti | abdominal pain, nausea, vomiting | Gastritis / Typhoid |

---

## Talking Points for Judges

### "Why a Graph Database?"
- Medical data is inherently relational — patients have conditions, conditions have risk factors, risk factors elevate other conditions
- The 4-hop comorbidity risk query (Q5) is impossible in SQL without 4 nested joins across 5 tables
- Neo4j does it in a single Cypher traversal with multiplier accumulation
- Drug interactions are an N-body problem — graph finds all paths, SQL requires N² self-joins

### "Why Multilingual Voice?"
- 800M Indians can't describe symptoms in English
- Sarvam AI is purpose-built for Indian languages (not a generic Western model)
- The AI speaks back in the same language — full loop from voice to diagnosis to voice

### "What's Real-time About It?"
- LiveKit sessions enable browser-based voice conversations (no phone needed)
- Twilio calls are actual phone calls to real numbers
- WebSocket alerts push risk flags to the doctor dashboard in < 100ms
- All AI responses are generated dynamically — no pre-recorded scripts

### "How is this Different from ChatGPT?"
- ChatGPT has no medical knowledge graph — it hallucinates medical facts
- AyuNet grounds every diagnosis in a graph traversal with weighted edges
- Drug interactions come from verified pharmaceutical data, not LLM guesses
- The LLM is used for language understanding and script generation, NOT for medical reasoning
- Medical reasoning happens in the graph — the LLM is the interface layer
