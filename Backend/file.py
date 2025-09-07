import os

BASE_DIR = 'flask_app'

structure = {
    'app.py': """
from flask import Flask
from views.analyze_view import analyze_bp
from controllers.frontend_controller import frontend_bp

app = Flask(__name__, static_folder='static/dist')

# Register blueprints
app.register_blueprint(analyze_bp)
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
""",

    'services/model_service.py': """
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'rf_model.pkl')

class RandomForestModel:
    def __init__(self):
        self.categorical_features = ['genre', 'version']
        self.numerical_features = [
            'bpm', 
            'mfcc_1', 'mfcc_2', 'mfcc_3', 'mfcc_4', 'mfcc_5', 'mfcc_6', 'mfcc_7', 'mfcc_8', 'mfcc_9', 'mfcc_10',
            'mfcc_11', 'mfcc_12', 'mfcc_13',
            'chroma_1', 'chroma_2', 'chroma_3', 'chroma_4', 'chroma_5', 'chroma_6',
            'chroma_7', 'chroma_8', 'chroma_9', 'chroma_10', 'chroma_11', 'chroma_12',
            'zcr_mean'
        ]
        self.model = None
        self.is_trained = False

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.is_trained = True
        else:
            raise FileNotFoundError(f"No model file at {MODEL_PATH}")

    def predict(self, input_dict):
        if not self.is_trained:
            raise Exception("Model not loaded")
        df = pd.DataFrame([{
            'genre': input_dict.get('genre', 'unknown'),
            'version': input_dict.get('version', 'unknown'),
            'bpm': input_dict['bpm'],
            **{k: input_dict[k] for k in self.numerical_features if k in input_dict}
        }])
        preds = self.model.predict(df)
        return {
            'score_rythme': float(preds[0][0]),
            'score_musicalite': float(preds[0][1])
        }
""",

    'services/feature_service.py': """
import librosa
import numpy as np

def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    bpm, _ = librosa.beat.beat_track(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = np.mean(zcr)

    features = {
        'bpm': bpm,
    }

    for i, v in enumerate(mfcc_mean, start=1):
        features[f'mfcc_{i}'] = v
    for i, v in enumerate(chroma_mean, start=1):
        features[f'chroma_{i}'] = v
    features['zcr_mean'] = zcr_mean

    return features
""",

    'views/analyze_view.py': """
import os
from flask import Blueprint, request, jsonify
from services.feature_service import extract_audio_features
from services.model_service import RandomForestModel

analyze_bp = Blueprint('analyze', __name__)

model = RandomForestModel()
model.load_model()

@analyze_bp.route('/analyze', methods=['POST'])
def analyze_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    tmp_dir = os.path.join(os.path.dirname(__file__), '..', 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, file.filename)
    file.save(tmp_path)

    try:
        features = extract_audio_features(tmp_path)
        genre = request.form.get('genre', 'unknown')
        version = request.form.get('version', 'unknown')
        input_data = features.copy()
        input_data['genre'] = genre
        input_data['version'] = version

        prediction = model.predict(input_data)

        os.remove(tmp_path)
        return jsonify({
            'bpm': features['bpm'],
            'scores': prediction
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
""",

    'controllers/frontend_controller.py': """
import os
from flask import Blueprint, send_from_directory

frontend_bp = Blueprint('frontend', __name__, url_prefix='')

static_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist')

@frontend_bp.route('/', defaults={'path': ''})
@frontend_bp.route('/<path:path>')
def serve_react(path):
    if path != '' and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')
"""
}

def create_files():
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    for path, content in structure.items():
        full_path = os.path.join(BASE_DIR, path)
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created {full_path}")

if __name__ == "__main__":
    create_files()
    print(f"\nProject structure created inside '{BASE_DIR}' folder.")