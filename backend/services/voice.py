import sys
import io
import base64
import httpx
from config import SARVAM_API_KEY

# Fix Windows console encoding for Indic scripts
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SARVAM_BASE = "https://api.sarvam.ai"

_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "api-subscription-key": SARVAM_API_KEY,
            },
        )
    return _http_client


LANGUAGE_MAP = {
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
    "kn": "kn-IN",
    "mr": "mr-IN",
    "en": "en-IN",
}


async def speech_to_text(audio_bytes: bytes, language: str = "hi") -> str:
    """Transcribe audio using Sarvam saarika:v2 STT."""
    client = _get_client()
    lang_code = LANGUAGE_MAP.get(language, "hi-IN")
    audio_b64 = base64.b64encode(audio_bytes).decode()

    resp = await client.post(
        f"{SARVAM_BASE}/speech-to-text",
        json={
            "input": audio_b64,
            "language_code": lang_code,
            "model": "saarika:v2",
            "with_timestamps": False,
        },
    )
    resp.raise_for_status()
    return resp.json().get("transcript", "")


async def text_to_speech(text: str, language: str = "hi") -> bytes:
    """Convert text to speech using Sarvam bulbul:v1 TTS. Returns audio bytes."""
    client = _get_client()
    lang_code = LANGUAGE_MAP.get(language, "hi-IN")

    # Sarvam bulbul:v1 has a ~500 char limit per request
    # If text is longer, split into chunks and concatenate audio
    max_chars = 480
    if len(text) <= max_chars:
        return await _tts_single(client, text, lang_code)

    # Split on sentence boundaries
    chunks = _split_text(text, max_chars)
    audio_parts = []
    for chunk in chunks:
        part = await _tts_single(client, chunk, lang_code)
        audio_parts.append(part)
    return b"".join(audio_parts)


async def _tts_single(client: httpx.AsyncClient, text: str, lang_code: str) -> bytes:
    """Single TTS request to Sarvam API."""
    resp = await client.post(
        f"{SARVAM_BASE}/text-to-speech",
        json={
            "input": text,
            "target_language_code": lang_code,
            "model": "bulbul:v1",
            "speaker": "pavithra",
            "pitch": 1,
            "pace": 0.9,
            "loudness": 1.3,
            "enable_preprocessing": True,
        },
    )
    if resp.status_code != 200:
        body = resp.text[:300]
        print(f"[TTS] Sarvam error {resp.status_code}: {body}")
        print(f"[TTS] Input was ({len(text)} chars): {text[:100]}...")
        resp.raise_for_status()
    data = resp.json()
    audio_b64 = data.get("audio_base64", data.get("audios", [""])[0])
    return base64.b64decode(audio_b64)


def _split_text(text: str, max_chars: int) -> list[str]:
    """Split text into chunks on sentence boundaries."""
    sentences = []
    for sep in ["। ", ". ", "! ", "? ", "।", ".\n"]:
        if sep in text:
            parts = text.split(sep)
            sentences = [p.strip() + sep.strip() for p in parts if p.strip()]
            break
    if not sentences:
        # No sentence boundaries found, split on spaces
        words = text.split()
        sentences = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                sentences.append(current.strip())
                current = word
            else:
                current += " " + word
        if current.strip():
            sentences.append(current.strip())
        return sentences

    # Merge short sentences into chunks under max_chars
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_chars:
            if current.strip():
                chunks.append(current.strip())
            current = s
        else:
            current += " " + s
    if current.strip():
        chunks.append(current.strip())
    return chunks


async def generate_filler_audio(language: str = "hi") -> dict[str, bytes]:
    """Pre-generate filler audio clips for a language. Returns dict of filler_name -> audio_bytes."""
    fillers = {
        "hi": ["Jee haan...", "Ek second, main dekh rahi hoon...", "Dhanyavaad, bahut accha..."],
        "ta": ["Sari...", "Oru nimisham paarunga...", "Nandri, romba nalla irukku..."],
        "te": ["Sare...", "Oka second, nenu check chestunna...", "Dhanyavaadalu..."],
        "bn": ["Accha...", "Ek second, ami check korchi...", "Dhonnobad..."],
        "kn": ["Sari...", "Ondu second, nanu check maadtiddeeni...", "Dhanyavaadagalu..."],
        "mr": ["Barobar...", "Ek second, mi check karte...", "Dhanyavaad..."],
        "en": ["Okay...", "One moment, let me check...", "Thank you, that's great..."],
    }

    lang_fillers = fillers.get(language, fillers["en"])
    result = {}
    for i, text in enumerate(lang_fillers):
        audio = await text_to_speech(text, language)
        result[f"filler_{i}"] = audio
    return result
