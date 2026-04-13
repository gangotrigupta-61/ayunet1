from datetime import date
from services import graph as graph_service
from services import caller as caller_service

# WebSocket broadcast function — set by main.py
_ws_broadcast = None


def set_ws_broadcast(fn):
    global _ws_broadcast
    _ws_broadcast = fn


async def check_and_trigger_followups():
    """Daily job: find due follow-ups and initiate calls."""
    try:
        due = graph_service.run_due_followups()
        patients = due.get("patients", [])
        print(f"[FollowUp] Found {len(patients)} due follow-ups")

        for patient in patients:
            try:
                call_prep = await caller_service.prepare_call(patient["patient_id"])
                call_sid = await caller_service.initiate_call(call_prep)
                print(f"[FollowUp] Called {patient['patient_name']}: {call_sid}")
            except Exception as e:
                print(f"[FollowUp] Failed to call {patient['patient_name']}: {e}")

    except Exception as e:
        print(f"[FollowUp] Job failed: {e}")


async def broadcast_turn(
    call_sid: str,
    turn: int,
    patient_speech: str,
    agent_response: str,
    extracted: dict | None = None,
    risk_flag: bool = False,
):
    """Broadcast a conversation turn to the dashboard via WebSocket."""
    if not _ws_broadcast:
        return

    payload = {
        "type": "call_transcript",
        "call_sid": call_sid,
        "turn": turn,
        "patient_speech": patient_speech,
        "agent_response": agent_response,
    }

    if extracted:
        payload["extracted"] = extracted

    if risk_flag:
        payload["risk_flag"] = True

    await _ws_broadcast(payload)


async def save_call_data(call_sid: str, state: dict):
    """Save accumulated call data to Neo4j when the call ends."""
    patient_id = state.get("patient_id", "")
    extracted = state.get("extracted_data", {})
    risk_flag = state.get("risk_flag", False)

    pain_score = extracted.get("pain_score", 0) or 0
    new_symptoms = extracted.get("new_symptoms", [])

    # If new symptoms were reported, run diagnosis + comorbidity checks
    if new_symptoms:
        try:
            diagnose_result = graph_service.run_diagnose(new_symptoms)
            risk_result = graph_service.run_comorbidity_risk(patient_id)
            state["realtime_diagnosis"] = diagnose_result
            state["realtime_risk"] = risk_result
            print(f"[FollowUp] Ran diagnosis for new symptoms: {new_symptoms}")
        except Exception as e:
            print(f"[FollowUp] Diagnosis query failed: {e}")

    # Upsert follow-up record to Neo4j
    followup_data = {
        "status": "completed",
        "pain_score": pain_score,
        "took_medication": extracted.get("took_medication", False),
        "new_symptoms": ",".join(new_symptoms) if new_symptoms else "",
        "risk_flag": risk_flag,
    }

    try:
        graph_service.upsert_followup(
            patient_id,
            f"fu_{patient_id}_{date.today().isoformat()}",
            followup_data,
        )
        print(f"[FollowUp] Saved call data for {patient_id}")
    except Exception as e:
        print(f"[FollowUp] Upsert failed: {e}")

    # Broadcast risk alert via WebSocket if needed
    if risk_flag and _ws_broadcast:
        await _ws_broadcast({
            "type": "risk_alert",
            "patient_id": patient_id,
            "patient_name": state.get("patient_name", ""),
            "pain_score": pain_score,
            "new_symptoms": new_symptoms,
            "risk_flag": True,
            "source": "followup_call",
            "call_sid": call_sid,
        })

    # Broadcast call summary
    if _ws_broadcast:
        await _ws_broadcast({
            "type": "call_completed",
            "call_sid": call_sid,
            "patient_id": patient_id,
            "patient_name": state.get("patient_name", ""),
            "turns": state.get("turn_count", 0),
            "risk_flag": risk_flag,
            "extracted_data": extracted,
            "conversation_history": state.get("conversation_history", []),
        })
