from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = None

from ... import model


def migrate_images(settings):
    image_map = {}
    for old_im in scrappy_meta.Session.query(scrappy_model.ImageMeta):
        print("image %s" % old_im.name)
        new_im = model.ImageMeta(
            id=old_im.id,
            name=old_im.name,
            alt=old_im.alt,
            title=old_im.title,
            original_ext=old_im.original_ext,
            width=old_im.width,
            height=old_im.height,
            created_time=old_im.created_time,
            updated_time=old_im.updated_time,
        )
        model.Session.add(new_im)
        # XXX Copy the actual image path!
        # XXX Copy image type?
        image_map[old_im] = new_im
    return image_map
