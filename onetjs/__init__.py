# -*- coding: utf-8 -*-

__version__ = "0.7.1"
__description__ = "TJS server"

from onetjs.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run()
