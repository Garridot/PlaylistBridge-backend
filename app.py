from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.spotify_controller import spotify_bp
from controllers.youtube_controller import youtube_bp
from config import Config
from database.db_connection import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Carga tu configuración desde config.py

    # Inicializa la base de datos con la app
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(spotify_bp, url_prefix='/spotify')
    app.register_blueprint(youtube_bp, url_prefix='/youtube')

    with app.app_context():
        # Crea todas las tablas en la base de datos si no existen
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    


