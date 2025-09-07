import os
import tempfile
from flask import Blueprint, request, jsonify
from services.feature_service import extract_audio_features
from services.model_service import RandomForestModel
from services.messages_service import message_analyse_score
import numpy as np
from services.musicality_score import score_musicality

analyze_bp = Blueprint('analyze', __name__)

model = RandomForestModel()
model.load_model()

# --- Sélection des features pertinents ---
FEATURES_RYTHMIQUE = [
    'bpm',
    'zcr_mean',
    'rms',
    'spectral_centroid',
    'spectral_bandwidth'
]

FEATURES_MUSICALITE = [
    'spectral_centroid',
    'spectral_rolloff',
    'spectral_bandwidth',
    'rms',
    'mfcc_1', 'mfcc_2', 'mfcc_3',
    'chroma_1', 'chroma_5', 'chroma_8',
    'contrast_1', 'contrast_4',
    'tonnetz_1', 'tonnetz_3'
]

def filtrer_features(features, score_type):
    if score_type.lower() == "rythmique":
        cles = FEATURES_RYTHMIQUE
    else:
        cles = FEATURES_MUSICALITE
    return {k: arrondir_valeur(features[k], 4) for k in cles if k in features}

@analyze_bp.route('/analyze', methods=['POST'])
def analyze_audio():
    try:
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'Aucun fichier audio reçu'}), 400

        if not audio_file.filename.endswith('.wav'):
            return jsonify({'error': 'Le fichier doit être au format WAV'}), 400

        genre = request.form.get('genre', 'unknown')

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
            audio_file.save(temp.name)
            temp_path = temp.name

        try:
            features = extract_audio_features(temp_path)
            features['genre'] = genre
            features['version'] = 'version_normale'

            predictions = model.predict(features)
            rhythm_score = round(predictions.get('score_rythme', 0), 1)
            musicality_score_modele = round(predictions.get('score_musicalite', 0), 1)

            # Ici score_musicality retourne (score, commentaire)
            musicality_score_val, musicality_commentaire = score_musicality(temp_path)

            # Moyenne pondérée des scores musicalité (priorité au score maison)
            poids_maison = 0.7
            poids_modele = 0.3
            musicality_score_final = round(poids_maison * musicality_score_val + poids_modele * musicality_score_modele, 1)

            audio_duration = features.get('duration', 0)

            filtered_rythmique = filtrer_features(features, "rythmique")
            filtered_musicalite = filtrer_features(features, "musicalité")

            commentaire_rythmique = message_analyse_score(
                'rythmique',
                rhythm_score,
                audio_duration,
                genre,
                features['version'],
                filtered_rythmique
            )

            # Après :
            features_musicalite = filtered_musicalite.copy()
            features_musicalite['commentaire'] = musicality_commentaire

            commentaire_musicalite = message_analyse_score(
                'musicalité',
                musicality_score_final,
                audio_duration,
                genre,
                features['version'],
                features_musicalite
            )

            
            print(jsonify({
                'predictions': predictions,
                'commentaire_rythmique': commentaire_rythmique,
                'commentaire_musicalite': commentaire_musicalite,
                'score_musicalite_maison': musicality_score_val,
                'score_musicalite_modele': musicality_score_modele,
                'score_musicalite_final': musicality_score_final,
                'commentaire_musicalite_maison': musicality_commentaire  # utile pour debug
            }))

            return jsonify({
                'predictions': predictions,
                'commentaire_rythmique': commentaire_rythmique,
                'commentaire_musicalite': commentaire_musicalite,
                'score_musicalite_maison': musicality_score_val,
                'score_musicalite_modele': musicality_score_modele,
                'score_musicalite_final': musicality_score_final,
                'commentaire_musicalite_maison': musicality_commentaire  # utile pour debug
            })

        finally:
            os.remove(temp_path)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


    
def arrondir_valeur(v, ndigits=4):
    if isinstance(v, (float, int)):
        return round(v, ndigits)
    elif isinstance(v, np.ndarray):
        return np.round(v, ndigits).tolist()  # convertit en liste pour faciliter l'usage
    else:
        return v  # ou gérer d'autres types si besoin

