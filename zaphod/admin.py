import os.path
from datetime import datetime

from formencode import Schema, NestedVariables, ForEach, validators
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
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
        client = get_client(request)
        client.index_object(im)
        return im

    def _handle_images(self, form, obj):
        request = self.request
        client = get_client(request)
        obj.image_associations[:] = []
        for image_params in form.data.pop('images'):
            if image_params['fresh']:
                im = self._handle_new_image(image_params)
            else:
                im = model.ImageMeta.get(image_params['id'])
            im.title = image_params['title']
            im.alt = image_params['alt']
            im.updated_by = request.user
            im.updated_time = datetime.utcnow()
            client.index_object(im)
            obj.image_associations.append(obj.ImageAssociation(
                image_meta=im,
                gravity=image_params['gravity'],
                published=image_params['published'],
                caption=image_params['caption'],
            ))

    def _touch_object(self, obj):
        request = self.request
        obj.updated_by = request.user
        obj.updated_time = datetime.utcnow()

    def _update_object(self, form, obj):
        request = self.request
        if 'images' in form.data:
            self._handle_images(form, obj)
        form.bind(obj)
        if hasattr(obj, 'elastic_document'):
            client = get_client(request)
            client.index_object(obj)
        request.flash('Saved changes.', 'success')

    @view_config(permission='admin', xhr=False)
    def edit(self):
        request = self.request
        obj = self._get_object()
        form = Form(request, schema=self.UpdateForm)
        if form.validate():
            self._touch_object(obj)
            self._update_object(form, obj)
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
            self._touch_object(obj)
            self._update_object(form, obj)
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

    def _make_page(self, q):
        request = self.request
        item_count = q.count()
        return Page(request, q,
                    page=int(request.params.get('page', 1)),
                    items_per_page=20,
                    item_count=item_count)

    @view_config(permission='admin')
    def index(self):
        request = self.request

        if 'q' in request.params:
            client = get_client(request)
            results = client.query(self.cls, q=request.params['q']).execute()
            objs = [self.cls.get(doc.id) for doc in results]
            if self.paginate:
                page = Page(request, objs,
                            page=int(request.params.get('page', 1)),
                            items_per_page=20,
                            item_count=results.total)
                return dict(page=page)
            else:
                return dict(objs=objs)
        else:
            q = model.Session.query(self.cls)
            final_q = q.order_by(self.cls.id.desc())
            if self.paginate:
                page = self._make_page(final_q)
                return dict(page=page)
            else:
                return dict(objs=final_q.all())


class BaseCreateView(object):

    def __init__(self, request):
        self.request = request

    def _create_object(self, form):
        request = self.request
        obj = self.cls(created_by=request.user,
                       updated_by=request.user,
                       **form.data)
        model.Session.add(obj)
        if hasattr(obj, 'elastic_document'):
            client = get_client(request)
            client.index_object(obj)
        return obj

    @view_config(permission='admin')
    def create(self):
        request = self.request

        form = Form(request, schema=self.CreateForm)
        if form.validate():
            obj = self._create_object(form)
            model.Session.flush()
            request.flash("Created.", 'success')
            return HTTPFound(location=request.route_url(self.obj_route_name,
                                                        id=obj.id))

        return {'renderer': FormRenderer(form)}


class BaseDeleteView(object):

    def __init__(self, request):
        self.request = request

    def _get_object(self):
        request = self.request
        obj = self.cls.get(request.matchdict['id'])
        if not obj:
            raise HTTPNotFound
        return obj

    @view_config(permission='admin')
    def delete(self):
        request = self.request
        form = Form(request, Schema)
        if form.validate():
            obj = self._get_object()
            if hasattr(obj, 'elastic_document'):
                client = get_client(request)
                client.delete_object(obj)
            model.Session.delete(obj)
            model.Session.flush()
            request.flash("Deleted.", 'success')
            return HTTPFound(location=request.route_url(self.list_route_name))
        else:
            raise HTTPBadRequest


class NodeUpdateForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]

    name = validators.String(max=255, not_empty=True, strip=True)
    override_path = custom_validators.URLString(if_missing=None)

    keywords = validators.String()
    teaser = validators.String()
    body = validators.String()

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
    name = validators.String(max=255, not_empty=True)


class NodeCreateView(BaseCreateView):
    CreateForm = NodeCreateForm


class NodeDeleteView(BaseDeleteView):
    pass
