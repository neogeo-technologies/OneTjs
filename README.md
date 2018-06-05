# README.md

## Installation

### Git Repository

Download the repository or clone it with:

`$ git clone https://github.com/neogeo-technologies/OneTjs.git`


### Virtual environment - Python 3

Install a python virtual environment:

    $ sudo apt-get install python3-venv
    $ python3 -m venv tjs-venv

Activate the virtual environment:

    $ source tjs-venv/bin/activate


### Requirements

Install the required python modules:

    (tjs-venv) $ cd OneTjs
    (tjs-venv) $ pip install -r requirements.txt


## Run the server

### ...using the Flask command

    (tjs-venv) $ flask run

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.


### ...using the manage.py script

    (tjs-venv) $ python manage.py runserver

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.


### ...using gunicorn

    (tjs-venv) $ gunicorn --bind 0.0.0.0:8000 app.wsgi:app


### ...using uwsgi

    (tjs-venv) $ uwsgi --socket 0.0.0.0:8000 --protocol=http -w app.wsgi:app
    

### ...using uwsgi and an ini file

    (tjs-venv) $ uwsgi --socket 0.0.0.0:8000 --protocol=http --ini uwsgi.ini

