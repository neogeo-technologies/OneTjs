# -*- coding: utf-8 -*-

from flask_script import Manager

from app import app

import logging
logging.basicConfig(level=logging.INFO)

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
