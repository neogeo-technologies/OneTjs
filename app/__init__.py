# -*- coding: utf-8 -*-

import logging
import os

from flask import Flask
from flask import render_template
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

logging.basicConfig(level=logging.INFO)

app = Flask(
    __name__,
    template_folder='./templates',
    static_folder='./static',
)

app_settings = os.getenv('APP_SETTINGS', 'app.config.DevelopmentConfig')
app.config.from_object(app_settings)
app.init_success = False


bcrypt = Bcrypt(app)

toolbar = DebugToolbarExtension(app)
bootstrap = Bootstrap(app)

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


from app.models import services_manager

app.services_manager = services_manager.ServicesManager()

# Blueprints
from app.tjs.views import tjs_blueprint
from app.public_pages.views import public_blueprint
app.register_blueprint(tjs_blueprint)
app.register_blueprint(public_blueprint)
