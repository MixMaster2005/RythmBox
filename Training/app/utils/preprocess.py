import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

# Charger le CSV d'origine (fusionné, complet)
df = pd.read_csv("merged_data.csv")

# Nettoyage rapide
df['score_rythme'] = pd.to_numeric(df['score_rythme'], errors='coerce')
df['score_musicalite'] = pd.to_numeric(df['score_musicalite'], errors='coerce')
df['bpm'] = pd.to_numeric(df['bpm'], errors='coerce')
df['genre'] = df['genre'].fillna('unknown')
df['version'] = df.get('version', '').fillna('original')
df['version'] = df['version'].replace('', 'original')

df['score_rythme'].fillna(df['score_rythme'].mean(), inplace=True)
df['score_musicalite'].fillna(df['score_musicalite'].mean(), inplace=True)
df['bpm'].fillna(df['bpm'].mean(), inplace=True)

categorical_features = ['genre', 'version']
numerical_features = [col for col in df.columns if col.startswith(('mfcc_', 'chroma_', 'zcr', 'score', 'bpm'))]

# Transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ])

# Fit + transform
X_num_cat = preprocessor.fit_transform(df)

# Récupérer noms des features numériques (même ordre que numerical_features)
num_features_names = numerical_features

# Récupérer noms des features encodées (genre, version)
cat_encoder = preprocessor.named_transformers_['cat']
cat_features_names = cat_encoder.get_feature_names_out(categorical_features)

# Concaténer noms
all_feature_names = list(num_features_names) + list(cat_features_names)

# Créer DataFrame à partir du tableau numpy transformé
df_processed = pd.DataFrame(X_num_cat, columns=all_feature_names)

# Facultatif : garder la colonne 'file' pour référence
df_processed.insert(0, 'file', df['file'])

# Sauvegarder dans un nouveau CSV
df_processed.to_csv("processed_data.csv", index=False)

print("✅ Préprocessing terminé, fichier saved: processed_data.csv")
