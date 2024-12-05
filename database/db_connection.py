from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import logging

db = SQLAlchemy()

def init_db(app):
    """
    Initializes the database with the given Flask app.
    
    Parameters:
    -----------
    app: Flask
        The Flask application instance to bind the database.

    Returns:
    --------
    None
    """
    try:
        # Inicializa la extensión SQLAlchemy con la aplicación Flask
        db.init_app(app)

        # Verifica la conexión con la base de datos al iniciar
        with app.app_context():
            engine = db.get_engine()
            connection = engine.connect()
            connection.close()
            app.logger.info("Database connection successful.")
    except OperationalError as e:
        app.logger.error(f"Database connection failed: {e}")
        raise RuntimeError("Failed to connect to the database. Check your configuration.") from e
