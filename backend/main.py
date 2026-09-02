import gc
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

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
    load_chunker();        gc.collect()
    load_embedding_model(); gc.collect()
    load_emotion_model();  gc.collect()
    load_tts_model();      gc.collect()
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
    combined_audio_b64: str = ""


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


@app.post("/synthesize")
def synthesize_speech(req: SynthesizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")

    if req.gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="gender must be 'male' or 'female'.")

    valid_age_ranges = ("0-5", "6-10", "11-17", "18-25", "26-40", "41-60", "61+")
    if req.age_range not in valid_age_ranges:
        raise HTTPException(status_code=400, detail=f"age_range must be one of {valid_age_ranges}.")

    def event_generator():
        chunks = split_into_chunks(req.text)
        embeddings = embed_sentences(chunks)
        all_audio = []
        current_sample_rate = 24000 # default fallback

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
            all_audio.append(audio)
            current_sample_rate = sample_rate

            # Step 5 — encode to base64 WAV
            audio_b64 = audio_to_base64(audio, sample_rate)

            second_label = emotions[1]["label"] if len(emotions) > 1 else ""
            second_score = round(emotions[1]["score"], 3) if len(emotions) > 1 else 0.0

            import re
            display_description = re.sub(r"^[^']+'s\s+", "The ", description)

            chunk_res = ChunkResult(
                text=chunk,
                emotion_label=emotions[0]["label"],
                emotion_score=round(emotions[0]["score"], 3),
                second_emotion_label=second_label,
                second_emotion_score=second_score,
                vad=vad,
                voice_description=display_description,
                audio_b64=audio_b64,
            )

            # Yield this chunk immediately
            yield f"data: {json.dumps({'type': 'chunk', 'data': chunk_res.model_dump()})}\n\n"

        combined_b64 = ""
        if all_audio:
            combined_audio = np.concatenate(all_audio)
            combined_b64 = audio_to_base64(combined_audio, current_sample_rate)

        yield f"data: {json.dumps({'type': 'done', 'combined_audio_b64': combined_b64})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")