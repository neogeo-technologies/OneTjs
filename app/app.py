# -*- coding: utf-8 -*-

import os
import sys
import logging

from flask import Flask
from flask import render_template

from werkzeug.contrib.fixers import ProxyFix

__all__ = ("create_app",)


def create_app(config=None, app_name="onetjs", blueprints=None):
    app = Flask(
        app_name,
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.path.pardir, "static")
        ),
        template_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "templates")
        ),
    )
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config.from_object("app.config")
    local_cfg_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, "local.cfg")
    )
    app.config.from_pyfile(local_cfg_file_path, silent=True)

    if config:
        app.config.from_pyfile(config)

    app.init_success = False
    from .models import services_manager

    app.services_manager = services_manager.ServicesManager(app)

    blueprints_fabrics(app)
    extensions_fabrics(app)
    # see https://github.com/xen/flask-project-template

    configure_logging(app)
    error_pages(app)

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
        return render_template("error.html", error_code=error.code), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("error.html", error_code=error.code), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error.html", error_code=error.code), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template("error.html", error_code=error.code), 405

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("error.html", error_code=error.code), 500


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    log_format = "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    log_levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }

    # Set info level on logger
    log_level = log_levels["INFO"]
    if app.debug or app.testing:
        log_level = log_levels["DEBUG"]
    if "LOG_LEVEL" in app.config:
        log_level = log_levels[app.config["LOG_LEVEL"]]

    if "LOG_FILE" in app.config:
        logging.basicConfig(
            level=log_level,
            datefmt=date_format,
            format=log_format,
            filename=app.config["LOG_FILE"],
        )
    else:
        logging.basicConfig(
            level=log_level, datefmt=date_format, format=log_format, stream=sys.stdout
        )

    app.logger.debug("Logging initialized")
