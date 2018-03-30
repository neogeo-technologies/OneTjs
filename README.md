# README.md

## Installation

### Virtual environment - Python 3


Create a project folder:

    $ mkdir tjs-server
    $ cd tjs-server

Install a python virtual environment:

    $ sudo apt-get install python3-venv
    $ python3 -m venv tjs-venv

Activate the virtual environment:

    $ cd tjs-venv
    $ . bin/activate


### Git Repository

Download the repository or clone it with:
`$ git clone git@github.com:neogeo-technologies/simple-tjs.git`


### Requirements

Install the required python modules:

    (tjs-venv) $ pip install -r /tjs/requirements.txt


### Run server

    (tjs-venv) $ cd simple-tjs-master
    (tjs-venv) $ python manage.py runserver

The server should run on port 5000.
