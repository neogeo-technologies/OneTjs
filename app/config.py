# -*- coding: utf-8 -*-

import os

class BaseConfig(object):
    SECRET_KEY = "app secret key, change me please"

    DEBUG = False
    DEBUG_TB_ENABLED = False
    TESTING = False

    BCRYPT_LOG_ROUNDS = 13

    WTF_CSRF_ENABLED = True

    DATA_DIR_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, "data")
    )
    LOG_DIR_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, "log")
    )


class DevConfig(object):
    DEBUG = True
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PANELS = (
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    )


class TestConfig(object):
    TESTING = True
    WTF_CSRF_ENABLED = False
