# -*- coding: utf-8 -*-


# TODO: documentation property of attributes are not supported at the moment.
# To do so, we would need a unique identifier per attribute

class DatasetAttribute(object):
    """DatasetAttribute represents an attribute of a dataset in the OGC TJS terminology
    One dataset attribute in associated with one and only one dataset
    """

    def __init__(self, **kwargs):
        # Default values
        self.dataset = None
        self.name = "default_attribute_name"
        self.tile = "Default attribute title"
        self.abstract = "Default attribute abstract"
        self.documentation = None
        self.type = None
        self.length = None
        self.decimals = None
        self.purpose = None
        self.values = None
        self.uom_short_form = None
        self.uom_long_form = None

        self.__dict__.update(kwargs)

    def __repr__(self):
        return u"%s(%r)" % (self.__class__, self.__dict__)