# OneTjs

[![Fiabilité](https://sonarqube.neogeo.fr/api/project_badges/measure?project=onetjs&metric=reliability_rating)](https://sonarqube.neogeo.fr/dashboard?id=onetjs)
[![Dette Technique](https://sonarqube.neogeo.fr/api/project_badges/measure?project=onetjs&metric=sqale_index)](https://sonarqube.neogeo.fr/dashboard?id=onetjs)

OneTjs is a server implementing the Open Geospatial Consortium standard called "Table Joining Service".

## TABLE DES MATIÈRES
  - [Startup](#Startup)
    - [Prerequisites](#Prerequisites)
    - [Installation](#Installation)
    - [Use](#Use)
    - [Running tests](#Running-tests)
  - [Versions](#Versions)
  - [Autors](#Autors)

---

## Startup

One of the main objectives of OneTjs is to provide a simple datasource for the Géoclip mapping tool
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

OneTjs is able to read data from:
* data files stored in the local file system: CSV and XLS files
* MySQL and PostgreSQL databases

### Prerequisites

Python 3.5 ou supérieur (PyYAML 4 needs at least Python 2.7 or Python 3.5)
Debian 

### Installation

Download the repository or clone it with:

```
$ git clone https://github.com/neogeo-technologies/OneTjs.git
```

Install a python virtual environment:

    $ sudo apt-get install python3-venv
    $ python3 -m venv tjs-venv

Activate the virtual environment:

    $ source tjs-venv/bin/activate



#### Run the server using the Flask command

    (tjs-venv) $ flask run

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.

Note : make sure the flask command tool you use is the one located in your Python virtual environment.  
You may specify it:

    (tjs-venv) $ ../tjs-venv/bin/flask run
    

#### Running the server using the manage.py script

    (tjs-venv) $ python manage.py runserver

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.


#### Running the server using gunicorn

    (tjs-venv) $ gunicorn --bind 0.0.0.0:8000 app.wsgi:app


#### Running the server using uwsgi

    (tjs-venv) $ uwsgi --socket 0.0.0.0:8000 --protocol=http -w app.wsgi:app

#### Requirements

Install the required python modules:

    (tjs-venv) $ cd OneTjs
    (tjs-venv) $ pip install -r requirements.txt

Note that some frameworks (Bootstrap and JQuery for instance) are used via CDN (see app/templates/base.html for example). You therefore need an internet 
connexion in order to make these web pages fully fonctionnal.


### Configuration

The environment variable `ONETJS_CONFIG_FILE_PATH` is used for specifying a custom config file.
Example:

    (tjs-venv) $ export ONETJS_CONFIG_FILE_PATH=/path/to/settings.cfg
    (tjs-venv) $ gunicorn --bind 0.0.0.0:8000 app.wsgi:app

You may also create a `onetjs.cfg` file at the root of the app.  
For example, copy the `onetjs.example.cfg` file, set its name to `onetjs.cfg` and edit its content.

See the [docs for further details](./docs/configuration.md).

### Use


### Running tests

TODO



## Versions
Voir le fichier [CHANGELOG](CHANGELOG.md)


## Autors
Neogeo Technologies

See the [contributing guide](./docs/contributing.md) to see how to give us some help.

Thanks to the [Région Hauts-de-France](http://www.hautsdefrance.fr/) for its support.
