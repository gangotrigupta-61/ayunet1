"""
LiveKit real-time voice agent for AyuNet.

Handles both browser-based (WebRTC) and phone-based (SIP trunk) conversations.
Pipeline: Audio In → Sarvam STT → Groq LLM → Sarvam TTS → Audio Out
"""

import asyncio
import base64
import json
import re
from config import GROQ_API_KEY, SARVAM_API_KEY
from services import voice as voice_service
from groq import AsyncGroq

groq_client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# In-memory session state: room_name -> session data
sessions: dict[str, dict] = {}


def create_session(room_name: str, patient_context: dict | None = None) -> dict:
    """Create a new conversation session for a LiveKit room."""
    context = patient_context or {
        "patient_name": "Patient",
        "language": "hi",
        "age": "unknown",
        "gender": "",
        "conditions": [],
        "medications": [],
        "symptoms": [],
        "followup_day": 1,
    }

    session = {
        "room_name": room_name,
        "context": context,
        "language": context.get("language", "hi"),
        "conversation_history": [],
        "turn_count": 0,
        "extracted_data": {},
        "risk_flag": False,
    }
    sessions[room_name] = session
    return session


def get_session(room_name: str) -> dict | None:
    return sessions.get(room_name)


def end_session(room_name: str) -> dict | None:
    return sessions.pop(room_name, None)


async def process_speech(room_name: str, speech_text: str) -> dict:
    """Process patient speech and generate AI response.

    Returns: {"response_text": str, "response_audio_b64": str, "should_continue": bool, ...}
    """
    session = sessions.get(room_name)
    if not session:
        return {
            "response_text": "Session not found.",
            "response_audio_b64": "",
            "should_continue": False,
            "risk_flag": False,
        }

    language = session["language"]
    session["turn_count"] += 1
    turn = session["turn_count"]

    # Add patient message to history
    session["conversation_history"].append({"role": "patient", "content": speech_text})

    # Detect language on first turn
    if turn == 1:
        try:
            detected = await _detect_language(speech_text)
            session["language"] = detected
            language = detected
        except Exception as e:
            print(f"[LiveKit] Language detection failed: {e}")

    # Generate AI response
    force_end = turn >= 14
    result = await _generate_response(
        session["context"],
        session["conversation_history"],
        speech_text,
        language,
        turn,
        force_end,
    )

    agent_text = result.get("response", "")
    should_continue = result.get("should_continue", True) and not force_end
    risk_flag = result.get("risk_flag", False)
    extracted = result.get("extracted_data", {})

    # Update session
    session["conversation_history"].append({"role": "assistant", "content": agent_text})
    session["risk_flag"] = session["risk_flag"] or risk_flag

    for key, val in extracted.items():
        if val is not None:
            if key == "new_symptoms" and isinstance(val, list) and val:
                existing = session["extracted_data"].get("new_symptoms", [])
                session["extracted_data"]["new_symptoms"] = list(set(existing + val))
            elif key != "new_symptoms":
                session["extracted_data"][key] = val

    # TTS
    audio_b64 = ""
    try:
        audio_bytes = await voice_service.text_to_speech(agent_text, language)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode()
    except Exception as e:
        print(f"[LiveKit] TTS failed for turn {turn}: {e}")

    return {
        "response_text": agent_text,
        "response_audio_b64": audio_b64,
        "should_continue": should_continue,
        "risk_flag": session["risk_flag"],
        "turn": turn,
        "extracted_data": session["extracted_data"],
    }


async def generate_greeting(room_name: str) -> dict:
    """Generate the opening greeting for a LiveKit session."""
    session = sessions.get(room_name)
    if not session:
        return {"text": "", "audio_b64": ""}

    from services import nlp as nlp_service

    language = session["language"]
    greeting = await nlp_service.generate_greeting(session["context"], language)

    session["conversation_history"].append({"role": "assistant", "content": greeting})

    audio_b64 = ""
    try:
        audio_bytes = await voice_service.text_to_speech(greeting, language)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode()
    except Exception as e:
        print(f"[LiveKit] Greeting TTS failed: {e}")

    return {"text": greeting, "audio_b64": audio_b64}


async def _detect_language(text: str) -> str:
    response = await groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Detect the language from this text. Return ONLY a 2-letter code: "
                    "hi, en, ta, te, bn, kn, mr. Default to 'hi'."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        max_tokens=10,
    )
    code = response.choices[0].message.content.strip().lower()[:2]
    valid = {"hi", "en", "ta", "te", "bn", "kn", "mr"}
    return code if code in valid else "hi"


async def _generate_response(
    patient_context: dict,
    conversation_history: list[dict],
    patient_message: str,
    language: str,
    turn_count: int,
    force_end: bool,
) -> dict:
    """Generate conversational response — same logic as nlp.generate_conversational_response."""
    from services import nlp as nlp_service

    return await nlp_service.generate_conversational_response(
        patient_context=patient_context,
        conversation_history=conversation_history,
        patient_message=patient_message,
        language=language,
        turn_count=turn_count,
        force_end=force_end,
    )
