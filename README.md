# OneTjs

[![Fiability](https://sonarqube.neogeo.fr/api/project_badges/measure?project=OneTjs&metric=reliability_rating)](https://sonarqube.neogeo.fr/dashboard?id=OneTjs)
[![Technical debt](https://sonarqube.neogeo.fr/api/project_badges/measure?project=OneTjs&metric=sqale_index)](https://sonarqube.neogeo.fr/dashboard?id=OneTjs)

OneTjs is a server implementing the Open Geospatial Consortium standard called "Table Joining Service".

## TABLE DES MATIÈRES
  - [Startup](#Startup)
    - [Prerequisites](#Prerequisites)
    - [Installation](#Installation)
    - [Configuration](#Configuration)
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

Python 3.5 or higher (PyYAML 4 needs at least Python 2.7 or Python 3.5).
The recommended (and the only supported) OS is Debian. 

Note that some frameworks (Bootstrap and JQuery for instance) are used via CDN (see app/templates/base.html for example). You therefore need an internet 
connexion in order to make these web pages fully fonctionnal.

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

Install OneTjs and the dependecies

    $ pip install -e .

You can also install directly through github (without a git clone before):

    $ pip install -e git+https://github.com/neogeo-technologies/OneTjs.git



#### Run the server using the Flask command

    (tjs-venv) $ FLASK_APP=onetjs flask run

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.

Note : make sure the flask command tool you use is the one located in your Python virtual environment.  
You may specify it:

    (tjs-venv) $ FLASK_APP=onetjs ../tjs-venv/bin/flask run
    

#### Running the server using the manage.py script

    (tjs-venv) $ python manage.py runserver

This command launches the Flask development server (Werkzeug).  
Do not use it for production.  
Default port: 5000.


#### Running the server using gunicorn

    (tjs-venv) $ gunicorn --bind 0.0.0.0:8000 app.wsgi:app


#### Running the server using uwsgi

    (tjs-venv) $ uwsgi --socket 0.0.0.0:8000 --protocol=http -w app.wsgi:app

#### Running the server using Apache and ModWSGI

Install Apache and mod_wsgi:

    apt update
    apt install apache2 libapache2-mod-wsgi-py3

Setup Apache to use the wsgi script:


    WSGIScriptAlias / /path/to/venv/src/onetjs/onetjs/wsgi_apache.py
    <Directory "/path/to/venv/src/onetjs/onetjs/">
        <Files "wsgi_apache.py">
            Require all granted
        </Files>
    </Directory>


### Configuration

The environment variable `ONETJS_CONFIG_FILE_PATH` is used for specifying a custom config file.
Example:

    (tjs-venv) $ export ONETJS_CONFIG_FILE_PATH=/path/to/settings.cfg
    (tjs-venv) $ gunicorn --bind 0.0.0.0:8000 app.wsgi:app

You may also create a `onetjs.cfg` file at the root of the app.  
For example, copy the `onetjs.example.cfg` file, set its name to `onetjs.cfg` and edit its content.

See the [docs for further details](./docs/configuration.md).

### Docker variables

If you don't override the `ONETJS_CONFIG_FILE_PATH` environment variable with your own file, you can use these environment variables to cofigure 
neTjs:

* `ONETJS_SECRET_KEY` (mandatory) used to enable flask sessions
* `ONETJS_ENV_DEV` set to 1 to enable development environement (debugtoolbar, logs...)
* `ONETJS_TESTING` set to 1 to enable logs and disable CSRF protection
* `ONETJS_DATA_DIR_PATH` to the path containing the data (by default set to /onetjs/data, remember to put this in a volume)
* `ONETJS_SERVER_NAME` the hostname (and optionaly the port), default is 'localhost.localdomain:8000'
* `ONETJS_SERVICE_ROOT_URL` the full url of the service, by default 'http://'+ ONETJS\_SERVER\_NAME

You should bind /onetjs/data/ and /onetjs to volumes.

WARNING configuration is only read on container startup. If you change services or configuration, you will have to restart the container

### Use

If you run the application user the test server, go to http://localhost:5000/

WARNING: ensure you use the hostname/port defined in you ONETJSi\_SERVER\_NAME/SERVER\_NAME variables, otherwise flask will answer with a 404

### Running tests

TODO



## Versions
See file [CHANGELOG](CHANGELOG.md)


## Autors
Neogeo Technologies

See the [contributing guide](./docs/contributing.md) to see how to give us some help.

Thanks to the [Région Hauts-de-France](http://www.hautsdefrance.fr/) for its support.
