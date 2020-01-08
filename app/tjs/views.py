# -*- coding: utf-8 -*-

from flask import render_template
from flask import make_response
from flask import request
from flask import redirect
from flask import Blueprint

from flask import current_app

try:
    import urllib.parse
    from urllib.parse import urlencode
except:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

from distutils.version import StrictVersion as Version
from collections import OrderedDict

from app import utils

SUPPORTED_VERSIONS = (Version("1.0"),)

tjs_blueprint = Blueprint("tjs", __name__, template_folder="templates")
tjs_geoclip_blueprint = Blueprint("tjs_geoclip", __name__, template_folder="templates")


@tjs_blueprint.route("/tjs/<service_name>", methods=["GET"])
@tjs_geoclip_blueprint.route("/tjs_geoclip/<service_name>", methods=["GET"])
def tjs_operation(service_name):
    """
    Function responding to every TJS request and calling specialized functions for each TJS operation.
    This function checks the validity of the more common TJS parameters.

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []
    right_service_type = True

    args = get_normalized_args()
    arg_service = args.get("service")
    arg_operation = args.get("request")

    blueprint_name = request.blueprint

    # Service instance
    service = current_app.services_manager.get_service_with_name(service_name)

    # If the service does not exist or is not activated -> 404
    if service is None or not service.activated:
        return render_template("error.html", error_code=404), 404

    # if no parameters, redirect to getcapabilities request
    if len(args) == 0:
        getcap_url = get_getcapabilities_url(serv=service)
        return redirect(getcap_url, code=302)

    # Missing service parameter
    if not arg_service:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! " "The 'service' parameter must be present.",
                "locator": "service",
            }
        )
        right_service_type = False

    # Wrong service name
    if arg_service and arg_service.lower() != "tjs":
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "The service type requested is not supported: {}. "
                "The only supported service type is TJS.".format(arg_service),
                "locator": "service={}".format(arg_service),
            }
        )
        right_service_type = False

    # Missing request parameter
    if not arg_operation:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! "
                "The 'request' parameter must be present. This TJS server cannot make a guess for this parameter.",
                "locator": "request",
            }
        )

    if arg_operation and right_service_type:

        # GetCapabilities
        if arg_operation.lower() == "getcapabilities":
            return get_capabilities(service, args, blueprint_name)

        # DescribeFrameworks
        elif arg_operation.lower() == "describeframeworks":
            return describe_frameworks(service, args, blueprint_name)

        # DescribeDatasets
        elif arg_operation.lower() == "describedatasets":
            return describe_datasets(service, args, blueprint_name)

        # DescribeData
        elif arg_operation.lower() == "describedata":
            return describe_data(service, args, blueprint_name)

        # GetData
        elif arg_operation.lower() == "getdata":
            return get_data(service, args, blueprint_name)

        # Unsupported operations
        elif arg_operation.lower() in (
            "describejoinabilities",
            "describekey",
            "joindata",
        ):
            exceptions.append(
                {
                    "code": "OperationNotSupported",
                    "text": "Oh là là ! "
                    "This operation is not supported by this TJS implementation: {}. "
                    "Supported operations are GetCapabilities, DescribeFrameworks, DescribeDatasets "
                    "and DescribeData.".format(arg_operation),
                    "locator": "request",
                }
            )

        # Unknown operations
        else:
            exceptions.append(
                {
                    "code": "InvalidParameterValue",
                    "text": "Oh là là ! "
                    "This operation is not a TJS operation: {}. "
                    "Supported operations are GetCapabilities, DescribeFrameworks, DescribeDatasets "
                    "and DescribeData.".format(arg_operation),
                    "locator": "request={}".format(arg_operation),
                }
            )

    raise OwsCommonException(exceptions=exceptions)


def get_normalized_args():
    """
    Function converting parameter names to lowercase strings

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    normalized_args = {}
    args = request.args

    for key, value in list(args.items()):
        normalized_args[key.lower()] = value

    return normalized_args


def get_capabilities(serv, args, blueprint_name):
    """
    Function used to answer to GetCapabilities requests

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []

    arg_accept_versions = args.get("acceptversions")
    # TODO: handle language parameter
    arg_language = args.get("language")

    tjs_version = None

    if arg_accept_versions:
        accepted_and_supported_versions = []

        for vrs in arg_accept_versions.split(","):
            try:
                strict_vrs = Version(vrs)
                for supported_vrs in SUPPORTED_VERSIONS:
                    if strict_vrs == supported_vrs:
                        accepted_and_supported_versions.append(strict_vrs)
            except ValueError as e:
                exceptions.append(
                    {
                        "code": "VersionNegotiationFailed",
                        "text": "Oh là là ! " "{}".format(e.message),
                        "locator": "acceptversions",
                    }
                )

        if accepted_and_supported_versions:
            tjs_version = str(accepted_and_supported_versions[0])
            print(tjs_version)
        else:
            exceptions.append(
                {
                    "code": "VersionNegotiationFailed",
                    "text": "Oh là là ! "
                    "The 'acceptversions' does not include any version supported by this server."
                    "Supported versions are: {}".format(
                        ",".join([str(vrs) for vrs in SUPPORTED_VERSIONS])
                    ),
                    "locator": "acceptversions",
                }
            )
    else:
        tjs_version = str(SUPPORTED_VERSIONS[0])

    if tjs_version == "1.0":
        template_name = blueprint_name + "/tjs_100_getcapabilities.xml"

        # TODO: handle language parameter
        arg_language = serv.languages[0]

        response_content = render_template(
            template_name,
            service=serv,
            tjs_version=tjs_version,
            onetjs_version=current_app.version,
        )
        response_content = utils.prettify_xml(
            xml_string=response_content, minify=not current_app.debug
        )
        response = make_response(response_content)
        response.headers["Content-Type"] = "application/xml"

        return response

    raise OwsCommonException(exceptions=exceptions)


def describe_frameworks(serv, args, blueprint_name):
    """
    Function used to answer to DescribeFrameworks requests

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []

    arg_version = args.get("version")
    # TODO: handle language parameter
    arg_language = args.get("language")
    arg_framework_uri = args.get("frameworkuri")

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    if arg_framework_uri:
        framework_uris = [item.strip() for item in arg_framework_uri.split(",")]
        frameworks = [serv.get_framework_with_uri(uri) for uri in framework_uris]
    else:
        frameworks = list(serv.get_frameworks())

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = blueprint_name + "/tjs_100_describeframeworks.xml"
    else:
        # TJS exception
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "This version of the TJS specifications is not supported by this TJS implementation: {}. "
                "Supported version numbers are: {}.".format(
                    arg_version, ", ".join(SUPPORTED_VERSIONS)
                ),
                "locator": "version={}".format(arg_version),
            }
        )

        raise OwsCommonException(exceptions=exceptions)

    response_content = render_template(
        template_name,
        service=serv,
        frameworks=frameworks,
        tjs_version=arg_version,
        language=arg_language,
        onetjs_version=current_app.version,
    )
    response_content = utils.prettify_xml(
        xml_string=response_content, minify=not current_app.debug
    )
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    return response


def describe_datasets(serv, args, blueprint_name):
    """
    Function used to answer to DescribeDatasets requests

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []

    arg_version = args.get("version")
    # TODO: handle language parameter
    arg_language = args.get("language")
    arg_framework_uri = args.get("frameworkuri")
    arg_dataset_uri = args.get("dataseturi")

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    framework_uri = None
    if arg_framework_uri:
        framework_uris = [item.strip() for item in arg_framework_uri.split(",")]
        if len(framework_uris) > 1:
            # TJS exception
            exceptions.append(
                {
                    "code": "InvalidParameterValue",
                    "text": "Oh là là ! "
                    "The frameworkuri parameter of the DescribeDatasets operation can only contain one uri. ",
                    "locator": "frameworkuri={}".format(arg_framework_uri),
                }
            )

            raise OwsCommonException(exceptions=exceptions)
        framework_uri = framework_uris[0]

    dataset_uri = None
    if arg_dataset_uri:
        dataset_uris = [item.strip() for item in arg_dataset_uri.split(",")]
        if len(dataset_uris) > 1:
            # TJS exception
            exceptions.append(
                {
                    "code": "InvalidParameterValue",
                    "text": "Oh là là ! "
                    "The dataseturi parameter of the DescribeDatasets operation can only contain one uri. ",
                    "locator": "dataseturi={}".format(arg_dataset_uri),
                }
            )

            raise OwsCommonException(exceptions=exceptions)
        dataset_uri = dataset_uris[0]

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = blueprint_name + "/tjs_100_describedatasets.xml"
    else:
        # TJS exception
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "This version of the TJS specifications is not supported by this TJS implementation: {}. "
                "Supported version numbers are: {}.".format(
                    arg_version, ", ".join(SUPPORTED_VERSIONS)
                ),
                "locator": "version={}".format(arg_version),
            }
        )

        raise OwsCommonException(exceptions=exceptions)

    response_content = render_template(
        template_name,
        service=serv,
        tjs_version=arg_version,
        language=arg_language,
        framework_uri=framework_uri,
        dataset_uri=dataset_uri,
        onetjs_version=current_app.version,
    )
    response_content = utils.prettify_xml(
        xml_string=response_content, minify=not current_app.debug
    )
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    return response


def describe_data(serv, args, blueprint_name):
    """
    Function used to answer to DescribeData requests

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []

    arg_version = args.get("version")
    # TODO: handle language parameter
    arg_language = args.get("language")
    arg_framework_uri = args.get("frameworkuri")
    arg_dataset_uri = args.get("dataseturi")
    arg_attributes = args.get("attributes")

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    framework_uri = None
    if arg_framework_uri:
        framework_uris = [item.strip() for item in arg_framework_uri.split(",")]
        if len(framework_uris) > 1:
            # TJS exception
            exceptions.append(
                {
                    "code": "InvalidParameterValue",
                    "text": "Oh là là ! "
                    "The frameworkuri parameter of the DescribeData operation can only contain one uri. ",
                    "locator": "frameworkuri={}".format(arg_framework_uri),
                }
            )
        framework_uri = framework_uris[0]
    else:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! " "The 'frameworkuri' parameter must be present.",
                "locator": "frameworkuri",
            }
        )

    dataset_uri = None
    if arg_dataset_uri:
        dataset_uris = [item.strip() for item in arg_dataset_uri.split(",")]
        if len(dataset_uris) > 1:
            # TJS exception
            exceptions.append(
                {
                    "code": "InvalidParameterValue",
                    "text": "Oh là là ! "
                    "The dataseturi parameter of the DescribeData operation can only contain one uri. ",
                    "locator": "dataseturi={}".format(arg_dataset_uri),
                }
            )
        dataset_uri = dataset_uris[0]
    else:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! " "The 'dataseturi' parameter must be present.",
                "locator": "dataseturi",
            }
        )

    # Check if the frameworkuri and dataseturi values are compatible
    dtst = serv.get_dataset_with_uri(dataset_uri)
    frwk = serv.get_framework_with_uri(framework_uri)
    if frwk not in dtst.get_frameworks():
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "The specified framework is not available for the specified dataseturi.",
                "locator": "frameworkuri",
            }
        )

    # Retrieve the DatasetAttribute records
    dtst_attributes = []
    if arg_attributes:
        attributes_names = [
            attribute_name.strip() for attribute_name in arg_attributes.split(",")
        ]
        for attribute_name in attributes_names:
            attribute = dtst.get_attribute_with_name(attribute_name)
            if attribute is None:
                exceptions.append(
                    {
                        "code": "InvalidParameterValue",
                        "text": "Oh là là ! "
                        "The requested attribute is not valid: {}.".format(
                            attribute_name
                        ),
                        "locator": "attributes={}".format(arg_attributes),
                    }
                )
            else:
                dtst_attributes.append(attribute)
    else:
        dtst_attributes = dtst.ds_attributes

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = blueprint_name + "/tjs_100_describedata.xml"
    else:
        # TJS exception
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "This version of the TJS specifications is not supported by this TJS implementation: {}. "
                "Supported version numbers are: {}.".format(
                    arg_version, ", ".join(SUPPORTED_VERSIONS)
                ),
                "locator": "version={}".format(arg_version),
            }
        )

    if exceptions:
        raise OwsCommonException(exceptions=exceptions)

    response_content = render_template(
        template_name,
        service=serv,
        tjs_version=arg_version,
        language=arg_language,
        framework=frwk,
        dataset=dtst,
        attributes=dtst_attributes,
        onetjs_version=current_app.version,
    )
    response_content = utils.prettify_xml(
        xml_string=response_content, minify=not current_app.debug
    )
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    return response


def get_data(serv, args, blueprint_name):
    """
    Function used to answer to GetData requests

    :param serv:    Service object
    :param args:    parameters of the TJS request
    :return:        request response
    """

    exceptions = []

    arg_version = args.get("version")
    # TODO: handle language parameter
    arg_language = args.get("language")
    arg_framework_uri = args.get("frameworkuri")
    arg_dataset_uri = args.get("dataseturi")
    arg_attributes = args.get("attributes")
    # TODO: handle linkagekeys parameter
    arg_linkage_keys = args.get("linkagekeys")
    # TODO: handle xsl parameter
    arg_xsl = args.get("xsl")
    # TODO: handle aid parameter
    arg_aid = args.get("aid")

    # Get the jinja template corresponding to the TJS specifications version
    if arg_version in ("1.0",):
        template_name = blueprint_name + "/tjs_100_getdata.xml"
    else:
        # TJS exception
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "This version of the TJS specifications is not supported by this TJS implementation: {}. "
                "Supported version numbers are: {}.".format(
                    arg_version, ", ".join(SUPPORTED_VERSIONS)
                ),
                "locator": "version={}".format(arg_version),
            }
        )

        raise OwsCommonException(exceptions=exceptions)

    # TODO: handle language parameter
    arg_language = serv.languages[0]

    # Missing frameworkuri parameter
    if not arg_framework_uri:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! "
                "The 'frameworkuri' parameter is mandatory for GetData operation. "
                "This TJS server cannot make a guess for this parameter.",
                "locator": "frameworkuri",
            }
        )

    # Missing dataseturi parameter
    if not arg_dataset_uri:
        exceptions.append(
            {
                "code": "MissingParameterValue",
                "text": "Oh là là ! "
                "The 'dataseturi' parameter is mandatory for GetData operation. "
                "This TJS server cannot make a guess for this parameter.",
                "locator": "dataseturi",
            }
        )

    if not (arg_framework_uri and arg_dataset_uri):
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the Framework record
    frwk = serv.get_framework_with_uri(arg_framework_uri)
    if frwk is None:
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "The parameter value for 'frameworkuri' is not valid: {}.".format(
                    arg_framework_uri
                ),
                "locator": "frameworkuri={}".format(arg_framework_uri),
            }
        )
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the Dataset record
    dtst = serv.get_dataset_with_uri(arg_dataset_uri)
    if dtst is None:
        exceptions.append(
            {
                "code": "InvalidParameterValue",
                "text": "Oh là là ! "
                "The parameter value for 'dataseturi' is not valid: {}.".format(
                    arg_dataset_uri
                ),
                "locator": "dataseturi={}".format(arg_dataset_uri),
            }
        )
        raise OwsCommonException(exceptions=exceptions)

    # Retrieve the DatasetAttribute records
    dtst_attributes = []
    if arg_attributes:
        attributes_names = [
            attribute_name.strip() for attribute_name in arg_attributes.split(",")
        ]
        for attribute_name in attributes_names:
            attribute = dtst.get_attribute_with_name(attribute_name)
            if attribute is None:
                exceptions.append(
                    {
                        "code": "InvalidParameterValue",
                        "text": "Oh là là ! "
                        "The requested attribute is not valid: {}.".format(
                            attribute_name
                        ),
                        "locator": "attributes={}".format(arg_attributes),
                    }
                )
            else:
                dtst_attributes.append(attribute)
        if len(attributes_names) != len(dtst_attributes):
            raise OwsCommonException(exceptions=exceptions)
    else:
        dtst_attributes = dtst.ds_attributes

    # TODO: handle the complete set of parameters declared in the TJS specification

    # Create a pandas data frame from the dataset datasource
    try:
        data = dtst.get_data(attributes=dtst_attributes, framework=frwk)
    except ValueError as e:
        current_app.logger.error(e.message)
        data = None

    # TODO: handle correctly empty pd_dataframe (None for example)
    response_content = render_template(
        template_name,
        service=serv,
        tjs_version=arg_version,
        language=arg_language,
        framework=frwk,
        dataset=dtst,
        attributes=dtst_attributes,
        data=data,
        onetjs_version=current_app.version,
    )
    response_content = utils.prettify_xml(
        xml_string=response_content, minify=not current_app.debug
    )
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"

    # if dtst.cached:
    #     max_age = dtst.cache_max_age or 3600
    #     response.cache_control.max_age = max_age
    #     response.cache_control.public = True

    return response


class OwsCommonException(Exception):
    """
    Class representing the exceptions described in the TJS standard.
    """

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
        self.message = "\n".join(
            [exception.get("text") for exception in self.exceptions]
        )


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_service_url(serv, geoclip=False):
    """
    Function building the URL to a service with specific blueprint (tjs/tjs_geoclip).

    :param serv:    Service instance
    :return:        URL
    """
    app_path = request.url_root
    blueprint_name = request.blueprint

    if blueprint_name == "public_pages":
        if geoclip == True:
            service_url = urllib.parse.urljoin(
                app_path, "/".join(("tjs_geoclip", serv.name))
            )
        else:
            service_url = urllib.parse.urljoin(app_path, "/".join(("tjs", serv.name)))
    else:
        service_url = urllib.parse.urljoin(
            app_path, "/".join((blueprint_name, serv.name))
        )
    return service_url


@tjs_blueprint.errorhandler(OwsCommonException)
@tjs_geoclip_blueprint.errorhandler(OwsCommonException)
def handle_tjs_exception(error):

    if error.tjs_version in ("1.0",):
        template_name = "ows_common_110_exception.xml"
    else:
        template_name = "ows_common_110_exception.xml"

    response_content = render_template(template_name, exceptions=error.exceptions)
    response_content = utils.prettify_xml(
        xml_string=response_content, minify=not current_app.debug
    )
    response = make_response(response_content)
    response.headers["Content-Type"] = "application/xml"
    response.status_code = error.status_code
    return response


def build_tjs_url(service, args):
    service_url = get_service_url(service)

    url_parts = list(urllib.parse.urlparse(service_url))
    query = OrderedDict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(args)
    url_parts[4] = urlencode(query)

    tjs_url = urllib.parse.urlunparse(url_parts)
    return tjs_url


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_getcapabilities_url(serv, language=None):
    args = OrderedDict()
    args["service"] = "TJS"
    args["request"] = "GetCapabilities"
    if language:
        args["language"] = language

    url = build_tjs_url(serv, args)
    return url


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_describeframeworks_url(serv, tjs_version=None, language=None, framework=None):
    args = OrderedDict()
    args["service"] = "TJS"
    if tjs_version:
        args["version"] = tjs_version
    else:
        args["version"] = serv.tjs_versions[-1]
    args["request"] = "DescribeFrameworks"
    if framework:
        args["frameworkuri"] = framework.uri
    if language:
        args["language"] = language

    url = build_tjs_url(serv, args)
    return url


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_describedatasets_url(
    serv, tjs_version=None, language=None, framework=None, dataset=None
):
    args = OrderedDict()
    args["service"] = "TJS"
    if tjs_version:
        args["version"] = tjs_version
    else:
        args["version"] = serv.tjs_versions[-1]
    args["request"] = "DescribeDatasets"
    if framework:
        args["frameworkuri"] = framework.uri
    if dataset:
        args["dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args["frameworkuri"] = dataset.get_one_framework().uri
    if language:
        args["language"] = language

    url = build_tjs_url(serv, args)
    return url


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_describedata_url(
    serv, tjs_version=None, language=None, framework=None, dataset=None, attributes=None
):
    args = OrderedDict()
    args["service"] = "TJS"
    if tjs_version:
        args["version"] = tjs_version
    else:
        args["version"] = serv.tjs_versions[-1]
    args["request"] = "DescribeData"
    if framework:
        args["frameworkuri"] = framework.uri
    if dataset:
        args["dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args["frameworkuri"] = dataset.get_one_framework().uri
    if attributes:
        args["attributes"] = ",".join([at.name for at in attributes])
    if language:
        args["language"] = language

    url = build_tjs_url(serv, args)
    return url


@tjs_blueprint.app_template_global()
@tjs_geoclip_blueprint.app_template_global()
def get_getdata_url(
    serv, tjs_version=None, dataset=None, framework=None, attributes=None
):
    args = OrderedDict()
    args["service"] = "TJS"
    if tjs_version:
        args["version"] = tjs_version
    else:
        args["version"] = serv.tjs_versions[-1]
    args["request"] = "GetData"
    if framework:
        args["frameworkuri"] = framework.uri
    if dataset:
        args["dataseturi"] = dataset.uri
        if not framework and dataset.frameworks:
            args["frameworkuri"] = dataset.get_one_framework().uri
    if dataset and attributes:
        consolidated_attributes = []

        # Add attributes that are not of "Attribute" type
        for at in dataset.ds_attributes:
            if at in attributes or at.purpose != "Attribute":
                consolidated_attributes.append(at)

        args["attributes"] = ",".join(
            [attribute.name for attribute in consolidated_attributes]
        )

    url = build_tjs_url(serv, args)
    return url
