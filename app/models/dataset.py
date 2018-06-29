# -*- coding: utf-8 -*-

import logging
import os
import pandas as pd
import psycopg2
import numpy as np

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
        self.data_source = {"type": None, "path": None}
        self.organization = None
        self.name = "default_dataset_name"
        self.title = "Default dataset title"
        self.abstract = "Default dataset abstract"
        self.documentation = None
        self.version = None
        self.reference_date = None
        self.start_date = None
        self.activated = False
        self.cache_max_age = 0
        self.yaml_file_path = None

        self.ds_attributes = []

        # Get the dataset attributes definitions
        dataset_attributes_dicts = {}
        try:
            dataset_attributes_dicts = dataset_dict.pop("attributes")
        except KeyError as e:
            logging.error(
                "'attributes' parameter not defined in dataset config file {0}".format(
                    self.yaml_file_path
                )
            )
            logging.exception(e)

        # Get the frameworks info
        frameworks_relations = {}
        try:
            frameworks_relations = dataset_dict.pop("frameworks")
        except KeyError as e:
            logging.error(
                "'frameworks' parameter not defined in dataset config file {0}".format(
                    self.yaml_file_path
                )
            )
            logging.exception(e)

        # Update the dataset object properties
        self.__dict__.update(dataset_dict)

        # Get the frameworks info
        for framework_relation in frameworks_relations:
            framework_uri = framework_relation["uri"]
            framework = service.get_framework_with_uri(framework_uri)
            framework_complete = framework_relation["complete"]
            framework_relationship = framework_relation["relationship"]

            self.frameworks[framework_uri] = framework
            self.frameworks_complete[framework_uri] = framework_complete
            self.frameworks_relationship[framework_uri] = framework_relationship

        # Create the DatasetAttribute instances and add them to the ds_attributes list proprety of the dataset
        for at_dict in dataset_attributes_dicts:
            at_dict["dataset"] = self
            at = DatasetAttribute(**at_dict)
            self.ds_attributes.append(at)

        # Check the data source et attributes existence
        self.check_data_source()

        if not self.uri:
            raise ValueError(
                "'uri' parameter not defined in service config file {0}".format(
                    self.yaml_file_path
                )
            )
        if not self.frameworks:
            raise ValueError(
                "'frameworks' parameter not defined in service config file {0}".format(
                    self.yaml_file_path
                )
            )

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

        if framework and framework not in self.get_frameworks():
            raise ValueError(
                "The framework with the uri {} is not available "
                "for the dataset with the uri {}".format(framework.uri, self.uri)
            )

        if not attributes:
            attributes = self.ds_attributes

        attributes_names = [at.name for at in attributes]
        attributes_types = [at.type for at in attributes]

        if not self.frameworks:
            raise ValueError(
                "There is not any framework available for the dataset with the uri {}.".format(
                    framework.uri, self.uri
                )
            )

        if not framework:
            framework = self.get_one_framework()

        key_col_name = framework.key_col["name"]
        key_col_type = framework.key_col["type"]

        data = None
        try:
            data = self._get_data(
                attributes_names, attributes_types, key_col_name, key_col_type
            )
        except ValueError as e:
            logging.exception(e)

        return data

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):
        pass

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class FileDataset(Dataset):
    def __init__(self, service, dataset_dict):
        super(FileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        data_source_found = False

        # Check the existence of the data source
        if os.path.exists(self.data_source["path"]):
            data_source_found = True
        else:
            temp_file_path = os.path.join(
                os.path.dirname(self.yaml_file_path), self.data_source["path"]
            )
            if os.path.exists(temp_file_path):
                data_source_found = True
                self.data_source["path"] = temp_file_path

        if not data_source_found:
            raise ValueError(
                "data source specified in dataset config file {0} cannot be found: {1}".format(
                    self.yaml_file_path, self.data_source["path"]
                )
            )

        if not os.path.isfile(self.data_source["path"]):
            raise ValueError(
                "data source specified in dataset config file {0} is not a file: {1}".format(
                    self.yaml_file_path, self.data_source["path"]
                )
            )

        # Check the existence of the attributes in the data source
        # TODO: check the attributes


def get_converter_for_xmlschema_type(xmlschema_type):
    if xmlschema_type == "https://www.w3.org/TR/xmlschema-2/#decimal":
        return pd.to_numeric
    elif xmlschema_type == "https://www.w3.org/TR/xmlschema-2/#integer":
        return pd.to_numeric
    else:
        return str


def get_converters_for_attributes(attributes_names, attributes_types):
    converters = dict()

    for i in range(len(attributes_names)):
        conv = get_converter_for_xmlschema_type(attributes_types[i])
        if conv:
            converters[attributes_names[i]] = conv

    return converters


class CsvFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "csv"

    def __init__(self, service, dataset_dict):
        super(CsvFileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        super(CsvFileDataset, self).check_data_source()

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):

        converters = get_converters_for_attributes(
            attributes_names + [key_col_name], attributes_types + [key_col_type]
        )

        # TODO: add exception handling for data reading troubles
        data = pd.read_csv(
            self.data_source["path"], dtype=object, converters=converters
        )
        data = data.where((pd.notnull(data)), None)
        data = data.set_index(key_col_name)
        dataframe = pd.DataFrame(data, columns=attributes_names)

        return dataframe


class XlsFileDataset(FileDataset):
    DATA_SOURCE_TYPE = "xls"

    def __init__(self, service, dataset_dict):
        super(XlsFileDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        super(XlsFileDataset, self).check_data_source()

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):

        converters = get_converters_for_attributes(
            attributes_names + [key_col_name], attributes_types + [key_col_type]
        )

        # TODO: add exception handling for data reading troubles
        data = pd.read_excel(self.data_source["path"], converters=converters)
        data = data.where((pd.notnull(data)), None)
        data = data.set_index(key_col_name)
        dataframe = pd.DataFrame(data, columns=attributes_names)

        return dataframe


class PostgreSqlDataset(Dataset):
    DATA_SOURCE_TYPE = "sql"

    def __init__(self, service, dataset_dict):
        super(PostgreSqlDataset, self).__init__(service, dataset_dict)

    def check_data_source(self):
        param_con = []
        for param in self.data_source["db_connection"]:
            param_con.append("{0}={1}".format(param, self.data_source["db_connection"][param]))
        conn_str = " ".join(param_con)
        conn = psycopg2.connect(conn_str)
        df = pd.read_sql(self.data_source["query"], con=conn)
        if df.empty:
            raise ValueError(
                "Connection error : please check 'db_connection' or 'query' parameters in the dataset config file {0}".format(
                    self.yaml_file_path
                )
            )

    def _get_data(self, attributes_names, attributes_types, key_col_name, key_col_type):

        param_con = []

        for param in self.data_source["db_connection"]:
            param_con.append("{0}={1}".format(param, self.data_source["db_connection"][param]))

        query = self.data_source["query"]

        conn_str = " ".join(param_con)
        conn = psycopg2.connect(conn_str)
        dataframe = pd.DataFrame()
        for chunk in pd.read_sql(query, con=conn, chunksize=5000):
            dataframe = dataframe.append(chunk)
        dataframe = dataframe.set_index(key_col_name)

        return dataframe
