from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import shutil

from formencode import Schema, validators
from pyramid.view import view_config
from pyramid_uniform import Form


class UploadSchema(Schema):
    allow_extra_fields = False
    id = validators.Regex('^[a-z0-9]+$')
    file = validators.FieldStorageUploadConverter()


class ImagesView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:images',
                 renderer='admin/images.html',
                 permission='authenticated')
    def index(self):
        return {}

    @view_config(route_name='admin:images:upload',
                 renderer='json',
                 request_method='POST',
                 permission='authenticated')
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
