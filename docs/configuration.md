# Configuration

At present, OneTjs can only be configured via various config files (there is no tool to ease the configuration 
process).

4 levels of config files must be used:
* onetjs.cfg: cfg file (.ini syntax) used to configure the options at app level
* services.yml: YAML file used for declaring your services
* frameworks.yml: YAML files for declaring the frameworks used by the datasets of each service
* what_ever_you_want.yml: YAML files for declaring the published datasets

The term "spatial framework" (framework for short in the TJS documentation) is defined in the TJS standard:
> a GIS representation, either point, line, or polygon, of any collection of physical or conceptual geographic objects. 
Municipalities, postal code areas, telephone area codes, ecoregions, watersheds, road segments, fire stations, and 
lighthouses are all examples of spatial frameworks.

Please note that OneTjs has no idea of the geometries of the items composing a framework since it only implements the 
Data access set of TJS operations. Therefore, the spatial joining operation (if needed) is delegated to the TJS client
application.

## App configuration

The default file for the app level configuration is onetjs.cfg. By default it should be located where the 
onetjs.example.cfg file is located. To create one follow these steps:
* copy the `onetjs.example.cfg` file
* set its name to `onetjs.cfg`
* edit its content (don't forget to change the secret key)

Example of customized config file:

```
SECRET_KEY = 'my new secret key'
ENV = 'production'
```

You may find useful to look at the Flask configuration documention:  
http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values

The name and location of this cfg file may be specified using the following environment variable: 
`ONETJS_CONFIG_FILE_PATH`.

    $ export ONETJS_CONFIG_FILE_PATH=/path/to/settings.cfg

If such a file is not provided to the app, the parameters defined in the app.config.BaseConfig class is applied by 
OneTjs.

## Services

The name of the configuration file for services must be `services.yml`.  
This file could be located in the directory referenced by the configuration parameter `DATA_DIR_PATH`. If this 
parameter is not set, OneTjs looks for it in its own file tree. If more than one services.yml are found, OneTjs uses 
the first file found.

Typical services.yml structure:

```yaml
# services
---
the_name_of_your_service:
  activated:         yes
  data_dir_path:     /the/path/to/a/directory/containing/your/datasets
  title:             The service title
  abstract:          Some kind of description of the service
  keywords:
                     - keyword1
                     - keyword2
                     - and so on
  service_provider:
    organization:    Name of the orgonization providing the service
    web_site:        https://acme.net
    contact_email:   contact@acme.net
  tjs_versions:
                     - 1.0
  languages:
                     - en
                     - fr
```

Each OneTjs deploiement may provide more that one TJS end-point. You may then have multiple instances of this block in 
your configuration file.

Please, note that whitespace indentation defines the structure of any YAML file. So, you should take care of not 
messing up the indentation of OneTjs configuration files.

**`the_name_of_your_service`**:
this is an identifier, not a natural language name. Limit yourself to lowercase letters, 
numbers and underscores. Do not use any kind of whitespaces and exotic caracters. This 
name will appear in the URL of the TJS end-points.

**`activated`**:
flag indicating if the TJS service is available or not (yes or no). Use it for deactivating temporarily the service. 

**`data_dir_path`**:
the path to the directory containing the declaration of the frameworks and datasets 
provided by this service.

**`title`**:
The service title. Something in natural language.

**`abstract`**:
A description fo the service. Something in natural language. Usually much longer than the title.

**`keywords`**:
List of keywords describing the service. Keywords are expressed in natural language.

**`service_provider/organization`**:
The name of the organization providing this service.

**`service_provider/web_site`**:
The complete URL of the web site of the organization.

**`service_provider/contact_email`**:
An email address for any contact related with this service. Avoid nominative email address.

**`tjs_versions`**:
List of the TJS versions implemented by OneTjs. Only one version of TJS exists: 1.0. Just leave 1.0.

**`languages`**:
Multilinguism is not yet supported by OneTjs. At present, you should declare the language you use in your datasets and
in the natural language fields of the OneTjs configuration files. Use a two letter code for the language.

Please, note that almost all these parameters are inserted in the GetCapabilities response produced by OneTjs. Please, 
refer to the OGC OWS Common specification, TJS specification and INSPIRE Technical Guidance for any additional 
information related to these parameters.

This is not the case for following parameters:
* name of the service: used for defining the URL of the service TJS end-points. This URL is used for computing the URL 
of each TJS operation end-point which appears in the GetCapabilities response
capabilities for documenting the 
* `activated`: only used by OneTjs in order to know if the service should be activated at startup
* `data_dir_path`: only used be OneTjs in order to find the configuration files for the service frameworks and datasets

## Frameworks

Not yet documented.


## Datasets

Not yet documented.

