from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from formencode import validators


class URLString(validators.Regex):
    """
    Custom FormEncode validator to check if a field is a URLString (e.g. only
    alphanumeric characters, slashes, and hyphens).
    """
    regex = '^[a-z0-9\-\/]+$'
