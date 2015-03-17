from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.response import FileResponse


@view_config(route_name='admin:docs', permission='authenticated')
def docs_view(request):
    settings = request.registry.settings
    docs_dir = os.path.normpath(settings['docs.build_dir'])
    relpath = request.matchdict['path'] or 'index.html'
    path = os.path.normpath(os.path.join(docs_dir, relpath))
    if not path.startswith(docs_dir):
        raise HTTPNotFound
    return FileResponse(path, request=request)
