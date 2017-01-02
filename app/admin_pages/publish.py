# -*- coding: utf-8 -*-

from app import db

from app.models import DataSource
from app.models import Dataset
from app.models import DatasetAttribute

# import pandas as pd
import os
from shutil import copyfile

from datetime import datetime

import tablib
import numpy


class DataPublicationException(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


def publish_csv_file(csv_file_path, dest_file_path, service, framework):
    # TODO: If csv_file_path is not valid raise an exception

    # TODO: if the csv file is already referenced, just replace the file and check if the attributes records
    # TODO: present in the database are still ok

    # Create destination directory
    dest_dir_path = os.path.dirname(dest_file_path)
    file_name = os.path.basename(dest_file_path)
    if not os.path.exists(dest_dir_path):
        os.makedirs(dest_dir_path)

    # Copy file into destination directory
    copyfile(csv_file_path, dest_file_path)

    # # Open the csv file
    # data = pd.read_csv(dest_file_path, index_col=False)
    # print(data.head())
    # print(data.columns)
    # print(data[u'code'].dtype)
    # print(data[u'commune'].dtype)
    # print(data[u'demandeurs_emploi_homme'].dtype)

    # #
    # print("data.columns")
    # print(data.columns)
    # print("data.index")
    # print(data.index)

    data = tablib.Dataset().load(open(dest_file_path).read(), delimiter=",", encoding="utf8")
    # data = tablib.Dataset().load(open(dest_file_path).read())
    print(dir(data))
    print(data.headers)

    np_array = numpy.array(data[u'code'])
    print np_array
    print(np_array.dtype)
    print(np_array.astype(numpy.int))
    print(np_array.astype(numpy.int).dtype)

    # print(u"is_alpha - {}".format(is_alpha))
    # print(u"is_decimal - {}".format(is_decimal))
    # print(u"is_alnum - {}".format(is_alnum))
    # print(u"is_numeric - {}".format(is_numeric))

    # Check if the attribute of the framework is present in the data
    framework_key_col_name = framework.key_col_name
    if framework_key_col_name not in data.headers:
        raise DataPublicationException(u"Aucune colonne du fichier en entrée ne correspond à la clef du framework.")

    # List all other attributes
    column_names = data.headers

    # check if the dataset is already referenced
    # search for datasources containing the dest_file_path
    data_sources = DataSource.query.filter(DataSource.type == "csv").all()
    candidate_data_sources = []
    for data_source in data_sources:
        connect_string = data_source.get_data_source_dir_path()
        if dest_file_path.startswith(connect_string):
            candidate_data_sources.append(data_source)
            print(data_source)

    # For each candidate date source, test all associated datesets
    for data_source in candidate_data_sources:
        datasets = Dataset.query.filter(Dataset.data_source == data_source)
        for dataset in datasets:
            file_path = os.path.join(data_source.get_data_source_dir_path(), dataset.data_source_subset)
            if os.path.normpath(file_path) == os.path.normpath(dest_file_path):
                raise DataPublicationException(
                    u"This dataset is already referenced in the database.")

    # if no candidate data source can contain the file
    # create a new data source record
    if len(candidate_data_sources) > 0:
        ds = candidate_data_sources[0]
    else:
        ds = DataSource(
            title=u"Répertoire de fichiers CSV {}".format(dest_dir_path),
            type="csv",
            connect_string="file://{}".format(dest_dir_path)
        )
        db.session.add(ds)

    # if the dataset is not referenced
    # create the dataset
    # Add a dataset record
    # TODO: use acceptable values for uri and organization
    new_dtst = Dataset(
        uri="http://www.regionhautsdefrance.fr/data/geostats/datasets/{}".format(file_name),
        framework=framework,
        data_source=ds,
        data_source_subset=u"{}".format(file_name),
        organization=u"Région Hauts-de-France",
        # title=u"{}".format(file_name),
        abstract=u"{}".format(file_name),
        # version=u"1",
        reference_date=datetime.now(),
        start_date=datetime.now(),
        activated=True,
        cached=False
    )
    db.session.add(new_dtst)

    # create the dataset attributes
    pass

    db.session.commit()
