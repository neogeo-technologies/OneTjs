# -*- coding: utf-8 -*-

import os
# import io
# import csv
# import urllib
# import json
# import operator
# import datetime

from flask import request
from flask import render_template
from flask import make_response
from flask import send_from_directory
# from flask import Response
# from flask import url_for
# from flask import redirect
# from flask import abort
# from flask import jsonify

from flask_login import login_required

from flask_admin.contrib.sqla import ModelView

from werkzeug.urls import url_encode
from werkzeug.urls import url_join

from app import app
from app import db
from app import admin


from models.models import Service
from models.models import DataSource
from models.models import Framework
from models.models import Dataset
from models.models import DatasetAttribute

import data


# TODO: create an admin view for symplifying the creation of datasets and datsetattribute records
# TODO: (just by selecting a datasource and a table)

# TODO: create a view listing the datasets, the relations with datasources, dataattributes, framwroks, services
# TODO: and previewing the data

# TODO: allow long text edition for abstract of Framework (multiple lines edit box)
# TODO: set a list of values for the key_col_type proprety of Framework: see the XML schema
class FrameworkView(ModelView):
    can_view_details = True
    column_list = (
        Framework.title,
        Framework.organization,
        Framework.version,
        Framework.reference_date
    )
    column_details_list = (
        Framework.id,
        Framework.uri,
        Framework.title,
        Framework.abstract,
        Framework.documentation,
        Framework.version,
        Framework.organization,
        Framework.reference_date,
        Framework.start_date,
        Framework.key_col_name,
        Framework.key_col_type,
        Framework.key_col_length,
        Framework.key_col_decimals,
        Framework.bbox_south,
        Framework.bbox_north,
        Framework.bbox_east,
        Framework.bbox_west
    )


# TODO: default organization for Dataset: the organization maintaining the server instance
# TODO: allow long text edition for abstract of Dataset (multiple lines edit box)
class DatasetView(ModelView):
    can_view_details = True
    column_list = (
        Dataset.title,
        Dataset.organization,
        Dataset.version,
        Dataset.reference_date,
        Dataset.activated
    )
    column_details_list = (
        Dataset.id,
        Dataset.uri,
        'framework.uri',
        'data_source.title',
        Dataset.title,
        Dataset.abstract,
        Dataset.documentation,
        Dataset.version,
        Dataset.organization,
        Dataset.reference_date,
        Dataset.start_date,
        Dataset.activated,
        Dataset.cached,
        Dataset.cache_max_age
    )


# TODO: set a list of values for the purpose proprety of DatasetAttribute: see the TJS specification
# TODO: set a list of values for the type proprety of DatasetAttribute: see the XML schema
# TODO: set a list of values for the values proprety of DatasetAttribute: see the TJS specification
# TODO: allow long text edition for abstract of DatasetAttribute (multiple lines edit box)
class DatasetAttributeView(ModelView):
    can_view_details = True
    column_list = (
        DatasetAttribute.id,
        DatasetAttribute.name,
        DatasetAttribute.title,
        DatasetAttribute.values
    )
    column_details_list = (
        DatasetAttribute.id,
        'dataset.uri',
        DatasetAttribute.purpose,
        DatasetAttribute.name,
        DatasetAttribute.type,
        DatasetAttribute.length,
        DatasetAttribute.decimals,
        DatasetAttribute.title,
        DatasetAttribute.abstract,
        DatasetAttribute.documentation,
        DatasetAttribute.values,
        DatasetAttribute.uom_short_form,
        DatasetAttribute.uom_long_form
    )


admin.add_view(ModelView(Service, db.session))

# TODO: set a list of values for the type proprety of DataSource: csv, Excel, db
admin.add_view(ModelView(DataSource, db.session))
admin.add_view(FrameworkView(Framework, db.session))
admin.add_view(DatasetView(Dataset, db.session))
admin.add_view(DatasetAttributeView(DatasetAttribute, db.session))


# import utils


def render_object_list(template_name, query, paginate_by=10, **context):
    page = request.args.get("page")
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    object_list = query.paginate(page, paginate_by)

    return render_template(template_name, object_list=object_list, **context)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template("index.html", cfg=app.config)


@app.route("/service/")
def service():
    return render_template("service.html", cfg=app.config)


@app.route("/frameworks/")
def framework_list():

    frameworks = Framework.query.order_by(Framework.title.desc())
    return render_object_list("framework_list.html", frameworks, cfg=app.config)


@app.route("/datasets/")
def dataset_list():

    datasets = Dataset.query.order_by(Dataset.title.desc())
    return render_object_list("dataset_list.html", datasets, cfg=app.config)


# TODO: use standard operation names
@app.route("/tjs/test")
def test():
    serv = Service.query.first()
    ds = Dataset.query.first()
    tjs_version = "1.0"

    # TODO: manage the complete set of operations parameters declared in the TJS specification

    if tjs_version in ("1.0",):
        template_name = "tjs_100_getdata.xml"
    else:
        # TJS exception
        response_content = render_template("getdata.xml", service=service, dataset=ds)
        response = make_response(response_content)
        response.headers["Content-Type"] = "application/xml"
        return response

    # TODO: Retrieve the attributes declared in the request parameters
    ds_attributes_names = [attribute.name for attribute in ds.attributes]

    # TODO: include exception handling for the cases where the data cannot be retrieved
    # TODO: test the type of datasource
    # TODO: pass the datasource object to the called function
    # TODO: make the framework - dataset relation a many to many one
    pd_dataframe = data.get_data_from_datasource(
        ds.data_source.connect_string,
        ds.data_source_subset,
        ds_attributes_names,
        ds.framework.key_col_name)

    response_content = render_template(template_name, service=serv, dataset=ds, data=pd_dataframe)
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    # TODO: add cache information in the response headers

    return response


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return "{}?{}".format(request.path, url_encode(args))


@app.template_global()
def get_describedatasets_url(serv, framework):
    app_path = request.url_root
    service_url = url_join(app_path, serv.path)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"version"] = 1
    args[u"request"] = u"DescribeDatasets"
    args[u"frameworkuri"] = framework.uri
    args[u"acceptlanguages"] = u"fr"

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_describedata_url(serv, dataset):
    app_path = request.url_root
    service_url = url_join(app_path, serv.path)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"version"] = 1
    args[u"request"] = u"DescribeData"
    args[u"frameworkuri"] = dataset.framework.uri
    args[u"dataseturi"] = dataset.uri
    args[u"acceptlanguages"] = u"fr"

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_getdata_url(serv, attribute):
    app_path = request.url_root
    service_url = url_join(app_path, serv.path)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"version"] = 1
    args[u"request"] = u"GetData"
    args[u"frameworkuri"] = attribute.dataset.framework.uri
    args[u"dataseturi"] = attribute.dataset.uri
    args[u"attributes"] = attribute.name
    args[u"acceptlanguages"] = u"fr"

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_getcapabilities_path(serv):
    app_path = request.url_root
    getcapabilities_path = url_join(app_path, serv.path)

    return getcapabilities_path
