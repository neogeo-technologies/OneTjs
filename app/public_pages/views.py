# -*- coding: utf-8 -*-

import os

from flask import render_template
from flask import send_from_directory
from flask import Blueprint
from flask import current_app

public_blueprint = Blueprint("public_pages", __name__, template_folder="templates")


@public_blueprint.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@public_blueprint.route("/")
def index():
    return render_template(
        "index.html",
        init_success=current_app.init_success,
        version=current_app.version
    )

@public_blueprint.route("/services/")
def services():
    return render_template(
        "services_list.html",
        services=current_app.services_manager.get_services(),
        version=current_app.version
    )


@public_blueprint.route("/services/<service_name>")
def service(service_name):
    this_service = current_app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    return render_template(
        "service.html",
        service=this_service,
        version=current_app.version
    )


@public_blueprint.route("/frameworks/")
def frameworks():
    return render_template(
        "frameworks_list.html",
        services=current_app.services_manager.get_services(),
        version=current_app.version
    )


@public_blueprint.route("/services/<service_name>/frameworks/<framework_name>")
def framework(service_name, framework_name):

    this_service = current_app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    this_framework = this_service.get_framework_with_name(framework_name)

    # If the framework does not exist -> 404
    if this_framework is None:
        return render_template("error.html", error_code=404), 404

    return render_template(
        "framework.html",
        framework=this_framework,
        version=current_app.version
    )


@public_blueprint.route("/datasets/")
def datasets():
    return render_template(
        "datasets_list.html",
        services=current_app.services_manager.get_services(),
        version=current_app.version
    )


@public_blueprint.route("/services/<service_name>/datasets/<dataset_name>")
def dataset(service_name, dataset_name):
    this_service = current_app.services_manager.get_service_with_name(service_name)

    # If the service does not exist -> 404
    if this_service is None:
        return render_template("error.html", error_code=404), 404

    this_dataset = this_service.get_dataset_with_name(dataset_name)

    # If the dataset does not exist -> 404
    if this_dataset is None:
        return render_template("error.html", error_code=404), 404

    try:
        data = this_dataset.get_data()
    except ValueError as e:
        current_app.logger.error(e.message)
        data = None

    return render_template(
        "dataset.html",
        dataset=this_dataset,
        data=data,
        version=current_app.version
    )
