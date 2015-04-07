from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import shutil

from formencode import Schema, validators
from pyramid.view import view_config, view_defaults
from pyramid_uniform import Form
from pyramid_es import get_client

from ... import model


class UploadSchema(Schema):
    allow_extra_fields = False
    id = validators.Regex('^[a-z0-9]+$')
    file = validators.FieldStorageUploadConverter()


@view_defaults(permission='admin')
class ImagesView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:images',
                 renderer='admin/images.html')
    def index(self):
        return {}

    @view_config(route_name='admin:images:upload',
                 renderer='json',
                 request_method='POST')
    def upload(self):
        request = self.request

        form = Form(request, schema=UploadSchema)
        if form.validate():
            # Copy the file into a temp folder.
            base_path = request.registry.settings['images.upload_dir']
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            with open(os.path.join(base_path, form.data['id']), 'wb') as f:
                shutil.copyfileobj(form.data['file'].file, f)

            return {'status': 'ok'}
        else:
            return {'status': 'fail'}

    @view_config(route_name='admin:images:search', renderer='json')
    def search(self):
        request = self.request
        q = request.params.get('q')

        client = get_client(request)
        results = client.query(model.ImageMeta, q=q).limit(40).execute()

        return {
            'total': results.total,
            'images': [
                {
                    'id': im._id,
                    'name': im.name,
                    'original_ext': im.original_ext,
                    'alt': im.alt,
                    'title': im.title,
                    'width': im.width,
                    'height': im.height,
                    'path': request.image_url(im.name, im.original_ext,
                                              request.params.get('filter')),
                    'original_path': request.image_url(im.name,
                                                       im.original_ext,
                                                       None),
                }
                for im in results
            ]
        }
