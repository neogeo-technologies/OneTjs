# -*- coding: utf-8 -*-

import os
import tempfile

temp_dir = tempfile.gettempdir()


class BaseConfig(object):
    """Base configuration."""
    SECRET_KEY = 'my_secret_key'
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DATA_DIR_PATH = "../data"


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = '1a4154e5ad05f8fbf361f4a019174378fb6f504668f3c0cc'
    DEBUG = False
    DEBUG_TB_ENABLED = False
