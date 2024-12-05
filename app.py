from flask import Flask, g, jsonify, request  
from werkzeug.exceptions import HTTPException  
from controllers.auth_controller import auth_bp
from controllers.spotify_controller import spotify_bp
from controllers.youtube_controller import youtube_bp
from controllers.migration_controller import migration_bp
from config import config
from database.db_connection import db, init_db
from flask_migrate import Migrate
from flask_talisman import Talisman
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger  
from prometheus_flask_exporter import PrometheusMetrics
from time import time
import os


def configure_logging(app):
    """
    Configures structured logging for the Flask application.

    Logs will be written to a rotating file or to stdout in JSON format.
    """
    # configure log level
    app.logger.setLevel(logging.INFO)

    # configure rotating file handler
    file_handler = RotatingFileHandler("app.log", maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    file_handler.setFormatter(formatter)

    # ddd the handler to the Flask logger
    app.logger.addHandler(file_handler)

    # redirect logs to stdout (useful for Render)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(stream_handler)

def register_error_handlers(app):
    """
    Registers global error handlers for the application.
    """
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled Exception: {e}")
        response = {"error": "An unexpected error occurred."}
        if isinstance(e, HTTPException):
            response["description"] = e.description
            return jsonify(response), e.code
        return jsonify(response), 500    


def add_timing_middleware(app):
    """
    set a middleware that tracks the response time for each incoming request.
    """
    @app.before_request
    def start_timer():
        g.start = time()

    @app.after_request
    def log_request(response):
        if hasattr(g, 'start'):
            duration = time() - g.start
            app.logger.info(f"Request took {duration:.4f} seconds")
        return response

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

    # use Flask-Prometheus to obtain server metrics.
    PrometheusMetrics(app)

    config_name = os.getenv("FLASK_ENV","default")
    # load the configuration from config.py.
    app.config.from_object(config[config_name])

    # configure logging
    configure_logging(app)

    # initialize the database with the app.
    init_db(app)

    Migrate(app, db)

    # security headers
    Talisman(app)

    # register a registers global error handlers for the application.
    register_error_handlers(app)

    # register a middleware that tracks the response time for each incoming request.
    add_timing_middleware(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(spotify_bp, url_prefix='/spotify')
    app.register_blueprint(youtube_bp, url_prefix='/youtube')
    app.register_blueprint(migration_bp, url_prefix="/migrate")
    
    return app

app = create_app()

if __name__ == "__main__":    
    app.logger.info("Starting the application")
    app.run(debug=False, host="0.0.0.0", port=5000)
    


