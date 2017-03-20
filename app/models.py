# -*- coding: utf-8 -*-

import yaml
import os
import logging

FRAMEWORKS_FILE_NAME = "frameworks.yml"


class Service(object):
    def __init__(self, **kwargs):
        # Default values
        self.cfg_file_path = None
        self.name = "default_service_name"
        self.activated = False
        self.title = "Default service title"
        self.abstract = "Default service abstract"
        self.tjs_versions = ["1.0.0"]
        self.language = "fr-FR"
        self.data_dir_path = None
        self.abs_data_dir_path = None
        self.frameworks = {}
        self.datasets = {}

        self.update_service_info(**kwargs)

    def update_service_info(self, **kwargs):

        self.__dict__.update(kwargs)

        # Search for the parameters of the datasets published with this service
        self.abs_data_dir_path = None
        if os.path.isabs(self.data_dir_path):
            temp_path = self.abs_data_dir_path
        else:
            # Concatenating the paths of directory containing the service config file and the data relative path
            temp_path = os.path.join(os.path.dirname(self.cfg_file_path), self.data_dir_path)

        # print(temp_path)
        if os.path.exists(temp_path):
            self.abs_data_dir_path = temp_path

        # print(u"Répertoire du service {0}".format(self.abs_data_dir_path))

        if self.abs_data_dir_path is not None and os.path.exists(self.abs_data_dir_path):
            self.update_frameworks_info()
            self.update_datasets_info()

        self.log_info()

    def update_frameworks_info(self):
        self.frameworks = {}

        # Recherche d'un fichier frameworks.yml
        frwks_yml_path = os.path.join(self.abs_data_dir_path, FRAMEWORKS_FILE_NAME)
        if os.path.exists(frwks_yml_path):

            with open(frwks_yml_path, 'r') as stream:
                try:
                    frameworks_dict = yaml.load(stream)

                    for k, v in frameworks_dict.iteritems():
                        v["name"] = k
                        f = Framework(**v)
                        self.frameworks[k] = f
                except yaml.YAMLError as e:
                    logging.exception(e)

    def update_datasets_info(self):
        self.datasets = {}

        # Recherche des autres fichiers yaml correspondant à des jeux de données
        for root, dirs, files in os.walk(self.abs_data_dir_path):
            for f in files:
                if f.endswith(".yml") and f != FRAMEWORKS_FILE_NAME:
                    yaml_file_path = os.path.join(root, f)
                    try:
                        ds = self.create_dataset_instance(yaml_file_path)
                        self.datasets[ds.name] = ds
                    except ValueError as e:
                        logging.exception(e)

    def log_info(self):
        logging.info("Service: {0} ({1})".format(self.name, "activated" if self.activated else "deactivated"))
        logging.info("- datapath: {0}".format(self.data_dir_path))
        for f in self.frameworks.items():
            logging.info("- framework: {0} - {1}".format(f[1].title, f[0]))
        for ds in self.datasets.items():
            logging.info("- dataset: {0} - {1}".format(ds[1].title, ds[0]))

    # factory function for datasets
    def create_dataset_instance(self, dataset_yaml_file_path):
        dataset_subclasses = [CsvFileDataset, XlsFileDataset, SqlDataset]
        dataset_subclass = None
        data_source_type = None

        # Get the data source type
        dataset_dict = {}
        with open(dataset_yaml_file_path, 'r') as stream:
            try:
                # Read the yaml file
                dataset_dict = yaml.load(stream)
            # TODO: should we raise an exception to stop the process?
            except yaml.YAMLError as e:
                logging.exception(e)

            # Save the yaml file path
            dataset_dict["yaml_file_path"] = dataset_yaml_file_path

            try:
                # Set the reference of the framework using its uri
                data_source_type = dataset_dict.get("data_source_type", None)
                framework_uri = dataset_dict.pop("framework_uri")
                framework = self.get_framework_with_uri(framework_uri)
                dataset_dict["framework"] = framework
            # TODO: should we raise an exception to stop the process?
            except KeyError as e:
                logging.exception(e)

        if data_source_type is None:
            raise ValueError(
                "'data_source_type' parameter not defined in dataset config file {0}".format(dataset_yaml_file_path))

        # Get the dataset class with this data source type
        for sc in dataset_subclasses:
            if sc.DATA_SOURCE_TYPE == data_source_type:
                dataset_subclass = sc

        # Instantiate the right class
        if dataset_subclass is not None:
            return dataset_subclass(dataset_dict)

    def get_datasets(self):
        return list(self.datasets.values())

    def get_dataset_with_uri(self, dataset_uri):
        for f in self.get_datasets():
            if f.uri == dataset_uri:
                return f

    def get_dataset_with_name(self, dataset_name):
        return self.datasets[dataset_name]

    def get_frameworks(self):
        return list(self.frameworks.values())

    def get_framework_with_uri(self, framework_uri):
        for f in self.get_frameworks():
            if f.uri == framework_uri:
                return f

    def get_framework_with_name(self, framework_name):
        return self.frameworks[framework_name]

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)


class Framework(object):
    """Framework represents a spatial framework in the OGC TJS terminology
    spatial framework
    a GIS representation, either point, line, or polygon, of any collection of physical or conceptual geographic
    objects. Municipalities, postal code areas, telephone area codes, ecoregions, watersheds, road segments, fire
    stations, and lighthouses are all examples of spatial frameworks.

    One framework may be associated with more than one service.
    One service may be associated with more than one framework
    """

    def __init__(self, **kwargs):
        # Default values
        self.name = "default_framework_name"
        self.uri = None
        self.organization = None
        self.tile = "Default framework title"
        self.abstract = "Default framework abstract"
        self.version = None
        self.reference_date = None
        self.start_date = None
        self.key_col = {
            "name": None,
            "type": None,
            "length": None,
            "decimals": None
        }
        self.bbox = {
            "south": -90,
            "north": 90,
            "west": -180,
            "east": 180,
        }

        self.__dict__.update(kwargs)

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)


class Dataset(object):
    """Dataset represents a dataset in the OGC TJS terminology
    One dataset in associated with one and only one framework
    """

    DATA_SOURCE_TYPE = None

    def __init__(self, dataset_dict):
        # Default values
        self.uri = None
        self.framework = None
        self.data_source_type = None
        self.data_source_path = None
        self.data_source_subset = None
        self.organization = None
        self.name = "default_dataset_name"
        self.tile = "Default dataset title"
        self.abstract = "Default dataset abstract"
        self.documentation = None
        self.version = None
        self.reference_date = None
        self.start_date = None
        self.activated = False
        self.cached = False
        self.cache_max_age = 0
        self.yaml_file_path = None

        self.ds_attributes = []

        # Get the dataset attributes definitions
        dataset_attributes_dicts = {}
        try:
            dataset_attributes_dicts = dataset_dict.pop("attributes")
        except KeyError as e:
            logging.error(
                "'attributes' parameter not defined in dataset config file {0}".format(self.yaml_file_path))
            logging.exception(e)

        # Update the dataset object properties
        self.__dict__.update(dataset_dict)

        # Create the DatasetAttribute instances and add them to the ds_attributes list proprety of the dataset
        for at_dict in dataset_attributes_dicts:
            at_dict["dataset"] = self
            at = DatasetAttribute(**at_dict)
            self.ds_attributes.append(at)

        # Check the data source et attributes existence
        self.check_data_source()

        if not self.uri:
            raise ValueError("'uri' parameter not defined in service config file {0}".format(self.yaml_file_path))
        if not self.framework:
            raise ValueError("'framework' parameter not defined in service config file {0}".format(self.yaml_file_path))

    def check_data_source(self):
        raise NotImplementedError()

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)


class FileDataset(Dataset):

    def __init__(self, dataset_dict):
        super(FileDataset, self).__init__(dataset_dict)

    def check_data_source(self):
        data_source_found = False

        # Check the existence of the data source
        if os.path.exists(self.data_source_path):
            data_source_found = True
        else:
            temp_file_path = os.path.join(os.path.dirname(self.yaml_file_path), self.data_source_path)
            if os.path.exists(temp_file_path):
                data_source_found = True
                self.data_source_path = temp_file_path

        if not data_source_found:
            raise ValueError("data source specified in dataset config file {0} cannot be found: {1}".format(
                self.yaml_file_path, self.data_source_path))

        if not os.path.isfile(self.data_source_path):
            raise ValueError("data source specified in dataset config file {0} is not a file: {1}".format(
                self.yaml_file_path, self.data_source_path))

        # Check the existence of the attributes in the data source
        # TODO: check the attributes


class CsvFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "csv"

    def __init__(self, dataset_dict):
        super(CsvFileDataset, self).__init__(dataset_dict)

    def check_data_source(self):
        super(CsvFileDataset, self).check_data_source()


class XlsFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "xls"

    def __init__(self, dataset_dict):
        super(XlsFileDataset, self).__init__(dataset_dict)

    def check_data_source(self):
        super(XlsFileDataset, self).check_data_source()


class SqlDataset(Dataset):
    DATA_SOURCE_TYPE = "sql"

    def __init__(self, dataset_dict):
        super(SqlDataset, self).__init__(dataset_dict)

    def check_data_source(self):
        pass


class DatasetAttribute(object):
    """DatasetAttribute represents an attribute of a dataset in the OGC TJS terminology
    One dataset attribute in associated with one and only one dataset
    """

    def __init__(self, **kwargs):
        # Default values
        self.dataset = None
        self.name = "default_attribute_name"
        self.tile = "Default attribute title"
        self.abstract = "Default attribute abstract"
        self.documentation = None
        self.type = None
        self.length = None
        self.decimals = None
        self.purpose = None
        self.values = None
        self.uom_short_form = None
        self.uom_long_form = None

        self.__dict__.update(kwargs)

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)
