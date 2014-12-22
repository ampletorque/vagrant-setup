from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import (HTTPClientError, HTTPInternalServerError,
                                    HTTPFound)
from pyramid.renderers import render_to_response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.settings import asbool


def error_view(context, request):
    data = {
        'exc': context,
    }
    error_template = '/error.html'
    response = render_to_response(error_template, data, request)
    response.status_int = context.code
    return response


def forbidden_view(context, request):
    """Handle ``403 Forbidden`` responses.

    If a user is logged in, a 403 indicates the user doesn't have the
    permissions necessary to view the resource. In this case, show an
    error page.

    If no user is logged in, redirect to the login page (unless signups
    are enabled via the ``accounts.allow_signup`` setting, in which case
    redirect to the signup page).

    NOTE: This usage of 403s is dictated by Pyramid's auth machinery. It
    uses 403s to indicate any unauthorized access to a protected resource,
    whether by an anonymous/unauthenticated user or by an authenticated user
    that doesn't have the appropriate permissions. Generally speaking, we
    shouldn't raise 403s ourselves (a 400, 401, or 404 can be used instead,
    depending on the circumstances).

    """
    # FIXME: Ultimately, it would be good to pass the current URL in the
    # redirect, so that the login handler can return the user to the originally
    # requested page.
    if not request.user:
        return HTTPFound(location=request.route_url('login'))
    return error_view(context, request)


def exc_view(context, request):
    """Convert uncaught exception to ``500 Internal Server Error``.

    The built-in ``excview`` tween will catch the exception, then call this
    view. Without this view, the exception would propagate up to uWSGI,
    which would then return an unhelpful 502 response.

    ``context`` is the exception.

    """
    return error_view(HTTPInternalServerError(str(context)), request)


def includeme(config):
    settings = config.registry.settings

    config.add_view(
        view=error_view,
        context=HTTPClientError,
        permission=NO_PERMISSION_REQUIRED)

    config.add_forbidden_view(forbidden_view)

    if not asbool(settings.get('debug')):
        config.add_view(
            view=exc_view,
            context=Exception,
            permission=NO_PERMISSION_REQUIRED)
