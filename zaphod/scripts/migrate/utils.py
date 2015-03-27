from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model

log = logging.getLogger(__name__)


def migrate_aliases(settings, old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        log.debug("      path: %r", alias.path)
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
        log.debug("      image assoc %s", old_assoc.image_meta_id)
        new_obj.image_associations.append(new_obj.ImageAssociation(
            image_meta_id=old_assoc.image_meta_id,
            gravity=old_assoc.gravity,
            published=old_assoc.published,
            caption=old_assoc.caption,
        ))


def convert_address(old):
    """
    Convert a supplied scrappy Address instance to a zaphod Address instance.
    """
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


def default_for_option(option):
    """
    Given a scrappy ProductOption instance, return the ID of the default option
    value for this option. If no default is currently specified, use the
    lowest-gravity value.
    """
    for ov in option.all_values:
        if ov.is_default:
            return ov
    return option.all_values[0]


def sku_for_option_values(product, option_values):
    """
    From a list of zaphod option values, return the corresponding SKU, or
    create a new one. This is the 'sloppy version' that allows for loosely
    specified objects. If the object is loosely specified, it will first be
    fully specified by filling in the 'defaults' for the options which have
    missing values.

    Due to the behavior used when migrating scrappy ProductOptions to zaphod
    Options, If an option does not have a default specified, the first value
    (the value with the lowest gravity) will be used.
    """
    q = model.Session.query(model.SKU).filter_by(product=product)

    opts_present = set()
    ovs = set()
    for ov in option_values:
        opts_present.add(ov.option)
        ovs.add(ov)

    all_opts = set(product.options)
    missing_opts = all_opts - opts_present

    for opt in missing_opts:
        ovs.add(opt.default_value)

    for ov in ovs:
        q = q.filter(model.SKU.option_values.any(id=ov.id))

    sku = q.first()
    if not sku:
        sku = model.SKU(product=product)
        for ov in ovs:
            sku.option_values.add(ov)
        model.Session.add(sku)

    return sku


def recode_avs_result(avs_result):
    """
    Recode the avs_result character to stripe pass/fail codes.
    """
    # address result, zip code result
    result_map = {
        'Y': ("pass", "pass"),
        'A': ("pass", "fail"),
        'Z': ("fail", "pass"),
        'N': ("fail", "fail"),
        'S': ('', ''),
        '': ('', ''),
    }
    return result_map[avs_result]


def recode_ccv_result(ccv_result):
    result_map = {
        'M': "pass",
        'N': "fail",
        'P': "unchecked",
        '': 'unchecked',
    }
    return result_map[ccv_result]
