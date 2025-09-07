import joblib
import pandas as pd

model = joblib.load('models/rf_model_refined.pkl')
print(type(model))  # Devrait être sklearn.pipeline.Pipeline

print(model.named_steps)  # Pour voir ce qu'il y a dans le pipeline

# Afficher les noms de colonnes attendues
from sklearn import set_config
set_config(transform_output="pandas")

sample = pd.DataFrame([{
    "genre": "rock",
    "version": "version_normale",
    "bpm": 120,
    "zcr_mean": 0.05,
    "rms_mean": 0.1,
    "rolloff_mean": 3000,
    "bandwidth_mean": 2000,
    **{f"mfcc_{i}": 0.1 for i in range(1, 14)},
    **{f"chroma_{i}": 0.1 for i in range(1, 13)},
    **{f"contrast_{i}": 0.1 for i in range(1, 8)},
    **{f"tonnetz_{i}": 0.1 for i in range(1, 7)},
}])

print(model.predict(sample))
