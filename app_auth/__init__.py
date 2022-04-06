from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from decouple import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # Google Cloud SQL (change this accordingly)
    PASSWORD = config("password")
    PUBLIC_IP_ADDRESS = config("public_ip_address")
    DBNAME = config("dbname")
    PROJECT_ID = config("project_id")
    INSTANCE_NAME = config("instance_name")

    # configuration
    app.config["SECRET_KEY"] = config("secret_key")
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f'mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .data_model import User, Insight

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
