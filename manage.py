from flask_migrate import Migrate, upgrade, init, migrate
from app import create_app
from database.db_connection import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    import sys    
    from flask.cli import FlaskGroup

    cli = FlaskGroup(app)

    # Comandos personalizados de migración (opcional)
    @cli.command("db_init")
    def db_init():
        """Inicializa el directorio de migraciones."""
        init()

    @cli.command("db_migrate")
    def db_migrate():
        """Genera un script de migración basado en cambios detectados."""
        migrate()

    @cli.command("db_upgrade")
    def db_upgrade():
        """Aplica las migraciones a la base de datos."""
        upgrade()

    cli.main(args=sys.argv[1:])
