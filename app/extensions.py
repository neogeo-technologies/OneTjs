# -*- coding: utf-8 -*-

from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

bcrypt = Bcrypt()

bootstrap = Bootstrap()

toolbar = DebugToolbarExtension()

# see https://github.com/xen/flask-project-template/blob/master/project/extensions.py
# from flask_mail import Mail
# mail = Mail()
#
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
#
# from flask_flatpages import FlatPages
# pages = FlatPages()
#
# import flask_restless
# manager = flask_restless.APIManager()
#
# from flask_login import LoginManager
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
#
# from flask_babel import Babel
# babel = Babel()
#
# from flask_migrate import Migrate
# migrate = Migrate()
#
# from flask_wtf.csrf import CsrfProtect
# csrf = CsrfProtect()
#
# from flask_cache import Cache
# cache = Cache()
#
# from celery import Celery
# celery = Celery()