import sys
import io
import base64
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

# Fix Windows console encoding for Indic scripts
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, BASE_URL
from services import graph as graph_service
from services import nlp as nlp_service
from services import voice as voice_service
from services.voice import LANGUAGE_MAP

twilio_client: Client | None = None

# In-memory call state: call_sid -> CallState
call_states: dict[str, dict] = {}

MAX_TURNS = 14


def get_twilio_client() -> Client:
    global twilio_client
    if twilio_client is None:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return twilio_client


async def prepare_call(patient_id: str) -> dict:
    """Prepare a call: fetch patient context and generate the opening greeting."""
    # 1. Get full patient context from Neo4j
    context = graph_service.run_patient_context(patient_id)

    patient_name = context.get("patient_name", "Patient")
    language = context.get("language", "hi")

    # 2. Generate only the opening greeting
    greeting_text = await nlp_service.generate_greeting(context, language)

    # 3. TTS the greeting
    audio_map = {}
    try:
        greeting_audio = await voice_service.text_to_speech(greeting_text, language)
        if greeting_audio and len(greeting_audio) > 0:
            audio_map["greeting"] = base64.b64encode(greeting_audio).decode()
    except Exception as e:
        print(f"[TTS] Greeting TTS failed: {e}")

    call_prep = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "language": language,
        "phone": context.get("phone", ""),
        "context": context,
        "greeting_text": greeting_text,
        "audio": audio_map,
        "conversation_history": [],
        "turn_count": 0,
        "extracted_data": {},
        "risk_flag": False,
    }
    return call_prep


async def initiate_call(call_prep: dict) -> str:
    """Initiate the Twilio call."""
    client = get_twilio_client()
    patient_phone = call_prep["phone"]

    call = client.calls.create(
        to=patient_phone,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{BASE_URL}/api/calls/webhook/start",
        status_callback=f"{BASE_URL}/api/calls/status",
        status_callback_event=["completed", "failed", "no-answer"],
    )

    call_sid = call.sid
    call_prep["call_sid"] = call_sid
    call_states[call_sid] = call_prep

    return call_sid


async def prepare_direct_call(phone_number: str, patient_name: str = "Patient", language: str = "hi", context_notes: str = "") -> dict:
    """Prepare a call to any phone number (not tied to a patient_id in Neo4j)."""
    # Build a minimal patient context for the AI conversation
    context = {
        "patient_name": patient_name,
        "language": language,
        "phone": phone_number,
        "age": "unknown",
        "gender": "",
        "conditions": [],
        "medications": [],
        "symptoms": [],
        "followup_day": 1,
    }
    if context_notes:
        context["notes"] = context_notes

    greeting_text = await nlp_service.generate_greeting(context, language)

    audio_map = {}
    try:
        greeting_audio = await voice_service.text_to_speech(greeting_text, language)
        if greeting_audio and len(greeting_audio) > 0:
            audio_map["greeting"] = base64.b64encode(greeting_audio).decode()
    except Exception as e:
        print(f"[TTS] Direct call greeting TTS failed: {e}")

    call_prep = {
        "patient_id": f"direct_{phone_number[-4:]}",
        "patient_name": patient_name,
        "language": language,
        "phone": phone_number,
        "context": context,
        "greeting_text": greeting_text,
        "audio": audio_map,
        "conversation_history": [],
        "turn_count": 0,
        "extracted_data": {},
        "risk_flag": False,
    }
    return call_prep


def build_greeting_twiml(call_sid: str) -> str:
    """Build TwiML for the opening greeting + first Gather."""
    state = call_states.get(call_sid, {})

    response = VoiceResponse()

    # Play greeting audio or fall back to Twilio TTS
    audio_b64 = state.get("audio", {}).get("greeting")
    if audio_b64:
        response.play(f"{BASE_URL}/api/calls/audio/{call_sid}/greeting")
    else:
        greeting_text = state.get("greeting_text", "")
        if greeting_text:
            response.say(greeting_text, language="hi-IN")

    # Add the greeting to conversation history
    greeting_text = state.get("greeting_text", "")
    if greeting_text:
        state.setdefault("conversation_history", []).append(
            {"role": "assistant", "content": greeting_text}
        )

    # First Gather uses hi-IN since greeting asks language in Hindi
    # Language will be updated after patient responds with preference
    gather = Gather(
        input="speech",
        action=f"{BASE_URL}/api/calls/webhook/{call_sid}/respond",
        language="hi-IN",
        speech_timeout="auto",
        timeout=15,
    )
    response.append(gather)

    # If no speech detected, prompt once more then hang up
    response.say(
        "I didn't hear anything. I'll call back later. Take care!",
        language="hi-IN",
    )
    response.hangup()

    return str(response)


async def handle_patient_response(call_sid: str, speech_text: str) -> str:
    """Core dynamic handler: process patient speech, generate AI response, return TwiML."""
    state = call_states.get(call_sid)
    if not state:
        response = VoiceResponse()
        response.say("Sorry, an error occurred. Goodbye.")
        response.hangup()
        return str(response)

    language = state.get("language", "hi")
    twilio_lang = LANGUAGE_MAP.get(language, "hi-IN")
    state["turn_count"] = state.get("turn_count", 0) + 1

    # Handle empty input (Gather timeout with no speech)
    if not speech_text or not speech_text.strip():
        response = VoiceResponse()
        response.say(
            "I didn't catch that. Could you please say that again?",
            language=twilio_lang,
        )
        gather = Gather(
            input="speech",
            action=f"{BASE_URL}/api/calls/webhook/{call_sid}/respond",
            language=twilio_lang,
            speech_timeout="auto",
            timeout=15,
        )
        response.append(gather)
        response.say("I'll call back later. Take care!", language=twilio_lang)
        response.hangup()
        # Don't count empty input as a turn
        state["turn_count"] -= 1
        return str(response)

    # Add patient message to conversation history
    state["conversation_history"].append({"role": "patient", "content": speech_text})

    # On first response, detect language preference and switch
    if state["turn_count"] == 1:
        try:
            detected_lang = await nlp_service.detect_language_preference(speech_text)
            state["language"] = detected_lang
            language = detected_lang
            twilio_lang = LANGUAGE_MAP.get(language, "hi-IN")
            print(f"[Lang] Detected language preference: {detected_lang} -> {twilio_lang}")
        except Exception as e:
            print(f"[Lang] Detection failed, keeping {language}: {e}")

    # Check if we need to force-end the conversation
    force_end = state["turn_count"] >= MAX_TURNS

    # Generate dynamic AI response
    try:
        result = await nlp_service.generate_conversational_response(
            patient_context=state["context"],
            conversation_history=state["conversation_history"],
            patient_message=speech_text,
            language=language,
            turn_count=state["turn_count"],
            force_end=force_end,
        )
    except Exception as e:
        print(f"[NLP] Conversational response failed: {e}")
        # Graceful fallback — end the call
        response = VoiceResponse()
        response.say(
            "Thank you for speaking with me. Please take your medications on time. Take care!",
            language=twilio_lang,
        )
        response.hangup()
        return str(response)

    agent_text = result.get("response", "")
    should_continue = result.get("should_continue", True) and not force_end
    risk_flag = result.get("risk_flag", False)
    extracted = result.get("extracted_data", {})

    # Update conversation history with agent response
    state["conversation_history"].append({"role": "assistant", "content": agent_text})

    # Update risk flag (sticky — once flagged, stays flagged)
    state["risk_flag"] = state.get("risk_flag", False) or risk_flag

    # Merge extracted data incrementally
    for key, val in extracted.items():
        if val is not None:
            if key == "new_symptoms" and isinstance(val, list) and val:
                existing = state["extracted_data"].get("new_symptoms", [])
                state["extracted_data"]["new_symptoms"] = list(set(existing + val))
            elif key != "new_symptoms":
                state["extracted_data"][key] = val

    # TTS the agent response
    turn_key = f"dynamic_{state['turn_count']}"
    try:
        audio = await voice_service.text_to_speech(agent_text, language)
        if audio and len(audio) > 0:
            state.setdefault("audio", {})[turn_key] = base64.b64encode(audio).decode()
            print(f"[TTS] Generated audio for turn {state['turn_count']}")
    except Exception as e:
        print(f"[TTS] Dynamic TTS failed for turn {state['turn_count']}: {e}")

    # Build TwiML response
    response = VoiceResponse()

    # Play agent's response
    audio_b64 = state.get("audio", {}).get(turn_key)
    if audio_b64:
        response.play(f"{BASE_URL}/api/calls/audio/{call_sid}/{turn_key}")
    else:
        response.say(agent_text, language=twilio_lang)
        print(f"[TwiML] Using <Say> fallback for turn {state['turn_count']}")

    if should_continue:
        # Gather next patient response
        gather = Gather(
            input="speech",
            action=f"{BASE_URL}/api/calls/webhook/{call_sid}/respond",
            language=twilio_lang,
            speech_timeout="auto",
            timeout=15,
        )
        response.append(gather)
        # Timeout fallback
        response.say("Are you still there?", language=twilio_lang)
        gather2 = Gather(
            input="speech",
            action=f"{BASE_URL}/api/calls/webhook/{call_sid}/respond",
            language=twilio_lang,
            speech_timeout="auto",
            timeout=10,
        )
        response.append(gather2)
        response.say("I'll call back later. Take care!", language=twilio_lang)
        response.hangup()
    else:
        response.hangup()

    print(
        f"[Call] {call_sid} turn={state['turn_count']} "
        f"continue={should_continue} risk={state['risk_flag']}"
    )
    return str(response)
