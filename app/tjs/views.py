# -*- coding: utf-8 -*-

from flask import render_template
from flask import make_response
from flask import request
from flask import Blueprint

from werkzeug.urls import url_encode
from werkzeug.urls import url_join

from app import app

from app.models import Service
from app.models import Dataset

import data

tjs_blueprint = Blueprint('tjs', __name__, template_folder="templates")

# TODO: use standard operation names
@tjs_blueprint.route("/tjs/test/")
def test():
    serv = Service.query.first()
    ds = Dataset.query.first()
    tjs_version = "1.0"

    # TODO: manage the complete set of operations parameters declared in the TJS specification

    if tjs_version in ("1.0",):
        template_name = "tjs_100_getdata.xml"
    else:
        # TJS exception
        response_content = render_template("getdata.xml", service=serv, dataset=ds)
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
