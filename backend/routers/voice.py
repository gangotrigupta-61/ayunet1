import base64
from fastapi import APIRouter, UploadFile, File, Form
from schemas.models import TTSRequest
from services import voice as voice_service
from services import nlp as nlp_service
from services import graph as graph_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...), language: str = Form("hi")):
    """Transcribe audio via Sarvam saarika:v2."""
    audio_bytes = await audio.read()
    transcript = await voice_service.speech_to_text(audio_bytes, language)
    return {"transcript": transcript, "language": language}


@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    """Convert text to speech via Sarvam bulbul:v1."""
    audio_bytes = await voice_service.text_to_speech(req.text, req.language)
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return {"audio_base64": audio_b64, "language": req.language}


@router.post("/analyze")
async def voice_analyze(audio: UploadFile = File(...), language: str = Form("hi")):
    """Full voice pipeline: audio -> STT -> Groq extract -> Q1 diagnosis -> TTS response."""
    import asyncio

    # 1. STT
    audio_bytes = await audio.read()
    transcript = await voice_service.speech_to_text(audio_bytes, language)

    if not transcript:
        return {"error": "Could not transcribe audio", "transcript": ""}

    # 2. Groq extract symptoms
    extracted = await nlp_service.extract_symptoms(transcript)
    symptoms = extracted.get("symptoms", [])
    detected_lang = extracted.get("language", language)

    if not symptoms:
        return {"transcript": transcript, "extracted": extracted, "diagnoses": [], "message": "No symptoms detected"}

    # 3. Q1 diagnosis + Q6 pagerank (parallel)
    loop = asyncio.get_event_loop()
    diagnose_task = loop.run_in_executor(None, graph_service.run_diagnose, symptoms)
    diagnose_result = await diagnose_task
    pagerank = graph_service.get_cached_pagerank()

    # 4. Generate spoken response
    response_text = await nlp_service.generate_diagnosis_response(
        diagnose_result.get("diagnoses", []), detected_lang
    )

    # 5. TTS response
    response_audio = await voice_service.text_to_speech(response_text, detected_lang)
    response_audio_b64 = base64.b64encode(response_audio).decode()

    return {
        "transcript": transcript,
        "extracted": extracted,
        "diagnoses": diagnose_result,
        "pagerank": pagerank,
        "response_text": response_text,
        "response_audio_base64": response_audio_b64,
        "language": detected_lang,
    }
