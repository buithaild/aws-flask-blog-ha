import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://bloguser:blogpass@localhost:5432/blogdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from . import models  # noqa: F401
    from .routes import blog
    app.register_blueprint(blog)

    with app.app_context():
        db.create_all()  # Lab only: use migrations in production
    return app
