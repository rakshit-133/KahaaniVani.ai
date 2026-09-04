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
    # Use float16 on CUDA, float32 on CPU (float16 on CPU can be unstable)
    dtype = torch.float16 if _device == "cuda" else torch.float32
    print(f"Loading Parler-TTS Mini on {_device} ({dtype})...")
    _model = ParlerTTSForConditionalGeneration.from_pretrained(
        "parler-tts/parler-tts-mini-v1",
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    ).to(_device)
    _tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")
    print("Parler-TTS loaded.")


def synthesize(text: str, description: str) -> tuple[np.ndarray, int]:
    if _model is None:
        raise RuntimeError("TTS model not loaded. Call load_tts_model() first.")

    # Sanitize quotes and apostrophes to prevent Parler-TTS gibberish
    clean_text = text.replace("'", "").replace('"', "").replace("`", "").replace("’", "").replace("“", "").replace("”", "")
    clean_desc = description.replace("'", "").replace('"', "").replace("`", "").replace("’", "").replace("“", "").replace("”", "")

    input_ids        = _tokenizer(clean_desc,  return_tensors="pt").input_ids.to(_device)
    prompt_input_ids = _tokenizer(clean_text, return_tensors="pt").input_ids.to(_device)

    with torch.no_grad():
        generation = _model.generate(
            input_ids=input_ids,
            prompt_input_ids=prompt_input_ids,
            max_new_tokens=4096,   # Increased from 2048 to prevent early truncation
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