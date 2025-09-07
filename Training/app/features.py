import os
import pandas as pd
import librosa
import numpy as np
import warnings

warnings.filterwarnings("ignore", message="n_fft=1024 is too large for input signal")

CSV_PATH = 'data/merged_data.csv'  # Ton fichier CSV avec les données existantes
AUDIO_DIR = 'audio'
DEGRADED_DIR = 'audio_degraded'

def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    # Extract basic features (tu peux ajouter d'autres comme discuté)
    bpm, _ = librosa.beat.beat_track(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = np.mean(zcr)

    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    rms = np.mean(librosa.feature.rms(y=y))

    features = {
        'bpm': bpm,
        'spectral_centroid': spectral_centroid,
        'spectral_bandwidth': spectral_bandwidth,
        'spectral_rolloff': spectral_rolloff,
        'rms': rms,
        'zcr_mean': zcr_mean,
    }

    for i, v in enumerate(mfcc_mean, start=1):
        features[f'mfcc_{i}'] = v
    for i, v in enumerate(chroma_mean, start=1):
        features[f'chroma_{i}'] = v

    return features

def find_audio_path(filename):
    # Cherche dans audio_degraded directement
    degraded_path = os.path.join(DEGRADED_DIR, filename)
    if os.path.isfile(degraded_path):
        return degraded_path

    # Sinon cherche récursivement dans audio/
    for root, dirs, files in os.walk(AUDIO_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None

def main():
    df = pd.read_csv(CSV_PATH)
    new_features_list = []

    for idx, row in df.iterrows():
        filename = row['file'].split('/')[-1]  # Garde que le nom de fichier sans dossier
        print(f"Extraction features pour : {filename}")

        audio_path = find_audio_path(filename)
        if audio_path is None:
            print(f"Fichier audio non trouvé : {filename} (ajoute des NaN)")
            new_features_list.append({**row.to_dict(), **{k: np.nan for k in
                                                       ['bpm', 'spectral_centroid', 'spectral_bandwidth', 'spectral_rolloff',
                                                        'rms', 'zcr_mean'] +
                                                       [f'mfcc_{i}' for i in range(1, 14)] +
                                                       [f'chroma_{i}' for i in range(1, 13)]}})
            continue

        try:
            features = extract_audio_features(audio_path)
            new_features_list.append({**row.to_dict(), **features})
        except Exception as e:
            print(f"Erreur extraction features pour {filename} : {e}")
            new_features_list.append({**row.to_dict(), **{k: np.nan for k in
                                                       ['bpm', 'spectral_centroid', 'spectral_bandwidth', 'spectral_rolloff',
                                                        'rms', 'zcr_mean'] +
                                                       [f'mfcc_{i}' for i in range(1, 14)] +
                                                       [f'chroma_{i}' for i in range(1, 13)]}})

    new_df = pd.DataFrame(new_features_list)
    new_df.to_csv('data_with_new_features.csv', index=False)
    print("Extraction terminée, fichier data_with_new_features.csv créé.")

if __name__ == '__main__':
    main()
