from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app() -> Flask:
    """
    Creates a flask app
    :return:
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Rgdw#&nI23$26Br7!'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Default page if not logged in
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id: str):
        return User.query.get(int(id))

    return app


def create_database(app: Flask) -> None:
    """
    Creates a new Database if there isn't one in the folder
    :param app: the flask app
    :return: None
    """
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("Created new Database")
