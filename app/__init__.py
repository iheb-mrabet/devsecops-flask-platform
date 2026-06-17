from pathlib import Path

from flask import Flask

from .config import Config
from .db import close_db, init_db
from .routes import main


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(close_db)
    app.register_blueprint(main)

    with app.app_context():
        init_db()

    return app
