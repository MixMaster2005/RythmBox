# RythmBox

RythmBox est une plateforme d'entraînement musical basée sur l'IA, permettant d'analyser, télécharger et explorer des sons, avec une interface web moderne.

## Structure du projet

```
RythmBox/
├── Backend/
│   ├── flask_app/
│   │   ├── app.py
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── services/
│   │   ├── views/
│   │   ├── static/
│   │   ├── tmp/
│   │   └── requirements.txt
│   └── monenv310/
├── Frontend/
│   └── melody-coach/
│       ├── index.html
│       ├── package.json
│       └── ...
├── Training/
│   ├── python.py
│   ├── run.py
│   ├── app/
│   └── freesound-python/
└── .gitignore
```

## Installation

### Backend

1. Aller dans `Backend/flask_app`
2. Installer les dépendances Python :
   ```sh
   pip install -r requirements.txt
   ```
3. Lancer le serveur Flask :
   ```sh
   python app.py
   ```

### Frontend

1. Aller dans `Frontend/melody-coach`
2. Installer les dépendances Node.js :
   ```sh
   npm install
   ```
3. Lancer le serveur de développement :
   ```sh
   npm run dev
   ```

### Training

1. Aller dans `Training`
2. Renseigner la clé API Freesound dans `.env` :
   ```
   FREESOUND_API_KEY=TA_CLE_API_ICI
   ```
3. Lancer le script de téléchargement :
   ```sh
   python python.py
   ```

## Fonctionnalités

- Téléchargement automatique de sons depuis Freesound (`Training/python.py`)
- API Flask pour l'analyse et la gestion des fichiers audio (`Backend/flask_app/app.py`)
- Interface web moderne avec Melody Coach (`Frontend/melody-coach`)

## Dépendances principales

- Flask, Flask-CORS
- Freesound Python Client
- Node.js, React, TailwindCSS (Frontend)