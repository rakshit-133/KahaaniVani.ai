import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# ── Voice Actors ─────────────────────────────────────────────────────────────
# Parler-TTS Mini v1 was trained on 34 specific speakers. Anchoring to a name
# activates that speaker's learned characteristics, improving consistency.
VOICE_ACTORS = {
    "female": {
        "Laura": "A clear, articulate, and versatile adult female voice.",
        "Lea": "A gentle, warm, and youthful female voice.",
        "Barbara": "A mature, firm, and authoritative adult female voice.",
        "Emily": "A soft, measured, and expressive female voice."
    },
    "male": {
        "Jon": "A lively, clear, and energetic adult male voice.",
        "Gary": "A deep, warm, and steady adult male voice.",
        "Rick": "A firm, commanding, and deliberate adult male voice.",
        "Ryan": "A fast-paced, youthful, and vibrant male voice."
    }
}

def generate_voice_description(
    emotions: list[dict],
    vad: dict,
    gender: str,
    voice_actor: str = "",
) -> str:

    top_emotion = emotions[0]["label"]
    top_score   = round(emotions[0]["score"] * 100)
    emotion_desc = f"{top_emotion} ({top_score}%)"

    if len(emotions) > 1 and emotions[1]["score"] > 0.15:
        second_score = round(emotions[1]["score"] * 100)
        emotion_desc += f" blended with {emotions[1]['label']} ({second_score}%)"

    gender_key = gender.lower() if gender.lower() in ("male", "female") else "female"
    
    # Resolve the requested voice actor, falling back to a default if not found
    actor_map = VOICE_ACTORS[gender_key]
    if not voice_actor or voice_actor not in actor_map:
        voice_actor = "Laura" if gender_key == "female" else "Jon"
        
    actor_desc = actor_map[voice_actor]

    prompt = f"""You are a voice director writing a description for Parler-TTS, an AI speech model.

FORMAT RULES (follow exactly):
1. Start with: "{voice_actor}'s voice is"
2. Use Parler-TTS vocabulary: very expressive, animated, monotone, whispering, laughing, energetic, trembling, flat, breathy, fast-paced, slow and deliberate, high-pitched, deep, hushed, sharp, warm, cold
3. End with exactly: "The recording is of very high quality, with no background noise."
4. Maximum 2 sentences total. Do NOT explain the emotion. Output ONLY the description.

Base Voice Identity: {actor_desc}
Emotion to convey: {emotion_desc}
Valence (positive=joy vs negative=pain, -1 to 1): {vad['v']}
Arousal (energetic vs calm, -1 to 1): {vad['a']}
Dominance (in-control vs powerless, -1 to 1): {vad['d']}

Voice description:"""

    try:
        response = requests.post(
            GEMINI_URL,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.6,
                    "maxOutputTokens": 150,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        time.sleep(1)
        result = text.strip()
        print(f"Voice description: {result}")
        return result

    except requests.exceptions.ConnectionError:
        return _fallback_description(voice_actor, top_emotion)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _fallback_description(voice_actor, top_emotion)


def _fallback_description(actor: str, emotion: str) -> str:
    # A generic fallback that preserves the actor identity and the emotion
    return f"{actor}'s voice is expressing {emotion.lower()} with clear articulation. The recording is of very high quality, with no background noise."