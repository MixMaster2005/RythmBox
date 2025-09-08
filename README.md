# 🎵 RythmBox — Plateforme d’entraînement musical IA

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)

## 📝 Description

RythmBox est une plateforme d’entraînement musical basée sur l’IA.  
Elle permet d’analyser, télécharger et explorer des sons avec une interface web moderne.

## 📂 Structure du projet

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

- **Backend** : API Flask pour l’analyse et la gestion audio.
- **Frontend** : Interface React + TailwindCSS moderne.
- **Training** : Scripts Python pour l’entraînement et l’intégration Freesound.

## 🚀 Installation

### Backend

```sh
cd Backend/flask_app
pip install -r requirements.txt
python app.py
```

### Frontend

```sh
cd Frontend/melody-coach
npm install
npm run dev
```

### Training

```sh
cd Training
# Ajouter la clé API dans .env
FREESOUND_API_KEY=TA_CLE_API_ICI
python python.py
```

## 🎯 Fonctionnalités

- Téléchargement automatique de sons depuis Freesound.
- API Flask pour l’analyse et la gestion audio.
- Interface React + TailwindCSS moderne.

## 📦 Dépendances principales

- **Backend** : Flask, Flask-CORS, Freesound Client.
- **Frontend** : Node.js, React, TailwindCSS.
- **Training** : Python,