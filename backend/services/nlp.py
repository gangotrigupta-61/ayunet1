import json
import re
from groq import AsyncGroq
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"


async def extract_symptoms(text: str) -> dict:
    """Extract structured symptoms from natural language (any Indic language or English)."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical NLP engine. Extract symptoms from patient text in any language "
                    "(Hindi, Tamil, Telugu, Bengali, Kannada, Marathi, English). "
                    "Return ONLY valid JSON: "
                    '{"symptoms": ["symptom1", "symptom2"], "duration_days": <int or null>, '
                    '"severity": "<mild|moderate|severe>", "language": "<detected 2-letter code: hi/ta/te/bn/kn/mr/en>"}'
                    "\nTranslate symptom names to English. Be precise and clinical."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        max_tokens=500,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


async def extract_followup_response(text: str) -> dict:
    """Extract structured data from patient follow-up verbal response."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract structured data from a patient's verbal follow-up response. "
                    "The patient may speak in any Indian language. Return ONLY valid JSON: "
                    '{"pain_score": <1-10 int>, "took_medication": <bool>, '
                    '"new_symptoms": ["symptom1"], "feeling_better": <bool>, "language": "<2-letter code>"}'
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        max_tokens=300,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


async def generate_followup_script(patient_context: dict, followup_day: int, language: str) -> dict:
    """Generate a full multi-turn empathetic follow-up call script from graph context."""

    # Build a concise medication summary for the prompt
    meds_summary = ""
    for med in patient_context.get("medications", []):
        meds_summary += f"  - {med.get('name', 'Unknown')}: {med.get('dosage', '')}\n"
    if not meds_summary:
        meds_summary = "  (no medications recorded)\n"

    conditions_summary = ", ".join(
        c.get("name", "") for c in patient_context.get("conditions", []) if c.get("name")
    ) or "general follow-up"

    symptoms_summary = ", ".join(patient_context.get("symptoms", [])) or "none recorded"

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AyuNet's caring health assistant making a follow-up phone call. "
                    f"The patient speaks {language}. Use their language throughout. Be warm, respectful, empathetic. "
                    "You have the patient's full medical context from a graph database. "
                    "\n\nIMPORTANT RULES FOR THE CALL SCRIPT:\n"
                    "1. Turn 1: Greet the patient BY NAME. Introduce yourself as AyuNet Health Assistant. "
                    "Verify identity (ask them to confirm their name).\n"
                    "2. Turn 2: Ask SPECIFICALLY about their current condition — reference their ACTUAL diagnosis. "
                    "Ask how they're feeling, if fever has come down, pain level (1-10), appetite, energy level.\n"
                    "3. Turn 3: Check medication adherence — mention EACH prescribed medication BY NAME and DOSAGE. "
                    "Ask if they're taking them on time, any side effects experienced. "
                    "Also suggest next recovery steps: rest, hydration, when to get next blood test, "
                    "when to see the doctor again.\n"
                    "4. Turn 4: Ask if the patient would like to hear some home remedies and tips "
                    "for faster recovery from their specific condition. Wait for their response.\n"
                    "5. Turn 5 (safe version — if patient is recovering well): Share 3-4 specific, safe, "
                    "evidence-based home remedies relevant to their condition (e.g., for dengue: papaya leaf juice "
                    "for platelets, tulsi/giloy kadha for immunity, light khichdi diet, coconut water for hydration). "
                    "End with warm wishes and remind them to call if any new symptoms appear.\n"
                    "6. Turn 5 (alert version — if concerning symptoms): Urgently advise them to visit the hospital. "
                    "Tell them a doctor has been alerted. Reassure them not to panic but to act quickly.\n"
                    "\nReturn ONLY valid JSON:\n"
                    "{\n"
                    '  "turn_1": {"script": "...", "expect": "identity_confirm"},\n'
                    '  "turn_2": {"script": "...", "expect": "condition_update"},\n'
                    '  "turn_3": {"script": "...", "expect": "medication_check"},\n'
                    '  "turn_4": {"script": "...", "expect": "home_remedy_consent"},\n'
                    '  "turn_5_safe": {"script": "...with home remedies and goodbye..."},\n'
                    '  "turn_5_alert": {"script": "...urgent doctor escalation..."}\n'
                    "}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Patient context from Neo4j graph:\n"
                    f"Name: {patient_context.get('patient_name', 'Patient')}\n"
                    f"Age: {patient_context.get('age', 'unknown')}, Gender: {patient_context.get('gender', '')}\n"
                    f"Diagnosis: {conditions_summary}\n"
                    f"Current symptoms: {symptoms_summary}\n"
                    f"Prescribed medications:\n{meds_summary}"
                    f"This is follow-up day {followup_day}."
                ),
            },
        ],
        temperature=0.7,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


async def generate_greeting(patient_context: dict, language: str) -> str:
    """Generate a bilingual greeting that asks the patient's language preference."""
    patient_name = patient_context.get("patient_name", "Patient")
    conditions = ", ".join(
        c.get("name", "") for c in patient_context.get("conditions", []) if c.get("name")
    ) or "general check-up"

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are AyuNet Health Assistant calling a patient for a follow-up. "
                    f"Generate ONLY the greeting — 3-4 sentences.\n"
                    f"- Start with a warm greeting in HINDI: 'Namaste {patient_name} ji'\n"
                    f"- Introduce yourself as AyuNet Health Assistant\n"
                    f"- Say this is a follow-up call regarding: {conditions}\n"
                    f"- Then ask their language preference. Say something like: "
                    f"'Aap kis bhasha mein baat karna chahenge? Hindi, English, "
                    f"ya koi aur bhasha?' (Which language would you like to talk in?)\n"
                    f"Return ONLY the spoken text. Keep it natural and warm."
                ),
            },
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


async def detect_language_preference(patient_response: str) -> str:
    """Detect which language the patient wants to speak from their first response."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "The patient was asked which language they prefer. "
                    "Detect the language from their response. "
                    "Return ONLY a 2-letter language code: "
                    "hi (Hindi), en (English), ta (Tamil), te (Telugu), "
                    "bn (Bengali), kn (Kannada), mr (Marathi). "
                    "If they responded IN a language (not naming it), detect that language. "
                    "If unclear, default to 'hi'. Return ONLY the 2-letter code, nothing else."
                ),
            },
            {"role": "user", "content": patient_response},
        ],
        temperature=0.1,
        max_tokens=10,
    )
    code = response.choices[0].message.content.strip().lower()[:2]
    valid = {"hi", "en", "ta", "te", "bn", "kn", "mr"}
    return code if code in valid else "hi"


async def generate_conversational_response(
    patient_context: dict,
    conversation_history: list[dict],
    patient_message: str,
    language: str,
    turn_count: int = 0,
    force_end: bool = False,
) -> dict:
    """Generate a dynamic AI response as a real healthcare professional.

    The LLM validates answers, asks clarifying follow-ups, discusses remedies,
    verifies medication adherence, shares recovery steps, and only ends
    the call after confirming the patient has no more questions.
    """
    # Build patient summary for the system prompt
    meds_summary = ""
    for med in patient_context.get("medications", []):
        meds_summary += f"  - {med.get('name', 'Unknown')}: {med.get('dosage', '')}\n"
    if not meds_summary:
        meds_summary = "  (none recorded)\n"

    conditions_summary = ", ".join(
        c.get("name", "") for c in patient_context.get("conditions", []) if c.get("name")
    ) or "general follow-up"

    symptoms_summary = ", ".join(patient_context.get("symptoms", [])) or "none recorded"

    followup_day = patient_context.get("followup_day", 1)

    # Determine conversation phase
    min_turns = 6
    if turn_count < min_turns and not force_end:
        phase_note = (
            f"\n\nCONVERSATION PHASE: You are on turn {turn_count} of the call. "
            f"You MUST continue the conversation (should_continue=true). "
            f"You have not yet covered all the important topics. Do NOT end the call yet. "
            f"Keep exploring — there is more to discuss."
        )
    elif force_end:
        phase_note = (
            "\n\nCONVERSATION PHASE: This is the FINAL turn. Wrap up NOW — "
            "summarize your key advice in 2-3 points, repeat any important medication "
            "instructions, wish them a speedy recovery, and say goodbye warmly. "
            "Set should_continue=false."
        )
    else:
        phase_note = (
            f"\n\nCONVERSATION PHASE: You are on turn {turn_count}. "
            f"You may end the call ONLY if you have covered: (1) how they feel, "
            f"(2) medication check, (3) recovery tips or remedies, AND (4) you have "
            f"explicitly asked 'Is there anything else you would like to ask me?' "
            f"and the patient said no. If ANY of these are missing, continue."
        )

    system_prompt = (
        f"You are AyuNet Health Assistant — a caring, knowledgeable healthcare professional "
        f"making a follow-up phone call. You speak {language} throughout the call.\n\n"
        f"═══ PATIENT FILE ═══\n"
        f"  Name: {patient_context.get('patient_name', 'Patient')}\n"
        f"  Age: {patient_context.get('age', 'unknown')}, Gender: {patient_context.get('gender', '')}\n"
        f"  Diagnosis: {conditions_summary}\n"
        f"  Presenting symptoms: {symptoms_summary}\n"
        f"  Prescribed medications:\n{meds_summary}"
        f"  Follow-up day: {followup_day}\n\n"
        f"═══ HOW TO BEHAVE ═══\n"
        f"You are a REAL healthcare professional, not a chatbot. Act like a nurse or "
        f"doctor who genuinely cares about this patient.\n\n"
        f"CONVERSATION RULES:\n"
        f"1. ONE TOPIC AT A TIME — ask about one thing, wait for the answer, then move on. "
        f"Never dump multiple questions in one response.\n"
        f"2. VALIDATE EVERY ANSWER — if the patient says 'I feel okay', probe deeper: "
        f"'That's good to hear. Has the fever completely gone? Any body pain still?' "
        f"If they say pain is 6/10, respond: 'I understand, 6 is still noticeable. "
        f"Where exactly is the pain? Is it constant or does it come and go?'\n"
        f"3. MEDICATION CHECK — ask about EACH medicine BY NAME and DOSAGE. Example: "
        f"'Are you taking your Paracetamol 500mg three times a day after meals?' "
        f"Ask about side effects: 'Any stomach upset or nausea from the medicines?'\n"
        f"4. SHARE RECOVERY ADVICE — give specific, actionable tips for their condition: "
        f"diet recommendations, hydration, rest, warning signs to watch for, "
        f"when to get the next blood test, when to see the doctor again.\n"
        f"5. HOME REMEDIES — offer safe, evidence-based home remedies specific to their "
        f"condition. For dengue: papaya leaf juice for platelets, tulsi kadha for immunity, "
        f"coconut water for hydration. For diabetes: methi seeds, bitter gourd juice, etc.\n"
        f"6. REPEAT IMPORTANT THINGS — if you give medication timing or dosage instructions, "
        f"say it clearly and repeat it: 'Remember, take Paracetamol after meals — "
        f"morning, afternoon, and night. After meals, okay?'\n"
        f"7. BEFORE ENDING — you MUST ask: 'Is there anything else you would like to ask me? "
        f"Any concern, no matter how small?' Only end after they confirm no more questions.\n"
        f"8. WARM CLOSING — when ending, summarize 2-3 key points they should remember, "
        f"wish them well, and remind them they can call back anytime.\n"
        f"9. CONCERNING SYMPTOMS — if they report high fever (>102°F), severe pain (>7/10), "
        f"difficulty breathing, chest pain, heavy bleeding, or confusion, immediately "
        f"acknowledge the severity, advise hospital visit, and set risk_flag=true.\n"
        f"10. TONE — speak gently like you're talking to a family member. Use their name. "
        f"Show empathy: 'I understand that must be difficult', 'That's very common, "
        f"don't worry'. Never sound rushed or robotic.\n\n"
        f"═══ TOPICS TO COVER (spread across the conversation) ═══\n"
        f"- How they are feeling overall (energy, appetite, sleep, mood)\n"
        f"- Specific symptom check related to their diagnosis\n"
        f"- Pain level (1-10) if relevant\n"
        f"- Medication adherence — each medicine by name\n"
        f"- Any side effects from medicines\n"
        f"- Diet and hydration\n"
        f"- Recovery tips and home remedies\n"
        f"- When to see the doctor next / when to get lab tests\n"
        f"- Any new symptoms or concerns\n"
        f"- Final: 'Anything else you want to ask?'\n\n"
        f"═══ RESPONSE FORMAT ═══\n"
        f"Return ONLY valid JSON:\n"
        f'{{\n'
        f'  "response": "What you say to the patient (in {language})",\n'
        f'  "should_continue": true or false,\n'
        f'  "risk_flag": true or false,\n'
        f'  "extracted_data": {{\n'
        f'    "pain_score": null or 1-10,\n'
        f'    "took_medication": null or true/false,\n'
        f'    "new_symptoms": [],\n'
        f'    "feeling_better": null or true/false\n'
        f'  }}\n'
        f'}}\n'
        f"Keep each response to 3-5 sentences. This is a phone call — be natural, not a wall of text."
        f"{phase_note}"
    )

    # Build messages: system + conversation history + latest patient message
    messages = [{"role": "system", "content": system_prompt}]
    for entry in conversation_history:
        role = "assistant" if entry["role"] == "assistant" else "user"
        messages.append({"role": role, "content": entry["content"]})
    messages.append({"role": "user", "content": patient_message})

    # Retry up to 2 times in case of malformed JSON from LLM
    last_error = None
    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.6 if attempt == 0 else 0.3,
                max_tokens=600,
            )
            raw = response.choices[0].message.content.strip()
            print(f"[NLP] Raw LLM response (attempt {attempt+1}, {len(raw)} chars): {raw[:200]}")

            # Strip markdown code fences
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            # Try direct JSON parse first
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                # Try to extract JSON object from the text using regex
                json_match = re.search(r'\{[\s\S]*\}', raw)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise

            # Hard enforce: never end before min turns unless force_end
            if turn_count < min_turns and not force_end:
                result["should_continue"] = True

            return result

        except Exception as e:
            last_error = e
            print(f"[NLP] Attempt {attempt+1} failed: {e}")
            if attempt == 0:
                # Add a stronger hint for the retry
                messages.append({"role": "assistant", "content": raw if 'raw' in dir() else ""})
                messages.append({"role": "user", "content": "ERROR: Your response was not valid JSON. Return ONLY a JSON object, no extra text."})

    # All retries failed — return a safe fallback that keeps the conversation going
    print(f"[NLP] All attempts failed, using fallback response. Last error: {last_error}")
    fallback_responses = {
        "hi": "Accha ji, mujhe aapki baat samajh aayi. Aap mujhe thoda aur bataiye, aap kaisa mehsoos kar rahe hain?",
        "en": "I understand. Could you tell me a bit more about how you're feeling right now?",
        "ta": "Puriyuthu. Neengal eppadi unarugireeergal endru konjam sollunga?",
        "te": "Arthamayindi. Meeru ippudu ela feel avutunnaro koncham cheppandi?",
    }
    return {
        "response": fallback_responses.get(language, fallback_responses["en"]),
        "should_continue": True,
        "risk_flag": False,
        "extracted_data": {"pain_score": None, "took_medication": None, "new_symptoms": [], "feeling_better": None},
    }


async def generate_diagnosis_response(diagnoses: list, language: str) -> str:
    """Generate a patient-friendly diagnosis explanation in their language."""
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a caring medical assistant. Explain diagnoses to a patient in {language}. "
                    "Be simple, reassuring, and clear. 2-3 sentences max."
                ),
            },
            {
                "role": "user",
                "content": f"Diagnoses found: {json.dumps(diagnoses)}",
            },
        ],
        temperature=0.5,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
