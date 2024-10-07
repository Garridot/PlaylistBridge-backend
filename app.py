from flask import Flask
from controllers.spotify_controller import spotify_bp
from controllers.youtube_controller import youtube_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Registrar los Blueprints
app.register_blueprint(spotify_bp, url_prefix='/spotify')
app.register_blueprint(youtube_bp, url_prefix='/youtube')

if __name__ == "__main__":
    app.run(debug=True)
    

