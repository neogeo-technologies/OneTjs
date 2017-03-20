# -*- coding: utf-8 -*-

import os

from flask import request
from flask import render_template
from flask import send_from_directory
from flask import Blueprint

from werkzeug.urls import url_encode

from app import app

from app.models import Framework
from app.models import Dataset

public_blueprint = Blueprint('public_pages', __name__, template_folder="templates")

# TODO: create a public view listing the datasets, the relations with datasources, dataattributes, framwroks, services
# TODO: and previewing the data


# def render_object_list(template_name, query, paginate_by=10, **context):
#     page = request.args.get("page")
#     if page and page.isdigit():
#         page = int(page)
#     else:
#         page = 1
#
#     object_list = query.paginate(page, paginate_by)
#
#     return render_template(template_name, object_list=object_list, **context)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template("index.html", cfg=app.config)


@app.route("/services/")
def services():
    return render_template("services_list.html", services=app.services_manager.get_services(), cfg=app.config)


@app.route("/services/<service_name>")
def service(service_name):
    this_service = app.services_manager.get_service_with_name(service_name)
    return render_template("service.html", service=this_service, cfg=app.config)


@app.route("/frameworks/")
def frameworks():
    return render_template("frameworks_list.html", services=app.services_manager.get_services(), cfg=app.config)


@app.route("/services/<service_name>/frameworks/<framework_name>")
def framework(service_name, framework_name):
    this_service = app.services_manager.get_service_with_name(service_name)
    this_framework = this_service.get_framework_with_name(framework_name)
    return render_template("framework.html", framework=this_framework, cfg=app.config)


@app.route("/datasets/")
def datasets():
    return render_template("datasets_list.html", services=app.services_manager.get_services(), cfg=app.config)


@app.route("/services/<service_name>/datasets/<dataset_name>")
def dataset(service_name, dataset_name):
    this_service = app.services_manager.get_service_with_name(service_name)
    this_dataset = this_service.get_dataset_with_name(dataset_name)
    return render_template("dataset.html", dataset=this_dataset, cfg=app.config)


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return "{}?{}".format(request.path, url_encode(args))
