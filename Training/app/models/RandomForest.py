import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

class RandomForestModel:
    def __init__(self):
        self.categorical_features = ['genre', 'version']
        self.numerical_features = [
            'bpm',
            'spectral_centroid', 'spectral_bandwidth', 'spectral_rolloff', 'rms',
            'zcr_mean',
            'mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4', 'mfcc_5', 'mfcc_6', 'mfcc_7', 'mfcc_8', 'mfcc_9', 'mfcc_10',
            'mfcc_11', 'mfcc_12', 'mfcc_13',
            'chroma_1', 'chroma_2', 'chroma_3', 'chroma_4', 'chroma_5', 'chroma_6',
            'chroma_7', 'chroma_8', 'chroma_9', 'chroma_10', 'chroma_11', 'chroma_12'
        ]

        self.preprocessor = ColumnTransformer(transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), self.categorical_features),
            ('num', StandardScaler(), self.numerical_features)
        ])

        self.model = Pipeline([
            ('preprocessor', self.preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])

        self.is_trained = False

    def train(self, df):
        X = df[self.categorical_features + self.numerical_features]
        y = df[['score_rythme', 'score_musicalite']]
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, input_dict_or_df):
        if not self.is_trained:
            raise Exception("Model not trained yet")
        # Accepte dict ou dataframe
        if isinstance(input_dict_or_df, dict):
            X = pd.DataFrame([input_dict_or_df])
        else:
            X = input_dict_or_df
        return self.model.predict(X)

    def save_model(self, path):
        joblib.dump(self.model, path)

    def load_model(self, path):
        if os.path.exists(path):
            self.model = joblib.load(path)
            self.is_trained = True
        else:
            raise FileNotFoundError(f"No model file found at {path}")
