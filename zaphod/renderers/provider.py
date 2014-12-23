from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid.renderers import render

from .. import model


def provider_renderer(node, system):
    request = system['request']
    vars = dict(provider=node)
    return render('provider.html', vars, request)


def includeme(config):
    config.add_node_renderer(provider_renderer, model.Provider)
