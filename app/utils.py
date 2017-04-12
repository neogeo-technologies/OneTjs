# -*- coding: utf-8 -*-

import xml.dom.minidom as minidom
import os


def u(s):
    """
    decodes utf8
    """
    if isinstance(s, unicode):
        return s.encode("utf-8")
    if isinstance(s, str):
        return s.decode("utf-8")
    # fix this, item may be unicode
    elif isinstance(s, list):
        return [i.decode("utf-8") for i in s]


def prettify_xml(xml_string, minify=False, indent="  ", newl=os.linesep):
    """
    Function prettifying or minifying an xml string

    :param xml_string:  The XML string to prettify or minify
    :param minify:      True for minification and False for prettification
    :param indent:      String used for indentation
    :param newl:        String used for new lines
    :return:            An XML string
    """

    # Function used to remove XML blank nodes
    def remove_blanks(node):
        for x in node.childNodes:
            if x.nodeType == minidom.Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == minidom.Node.ELEMENT_NODE:
                remove_blanks(x)

    xml = minidom.parseString(u(xml_string))
    remove_blanks(xml)
    xml.normalize()

    if minify:
        pretty_xml_as_string = xml.toxml()
    else:
        pretty_xml_as_string = xml.toprettyxml(indent=indent, newl=newl)

    return pretty_xml_as_string
