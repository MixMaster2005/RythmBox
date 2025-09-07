import os
import csv
import librosa
import numpy as np

# Dossiers à parcourir
AUDIO_DIRS = ["audio", "audio_degraded"]

# Sortie CSV
OUTPUT_CSV = "audio_features.csv"

def extract_features(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        # MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)

        # Concaténation des features
        features = np.concatenate([mfcc_mean, chroma_mean, [zcr_mean]])
        return features
    except Exception as e:
        print(f"Erreur extraction features pour {audio_path}: {e}")
        return None

def get_all_audio_files(root_folders):
    audio_files = []
    for root_folder in root_folders:
        if not os.path.exists(root_folder):
            continue
        for dirpath, _, filenames in os.walk(root_folder):
            for f in filenames:
                if f.lower().endswith(('.mp3', '.wav', '.flac', '.ogg')):
                    full_path = os.path.join(dirpath, f)
                    audio_files.append(full_path)
    return audio_files

def main():
    audio_files = get_all_audio_files(AUDIO_DIRS)

    print(f"{len(audio_files)} fichiers audio trouvés.")

    # Préparer les en-têtes CSV
    header = []
    # 13 MFCC
    header += [f"mfcc_{i+1}" for i in range(13)]
    # 12 Chroma
    header += [f"chroma_{i+1}" for i in range(12)]
    # ZCR
    header.append("zcr_mean")

    # Ajout colonne fichier
    header = ["file"] + header

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for audio_path in audio_files:
            features = extract_features(audio_path)
            if features is not None:
                row = [audio_path.replace("\\", "/")] + features.tolist()
                writer.writerow(row)

    print(f"Extraction terminée. Données sauvegardées dans {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
