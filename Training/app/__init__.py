import os
from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for
import csv
import librosa

CSV_PATH = os.path.join(os.path.dirname(__file__), "metadata.csv")

def create_app():
    app = Flask(__name__)
    app.config['AUDIO_FOLDER'] = os.path.join(app.root_path, "audio")

    if not os.path.exists(app.config['AUDIO_FOLDER']):
        os.makedirs(app.config['AUDIO_FOLDER'])

    def get_all_audio_files(root_folder):
        audio_files = []
        for dirpath, _, filenames in os.walk(root_folder):
            for f in filenames:
                # Corrige automatiquement les fichiers du type .wav.mp3
                if f.endswith(".wav.mp3"):
                    old_path = os.path.join(dirpath, f)
                    new_filename = f.replace(".wav.mp3", ".mp3")
                    new_path = os.path.join(dirpath, new_filename)
                    os.rename(old_path, new_path)
                    f = new_filename  # mets à jour le nom
                elif f.endswith(".mp3") or f.endswith(".wav"):
                    relative_path = os.path.relpath(os.path.join(dirpath, f), root_folder).replace("\\", "/")
                    audio_files.append(relative_path)
        audio_files.sort()
        return audio_files


    def load_metadata():
        data = {}
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data[row['file']] = row
        return data

    def estimate_bpm(audio_path):
        try:
            y, sr = librosa.load(audio_path, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            if hasattr(tempo, '__len__'):  # Si c'est un array
                tempo = float(tempo[0])
            return round(float(tempo))
        except Exception as e:
            print(f"Erreur BPM pour {audio_path}: {e}")
            return ""

    @app.route("/", methods=["GET"])
    def index():
        audio_files = get_all_audio_files(app.config['AUDIO_FOLDER'])
        existing_data = load_metadata()

        # Mise à jour automatique du bpm si absent dans metadata
        for audio_file in audio_files:
            meta = existing_data.get(audio_file, {})
            if not meta.get('bpm'):
                full_path = os.path.join(app.config['AUDIO_FOLDER'], audio_file)
                bpm_estimated = estimate_bpm(full_path)
                if bpm_estimated:
                    meta['bpm'] = str(bpm_estimated)
                    existing_data[audio_file] = meta

        # Sauvegarde automatique des bpm estimés
        if existing_data:
            fieldnames = ['file', 'genre', 'bpm', 'score_rythme', 'score_musicalite', 'commentaire']
            rows = []
            for f in audio_files:
                row = existing_data.get(f, {key: '' for key in fieldnames})
                row['file'] = f
                rows.append(row)
            with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        # Trouve le premier fichier sans metadata complète (genre ou score manquant)
        start_index = 0
        for i, file in enumerate(audio_files):
            meta = existing_data.get(file, {})
            if not meta.get('genre') or not meta.get('score_rythme') or not meta.get('score_musicalite'):
                start_index = i
                break
        else:
            return "Tu as terminé la revue de tous les audios. Merci !"

        index = int(request.args.get("index", start_index))
        if index >= len(audio_files):
            return "Tu as terminé la revue de tous les audios. Merci !"

        file = audio_files[index]
        meta = existing_data.get(file, {})
        return render_template("index.html", audio=file, meta=meta, index=index, total=len(audio_files))

    @app.route('/save_metadata', methods=['POST'])
    def save_metadata():
        data = request.form
        file = data['file']
        rows = []
        fieldnames = ['file', 'genre', 'bpm', 'score_rythme', 'score_musicalite', 'commentaire']
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        found = False
        for row in rows:
            if row['file'] == file:
                for key in fieldnames[1:]:
                    row[key] = data.get(key, '')
                found = True
                break
        if not found:
            new_row = {key: data.get(key, '') for key in fieldnames}
            rows.append(new_row)

        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        next_index = int(data.get('index', 0)) + 1
        return redirect(url_for('index', index=next_index))


    @app.route("/audio/<path:filename>")
    def serve_audio(filename):
        full_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
        if os.path.exists(full_path):
            return send_from_directory(app.config['AUDIO_FOLDER'], filename)
        else:
            abort(404)

    return app
