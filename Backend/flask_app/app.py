from flask import Flask
from flask_cors import CORS  # <-- ajouté
from views.analyze_view import analyze_bp
from controllers.frontend_controller import frontend_bp

app = Flask(__name__, static_folder='static/dist')

# Activer CORS pour toute l'application
CORS(app)

# Register blueprints
app.register_blueprint(analyze_bp)
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    app.run(debug=False, port=5000)
