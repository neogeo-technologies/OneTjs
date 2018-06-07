# -*- coding: utf-8 -*-

from flask_script import Manager
import logging

from app.app import create_app

logging.basicConfig(level=logging.INFO)

manager = Manager(create_app)

if __name__ == "__main__":
    manager.run()
