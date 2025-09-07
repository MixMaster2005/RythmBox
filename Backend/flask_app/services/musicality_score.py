import librosa
import numpy as np

# Patterns de base (12 demi-tons chroma)
BASE_MAJOR = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])        # triade majeure (C E G)
BASE_MINOR = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])        # triade mineure (C Eb G)
BASE_7_MAJOR = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])      # C E G B (maj7)
BASE_7_MINOR = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0])      # C Eb G Bb (min7)
BASE_SUS2 = np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0])         # C D G (sus2)
BASE_SUS4 = np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0])         # C F G (sus4)

notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

ACCORDS = {}
for i, note in enumerate(notes):
    ACCORDS[f"{note}_major"] = np.roll(BASE_MAJOR, i)
    ACCORDS[f"{note}_minor"] = np.roll(BASE_MINOR, i)
    ACCORDS[f"{note}_7_major"] = np.roll(BASE_7_MAJOR, i)
    ACCORDS[f"{note}_7_minor"] = np.roll(BASE_7_MINOR, i)
    ACCORDS[f"{note}_sus2"] = np.roll(BASE_SUS2, i)
    ACCORDS[f"{note}_sus4"] = np.roll(BASE_SUS4, i)

def detect_chord(chroma_vec):
    """Détecte l'accord le plus proche et retourne la similarité cosinus."""
    if np.max(chroma_vec) == 0:
        return None, 0.0
    chroma_vec_norm = chroma_vec / np.linalg.norm(chroma_vec)
    best_chord = None
    best_sim = -1
    for chord, pattern in ACCORDS.items():
        pattern_norm = pattern / np.linalg.norm(pattern)
        sim = np.dot(chroma_vec_norm, pattern_norm)
        if sim > best_sim:
            best_sim = sim
            best_chord = chord
    return best_chord, best_sim

def score_musicality(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y=y)
    rms = librosa.feature.rms(y=y)
    
    chord_sims = [detect_chord(chroma[:, i])[1] for i in range(chroma.shape[1])]
    mean_chord_sim = np.mean(chord_sims)
    # Recentre la similarité d'accords autour de 0.3 minimum
    mean_chord_sim = max(mean_chord_sim, 0.3)
    
    tonnetz_var = np.var(tonnetz)
    stability_score = max(0.5, 1 - tonnetz_var * 5)  # plancher 0.5
    
    mean_zcr = np.mean(zcr)
    zcr_score = max(0.6, 1 - mean_zcr * 5)  # plancher 0.6, moins sévère
    
    mean_rms = np.mean(rms)
    rms_score = max(0.5, min(1, mean_rms * 5))  # plancher 0.5
    
    score = (
        0.1 * mean_chord_sim +      # accords, un peu plus
        0.6 * stability_score +     # stabilité tonale, poids plus fort
        0.15 * zcr_score +          # bruit, faible poids
        0.15 * rms_score            # dynamique
    )
    
    final_score = round(score * 100, 2)

    stability_comment = "Stabilité tonale globalement bonne." if stability_score > 0.7 else "Légère instabilité tonale."
    noise_comment = "Un peu de bruit, mais ça reste clair." if zcr_score > 0.7 else "Bruit perceptible."
    dynamics_comment = "Bonne dynamique sonore." if rms_score > 0.6 else "Dynamique sonore faible."
    
    commentaire = f"{stability_comment} {noise_comment} {dynamics_comment}"
    
    print(final_score)
    print(commentaire)

    return final_score, commentaire


# Exemple d'utilisation
# score, commentaire = score_musicality('ton_audio.wav')
# print("Score:", score)
# print("Commentaire:", commentaire)

# Exemple
# print(score_musicality('ton_audio.wav'))
