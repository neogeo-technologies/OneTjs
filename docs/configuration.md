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
DATA_DIR_PATH = ''
SERVER_NAME = 'my.domain.org:5000'
TJS_SERVICE_ROOT_URL = 'https://' + SERVER_NAME
```

* `DATA_DIR_PATH`: path to the directory containing the configuration of the services, frameworks, datasets...
* `SERVER_NAME`: server name (domain and port)
* `TJS_SERVICE_ROOT_URL`: url to the root of all TJS services

You may find useful to look at the Flask configuration documention:  
http://flask.pocoo.org/docs/1.0/config/#builtin-configuration-values

The name and location of this cfg file may be specified using the following environment variable:
`ONETJS_CONFIG_FILE_PATH`.

    $ export ONETJS_CONFIG_FILE_PATH=/path/to/settings.cfg

If such a file is not provided to the app, the parameters defined in the app.config.BaseConfig class is applied by
OneTjs.


Typical data file tree:
```
data
│── services.yml
│── service_a
│   │── frameworks.yml
│   │── dataset_a1
│   │    │── dataset_a1_1.csv
│   │    │── dataset_a1_1.yml
│   │    │── dataset_a1_2.xls
│   │    └── dataset_a1_2.yml
│   └── dataset_a2
│       └── dataset_a2_1.yml
│── service_b
│   │── frameworks.yml
│   └── dataset_b1
│       └── ...
└── ...
```

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
    organization:    Name of the organization providing the service
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

Please, note that almost all these parameters are inserted in the GetCapabilities
response produced by OneTjs. Please,
refer to the OGC OWS Common specification, TJS specification and INSPIRE Technical
Guidance for any additional information related to these parameters.

This is not the case for following parameters:
* name of the service: used for defining the URL of the service TJS end-points. This URL is used for computing the URL
of each TJS operation end-point which appears in the GetCapabilities response
capabilities for documenting the
* `activated`: only used by OneTjs in order to know if the service should be activated at startup
* `data_dir_path`: only used be OneTjs in order to find the configuration files for the service frameworks and datasets

## Frameworks

The name of the configuration file for services must be *frameworks.yml*.
Each service could have its own frameworks configuration file, located in the service folder.

Typical frameworks.yml structure:

```yaml
# frameworks
---
framework_name:
  uri:               framework_URI
  organization:      Name of the organization providing the framework
  title:             Framework title
  abstract:          Some kind of description of the framework
  version:           Version identifier for this framework
  start_date:        (optional) Start of a time period to which the framework or dataset applies.
  reference_date:    The date to which the framework dataset applies.
  key_col:
    name:            Name of the field that have to join to the geographic data
    type:            Datatype of the field, as defined by XML schema (ex: https://www.w3.org/TR/xmlschema-2/#string)
    length:          (optional) Length of the field
    decimals:        (optional) Number of decimals if field type is 'decimal'
  bbox:
    south:           -22.0
    north:           52.0
    west:            -62.0
    east:            56.0
```

**`framework_name`**:
Identifier of the framework. It must not contain capital letters, special characters, or spaces.

**`uri`**: The [URI](https://fr.wikipedia.org/wiki/Uniform_Resource_Identifier#Exemples) that uniquely references the spatial framework.


**`organization`**:
The name of the organization providing the framework.

**`title`**:
A human readable sentence fragment that might form a title if the framework dataset were displayed in map form.

**`abstract`**:
A complete description or abstract that describes the framework dataset.

**`version`**:
A version identifier for this framework. For example, it can be a year or a date since the administrative divisions
are regularly reorganized.

**`start_date`**:
(optional) Start of a time period to which the framework or dataset applies.

**`reference_date`**:
The date to which the framework dataset applies.

NB : If "**startDate**" is included then "**ReferenceDate**" describes a range of time (from "startDate" to "ReferenceDate")
to which the framework/dataset applies. If "startDate" is not included then "ReferenceDate" describes a
representative point in time to which the framework/dataset applies. The data type is as defined for
"ReferenceDate".

**`key_col/name`**:
The name of the field that have to join to the geographic data.

**`key_col/type`**:
The datatype of the field, as defined by XML schema. See the full list: [W3C 3.2-Primitive datatypes](https://www.w3.org/TR/xmlschema-2/).

**`key_col/length`**:
(optional) Length of the field, in characters or digits.

**`key_col/decimals`**:
(optional) Number of digits after the decimal, only for decimal numbers with a fixed number of digits after the decimal.

**`bbox`**:
Bounding coordinates (north, south, west, east) of the spatial framework.


Note that almost all these parameters are inserted in the DescribeFrameworks
response produced by OneTjs.

## Datasets

Datasets can be located in one or more folders. Each folder can contain one 
or more datasets.

Each dataset must have a configuration file. The name of this configuration file
is not imposed, it only needs to have the extension '.yml' (ex: *dataset_name.yml*).

If the data is stored in a file (CSV or XLS), the data file must be specified
in the configuration file.
If the data is stored in a database (Postgres), there is only configuration file.


Typical dataset configuration structure:

```yaml
# dataset
---
name:              dataset_name
uri:               dataset_URI
organization:      Name of the organization providing the dataset
title:             Dataset title
abstract:          Some kind of description of the dataset
documentation:     (optional) Additional documentation
version:           Version identifier for this dataset
start_date:        (optional) Start of a time period to which the framework or dataset applies.
reference_date:    The date to which the framework dataset applies.
activated:         yes
frameworks:
  - name:            framework_name
    uri:             framework_URI
    complete:        yes # must be 'yes' -> data concerns the entire framework = complete dataset
    relationship:    one # Identifies if the relationship between the Framework and the Attribute datasets are 1:1 (one) or 1:many (many).
datasource:
    ...
attributes:
    ...
```

Some "data_source" parameter examples:

```yaml
# CSV file (separator = ",") or XLS file
data_source:
  type:              csv
  path:              datafile_name.csv
```

```yaml
# Excel file
data_source:
  type:              xls
  path:              datafile_name.xls

```yaml
# PostgreSQL database
data_source:
  type:              pgsql
  query:             SQL query
  table:             table name
  db_connection:
    host:              database host address
    port:              connection port number (defaults to 5432 if not provided)
    dbname:            database name
    user:              database user name used to authenticate
    password:          user password used to authenticate
```

```yaml
# MySQL database
data_source:
  type:              mysql
  query:             SQL query
  table:             table name
  db_connection:
    host:              database host address
    port:              connection port number (defaults to 3306 if not provided)
    database:          database name
    user:              database user name used to authenticate
    password:          user password used to authenticate
```

Notes SQL datasources:
- For MySQL and PostgreSQL datasources, either query or table must be present.
- The SQL query when the table parameter is used is "SELECT * FROM tablename".
- If both parameters are present, OneTJS only takes into account the query parameter.
- The database name parameter is slightly different for MySQL and PostgreSQL: database and dbname respectively.

```
The "attributes" parameter depends on the column data type:
```yaml
attributes:
  - name:              Name of the attribute that contains the data to display on the map
    title:             Attribute title
    abstract:          (optional) Some kind of description of the data to display on the map
    type:              Datatype of the field, as defined by XML schema (ex: https://www.w3.org/TR/xmlschema-2/#string)
    length:            (optional) Length of the field
    decimals:          (optional) Number of decimals if field type is 'decimal'
    purpose:           Attribute # must be 'Attribute' right now. Otherwise, purpose that indicates whether the attribute contains data, a linkage key, or other content.

    # If data type is Count
    values:            Count
    uom_short_form:    Unit of Measure -> short form (ex: 'ha')
    uom_long_form:     Unit of Measure -> long form (ex: 'hectares')

    # If data type is Measure
    values:            Measure
    uom_short_form:    Unit of Measure -> short form (ex: '%')
    uom_long_form:     Unit of Measure -> long form (ex: 'percent')

    # If data type is nominal
    values:            Nominal
    choices:
      - identifier:    Identifier of the category (ex: 1)
        title:         Title of this category
        abstract:      Some kind of description of this category
        color:         HEX color of this category (ex: ffffff)

    # If data type is ordinal
    ### Not yet implemented ###
```
