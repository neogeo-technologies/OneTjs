# README.md

##Description##

OneTjs is a server implementing the Open Geospatial Consortium standard called "Table Joining Service".

It implements the Data Access operations:
*GetCapabilities
*DescribeFrameworks
*DescribeDatasets
*DescribeData
*GetData

Unsupported options:
* HTTP POST requests
* SOAP requests
* WSDL
* multilinguism
* "documentation" attibute
* some GetCapabilities request parameters: language, AcceptFormats, Sections and updateSequence
* one DescribeFrameworks request parameters: language
* some GetData request parameters: language, LinkageKeys , FilterColumn, FilterValue, XSL, Aid

OneTjs is able to read CSV and Excel data files stored in the local file system.

OneTjs is not yet able to read table (nor views) from SQL databases (this a planned feature).


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

Note : make sure the flask command tool you use is the one located in your Python virtual environment.  
You may specify it:

    (tjs-venv) $ ../tjs-venv/bin/flask run
    

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
