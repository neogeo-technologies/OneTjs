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
from flask.ext.admin.form import rules
# from flask.ext.admin.contrib.sqla.filters import FilterEqual
# from flask.ext.admin.contrib.sqla.filters import BaseSQLAFilter


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

# TODO: only admin users should have access to the admin views

# TODO: use secure forms with Falsk-Admin:
# http://flask-admin.readthedocs.io/en/latest/advanced/#enabling-csrf-protection

# TODO: create an admin view for symplifying the creation of datasets and datsetattribute records
# TODO: (just by selecting a datasource and a table)

# TODO: create a view listing the datasets, the relations with datasources, dataattributes, framwroks, services
# TODO: and previewing the data


class ServiceView(ModelView):
    can_view_details = True
    column_list = (
        Service.title,
        Service.path,
        Service.activated
    )
    column_details_list = (
        Service.id,
        Service.path,
        Service.title,
        Service.abstract,
        Service.tjs_versions,
        Service.language,
        Service.activated
    )


class DataSourceView(ModelView):
    can_view_details = True
    column_list = (
        DataSource.title,
        DataSource.type,
        DataSource.connect_string
    )
    column_details_list = (
        DataSource.id,
        DataSource.title,
        DataSource.type,
        DataSource.connect_string
    )
    column_filters = (DataSource.title, DataSource.type, DataSource.connect_string)
    form_choices = {
        "type": [
            ('db', u'Base relationnelle'),
            ('csv', u'Fichier CSV'),
            ('xls', u'Fichier Excel')
        ]
    }


# TODO: allow long text edition for abstract of Framework (multiple lines edit box)
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
    form_choices = {
        "key_col_type": [
            ('https://www.w3.org/TR/xmlschema-2/#integer', u'Nombre entier'),
            ('https://www.w3.org/TR/xmlschema-2/#decimal', u'Nombre décimal'),
            ('https://www.w3.org/TR/xmlschema-2/#float', u'Nombre réel'),
            ('https://www.w3.org/TR/xmlschema-2/#string', u'Chaîne de caractères'),
            ('https://www.w3.org/TR/xmlschema-2/#boolean', u'Booléen')
        ]
    }
    column_filters = (Framework.title, Framework.abstract, Framework.organization)


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
        Dataset.title,
        Dataset.abstract,
        Dataset.organization,
        Dataset.version,
        Dataset.reference_date,
        Dataset.start_date,
        'data_source.title',
        Dataset.data_source_subset,
        'framework.uri',
        'attributes',
        Dataset.activated,
        Dataset.cached,
        Dataset.cache_max_age,
        Dataset.documentation
    )
    column_filters = (Dataset.title, Dataset.abstract)


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
        DatasetAttribute.name,
        DatasetAttribute.title,
        DatasetAttribute.abstract,
        DatasetAttribute.type,
        DatasetAttribute.length,
        DatasetAttribute.decimals,
        DatasetAttribute.purpose,
        DatasetAttribute.values,
        DatasetAttribute.uom_short_form,
        DatasetAttribute.uom_long_form,
        DatasetAttribute.documentation
    )
    form_choices = {
        "purpose": [
            ('Attribute', u'Attribute'),
            ('SpatialComponentIdentifier', u'SpatialComponentIdentifier'),
            ('SpatialComponentProportion', u'SpatialComponentProportion'),
            ('SpatialComponentPercentage', u'SpatialComponentPercentage'),
            ('TemporalIdentifier', u'TemporalIdentifier'),
            ('TemporalValue', u'TemporalValue'),
            ('VerticalIdentifier', u'VerticalIdentifier'),
            ('VerticalValue', u'VerticalValue'),
            ('OtherSpatialIdentifier', u'OtherSpatialIdentifier'),
            ('NonSpatialIdentifer', u'NonSpatialIdentifer')
        ],
        "values": [
            ('Count', u'Dénombrement'),
            ('Measure', u'Mesure'),
            ('Ordinal', u'Valeur ordinale'),
            ('Nominal', u'Valeur symbolique / nominale')
        ],
        "type": [
            ('https://www.w3.org/TR/xmlschema-2/#integer', u'Nombre entier'),
            ('https://www.w3.org/TR/xmlschema-2/#decimal', u'Nombre décimal'),
            ('https://www.w3.org/TR/xmlschema-2/#float', u'Nombre réel'),
            ('https://www.w3.org/TR/xmlschema-2/#string', u'Chaîne de caractères'),
            ('https://www.w3.org/TR/xmlschema-2/#boolean', u'Booléen')
        ]
    }
    column_filters = (DatasetAttribute.name,
                      DatasetAttribute.title,
                      DatasetAttribute.abstract,
                      DatasetAttribute.values)
    form_create_rules = [
        rules.FieldSet(("name", "title", "abstract"), u'Identification'),
        rules.FieldSet(("type", "length", "decimals", "purpose", "values"), u'Typologie'),
        rules.FieldSet(("uom_short_form", "uom_long_form"), u'Unité'),
        rules.FieldSet(("documentation",), u'Autres')
    ]

    # Use same rule set for edit page
    form_edit_rules = form_create_rules


admin.add_view(ServiceView(Service, db.session))
admin.add_view(DataSourceView(DataSource, db.session))
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
