import torch
import numpy as np
import soundfile as sf
import io
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

_model = None
_tokenizer = None
_device = None


def load_tts_model():
    global _model, _tokenizer, _device
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Parler-TTS Mini on {_device}...")
    _model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-v1"
    ).to(_device)
    _tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
    print("Parler-TTS loaded.")


def synthesize(text: str, description: str) -> tuple[np.ndarray, int]:
    if _model is None:
        raise RuntimeError("TTS model not loaded. Call load_tts_model() first.")

    input_ids = _tokenizer(description, return_tensors="pt").input_ids.to(_device)
    prompt_input_ids = _tokenizer(text, return_tensors="pt").input_ids.to(_device)

    with torch.no_grad():
        generation = _model.generate(
            input_ids=input_ids,
            prompt_input_ids=prompt_input_ids,
        )

    audio = generation.cpu().numpy().squeeze().astype(np.float32)
    sample_rate = _model.config.sampling_rate
    return audio, sample_rate


def audio_to_base64(audio: np.ndarray, sample_rate: int) -> str:
    import base64
    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")