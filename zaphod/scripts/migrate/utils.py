from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model


def migrate_aliases(settings, old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        print("  path: %r" % alias.path)
        if alias.canonical:
            canonical_path = alias.path
        new_node.update_path(alias.path)
    if canonical_path:
        new_node.update_path(canonical_path)


def migrate_comments(old_obj, new_obj, user_map):
    for old_comment in old_obj.comments:
        new_obj.comments.append(new_obj.Comment(
            created_time=old_comment.created_time,
            created_by=user_map[old_comment.created_by],
            body=old_comment.body,
        ))


def migrate_image_associations(settings, old_obj, new_obj):
    for old_assoc in old_obj._image_associations:
        print("  image assoc %s" % old_assoc.image_meta_id)
        new_obj.image_associations.append(new_obj.ImageAssociation(
            image_meta_id=old_assoc.image_meta_id,
            gravity=old_assoc.gravity,
            published=old_assoc.published,
            caption=old_assoc.caption,
        ))


def convert_address(old):
    return model.Address(first_name=old.first_name,
                         last_name=old.last_name,
                         company=old.company,
                         phone=old.phone,
                         address1=old.address1,
                         address2=old.address2,
                         city=old.city,
                         state=old.state,
                         postal_code=old.postal_code,
                         country_code=old.country)
