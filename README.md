# README.md

##Description

OneTjs is a server implementing the Open Geospatial Consortium standard called "Table Joining Service".

One of the main objectives of OneTjs is to provide a simple datasource for the Céoclip mapping tool
(https://www.geoclip.fr/?lang=en).

It implements the Data Access operations:
* GetCapabilities
* DescribeFrameworks
* DescribeDatasets
* DescribeData
* GetData

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


## License and contributors

OneTjs is mainly developed by Neogeo Technologies under the following license:  
Apache License 2.0

> Copyright 2018 Neogeo Technologies  
>  
> Licensed under the Apache License, Version 2.0 (the "License");  
> you may not use this file except in compliance with the License.  
> You may obtain a copy of the License at  
>  
> http://www.apache.org/licenses/LICENSE-2.0
>  
> Unless required by applicable law or agreed to in writing, software  
> distributed under the License is distributed on an "AS IS" BASIS,  
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
> See the License for the specific language governing permissions and  
> limitations under the License.


Thanks to the [Région Hauts-de-France](http://www.hautsdefrance.fr/) for its support.


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
