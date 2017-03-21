# -*- coding: utf-8 -*-

import pandas as pd
import os
from app import app


def get_data_from_datasource(dataset, dataset_attributes, framework):

    # TODO: the data type for each column should be specified in order to avoid wrong type inferance
    # example: insee code wrongly interpreted as integers
    # forcing datatypes with pandas: d = pandas.read_csv('foo.csv', dtype={'BAR': 'S10'})

    attributes_names = [at.name for at in dataset_attributes]

    data_source_type = dataset.data_source["type"]

    if data_source_type == "csv":
        data = pd.read_csv(dataset.data_source["path"], index_col=framework.key_col["name"])
        dataframe = pd.DataFrame(data, columns=attributes_names)
        return dataframe
    elif data_source_type == "xls":
        data = pd.read_excel(dataset.data_source["path"], index_col=framework.key_col["name"])
        dataframe = pd.DataFrame(data, columns=attributes_names)
        return dataframe
    elif data_source_type == "sql":
        pass
