from groq import Groq
import os

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

def construire_prompt_analyse_score(
    score_type: str,
    score: int,
    audio_duration: float,
    genre: str,
    version: str,
    features: dict
) -> str:
    # Si features contient un commentaire préformaté, on l'utilise tel quel
    if 'commentaire' in features and isinstance(features['commentaire'], str):
        feature_lines = features['commentaire']
    else:
        feature_lines = "\n".join([
            f"- {key.replace('_', ' ').capitalize()} : {value}"
            for key, value in features.items()
        ])

    return f"""
Tu es un expert en analyse musicale.

**Important : Ne mentionne jamais les indicateurs, le score, ni les données techniques dans ta réponse.**

Évalue uniquement la {score_type} d'une performance musicale sur la base des données fournies.

Données :
- Durée : {audio_duration:.2f} sec
- Genre : {genre}
- Version modèle : {version}
- Score interne (non à mentionner) : {score}/100

Caractéristiques audio :
{feature_lines}

Ta tâche est simple :
- Donne un point fort et un point à améliorer liés à la {score_type}.
- Ne parle pas des indicateurs, des chiffres, ou du score.
- Ta réponse doit être concise : 2 à 4 phrases, maximum 120 mots.
- Ne fais aucune autre remarque.

Merci.
"""



def message_analyse_score(
    score_type: str,
    score: int,
    audio_duration: float,
    genre: str,
    version: str,
    features: dict
) -> str:
    prompt = construire_prompt_analyse_score(
        score_type, score, audio_duration, genre, version, features
    )
    try:
        reponse = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192"
        )
        return reponse.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur lors de l'interaction avec LLaMA 3 : {e}"
