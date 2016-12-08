# -*- coding: utf-8 -*-


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
