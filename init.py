from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from passwords import *
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()
def create_app(): 
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Secret_Key_Pass 
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from views import views
    from auth import auth
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from models import User, Post, Comment, Like

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # NOTE THIS IS FOR THE FLASK email authentication:
    app.config["MAIL_SERVER"] = 'smtp.gmail.com'
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = emailName
    app.config["MAIL_PASSWORD"] = emailPassword
    app.config["MAIL_DEFAULT_SENDER"] = 'your_email@example.com'
    mail.init_app(app)
    
    return app 


#def create_database(app):
   # if not path.exists("BLOGPAGE/"+ DB_NAME):
   #     db.create_all(app=app)
   #     print("Created Database!")


def create_database(app):
    db_path = path.join(app.root_path,"blogpage",DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("Created Database!")