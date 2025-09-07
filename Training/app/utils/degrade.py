import os
import csv
import librosa
import soundfile as sf
import re
from librosa.effects import pitch_shift

# Répertoires et chemins
BASE_DIR     = os.getcwd()
AUDIO_DIR    = os.path.join(BASE_DIR, "audio")
DEGRADED_DIR = os.path.join(BASE_DIR, "audio_degraded")
CSV_PATH     = os.path.join(BASE_DIR, "metadata.csv")

os.makedirs(DEGRADED_DIR, exist_ok=True)

# Nettoyage nom de fichier
def safe_filename(name):
    return re.sub(r'[^\w\-_\. ]', '_', name)

# Fonction pour dégrader un score de x% tout en restant ≥0
def degrade_score(score, reduction_ratio=0.3):
    try:
        s = float(score)
        return max(0, round(s * (1 - reduction_ratio)))
    except:
        return 0

# Règles de dégradation audio
def degrade_audio_rhythm(y, sr):
    # ralentit de 20% → dégradation rythmique
    return librosa.effects.time_stretch(y, rate=0.8)

def degrade_audio_musicality(y, sr):
    # baisse de 2 demi-tons → altération musicale
    return pitch_shift(y=y, sr=sr, n_steps=-2)

# Lecture du CSV existant
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    originals = list(reader)

# Préparer les colonnes
fieldnames = reader.fieldnames.copy()
if 'version' not in fieldnames:
    fieldnames.append('version')
if 'score_rythme_alt' not in fieldnames:
    fieldnames.append('score_rythme_alt')
if 'score_musicalite_alt' not in fieldnames:
    fieldnames.append('score_musicalite_alt')

all_rows = []

for row in originals:
    all_rows.append(row)  # ligne originale

    original_file = row['file'].replace("\\", "/")
    path_in = os.path.join(AUDIO_DIR, original_file)
    if not os.path.exists(path_in):
        print(f"⚠️ Fichier introuvable : {path_in}")
        continue

    try:
        y, sr = librosa.load(path_in, sr=None)

        # Nettoyer nom de base
        base_raw, ext = os.path.splitext(original_file)
        base_clean = safe_filename(base_raw)

        # 1) Dégradé rythmique
        y_r = degrade_audio_rhythm(y, sr)
        fn_r = f"{base_clean}__degraded_rhythm.wav"
        path_r = os.path.join(DEGRADED_DIR, fn_r)
        sf.write(path_r, y_r, sr)

        new_r = row.copy()
        new_r['file']                 = os.path.join("audio_degraded", fn_r).replace("\\", "/")
        new_r['version']              = 'degraded_rhythm'
        new_r['score_rythme_alt']     = degrade_score(row.get('score_rythme', 0), 0.3)
        new_r['score_musicalite_alt'] = row.get('score_musicalite', '')
        all_rows.append(new_r)

        # 2) Dégradé musical
        y_m = degrade_audio_musicality(y, sr)
        fn_m = f"{base_clean}__degraded_musicality.wav"
        path_m = os.path.join(DEGRADED_DIR, fn_m)
        sf.write(path_m, y_m, sr)

        new_m = row.copy()
        new_m['file']                 = os.path.join("audio_degraded", fn_m).replace("\\", "/")
        new_m['version']              = 'degraded_musicality'
        new_m['score_rythme_alt']     = row.get('score_rythme', '')
        new_m['score_musicalite_alt'] = degrade_score(row.get('score_musicalite', 0), 0.3)
        all_rows.append(new_m)

        print(f"✅ Dégradé créé pour {original_file}")

    except Exception as e:
        print(f"❌ Erreur traitement {original_file}: {e}")

# Réécriture du CSV avec tous les fichiers
with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print("🎉 Tous les fichiers ont été traités, metadata.csv mis à jour.")
