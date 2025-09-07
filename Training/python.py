import os
from pathlib import Path
from dotenv import load_dotenv
from freesound import FreesoundClient
from flask import Flask, render_template

# 1. Création structure dossier de projet Flask
project_root = Path(__file__).parent.resolve()
dirs_to_create = [
    "app",
    "app/static",
    "app/templates",
    "app/audio",
]

for d in dirs_to_create:
    path = project_root / d
    path.mkdir(parents=True, exist_ok=True)
print("[+] Structure de dossiers créée")

# 2. Création fichier .env pour la clé API (à éditer)
env_path = project_root / ".env"
if not env_path.exists():
    env_path.write_text("FREESOUND_API_KEY=TA_CLE_API_ICI\n")
    print("[+] Fichier .env créé, mets ta clé API dedans")

# 3. Chargement des variables d'environnement
load_dotenv(dotenv_path=env_path)

# 4. Récupération clé API
API_KEY = os.getenv("FREESOUND_API_KEY")
if not API_KEY or API_KEY == "TA_CLE_API_ICI":
    print("⚠️ Mets ta clé API dans le fichier .env avant de lancer ce script")
    exit(1)

# 5. Initialisation client Freesound
client = FreesoundClient()
client.set_token(API_KEY, "token")

# 6. Fonction récupération sons guitare
def download_guitar_sounds(limit=10):
    download_folder = project_root / "app/audio"
    results = client.text_search(
        query="guitar clean",
        filter='duration:[3 TO 10] license:"Creative Commons 0"',
        fields="id,name,previews,avg_rating",
        sort="rating_desc",
        page_size=limit,
    )
    print(f"🔍 {results.count} sons trouvés, téléchargement des {limit} premiers...")
    for sound in results:
        safe_name = f"{sound.id}_{sound.name}".replace("/", "_").replace(" ", "_")
        dest_path = download_folder / f"{safe_name}.mp3"
        if not dest_path.exists():
            print(f"⬇️ Téléchargement : {safe_name}.mp3")
            sound.retrieve_preview(str(download_folder), f"{safe_name}.mp3")
        else:
            print(f"✅ Déjà téléchargé : {safe_name}.mp3")

# 7. Créer fichier Flask minimaliste dans app/__init__.py
flask_init_path = project_root / "app" / "__init__.py"
if not flask_init_path.exists():
    flask_init_path.write_text(
        '''
import os
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)
    app.config['AUDIO_FOLDER'] = os.path.join(app.root_path, "audio")

    @app.route("/")
    def index():
        # Liste fichiers audio dans audio/
        audio_files = []
        for f in os.listdir(app.config['AUDIO_FOLDER']):
            if f.endswith(".mp3") or f.endswith(".wav"):
                audio_files.append(f)
        return render_template("index.html", audio_files=audio_files)

    return app
        '''
    )
    print("[+] app/__init__.py créé")

# 8. Créer template minimaliste app/templates/index.html
template_path = project_root / "app" / "templates" / "index.html"
if not template_path.exists():
    template_path.write_text(
        '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8" />
    <title>Play & Learn - Audio Library</title>
</head>
<body>
    <h1>Bibliothèque d'audios téléchargés</h1>
    <ul>
    {% for audio in audio_files %}
        <li>{{ audio }}</li>
    {% else %}
        <li>Aucun audio disponible</li>
    {% endfor %}
    </ul>
</body>
</html>
        '''
    )
    print("[+] Template index.html créé")

# 9. Créer un runner Flask pour dev
runner_path = project_root / "run.py"
if not runner_path.exists():
    runner_path.write_text(
        '''
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
        '''
    )
    print("[+] run.py créé")

# 10. Lancer le téléchargement
download_guitar_sounds(limit=10)
print("[✅] Setup terminé. Lance `python run.py` pour démarrer le serveur Flask.")
