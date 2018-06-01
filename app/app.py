# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask import render_template

from .reverse_proxied import ReverseProxied

__all__ = ('create_app', )


def create_app(config=None, app_name='simple_tjs', blueprints=None):
    app = Flask(app_name,
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'static')),
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
                )
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    app.config.from_object('app.config')
    local_cfg_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'local.cfg'))
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

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handlers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_DIR_PATH'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)
