from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.config import Configurator
from pyramid.events import BeforeRender, NewResponse
from sqlalchemy import engine_from_config

from gimlet.factories import session_factory_from_settings

from . import helpers
from .logging import init_querytimer
from .model import Session, Base


def add_renderer_globals(event):
    event['h'] = helpers


class Root(object):
    def __init__(self, request):
        self.request = request


def new_response_subscriber(event):
    request, response = event.request, event.response
    request.session.response_callback(request, response)


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    init_querytimer(engine)
    Session.configure(bind=engine)
    Base.metadata.bind = engine

    session_factory = session_factory_from_settings(settings)

    config = Configurator(
        request_factory='.request.Request',
        root_factory=Root,
        session_factory=session_factory,
        settings=settings,
    )

    config.include('pyramid_tm')
    config.include('pyramid_es')
    config.include('pyramid_frontend')
    config.include('pyramid_mailer')
    config.include('pyramid_cron')

    config.include('.renderers')
    config.include('.auth')
    config.include('.themes')
    config.include('.nodes')
    config.include('.views')

    config.add_subscriber(new_response_subscriber, NewResponse)
    config.add_subscriber(add_renderer_globals, BeforeRender)

    config.add_tween('.logging.request_log_tween_factory')

    return config.make_wsgi_app()
