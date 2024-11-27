from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.spotify_controller import spotify_bp
from controllers.youtube_controller import youtube_bp
from controllers.migration_controller import migration_bp
from config import Config
from database.db_connection import db

def create_app():
    """
    Configures and creates an instance of the Flask app with the necessary settings and extensions.

    Steps:
        - Loads configuration settings from config.py.
        - Initializes the database connection with db.init_app(app).
        - Registers blueprints for modular route handling:
            /auth: Routes related to authentication.
            /spotify: Routes for Spotify integrations.
            /youtube: Routes for YouTube integrations.
        - Creates database tables based on the models if they do not already exist using db.create_all().

        Returns: 
            Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)  # load the configuration from config.py.

    # initialize the database with the app.
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(spotify_bp, url_prefix='/spotify')
    app.register_blueprint(youtube_bp, url_prefix='/youtube')
    app.register_blueprint(migration_bp, url_prefix="/migrate")
    with app.app_context(): # creates all tables in the database if they do not exist.       
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":    
    app.run(debug=True)
    


