import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model_refined.pkl')

class RandomForestModel:
    def __init__(self):
        self.categorical_features = ['genre', 'version']
        self.numerical_features = [
            'bpm',
            'spectral_centroid',
            'spectral_bandwidth',
            'spectral_rolloff',
            'rms',
            'zcr_mean',
            # MFCC
            *[f'mfcc_{i}' for i in range(1, 14)],
            # Chroma
            *[f'chroma_{i}' for i in range(1, 13)],
            # Spectral Contrast
            *[f'contrast_{i}' for i in range(1, 8)],
            # Tonnetz
            *[f'tonnetz_{i}' for i in range(1, 7)],
        ]

        self.model = None
        self.is_trained = False

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.is_trained = True
        else:
            raise FileNotFoundError(f"No model file at {MODEL_PATH}")

    def predict(self, input_dict):
        if not self.is_trained:
            raise Exception("Model not loaded")
        
        df = pd.DataFrame([{
            'genre': input_dict.get('genre', 'unknown'),
            'version': input_dict.get('version', 'unknown'),
            **{k: input_dict.get(k, 0.0) for k in self.numerical_features}
        }])
        
        preds = self.model.predict(df)
        return {
            'score_rythme': float(preds[0][0]),
            'score_musicalite': float(preds[0][1])
        }
