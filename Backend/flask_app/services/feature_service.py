import librosa
import numpy as np

def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)  # 👈 durée calculée ici
    bpm, _ = librosa.beat.beat_track(y=y, sr=sr)

    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    rms = np.mean(librosa.feature.rms(y=y))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    zcr_mean = np.mean(librosa.feature.zero_crossing_rate(y=y))

    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = np.mean(contrast, axis=1)

    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    tonnetz_mean = np.mean(tonnetz, axis=1)

    features = {
        'bpm': bpm,
        'spectral_centroid': spectral_centroid,
        'spectral_rolloff': spectral_rolloff,
        'rms': rms,
        'spectral_bandwidth': spectral_bandwidth,
        'zcr_mean': zcr_mean,
        'duration': duration  # 👈 ajout ici
    }

    features.update({f'mfcc_{i+1}': v for i, v in enumerate(mfcc_mean)})
    features.update({f'chroma_{i+1}': v for i, v in enumerate(chroma_mean)})
    features.update({f'contrast_{i+1}': v for i, v in enumerate(contrast_mean)})
    features.update({f'tonnetz_{i+1}': v for i, v in enumerate(tonnetz_mean)})

    return features
