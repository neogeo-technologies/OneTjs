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


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return "{}?{}".format(request.path, url_encode(args))
