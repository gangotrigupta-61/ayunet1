import sys
import io
import base64
import traceback
from fastapi import APIRouter, Request, Form
from fastapi.responses import Response

# Fix Windows console encoding for Indic scripts
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from schemas.models import CallInitiateRequest, CallNumberRequest
from services import caller as caller_service
from services import followup as followup_service
from services import graph as graph_service

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.post("/initiate")
async def initiate_call(req: CallInitiateRequest):
    """Prepare + initiate a Twilio follow-up call to a patient."""
    call_prep = await caller_service.prepare_call(req.patient_id)
    call_sid = await caller_service.initiate_call(call_prep)
    return {
        "call_sid": call_sid,
        "patient_id": req.patient_id,
        "patient_name": call_prep["patient_name"],
        "status": "initiated",
        "greeting": call_prep.get("greeting_text", ""),
    }


@router.post("/call-number")
async def call_number(req: CallNumberRequest):
    """Call any phone number directly (not tied to a patient in Neo4j)."""
    call_prep = await caller_service.prepare_direct_call(
        phone_number=req.phone_number,
        patient_name=req.patient_name,
        language=req.language,
        context_notes=req.context_notes,
    )
    call_sid = await caller_service.initiate_call(call_prep)
    return {
        "call_sid": call_sid,
        "phone_number": req.phone_number,
        "patient_name": req.patient_name,
        "status": "initiated",
        "greeting": call_prep.get("greeting_text", ""),
    }


@router.post("/webhook/start")
async def webhook_start(request: Request):
    """Twilio hits this when the call connects. Play greeting + gather first response."""
    try:
        form = await request.form()
        call_sid = form.get("CallSid", "")
        print(f"[Webhook] START for call_sid={call_sid}")

        state = caller_service.call_states.get(call_sid)
        if not state:
            print(f"[Webhook] WARNING: No state found for {call_sid}")

        twiml = caller_service.build_greeting_twiml(call_sid)
        return Response(content=twiml, media_type="application/xml")
    except Exception as e:
        print(f"[Webhook] CRITICAL ERROR in /webhook/start: {e}")
        traceback.print_exc()
        from twilio.twiml.voice_response import VoiceResponse
        fallback = VoiceResponse()
        fallback.say("We are experiencing a technical issue. We will call you back shortly. Thank you.", language="en-US")
        fallback.hangup()
        return Response(content=str(fallback), media_type="application/xml")


@router.post("/webhook/{call_sid}/respond")
async def webhook_respond(call_sid: str, request: Request):
    """Dynamic conversation handler — processes patient speech and generates AI response."""
    try:
        form = await request.form()
        speech_result = form.get("SpeechResult", "")

        state = caller_service.call_states.get(call_sid)
        turn = state.get("turn_count", 0) + 1 if state else 0

        try:
            print(f"[Webhook] RESPOND call_sid={call_sid} turn={turn} speech='{speech_result[:80]}'")
        except UnicodeEncodeError:
            print(f"[Webhook] RESPOND call_sid={call_sid} turn={turn} speech=(non-ASCII, {len(speech_result)} chars)")

        # Generate dynamic AI response + TwiML
        twiml = await caller_service.handle_patient_response(call_sid, speech_result)

        # Broadcast the complete turn to the dashboard (non-critical — don't let it kill the webhook)
        try:
            if state and speech_result and state.get("conversation_history"):
                last_agent = state["conversation_history"][-1]
                agent_text = last_agent["content"] if last_agent["role"] == "assistant" else ""
                await followup_service.broadcast_turn(
                    call_sid=call_sid,
                    turn=state.get("turn_count", turn),
                    patient_speech=speech_result,
                    agent_response=agent_text,
                    extracted=state.get("extracted_data", {}),
                    risk_flag=state.get("risk_flag", False),
                )
        except Exception as e:
            print(f"[Webhook] broadcast_turn failed (non-critical): {e}")

        return Response(content=twiml, media_type="application/xml")
    except Exception as e:
        print(f"[Webhook] CRITICAL ERROR in /webhook/{call_sid}/respond: {e}")
        traceback.print_exc()
        from twilio.twiml.voice_response import VoiceResponse
        fallback = VoiceResponse()
        fallback.say("We are experiencing a technical issue. We will call you back shortly. Thank you.", language="en-US")
        fallback.hangup()
        return Response(content=str(fallback), media_type="application/xml")


@router.get("/audio/{call_sid}/{turn_key}")
async def get_call_audio(call_sid: str, turn_key: str):
    """Serve generated audio for a specific call turn."""
    state = caller_service.call_states.get(call_sid, {})

    audio_b64 = state.get("audio", {}).get(turn_key)

    if not audio_b64:
        print(f"[Audio] 404 - No audio for {call_sid}/{turn_key}")
        return Response(status_code=404)

    audio_bytes = base64.b64decode(audio_b64)
    print(f"[Audio] Serving {len(audio_bytes)} bytes for {turn_key}")
    return Response(content=audio_bytes, media_type="audio/wav")


@router.post("/status")
async def call_status(request: Request):
    """Twilio status callback — call completed/failed. Persist data to Neo4j."""
    form = await request.form()
    call_sid = form.get("CallSid", "")
    status = form.get("CallStatus", "")

    state = caller_service.call_states.get(call_sid)
    if state:
        print(
            f"[Call] {call_sid} -> {status} "
            f"(patient: {state.get('patient_name')}, turns: {state.get('turn_count', 0)})"
        )

        # Save accumulated call data to Neo4j
        await followup_service.save_call_data(call_sid, state)

        # Clean up
        caller_service.call_states.pop(call_sid, None)

    return {"status": "ok"}


@router.post("/end/{call_sid}")
async def end_call(call_sid: str):
    """End an active call via Twilio API."""
    try:
        client = caller_service.get_twilio_client()
        call = client.calls(call_sid).update(status="completed")
        print(f"[Call] Manually ended {call_sid}")
        return {"status": "ended", "call_sid": call_sid}
    except Exception as e:
        print(f"[Call] Failed to end {call_sid}: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/demo-trigger")
async def demo_trigger():
    """One-click: find first due follow-up, prepare, and initiate call."""
    due = graph_service.run_due_followups()
    patients = due.get("patients", [])

    if not patients:
        return {"error": "No follow-ups due today", "patients": []}

    patient = patients[0]
    call_prep = await caller_service.prepare_call(patient["patient_id"])
    call_sid = await caller_service.initiate_call(call_prep)

    return {
        "call_sid": call_sid,
        "patient": patient,
        "status": "initiated",
    }


@router.get("/followups/due")
async def get_due_followups():
    """Get today's due follow-ups."""
    result = graph_service.run_due_followups()
    return {"followups": result}
