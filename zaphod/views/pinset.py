from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pkg_resources
from six import BytesIO

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from PIL import Image

from .. import model


def load_pil_logo():
    path = pkg_resources.resource_filename('zaphod.themes.teal',
                                           'static/images/cslogo-pinset.png')
    return Image.open(path)


def build_image_pinset(images, width=400, gutter=10, background='white'):
    resized = []
    height = 0
    for im in images:
        w, h = im.size
        new_h = int(float(h) * (float(width) / w))
        new_im = im.resize((width, new_h), Image.ANTIALIAS)
        resized.append(new_im)
        height += new_h + gutter

    logo_im = load_pil_logo()
    logo_w, logo_h = logo_im.size
    resized.append(logo_im)
    height += logo_h

    base = Image.new('RGB', (width, height), background)
    cursor = 0
    for im in resized:
        base.paste(im, (0, cursor))
        cursor += im.size[1] + gutter

    return base


def load_pil_images(request, image_metas):
    for im in image_metas:
        path = request.image_original_path(im.name, im.original_ext)
        yield Image.open(path)


def key_generator(namespace, fn, **kw):
    fname = fn.__name__

    def generate_key(*arg):
        return namespace + '_' + fname + '_'.join(str(s) for s in arg)
    return generate_key


def build_node_pinset(request, id):
    node = model.Node.get(id)
    if not node:
        raise HTTPNotFound
    image_metas = [assoc.image_meta
                   for assoc in node.image_associations
                   if assoc.published][:8]
    pil_images = load_pil_images(request, image_metas)
    pinset_im = build_image_pinset(pil_images)
    buf = BytesIO()

    pinset_im.save(buf, format='JPEG', quality=80)
    return buf.getvalue()


@view_config(route_name='pinset')
def pinset_view(request):
    node_id = request.matchdict['id']

    def creator():
        return build_node_pinset(request, node_id)

    cache = request.theme.cache_regions['default']
    buf = cache.get_or_create('project-%s-pinset' % node_id, creator)
    return Response(buf, content_type=str('image/jpeg'))
