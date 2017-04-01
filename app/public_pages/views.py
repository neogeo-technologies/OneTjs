# -*- coding: utf-8 -*-

import os

from flask import request
from flask import render_template
from flask import send_from_directory
from flask import Blueprint

from werkzeug.urls import url_encode

from app import app

public_blueprint = Blueprint('public_pages', __name__, template_folder="templates")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template("index.html", init_success=app.init_success)


@app.route("/services/")
def services():
    return render_template("services_list.html", services=app.services_manager.get_services())


@app.route("/services/<service_name>")
def service(service_name):
    this_service = app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    return render_template("service.html", service=this_service)


@app.route("/frameworks/")
def frameworks():
    return render_template("frameworks_list.html", services=app.services_manager.get_services())


@app.route("/services/<service_name>/frameworks/<framework_name>")
def framework(service_name, framework_name):

    this_service = app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    this_framework = this_service.get_framework_with_name(framework_name)

    # If the framework does not exist -> 404
    if this_framework is None:
        return render_template("error.html", error_code=404), 404

    return render_template("framework.html", framework=this_framework)


@app.route("/datasets/")
def datasets():
    return render_template("datasets_list.html", services=app.services_manager.get_services())


@app.route("/services/<service_name>/datasets/<dataset_name>")
def dataset(service_name, dataset_name):
    this_service = app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    this_dataset = this_service.get_dataset_with_name(dataset_name)

    # If the dataset does not exist -> 404
    if this_dataset is None:
        return render_template("error.html", error_code=404), 404

    return render_template("dataset.html", dataset=this_dataset,
                           data=this_dataset.get_data())
