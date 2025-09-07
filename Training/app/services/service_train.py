import os
import pandas as pd
from app.models.RandomForest import RandomForestModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /services ou équivalent selon ton arborescence
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "data_with_new_features.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_model_refined.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_save():
    df = pd.read_csv(DATA_PATH)
    # Nettoyage rapide
    df.dropna(subset=['score_rythme', 'score_musicalite'], inplace=True)
    # S'assurer que toutes les colonnes nécessaires sont présentes et converties en float au besoin
    numeric_cols = [
        'bpm',
        'spectral_centroid', 'spectral_bandwidth', 'spectral_rolloff', 'rms',
        'zcr_mean'
    ] + [f"mfcc_{i}" for i in range(1,14)] + [f"chroma_{i}" for i in range(1,13)]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    model = RandomForestModel()
    model.train(df)
    model.save_model(MODEL_PATH)
    print(f"Model saved at {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
