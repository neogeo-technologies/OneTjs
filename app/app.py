# -*- coding: utf-8 -*-

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask import render_template
from flask.logging import default_handler

from .reverse_proxied import ReverseProxied

from . import __version__

__all__ = ("create_app",)


def create_app(app_name="onetjs", blueprints=None):

    app = Flask(
        app_name,
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir, "static")
        ),
        template_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "templates")
        ),
    )

    with app.app_context():
        app.wsgi_app = ReverseProxied(app.wsgi_app)

        # Default config
        app.config.from_object("app.config.BaseConfig")

        # Local config file set via the ONETJS_CONFIG_FILE_PATH environment variable or a onetjs.cfg file
        local_cfg_file_path = os.environ.get(
            "ONETJS_CONFIG_FILE_PATH",
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.path.pardir, "onetjs.cfg")
            ),
        )
        app.config.from_pyfile(local_cfg_file_path, silent=True)

        # Some adjustments for development and testing configs
        if app.config["ENV"] == "development":
            app.config.from_object("app.config.DevConfig")

        if app.config["TESTING"] == True:
            app.config.from_object("app.config.TestConfig")

        app.init_success = False
        from .models import services_manager

        app.services_manager = services_manager.ServicesManager(app)

        blueprints_fabrics(app)
        extensions_fabrics(app)
        # see https://github.com/xen/flask-project-template

        configure_logging(app)
        error_pages(app)
        app.version = __version__

    return app


def blueprints_fabrics(app):
    """Configure blueprints in views."""

    from .tjs.views import tjs_blueprint
    from .public_pages.views import public_blueprint

    app.register_blueprint(tjs_blueprint)
    app.register_blueprint(public_blueprint)

    from .tjs.views import tjs_geoclip_blueprint

    app.register_blueprint(tjs_geoclip_blueprint)


def extensions_fabrics(app):
    # see https://github.com/xen/flask-project-template

    from flask_bcrypt import Bcrypt

    bcrypt = Bcrypt()
    bcrypt.init_app(app)

    from flask_bootstrap import Bootstrap

    bootstrap = Bootstrap()
    bootstrap.init_app(app)

    from flask_debugtoolbar import DebugToolbarExtension

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)


def error_pages(app):
    # HTTP error pages definitions
    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("error.html", error_code=401), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("error.html", error_code=403), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error.html", error_code=404), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template("error.html", error_code=405), 405

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("error.html", error_code=500), 500


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    log_format = app.config.get(
        "LOGGING_FORMAT",
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    )
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    log_formatter = logging.Formatter(log_format, date_format)
    log_level = log_levels.get(app.config["LOGGING_LEVEL"], log_levels["INFO"])

    if "LOGGING_LOCATION" in app.config:

        log_file_name = app.config["LOGGING_LOCATION"]
        parent_dir = os.path.abspath(os.path.join(log_file_name, os.pardir))

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        log_handler = RotatingFileHandler(
            filename=log_file_name, maxBytes=10000, backupCount=5
        )
        log_handler.setLevel(log_level)
        log_handler.setFormatter(log_formatter)
        app.logger.addHandler(log_handler)

        app.logger.debug("Logging initialized...")
        app.logger.debug(
            "... log file location: {}".format(app.config.get("LOGGING_LOCATION"))
        )
    else:
        default_handler.setLevel(log_level)
        default_handler.setFormatter(log_formatter)
        log_handler = logging.basicConfig(stream=sys.stdout)
        app.logger.debug("Logging initialized...")
        app.logger.debug("... default flask logging handler")
