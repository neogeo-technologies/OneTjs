# -*- coding: utf-8 -*-


class Framework(object):
    """Framework represents a spatial framework in the OGC TJS terminology
    spatial framework
    a GIS representation, either point, line, or polygon, of any collection of physical or conceptual geographic
    objects. Municipalities, postal code areas, telephone area codes, ecoregions, watersheds, road segments, fire
    stations, and lighthouses are all examples of spatial frameworks.

    One framework may be associated with more than one service.
    One service may be associated with more than one framework
    """

    def __init__(self, **kwargs):
        # Default values
        self.name = "default_framework_name"
        self.uri = None
        self.organization = None
        self.title = "Default framework title"
        self.abstract = "Default framework abstract"
        self.documentation = None
        self.version = None
        self.reference_date = None
        self.start_date = None
        self.key_col = {"name": None, "type": None, "length": None, "decimals": None}
        self.bbox = {"south": -90, "north": 90, "west": -180, "east": 180}

        self.__dict__.update(kwargs)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
