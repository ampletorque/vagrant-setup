from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from webhelpers2.html.tags import HTML, hidden


token_key = "_authentication_token"


def authentication_token(request):
    """
    Return current session's XSRF auth token, creating it first if it doesn't
    exist.
    """
    return request.session.get_csrf_token()


def auth_token_hidden_field(request):
    """
    Return a hidden form field with the current session's XSRF auth token,
    creating it first if it doesn't exist.
    """
    token = hidden(token_key, authentication_token(request))
    return HTML.div(token, style="display: none;")


def auth_token_get_param(request):
    """
    Return a dict with the current session's XSRF auth token, creating it first
    if it doesn't exist, for use as a kwarg to form a GET action URL.
    """
    return {token_key: authentication_token(request)}
