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


@tjs_blueprint.route("/tjs/", methods=['GET', 'POST'])
def tjs_operation():
    exceptions = []
    right_service_type = True

    args = get_normalized_args()
    arg_service = args.get('service')
    arg_operation = args.get('request')

    # Missing service parameter
    if not arg_service:
        exceptions.append({
            "code": u"MissingParameterValue",
            "text": u"Oh là là ! "
                    u"The service parameter must be present.",
            "locator": u"service"})
        right_service_type = False

    # Wrong service name
    if arg_service and arg_service.lower() != "tjs":
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"The service type requested is not supported: {}. "
                    u"The only supported service type is TJS.".format(arg_service),
            "locator": u"service={}".format(arg_service)})
        right_service_type = False

    # Missing request parameter
    if not arg_operation:
        exceptions.append({
            "code": u"MissingParameterValue",
            "text": u"Oh là là ! "
                    u"The request parameter must be present. This TJS server cannot make a guess for this parameter.",
            "locator": u"request"})

    if arg_operation and right_service_type:

        # GetCapabilities
        if arg_operation.lower() == "getcapabilities":
            return get_data(args)

        # DescribeFrameworks
        elif arg_operation.lower() == "describeframeworks":
            return get_data(args)

        # DescribeDatasets
        elif arg_operation.lower() == "describedatasets":
            return get_data(args)

        # DescribeData
        elif arg_operation.lower() == "describedata":
            return get_data(args)

        # GetData
        elif arg_operation.lower() == "getdata":
            return get_data(args)

        # Unsupported operations
        elif arg_operation.lower() in ("describejoinabilities", "describekey", "joindata"):
            exceptions.append({
                "code": u"OperationNotSupported",
                "text": u"Oh là là ! "
                        u"This operation is not supported by this TJS implementation: {}. "
                        u"Supported operations are GetCapabilities, DescribeFrameworks, DescribeDatasets "
                        u"and DescribeData.".format(arg_operation),
                "locator": u"request"})

        # Unknown operations
        else:
            exceptions.append({
                "code": u"InvalidParameterValue",
                "text": u"Oh là là ! "
                        u"This operation is not a TJS operation: {}. "
                        u"Supported operations are GetCapabilities, DescribeFrameworks, DescribeDatasets "
                        u"and DescribeData.".format(arg_operation),
                "locator": u"request={}".format(arg_operation)})

    raise OwsCommonException(exceptions=exceptions)


def get_normalized_args():
    normalized_args = {}
    args = request.args

    for key, value in args.iteritems():
        normalized_args[key.lower()] = value

    return normalized_args


def get_data(args):
    exceptions = []

    arg_version = args.get('version')
    arg_framework_uri = args.get('frameworkuri')
    arg_dataset_uri = args.get('dataseturi')
    arg_attributes = args.get('attributes')
    arg_linkage_keys = args.get('linkagekeys')
    arg_xsl = args.get('xsl')
    arg_aid = args.get('aid')

    # Retrieve the service record
    service_path = [part for part in request.path.split("/") if part != ""][0]
    serv = Service.query.filter(Service.path == service_path).first()

    # Retrieve the dataset record
    ds = Dataset.query.first()

    # TODO: manage the complete set of operations parameters declared in the TJS specification

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = "tjs_100_getdata.xml"
    else:
        # TJS exception
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"This version of the TJS specifications is not supported by this TJS implementation: {}. "
                    u"Supported operations are GetCapabilities, DescribeFrameworks, DescribeDatasets "
                    u"and DescribeData.".format(arg_version),
            "locator": u"version={}".format(arg_version)})

        raise OwsCommonException(exceptions=exceptions)


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


class OwsCommonException(Exception):
    status_code = 400
    tjs_version = "1.0"

    # OperationNotSupported
    #     Request is for an operation that is not supported by this server
    #     Name of operation not supported
    #
    # OptionNotSupported
    #     Request is for an option that is not supported by this server
    #     Identifier of option not supported
    #
    # InvalidUpdateSequence
    #     Value of(optional) updateSequence parameter, in GetCapabilities operation request, is greater than current value of service metadata updateSequence number
    #     None, omit “locator” parameter
    #
    # MissingParameterValue
    #     Operation request does not include a parameter value
    #     Name of missing parameter
    #
    # InvalidParameterValue
    #     Operation request contains an invalid parameter value
    #     Name of parameter with invalid value
    #
    # VersionNegotiationFailed
    #     List of versions in “AcceptVersions” parameter value, in GetCapabilities operation request, did not include any version supported by this server
    #     None, omit “locator” parameter
    #
    # NoApplicableCode
    #     No other exceptionCode specified by this service and server applies to this exception
    #     None, omit “locator” parameter
    #
    # InvalidAttributeName
    #     Operation request included an attribute identifier not available for the requested dataset
    #     Name of invalid attribute
    #
    # InvalidKey
    #     Operation request included a Key that does not exist for the requested dataset
    #     Identifier of invalid Key

    def __init__(self, exceptions=None, status_code=None):
        Exception.__init__(self)
        if status_code is not None:
            self.status_code = status_code
        self.exceptions = exceptions
        self.message = u"\n".join([exception.get("text") for exception in self.exceptions])


@app.errorhandler(OwsCommonException)
def handle_tjs_exception(error):
    if error.tjs_version in ("1.0",):
        template_name = "ows_common_110_exception.xml"
    else:
        template_name = "ows_common_110_exception.xml"

    response_content = render_template(template_name, exceptions=error.exceptions)
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"
    response.status_code = error.status_code
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
