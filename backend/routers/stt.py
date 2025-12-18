from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.ml.audio_transcription import transcribe_audio_bytes

router = APIRouter(prefix="/stt", tags=["speech-to-text"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio"):
        raise HTTPException(400, "Invalid audio file")

    audio_bytes = await file.read()
    text = transcribe_audio_bytes(audio_bytes)

    if not text:
        raise HTTPException(500, "Transcription failed")

    return {"text": text}
