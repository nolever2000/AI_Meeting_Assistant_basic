import librosa


def to_16k(audio, sr):
    return librosa.resample(audio, orig_sr=sr, target_sr=16000)