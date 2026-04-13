"""
LiveKit router — token generation and session management for real-time voice.
"""

import time
from fastapi import APIRouter
from pydantic import BaseModel
from config import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
from services import livekit_agent

router = APIRouter(prefix="/api/livekit", tags=["livekit"])


class TokenRequest(BaseModel):
    room_name: str | None = None
    participant_name: str = "user"
    patient_name: str = "Patient"
    language: str = "hi"


class SpeechRequest(BaseModel):
    room_name: str
    speech_text: str


class RoomRequest(BaseModel):
    room_name: str


@router.post("/token")
async def create_token(req: TokenRequest):
    """Generate a LiveKit access token for the frontend to join a room."""
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return {"error": "LiveKit credentials not configured"}

    from livekit.api import AccessToken, VideoGrants

    room_name = req.room_name or f"ayunet-{int(time.time())}"

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(req.participant_name)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room_name,
            )
        )
    )

    # Create session for this room
    livekit_agent.create_session(
        room_name=room_name,
        patient_context={
            "patient_name": req.patient_name,
            "language": req.language,
            "age": "unknown",
            "gender": "",
            "conditions": [],
            "medications": [],
            "symptoms": [],
            "followup_day": 1,
        },
    )

    return {
        "token": token.to_jwt(),
        "url": LIVEKIT_URL,
        "room_name": room_name,
    }


@router.post("/greeting")
async def get_greeting(req: RoomRequest):
    """Generate and return the AI greeting for a session."""
    result = await livekit_agent.generate_greeting(req.room_name)
    return result


@router.post("/respond")
async def respond_to_speech(req: SpeechRequest):
    """Process user speech and return AI response with audio."""
    result = await livekit_agent.process_speech(req.room_name, req.speech_text)
    return result


@router.post("/end")
async def end_session(req: RoomRequest):
    """End a LiveKit voice session."""
    session = livekit_agent.end_session(req.room_name)
    return {
        "status": "ended",
        "room_name": req.room_name,
        "turns": session.get("turn_count", 0) if session else 0,
        "extracted_data": session.get("extracted_data", {}) if session else {},
        "risk_flag": session.get("risk_flag", False) if session else False,
    }


@router.get("/status")
async def livekit_status():
    """Check if LiveKit is configured."""
    return {
        "configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET and LIVEKIT_URL),
        "url": LIVEKIT_URL if LIVEKIT_URL else None,
        "active_sessions": len(livekit_agent.sessions),
    }
