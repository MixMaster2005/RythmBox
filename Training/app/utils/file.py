import os
import time
import freesound
import requests

# Ton token Freesound ici (obtenu sur https://freesound.org/apiv2/apply/)
FREESOUND_API_KEY = "IK0R09x3ehatuPhtgPGWPMEi5YpLTRDjXtmXZkyl"

# Répertoire racine pour les sons
BASE_DIR = "./audio"
os.makedirs(BASE_DIR, exist_ok=True)

# Catégories sonores et mots-clés associés
CATEGORIES = {
    "guitar": ["electric guitar", "acoustic guitar", "guitar riff"],
    "drums": ["drum loop", "kick", "snare", "hi-hat"],
    "piano": ["piano melody", "piano chord", "grand piano"],
    "voice": ["vocal", "human voice", "spoken"],
    "ambient": ["ambience", "city sounds", "nature", "rain", "wind"],
    "sfx": ["explosion", "swoosh", "footsteps", "glass", "impact"],
    "synth": ["synth loop", "analog synth", "electronic pad"],
    "percussion": ["bongo", "conga", "percussion loop"],
}

# Nombre de sons à télécharger par catégorie
FILES_PER_CATEGORY = 15

# Initialisation du client
client = freesound.FreesoundClient()
client.set_token(FREESOUND_API_KEY, "token")

# Fonction de téléchargement
def download_preview(sound, dest_folder):
    try:
        preview_url = sound.previews.preview_hq_mp3
        filename = f"{sound.id}_{sound.name.replace(' ', '_')}.mp3"
        filepath = os.path.join(dest_folder, filename)
        if not os.path.exists(filepath):
            r = requests.get(preview_url)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"✅ {filename}")
        else:
            print(f"⏩ {filename} déjà téléchargé.")
    except Exception as e:
        print(f"❌ Erreur: {sound.id} → {e}")

# Boucle principale
for category, keywords in CATEGORIES.items():
    print(f"\n🔎 Téléchargement pour la catégorie: {category}")
    dest_folder = os.path.join(BASE_DIR, category)
    os.makedirs(dest_folder, exist_ok=True)

    downloaded = 0
    for keyword in keywords:
        if downloaded >= FILES_PER_CATEGORY:
            break
        results = client.text_search(query=keyword, fields="id,name,previews", page_size=10, sort="score")
        for sound in results:
            if downloaded >= FILES_PER_CATEGORY:
                break
            download_preview(sound, dest_folder)
            downloaded += 1
            time.sleep(0.3)  # pour éviter le throttling API

print("\n🎉 Téléchargement terminé. Les sons sont classés dans ./audio/")
