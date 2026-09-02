import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

AGE_VOICE_MAP = {
    "0-5":   "Speaker is 0-5 years old — very high pitched, slow and simple speech, soft and childlike.",
    "6-10":  "Speaker is 6-10 years old — high pitched, energetic, slightly uneven pacing, bright and curious tone.",
    "11-17": "Speaker is 11-17 years old — voice may be breaking if male, slightly higher than adult, self-conscious energy.",
    "18-25": "Speaker is 18-25 years old — youthful, energetic, faster pace, lighter and more expressive.",
    "26-40": "Speaker is 26-40 years old — full, confident, steady and authoritative adult voice.",
    "41-60": "Speaker is 41-60 years old — deeper, measured, calm authority with lived-in warmth.",
    "61+":   "Speaker is 61 or older — slower pace, gravitas, slight roughness or breathiness, deeply warm.",
}

# ── Named Parler-TTS speakers mapped to emotions ─────────────────────────────
# Parler-TTS Mini v1 was trained on 34 specific speakers. Anchoring to a name
# activates that speaker's learned characteristics, dramatically improving
# expressiveness vs a generic description.
EMOTION_SPEAKER_MAP = {
    "female": {
        "admiration":     "Lea",
        "amusement":      "Jenna",
        "anger":          "Barbara",
        "annoyance":      "Rose",
        "approval":       "Rebecca",
        "caring":         "Lea",
        "confusion":      "Eileen",
        "curiosity":      "Naomie",
        "desire":         "Anna",
        "disappointment": "Carol",
        "disapproval":    "Barbara",
        "disgust":        "Karen",
        "embarrassment":  "Tina",
        "excitement":     "Jenna",
        "fear":           "Tina",
        "gratitude":      "Lea",
        "grief":          "Emily",
        "joy":            "Joy",
        "love":           "Lauren",
        "nervousness":    "Eileen",
        "neutral":        "Laura",
        "optimism":       "Rebecca",
        "pride":          "Karen",
        "realization":    "Laura",
        "relief":         "Lauren",
        "remorse":        "Carol",
        "sadness":        "Emily",
        "surprise":       "Joy",
    },
    "male": {
        "admiration":     "Gary",
        "amusement":      "Jon",
        "anger":          "Rick",
        "annoyance":      "Jerry",
        "approval":       "Mike",
        "caring":         "Gary",
        "confusion":      "Jordan",
        "curiosity":      "Jason",
        "desire":         "Patrick",
        "disappointment": "Eric",
        "disapproval":    "Rick",
        "disgust":        "Will",
        "embarrassment":  "Aaron",
        "excitement":     "Jon",
        "fear":           "Aaron",
        "gratitude":      "Gary",
        "grief":          "James",
        "joy":            "Jon",
        "love":           "Bill",
        "nervousness":    "Aaron",
        "neutral":        "Tom",
        "optimism":       "Mike",
        "pride":          "David",
        "realization":    "Tom",
        "relief":         "Bill",
        "remorse":        "James",
        "sadness":        "James",
        "surprise":       "Will",
    },
}

# ── Named-speaker fallbacks (used when Gemini is unavailable) ─────────────────
FALLBACKS = {
    "admiration": {
        "female": "Lea's voice is warm and genuinely admiring, with a steady pace and gently uplifted tone. The recording is of very high quality, with no background noise.",
        "male":   "Gary's voice is composed and appreciative, with a measured pace and quiet warmth. The recording is of very high quality, with no background noise.",
    },
    "amusement": {
        "female": "Jenna's voice is light and playful, with a smiling tone and bouncy slightly fast rhythm. The recording is of very high quality, with no background noise.",
        "male":   "Jon's voice is relaxed and amused, with easy rhythm and a hint of laughter underneath. The recording is of very high quality, with no background noise.",
    },
    "anger": {
        "female": "Barbara's voice is clipped and tense, with sharp articulation and barely controlled fury at a deliberate pace. The recording is of very high quality, with no background noise.",
        "male":   "Rick's voice is deep and forceful, with heavy deliberate weight on each syllable and barely restrained aggression. The recording is of very high quality, with no background noise.",
    },
    "annoyance": {
        "female": "Rose's voice is dry and impatient, with clipped phrasing and a flat elevated tone. The recording is of very high quality, with no background noise.",
        "male":   "Jerry's voice is flat and irritated, with short phrases and minimal inflection. The recording is of very high quality, with no background noise.",
    },
    "approval": {
        "female": "Rebecca's voice is warm and affirming, with an encouraging uplifted tone and steady moderate pace. The recording is of very high quality, with no background noise.",
        "male":   "Mike's voice is confident and positive, with clear articulation and supportive energy. The recording is of very high quality, with no background noise.",
    },
    "caring": {
        "female": "Lea's voice is gentle and nurturing, speaking softly and slowly with genuine warmth and patience. The recording is of very high quality, with no background noise.",
        "male":   "Gary's voice is low and kind, with a slow deliberate pace and genuine tenderness in every word. The recording is of very high quality, with no background noise.",
    },
    "confusion": {
        "female": "Eileen's voice is hesitant and uncertain, with rising intonation and uneven searching pacing. The recording is of very high quality, with no background noise.",
        "male":   "Jordan's voice is puzzled and searching, with uneven rhythm and an upward trail at the end of phrases. The recording is of very high quality, with no background noise.",
    },
    "curiosity": {
        "female": "Naomie's voice is bright and interested, with forward-leaning energy and a questioning lift at phrase endings. The recording is of very high quality, with no background noise.",
        "male":   "Jason's voice is engaged and probing, with an alert inquisitive tone at a slightly faster pace. The recording is of very high quality, with no background noise.",
    },
    "desire": {
        "female": "Anna's voice is low and intent, with a slow deliberate pace and quiet restrained intensity. The recording is of very high quality, with no background noise.",
        "male":   "Patrick's voice is measured and focused, with a deeper pitch and restrained urgency. The recording is of very high quality, with no background noise.",
    },
    "disappointment": {
        "female": "Carol's voice is deflated and quiet, with a slow pace and downward drifting pitch. The recording is of very high quality, with no background noise.",
        "male":   "Eric's voice is heavy and subdued, with flat delivery and a reluctant halting phrasing. The recording is of very high quality, with no background noise.",
    },
    "disapproval": {
        "female": "Barbara's voice is cool and precise, with clipped endings and a stern measured undertone. The recording is of very high quality, with no background noise.",
        "male":   "Rick's voice is firm and deliberate, stressing critical words with controlled authority. The recording is of very high quality, with no background noise.",
    },
    "disgust": {
        "female": "Karen's voice is dry and contemptuous, with a flat tone and barely concealed distaste in every phrase. The recording is of very high quality, with no background noise.",
        "male":   "Will's voice is blunt and rough, with minimal inflection and dismissive clipped pacing. The recording is of very high quality, with no background noise.",
    },
    "embarrassment": {
        "female": "Tina's voice is soft and slightly rushed, with lower volume and self-conscious hesitation in her phrasing. The recording is of very high quality, with no background noise.",
        "male":   "Aaron's voice is quiet and tight, with a reduced pitch range and awkward micro-pauses. The recording is of very high quality, with no background noise.",
    },
    "excitement": {
        "female": "Jenna's voice is fast and effervescent, with a wide pitch range and barely-contained energy throughout. The recording is of very high quality, with no background noise.",
        "male":   "Jon's voice is rapid and vibrant, with strong forward momentum and kinetic enthusiasm. The recording is of very high quality, with no background noise.",
    },
    "fear": {
        "female": "Tina's voice is hushed and trembling, with irregular pacing and shallow audible breath between phrases. The recording is of very high quality, with no background noise.",
        "male":   "Aaron's voice is strained and quiet, with uneven rhythm and taut barely-contained tension. The recording is of very high quality, with no background noise.",
    },
    "gratitude": {
        "female": "Lea's voice is warm and sincere, with a soft steady pace and heartfelt tone. The recording is of very high quality, with no background noise.",
        "male":   "Gary's voice is deep and appreciative, with calm delivery and quiet sincerity. The recording is of very high quality, with no background noise.",
    },
    "grief": {
        "female": "Emily's voice is broken and hushed, with long pauses and a wavering pitch that barely holds together. The recording is of very high quality, with no background noise.",
        "male":   "James's voice is hollow and effortful, delivered in slow fragments with heavy silence between thoughts. The recording is of very high quality, with no background noise.",
    },
    "joy": {
        "female": "Joy's voice is bright and warm, with an upward lilt and a natural smile radiating through every word. The recording is of very high quality, with no background noise.",
        "male":   "Jon's voice is rich and hearty, with confident warmth and celebratory energy at a lively pace. The recording is of very high quality, with no background noise.",
    },
    "love": {
        "female": "Lauren's voice is soft and intimate, speaking slowly with deep warmth and closeness in every breath. The recording is of very high quality, with no background noise.",
        "male":   "Bill's voice is low and gentle, with an unhurried pace and tender careful delivery. The recording is of very high quality, with no background noise.",
    },
    "nervousness": {
        "female": "Eileen's voice is light and slightly hurried, with uptalk and faint breathiness between words. The recording is of very high quality, with no background noise.",
        "male":   "Aaron's voice is clipped and tight, with irregular pacing and noticeable tension in every phrase. The recording is of very high quality, with no background noise.",
    },
    "neutral": {
        "female": "Laura's voice is clear and calm, with a steady moderate pace and even natural pitch. The recording is of very high quality, with no background noise.",
        "male":   "Tom's voice is clear and steady, with natural intonation and composed measured delivery. The recording is of very high quality, with no background noise.",
    },
    "optimism": {
        "female": "Rebecca's voice is bright and forward-looking, with a lifted tone and energetic pace. The recording is of very high quality, with no background noise.",
        "male":   "Mike's voice is confident and upbeat, with steady rhythm and positive forward momentum. The recording is of very high quality, with no background noise.",
    },
    "pride": {
        "female": "Karen's voice is poised and assured, with elevated pitch and deliberate careful articulation. The recording is of very high quality, with no background noise.",
        "male":   "David's voice is deep and commanding, with measured authority and quiet self-assurance. The recording is of very high quality, with no background noise.",
    },
    "realization": {
        "female": "Laura's voice is suddenly alert, with a brief thoughtful pause then steady measured delivery. The recording is of very high quality, with no background noise.",
        "male":   "Tom's voice is contemplative, with a meaningful pause before continuing at a slower deliberate pace. The recording is of very high quality, with no background noise.",
    },
    "relief": {
        "female": "Lauren's voice softly exhales with a slower unwinding pace and released tension in every phrase. The recording is of very high quality, with no background noise.",
        "male":   "Bill's voice is low and unwinding, with longer phrase endings and deeply settled energy. The recording is of very high quality, with no background noise.",
    },
    "remorse": {
        "female": "Carol's voice is quiet and heavy, with a slow pace and genuine deep regret in every word. The recording is of very high quality, with no background noise.",
        "male":   "James's voice is subdued and strained, with flat pitch and reluctant effortful delivery. The recording is of very high quality, with no background noise.",
    },
    "sadness": {
        "female": "Emily's voice is soft and subdued, speaking slowly with long pauses and quiet emotional weight in every phrase. The recording is of very high quality, with no background noise.",
        "male":   "James's voice is low and measured, with flat pitch and weary heavy delivery. The recording is of very high quality, with no background noise.",
    },
    "surprise": {
        "female": "Joy's voice is sharp and animated, with sudden pitch jumps and startled pauses mid-phrase. The recording is of very high quality, with no background noise.",
        "male":   "Will's voice is clipped and abrupt, with fast buildup then a halting pause on the revelation. The recording is of very high quality, with no background noise.",
    },
}


def generate_voice_description(
    emotions: list[dict],
    vad: dict,
    gender: str,
    age_range: str = "26-40",
) -> str:

    top_emotion = emotions[0]["label"]
    top_score   = round(emotions[0]["score"] * 100)
    emotion_desc = f"{top_emotion} ({top_score}%)"

    if len(emotions) > 1 and emotions[1]["score"] > 0.15:
        second_score = round(emotions[1]["score"] * 100)
        emotion_desc += f" blended with {emotions[1]['label']} ({second_score}%)"

    age_note = AGE_VOICE_MAP.get(age_range, AGE_VOICE_MAP["26-40"])

    # Pick the Parler-TTS named speaker for this emotion × gender
    gender_key   = gender.lower() if gender.lower() in ("male", "female") else "female"
    default_name = "Laura" if gender_key == "female" else "Tom"
    speaker_name = EMOTION_SPEAKER_MAP[gender_key].get(top_emotion, default_name)

    prompt = f"""You are a voice director writing a description for Parler-TTS, an AI speech model.

FORMAT RULES (follow exactly):
1. Start with: "{speaker_name}'s voice is"
2. Use Parler-TTS vocabulary: very expressive, animated, monotone, whispering, laughing, energetic, trembling, flat, breathy, fast-paced, slow and deliberate, high-pitched, deep, hushed, sharp, warm, cold
3. End with exactly: "The recording is of very high quality, with no background noise."
4. Maximum 2 sentences total. Do NOT explain the emotion. Output ONLY the description.

Emotion to convey: {emotion_desc}
Valence (positive=joy vs negative=pain, -1 to 1): {vad['v']}
Arousal (energetic vs calm, -1 to 1): {vad['a']}
Dominance (in-control vs powerless, -1 to 1): {vad['d']}
Speaker age: {age_note}

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
        return _fallback_description(top_emotion, gender_key)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _fallback_description(top_emotion, gender_key)


def _fallback_description(emotion: str, gender: str) -> str:
    gender_key = gender.lower() if gender.lower() in ("male", "female") else "female"
    entry = FALLBACKS.get(emotion.lower(), FALLBACKS["neutral"])
    return entry[gender_key]