# -*- coding: utf-8 -*-

import logging
import os
import pandas as pd

from app.models.dataset_attribute import DatasetAttribute


class Dataset(object):
    """Dataset represents a dataset in the OGC TJS terminology
    One dataset in associated with one and only one framework
    """

    DATA_SOURCE_TYPE = None

    def __init__(self, service, dataset_dict):
        # Default values
        self.uri = None
        self.frameworks = {}
        self.frameworks_complete = {}
        self.frameworks_relationship = {}
        self.data_source = {"type": None, "path": None, "subset": None}
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

        # Get the frameworks info
        frameworks_relations = {}
        try:
            frameworks_relations = dataset_dict.pop("frameworks")
        except KeyError as e:
            logging.error(
                "'frameworks' parameter not defined in dataset config file {0}".format(self.yaml_file_path))
            logging.exception(e)

        # Update the dataset object properties
        self.__dict__.update(dataset_dict)

        # Get the frameworks info
        for framework_relation in frameworks_relations:
            framework_uri = framework_relation["uri"]
            framework = service.get_framework_with_uri(framework_uri)
            framework_complete = framework_relation["complete"]
            framework_relationship = framework_relation["relationship"]

            self.frameworks["uri"] = framework
            self.frameworks_complete["uri"] = framework_complete
            self.frameworks_relationship["uri"] = framework_relationship

        # Create the DatasetAttribute instances and add them to the ds_attributes list proprety of the dataset
        for at_dict in dataset_attributes_dicts:
            at_dict["dataset"] = self
            at = DatasetAttribute(**at_dict)
            self.ds_attributes.append(at)

        # Check the data source et attributes existence
        self.check_data_source()

        if not self.uri:
            raise ValueError("'uri' parameter not defined in service config file {0}".format(self.yaml_file_path))
        if not self.frameworks:
            raise ValueError("'frameworks' parameter not defined in service config file {0}".format(
                self.yaml_file_path))

    def check_data_source(self):
        raise NotImplementedError()

    def get_attribute_with_name(self, attribute_name):
        for at in self.ds_attributes:
            if at.name == attribute_name:
                return at

    def get_frameworks(self):
        return list(self.frameworks.values())

    def get_one_framework(self):
        frameworks = self.get_frameworks()
        if frameworks:
            return frameworks[0]
        else:
            return None

    def get_framework_with_name(self, framework_name):
        for f in self.get_frameworks():
            if f.name == framework_name:
                return f

    def get_framework_with_uri(self, framework_uri):
        return self.frameworks.get(framework_uri, None)

    def get_framework_relationship_info(self, framework_uri):
        return self.frameworks_relationship.get(framework_uri, None)

    def get_framework_complete_info(self, framework_uri):
        return self.frameworks_complete.get(framework_uri, None)

    def get_data(self, attributes=None, framework=None):

        # TODO: check if the framework is one of the frameworks configured for the dataset

        # TODO: the data type for each column should be specified in order to avoid wrong type inferance
        # example: insee code wrongly interpreted as integers
        # forcing datatypes with pandas: d = pandas.read_csv('foo.csv', dtype={'BAR': 'S10'})

        if attributes:
            attributes_names = [at.name for at in attributes]
            attributes_types = []
        else:
            attributes_names = [at.name for at in self.ds_attributes]
            attributes_types = []

        if not self.frameworks:
            return None

        if not framework:
            framework = self.get_one_framework()

        key_col_name = framework.key_col["name"]
        key_col_type = None

        data = self._get_data(attributes_names, attributes_types, key_col_name, key_col_type)

        return data

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):
        pass

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)


class FileDataset(Dataset):

    def __init__(self, service, dataset_dict):
        super(FileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        data_source_found = False

        # Check the existence of the data source
        if os.path.exists(self.data_source["path"]):
            data_source_found = True
        else:
            temp_file_path = os.path.join(os.path.dirname(self.yaml_file_path), self.data_source["path"])
            if os.path.exists(temp_file_path):
                data_source_found = True
                self.data_source["path"] = temp_file_path

        if not data_source_found:
            raise ValueError("data source specified in dataset config file {0} cannot be found: {1}".format(
                self.yaml_file_path, self.data_source["path"]))

        if not os.path.isfile(self.data_source["path"]):
            raise ValueError("data source specified in dataset config file {0} is not a file: {1}".format(
                self.yaml_file_path, self.data_source["path"]))

        # Check the existence of the attributes in the data source
        # TODO: check the attributes


class CsvFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "csv"

    def __init__(self, service, dataset_dict):
        super(CsvFileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        super(CsvFileDataset, self).check_data_source()

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):
        # TODO: add exception handling for data reading troubles
        data = pd.read_csv(self.data_source["path"], index_col=key_col_name)
        dataframe = pd.DataFrame(data, columns=attributes_names)
        return dataframe


class XlsFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "xls"

    def __init__(self, service, dataset_dict):
        super(XlsFileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        super(XlsFileDataset, self).check_data_source()

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):
        # TODO: add exception handling for data reading troubles
        data = pd.read_excel(self.data_source["path"], index_col=key_col_name)
        dataframe = pd.DataFrame(data, columns=attributes_names)
        return dataframe


class SqlDataset(Dataset):
    DATA_SOURCE_TYPE = "sql"

    def __init__(self, service, dataset_dict):
        super(SqlDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        pass

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):
        pass