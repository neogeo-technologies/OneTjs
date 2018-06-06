# -*- coding: utf-8 -*-

from flask_script import Manager
import logging

from app import create_app

logging.basicConfig(level=logging.INFO)

manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config", required=False, help="config file")


if __name__ == "__main__":
    manager.run()
