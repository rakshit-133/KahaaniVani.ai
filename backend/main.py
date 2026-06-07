import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chunker import load_chunker, split_into_chunks
from embeddings import load_embedding_model, embed_sentences
from emotion import load_emotion_model, classify_emotion
from vad import blend_vad
from voice_builder import generate_voice_description
from tts import load_tts_model, synthesize, audio_to_base64


# ── Startup: load all models once ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== Starting model loading ===")
    load_chunker()
    load_embedding_model()
    load_emotion_model()
    load_tts_model()
    print("=== All models ready ===")
    yield


app = FastAPI(title="Emotion-Aware TTS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response shapes ──────────────────────────────────────────────

class SynthesizeRequest(BaseModel):
    text: str
    gender: str = "female"          # "male" | "female"
    age_range: str = "26-40"        # "0-5" | "6-10" | "11-17" | "18-25" | "26-40" | "41-60" | "61+"


class AnalyzeRequest(BaseModel):
    text: str


class ChunkResult(BaseModel):
    text: str
    emotion_label: str
    emotion_score: float
    second_emotion_label: str
    second_emotion_score: float
    vad: dict
    voice_description: str
    audio_b64: str


class SynthesizeResponse(BaseModel):
    chunks: list[ChunkResult]


class EmotionChunk(BaseModel):
    text: str
    emotion_label: str
    emotion_score: float
    second_emotion_label: str
    second_emotion_score: float
    vad: dict


class AnalyzeResponse(BaseModel):
    chunks: list[EmotionChunk]


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")

    chunks = split_into_chunks(req.text)
    embeddings = embed_sentences(chunks)
    results = []

    for chunk, embedding in zip(chunks, embeddings):
        emotions = classify_emotion(embedding, chunk)
        vad = blend_vad(emotions)

        second_label = emotions[1]["label"] if len(emotions) > 1 else ""
        second_score = round(emotions[1]["score"], 3) if len(emotions) > 1 else 0.0

        results.append(EmotionChunk(
            text=chunk,
            emotion_label=emotions[0]["label"],
            emotion_score=round(emotions[0]["score"], 3),
            second_emotion_label=second_label,
            second_emotion_score=second_score,
            vad=vad,
        ))

    return AnalyzeResponse(chunks=results)


@app.post("/synthesize", response_model=SynthesizeResponse)
def synthesize_speech(req: SynthesizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")

    if req.gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="gender must be 'male' or 'female'.")

    valid_age_ranges = ("0-5", "6-10", "11-17", "18-25", "26-40", "41-60", "61+")
    if req.age_range not in valid_age_ranges:
        raise HTTPException(status_code=400, detail=f"age_range must be one of {valid_age_ranges}.")

    chunks = split_into_chunks(req.text)
    embeddings = embed_sentences(chunks)
    results = []

    for chunk, embedding in zip(chunks, embeddings):
        # Step 1 — detect emotions
        emotions = classify_emotion(embedding, chunk)

        # Step 2 — blend into VAD coordinates
        vad = blend_vad(emotions)

        # Step 3 — generate voice description via Gemini
        description = generate_voice_description(
            emotions,
            vad,
            req.gender,
            req.age_range,
        )

        # Step 4 — synthesize audio
        audio, sample_rate = synthesize(chunk, description)

        # Step 5 — encode to base64 WAV
        audio_b64 = audio_to_base64(audio, sample_rate)

        second_label = emotions[1]["label"] if len(emotions) > 1 else ""
        second_score = round(emotions[1]["score"], 3) if len(emotions) > 1 else 0.0

        results.append(ChunkResult(
            text=chunk,
            emotion_label=emotions[0]["label"],
            emotion_score=round(emotions[0]["score"], 3),
            second_emotion_label=second_label,
            second_emotion_score=second_score,
            vad=vad,
            voice_description=description,
            audio_b64=audio_b64,
        ))

    return SynthesizeResponse(chunks=results)