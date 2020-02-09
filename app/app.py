# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask import render_template

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
