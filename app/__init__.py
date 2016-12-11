# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

import os

import logging

logging.basicConfig(level=logging.INFO)

app = Flask(
    __name__,
    template_folder='./templates',
    static_folder='./static'
)
app_settings = os.getenv('APP_SETTINGS', 'app.config.DevelopmentConfig')
app.config.from_object(app_settings)

login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
admin = Admin(app, template_mode='bootstrap3')

from app.models import User

login_manager.login_view = "login"
login_manager.login_message_category = 'danger'


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


@app.errorhandler(401)
def error_page(error):
    return render_template("error.html", error=error), 401


@app.errorhandler(403)
def error_page(error):
    return render_template("error.html", error=error), 403


@app.errorhandler(404)
def error_page(error):
    return render_template("error.html", error=error), 404


@app.errorhandler(500)
def error_page(error):
    return render_template("error.html", error=error), 500


# Blueprints
from app.login.views import login_blueprint
from app.tjs.views import tjs_blueprint
from app.admin_pages.views import admin_blueprint
from app.public_pages.views import public_blueprint
app.register_blueprint(login_blueprint)
app.register_blueprint(tjs_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(public_blueprint)
