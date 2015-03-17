from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
from datetime import datetime

from formencode import Schema, NestedVariables, ForEach, validators
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid_frontend.images.files import check_and_save_image

from pyramid_uniform import Form, FormRenderer
from pyramid_es import get_client

from . import model, custom_validators
from .helpers.paginate import Page


class BaseEditView(object):
    def __init__(self, request):
        self.request = request

    def _get_object(self):
        request = self.request
        obj = self.cls.get(request.matchdict['id'])
        if not obj:
            raise HTTPNotFound
        return obj

    def _handle_new_image(self, image_params):
        request = self.request
        settings = request.registry.settings
        base_path = settings['images.upload_dir']

        orig_name = image_params['name']
        name = model.to_url_name(orig_name.rsplit('.', 1)[0])
        name = model.dedupe_name(model.ImageMeta, 'name', name)
        with open(os.path.join(base_path, image_params['id']), 'rb') as f:
            info = check_and_save_image(settings, name, f)
        im = model.ImageMeta(
            name=name,
            original_ext=info['ext'],
        )
        im.width, im.height = info['size']
        model.Session.add(im)
        return im

    def _handle_images(self, form, obj):
        obj.image_associations[:] = []
        for image_params in form.data.pop('images'):
            if image_params['fresh']:
                im = self._handle_new_image(image_params)
            else:
                im = model.ImageMeta.get(image_params['id'])
            im.title = image_params['title']
            im.alt = image_params['alt']
            obj.image_associations.append(obj.ImageAssociation(
                image_meta=im,
                gravity=image_params['gravity'],
                published=image_params['published'],
                caption=image_params['caption'],
            ))

    def _touch_obj(self, obj):
        request = self.request
        obj.updated_by = request.user
        obj.updated_time = datetime.utcnow()

    def _update_obj(self, form, obj):
        request = self.request
        if 'images' in form.data:
            self._handle_images(form, obj)
        form.bind(obj)
        request.flash('Saved changes.', 'success')

    @view_config(permission='admin', xhr=False)
    def edit(self):
        request = self.request
        obj = self._get_object()
        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            self._touch_obj(obj)
            self._update_obj(form, obj)
            return HTTPFound(location=request.current_route_url())
        return {
            'obj': obj,
            'renderer': FormRenderer(form),
        }

    @view_config(permission='admin', xhr=True, renderer='json')
    def edit_ajax(self):
        request = self.request
        obj = self._get_object()
        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            self._update_obj(form, obj)
            return {
                'status': 'ok',
                'location': request.current_route_url(),
            }
        else:
            return {
                'status': 'fail',
                'errors': form.errors,
            }


class BaseListView(object):
    paginate = False

    def __init__(self, request):
        self.request = request

    @view_config(permission='admin')
    def index(self):
        request = self.request

        if 'q' in request.params:
            client = get_client(request)
            results = client.query(self.cls, q=request.params['q']).execute()
            return dict(results=results)
        else:
            q = model.Session.query(self.cls)
            final_q = q.order_by(self.cls.id.desc())
        if self.paginate:
            item_count = final_q.count()

            page = Page(request, final_q,
                        page=int(request.params.get('page', 1)),
                        items_per_page=20,
                        item_count=item_count)

            return dict(page=page)
        else:
            return dict(objs=final_q.all())


class BaseCreateView(object):

    def __init__(self, request):
        self.request = request

    @view_config(permission='admin')
    def create(self):
        request = self.request

        form = Form(request, schema=self.CreateForm)
        if form.validate():
            obj = self.cls(**form.data)
            model.Session.add(obj)
            model.Session.flush()
            request.flash("Created.", 'success')
            return HTTPFound(location=request.route_url(self.obj_route_name,
                                                        id=obj.id))

        return {'renderer': FormRenderer(form)}


class NodeUpdateForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]

    name = validators.UnicodeString(max=255, not_empty=True)
    override_path = custom_validators.URLString(if_missing=None)

    keywords = validators.UnicodeString()
    teaser = validators.UnicodeString()
    body = validators.UnicodeString()

    listed = validators.Bool()
    published = validators.Bool()

    new_comment = custom_validators.CommentBody()
    images = ForEach(custom_validators.ImageAssociation())


class NodeEditView(BaseEditView):
    UpdateForm = NodeUpdateForm


class NodeListView(BaseListView):
    pass


class NodeCreateForm(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString(max=255, not_empty=True)


class NodeCreateView(BaseCreateView):
    CreateForm = NodeCreateForm
