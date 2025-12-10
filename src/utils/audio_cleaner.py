import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
from io import BytesIO

def clean_audio(file_bytes):
    # Load audio into numpy array
    audio, sr = librosa.load(BytesIO(file_bytes), sr=16000, mono=True)

    # STEP 1: Noise reduction (spectral gating)
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.85)

    # STEP 2: Normalize volume
    normalized = librosa.util.normalize(reduced_noise)

    # STEP 3: Soft high-pass filter (rumble removal)
    filtered = librosa.effects.preemphasis(normalized, coef=0.97)

    # Convert back to AudioSegment for Whisper compatibility
    buf = BytesIO()
    pcm_data = (filtered * 32767).astype(np.int16)

    audio_seg = AudioSegment(
        data=pcm_data.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    )

    audio_seg.export(buf, format="wav")
    buf.seek(0)

    return buf

