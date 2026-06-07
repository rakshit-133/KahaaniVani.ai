import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"

AGE_VOICE_MAP = {
    "0-5":   "Speaker is 0-5 years old — very high pitched, slow and simple speech, soft and childlike.",
    "6-10":  "Speaker is 6-10 years old — high pitched, energetic, slightly uneven pacing, bright and curious tone.",
    "11-17": "Speaker is 11-17 years old — voice may be breaking if male, slightly higher than adult, self-conscious energy.",
    "18-25": "Speaker is 18-25 years old — youthful, energetic, faster pace, lighter and more expressive.",
    "26-40": "Speaker is 26-40 years old — full, confident, steady and authoritative adult voice.",
    "41-60": "Speaker is 41-60 years old — deeper, measured, calm authority with lived-in warmth.",
    "61+":   "Speaker is 61 or older — slower pace, gravitas, slight roughness or breathiness, deeply warm.",
}

FALLBACKS = {
    "admiration":     {"female": "A warm, respectful female voice with steady pace and uplifted tone.", "male": "A composed, appreciative male voice with measured pace and genuine warmth."},
    "amusement":      {"female": "A light, playful female voice with a smile in the tone and bouncy rhythm.", "male": "A relaxed, amused male voice with easy rhythm and a hint of laughter underneath."},
    "anger":          {"female": "A clipped, tense female voice with sharp articulation and controlled fury.", "male": "A deep, forceful male voice with deliberate heavy weight on each syllable."},
    "annoyance":      {"female": "A dry, impatient female voice with clipped phrasing and elevated pitch.", "male": "A flat, irritated male voice with short phrases and minimal inflection."},
    "approval":       {"female": "A warm, affirming female voice with encouraging tone and steady pace.", "male": "A confident, positive male voice with clear articulation and supportive energy."},
    "caring":         {"female": "A gentle, nurturing female voice speaking softly with warmth and patience.", "male": "A low, kind male voice with slow deliberate pace and genuine tenderness."},
    "confusion":      {"female": "A hesitant female voice with rising intonation and uncertain pacing.", "male": "A puzzled male voice with uneven rhythm and a searching tone."},
    "curiosity":      {"female": "A bright, interested female voice with forward-leaning energy and questioning inflection.", "male": "An engaged, probing male voice with alert inquisitive tone."},
    "desire":         {"female": "A low, intent female voice with slow deliberate pace and quiet intensity.", "male": "A measured, focused male voice with deeper pitch and restrained urgency."},
    "disappointment": {"female": "A deflated, quiet female voice with slow pace and downward pitch drift.", "male": "A heavy, subdued male voice with flat delivery and reluctant phrasing."},
    "disapproval":    {"female": "A cool, precise female voice with clipped endings and stern undertone.", "male": "A firm, measured male voice with deliberate stress on critical words."},
    "disgust":        {"female": "A dry, contemptuous female voice with flat tone and distaste in articulation.", "male": "A blunt, rough male voice with minimal inflection and dismissive pacing."},
    "embarrassment":  {"female": "A soft, slightly rushed female voice with lower volume and self-conscious hesitation.", "male": "A quiet, tight male voice with reduced pitch range and awkward micro-pauses."},
    "excitement":     {"female": "A fast, effervescent female voice with wide pitch range and barely-contained energy.", "male": "A rapid, vibrant male voice with forward momentum and kinetic enthusiasm."},
    "fear":           {"female": "A hushed, trembling female voice with irregular pacing and shallow audible breath.", "male": "A strained, quiet male voice with uneven rhythm and taut tension."},
    "gratitude":      {"female": "A warm, sincere female voice with soft steady pace and heartfelt tone.", "male": "A deep, appreciative male voice with calm delivery and quiet sincerity."},
    "grief":          {"female": "A broken, hushed female voice with long pauses and wavering pitch.", "male": "A hollow, effortful male voice in slow fragments with heavy silence between thoughts."},
    "joy":            {"female": "A bright, warm female voice with upward lilt and a natural smile in the tone.", "male": "A rich, hearty male voice with confident warmth and celebratory energy."},
    "love":           {"female": "A soft, intimate female voice speaking slowly with deep warmth and closeness.", "male": "A low, gentle male voice with unhurried pace and tender careful delivery."},
    "nervousness":    {"female": "A light, slightly hurried female voice with uptalk and faint breathiness.", "male": "A clipped, tight male voice with irregular pacing and noticeable tension."},
    "neutral":        {"female": "A clear, calm female voice with steady moderate pace and even pitch.", "male": "A clear, steady male voice with natural intonation and composed delivery."},
    "optimism":       {"female": "A bright, forward-looking female voice with lifted tone and energetic pace.", "male": "A confident, upbeat male voice with steady rhythm and positive momentum."},
    "pride":          {"female": "A poised, assured female voice with elevated pitch and deliberate articulation.", "male": "A deep, commanding male voice with measured authority and quiet self-assurance."},
    "realization":    {"female": "A suddenly alert female voice with a brief pause then steady measured delivery.", "male": "A thoughtful male voice with a contemplative pause and slower pacing."},
    "relief":         {"female": "A softly exhaling female voice with slower pace and released tension in the tone.", "male": "A low, unwinding male voice with longer phrase endings and settled energy."},
    "remorse":        {"female": "A quiet, heavy female voice with slow pace and genuine regret in every word.", "male": "A subdued, strained male voice with flat pitch and reluctant delivery."},
    "sadness":        {"female": "A soft, subdued female voice speaking slowly with long pauses and quiet emotional weight.", "male": "A low, measured male voice with flat pitch and weary delivery."},
    "surprise":       {"female": "A sharp, animated female voice with sudden pitch jumps and startled pauses.", "male": "A clipped, abrupt male voice with fast buildup then a halting pause on the revelation."},
}


def generate_voice_description(
    emotions: list[dict],
    vad: dict,
    gender: str,
    age_range: str = "26-40",
) -> str:

    top_emotion = emotions[0]["label"]
    top_score = round(emotions[0]["score"] * 100)
    emotion_desc = f"{top_emotion} ({top_score}%)"

    if len(emotions) > 1 and emotions[1]["score"] > 0.15:
        second_score = round(emotions[1]["score"] * 100)
        emotion_desc += f" blended with {emotions[1]['label']} ({second_score}%)"

    age_note = AGE_VOICE_MAP.get(age_range, AGE_VOICE_MAP["26-40"])

    prompt = f"""You are an expert voice director for audiobook narration.
Given an emotion profile, write a single short paragraph describing exactly how a {gender} voice should sound.
Be specific about: pace, pitch, breathiness, pauses, articulation, and energy level.
Do not use bullet points. Do not explain the emotion. Just describe the voice.
Keep it under 60 words.

Emotion: {emotion_desc}
Valence (positive vs negative, -1 to 1): {vad['v']}
Arousal (energetic vs calm, -1 to 1): {vad['a']}
Dominance (in-control vs powerless, -1 to 1): {vad['d']}
Speaker gender: {gender}
Speaker age: {age_note}

Voice description:"""

    try:
        response = requests.post(
            GEMINI_URL,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 120,
                },
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        time.sleep(1)
        return text.strip()

    except requests.exceptions.ConnectionError:
        return _fallback_description(top_emotion, gender)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _fallback_description(top_emotion, gender)


def _fallback_description(emotion: str, gender: str) -> str:
    gender_key = gender.lower() if gender.lower() in ("male", "female") else "female"
    entry = FALLBACKS.get(emotion.lower(), FALLBACKS["neutral"])
    return entry[gender_key]