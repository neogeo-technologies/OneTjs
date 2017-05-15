# -*- coding: utf-8 -*-

import os

SECRET_KEY = 'change me please'
DEBUG = True
BCRYPT_LOG_ROUNDS = 13
WTF_CSRF_ENABLED = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
DATA_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "data"))
LOG_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "log"))
