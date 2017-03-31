# -*- coding: utf-8 -*-

from flask import render_template
from flask import make_response
from flask import request
from flask import redirect
from flask import Blueprint

from werkzeug.urls import url_encode
from werkzeug.urls import url_join

from app import app

SUPPORTED_VERSIONS = ["1.0"]

tjs_blueprint = Blueprint('tjs', __name__, template_folder="templates")


@tjs_blueprint.route("/tjs/<service_name>", methods=['GET', 'POST'])
def tjs_operation(service_name):
    exceptions = []
    right_service_type = True

    args = get_normalized_args()
    arg_service = args.get('service')
    arg_operation = args.get('request')

    # Service instance
    service = app.services_manager.get_service_with_name(service_name)

    # If the service does not exist or is not activated -> 404
    if service is None or not service.activated:
        return render_template("error.html", error_code=404), 404

    # if no parameters, redirect to getcapabilities request
    if len(args) == 0:
        getcap_url = get_getcapabilities_url(serv=service)
        return redirect(getcap_url, code=302)

    # Missing service parameter
    if not arg_service:
        exceptions.append({
            "code": u"MissingParameterValue",
            "text": u"Oh là là ! "
                    u"The 'service' parameter must be present.",
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
                    u"The 'request' parameter must be present. This TJS server cannot make a guess for this parameter.",
            "locator": u"request"})

    if arg_operation and right_service_type:

        # GetCapabilities
        if arg_operation.lower() == "getcapabilities":
            return get_capabilities(service, args)

        # DescribeFrameworks
        elif arg_operation.lower() == "describeframeworks":
            return describe_frameworks(service, args)

        # DescribeDatasets
        elif arg_operation.lower() == "describedatasets":
            return get_data(service, args)

        # DescribeData
        elif arg_operation.lower() == "describedata":
            return get_data(service, args)

        # GetData
        elif arg_operation.lower() == "getdata":
            return get_data(service, args)

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


def get_capabilities(serv, args):
    exceptions = []

    # TODO: manage the complete set of operations parameters declared in the TJS specification
    arg_accept_versions = args.get('AcceptVersions')
    arg_sections = args.get('Sections')
    arg_accept_formats = args.get('AcceptFormats')
    arg_language = args.get('language')
    arg_update_sequence = args.get('updateSequence')

    # TODO: need a real version negociation process
    tjs_version = "1.0"
    template_name = "tjs_100_getcapabilities.xml"

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    response_content = render_template(template_name, service=serv, tjs_version=tjs_version)
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    return response


def describe_frameworks(serv, args):
    exceptions = []

    arg_version = args.get('version')
    arg_language = args.get('language')
    arg_framework_uri = args.get('frameworkuri')

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    if arg_framework_uri:
        framework_uris = [item.strip() for item in arg_framework_uri.split(",")]
        frameworks = [serv.get_framework_with_uri(uri) for uri in framework_uris]
    else:
        frameworks = list(serv.get_frameworks())

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = "tjs_100_describeframeworks.xml"
    else:
        # TJS exception
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"This version of the TJS specifications is not supported by this TJS implementation: {}. "
                    u"Supported version numbers are: {}.".format(arg_version, ", ".join(SUPPORTED_VERSIONS)),
            "locator": u"version={}".format(arg_version)})

        raise OwsCommonException(exceptions=exceptions)

    response_content = render_template(template_name, service=serv, frameworks=frameworks,
                                       tjs_version=arg_version, language=arg_language)
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    return response


def get_data(serv, args):
    exceptions = []

    arg_version = args.get('version')
    arg_language = args.get('language')
    arg_framework_uri = args.get('frameworkuri')
    arg_dataset_uri = args.get('dataseturi')
    arg_attributes = args.get('attributes')
    arg_linkage_keys = args.get('linkagekeys')
    arg_xsl = args.get('xsl')
    arg_aid = args.get('aid')

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = "tjs_100_getdata.xml"
    else:
        # TJS exception
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"This version of the TJS specifications is not supported by this TJS implementation: {}. "
                    u"Supported version numbers are: {}.".format(arg_version, ", ".join(SUPPORTED_VERSIONS)),
            "locator": u"version={}".format(arg_version)})

        raise OwsCommonException(exceptions=exceptions)

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    # Missing frameworkuri parameter
    if not arg_framework_uri:
        exceptions.append({
            "code": u"MissingParameterValue",
            "text": u"Oh là là ! "
                    u"The 'frameworkuri' parameter is mandatory for GetData operation. "
                    u"This TJS server cannot make a guess for this parameter.",
            "locator": u"frameworkuri"})

    # Missing dataseturi parameter
    if not arg_dataset_uri:
        exceptions.append({
            "code": u"MissingParameterValue",
            "text": u"Oh là là ! "
                    u"The 'dataseturi' parameter is mandatory for GetData operation. "
                    u"This TJS server cannot make a guess for this parameter.",
            "locator": u"dataseturi"})

    if not (arg_framework_uri and arg_dataset_uri):
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the Framework record
    # TODO: handle exception (can't retrieve Framework record)
    frwk = serv.get_framework_with_uri(arg_framework_uri)
    if frwk is None:
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"The parameter value for 'frameworkuri' is not valid: {}.".format(arg_framework_uri),
            "locator": u"frameworkuri={}".format(arg_framework_uri)})
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the Dataset record
    # TODO: handle exception (can't retrieve Dataset record)
    # dtst = Dataset.query.filter(Dataset.uri == arg_dataset_uri).first()
    dtst = serv.get_dataset_with_uri(arg_dataset_uri)
    if dtst is None:
        exceptions.append({
            "code": u"InvalidParameterValue",
            "text": u"Oh là là ! "
                    u"The parameter value for 'dataseturi' is not valid: {}.".format(arg_dataset_uri),
            "locator": u"dataseturi={}".format(arg_dataset_uri)})
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the DatasetAttribute records
    dtst_attributes = []
    if arg_attributes:
        attributes_names = [attribute_name.strip() for attribute_name in arg_attributes.split(",")]
        for attribute_name in attributes_names:
            attribute = dtst.get_attribute_with_name(attribute_name)
            if attribute is None:
                exceptions.append({
                    "code": u"InvalidParameterValue",
                    "text": u"Oh là là ! "
                            u"The requested attribute is not valid: {}.".format(attribute_name),
                    "locator": u"attributes={}".format(arg_attributes)})
            else:
                dtst_attributes.append(attribute)
        if len(attributes_names) != len(dtst_attributes):
            raise OwsCommonException(exceptions=exceptions)
    else:
        dtst_attributes = dtst.ds_attributes

    # TODO: manage the complete set of operations parameters declared in the TJS specification

    # Create a pandas data frame from the dataset datasource
    pd_dataframe = dtst.get_data(attributes=dtst_attributes, framework=frwk)

    # TODO: handle correctly empty pd_dataframe (None for example)
    response_content = render_template(template_name, service=serv, tjs_version=arg_version, language=arg_language,
                                       framework=frwk, dataset=dtst, attributes=dtst_attributes, data=pd_dataframe)
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    if dtst.cached:
        max_age = dtst.cache_max_age or 3600
        response.cache_control.max_age = max_age
        response.cache_control.public = True

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
    #     Value of(optional) updateSequence parameter, in GetCapabilities operation request, is greater than current
    #     value of service metadata updateSequence number
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
    #     List of versions in “AcceptVersions” parameter value, in GetCapabilities operation request, did not include
    #     any version supported by this server
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


@app.template_global()
def get_service_url(serv):
    app_path = request.url_root
    return url_join(app_path, "tjs/{}".format(serv.name))


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


# TODO: create a more generic build request function
# TODO: use ordereddict for request parameters
@app.template_global()
def get_getcapabilities_url(serv, language=None):
    service_url = get_service_url(serv)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"request"] = u"GetCapabilities"
    if language:
        args[u"language"] = language

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_describeframeworks_url(serv, tjs_version=None, language=None, framework=None):
    service_url = get_service_url(serv)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"request"] = u"DescribeFrameworks"
    if tjs_version:
        args[u"version"] = tjs_version
    if framework:
        args[u"frameworkuri"] = framework.uri
    if language:
        args[u"language"] = language

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_describedatasets_url(serv, tjs_version=None, language=None, framework=None, dataset=None):
    service_url = get_service_url(serv)
    args = dict()
    args[u"service"] = u"TJS"
    args[u"request"] = u"DescribeDatasets"
    if tjs_version:
        args[u"version"] = tjs_version
    if framework:
        args[u"frameworkuri"] = framework.uri
    if dataset:
        args[u"dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args[u"frameworkuri"] = dataset.get_one_framework().uri
    if language:
        args[u"language"] = language

    return "{}?{}".format(service_url, url_encode(args))


@app.template_global()
def get_describedata_url(serv, tjs_version=None, language=None, framework=None, dataset=None, attributes=None):
    service_url = get_service_url(serv)
    args = dict()
    args[u"service"] = u"TJS"
    if tjs_version:
        args[u"version"] = tjs_version
    args[u"request"] = u"DescribeData"
    if framework:
        args[u"frameworkuri"] = framework.uri
    if dataset:
        args[u"dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args[u"frameworkuri"] = dataset.get_one_framework().uri
    if attributes:
        args[u"attributes"] = ",".join([at.name for at in attributes])
    if language:
        args[u"language"] = language

    return "{}?{}".format(service_url, url_encode(args))


# TODO: make sure this function works fine for more than one attribute
@app.template_global()
def get_getdata_url(serv, tjs_version=None, dataset=None, framework=None, attribute=None):
    service_url = get_service_url(serv)
    args = dict()
    args[u"service"] = u"TJS"
    if tjs_version:
        args[u"version"] = tjs_version
    args[u"request"] = u"GetData"
    if framework:
        args[u"frameworkuri"] = framework.uri
    if dataset:
        args[u"dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args[u"frameworkuri"] = dataset.get_one_framework().uri
    if attribute:
        args[u"attributes"] = attribute.name

    return "{}?{}".format(service_url, url_encode(args))
