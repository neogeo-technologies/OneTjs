# -*- coding: utf-8 -*-

import pandas as pd
import os
from app import app


def get_data_from_datasource(db_connect_string, db_subset, attributes, index):

    # TODO: check if the data should be retrieved from the data source or from a cached version?
    # TODO: or should be simply rely on the web server for managing cached data?

    # TODO: the data type for each column should be specified in order to avoid wrong type inferance
    # example: insee code wrongly interpreted as integers
    # forcing datatypes with pandas: d = pandas.read_csv('foo.csv', dtype={'BAR': 'S10'})

    root_path = app.root_path
    db_connect_string = os.path.abspath(
        os.path.join(root_path, os.path.pardir, os.path.pardir, "data", "demandeurs_emploi_hommes.csv"))

    # test if the connection string points to a file or is a db connection string
    # file
    if os.path.exists(db_connect_string):

        # test if the file is a csv file
        print(os.path.splitext(db_connect_string)[1])
        if os.path.splitext(db_connect_string)[1] == u".csv":
            data = pd.read_csv(db_connect_string, index_col="code")
            dataframe = pd.DataFrame(data, columns=attributes)
            # print(dataframe.head())
            return dataframe
        # TODO : test for Excel file
        else:
            pass
    # database
    else:
        pass
