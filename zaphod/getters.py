from operator import attrgetter

from . import model


def get_project(project_id):
    return model.Project.get(project_id)


def get_image(image_id):
    return model.ImageMeta.get(image_id)


def creators_for_select():
    return model.Session.query(model.Creator.id, model.Creator.name).\
        order_by(model.Creator.name)


def provider_types_for_select():
    return model.Session.query(model.ProviderType.id,
                               model.ProviderType.name).\
        order_by(model.ProviderType.name)


def vendors_for_select():
    return model.Session.query(model.Vendor.id, model.Vendor.name).\
        order_by(model.Vendor.name)


def featured_projects_for_cart(cart, limit=None):
    """
    Return a list of projects that are:
        - 'related to' projects represented in this cart, but not on already
        in the cart
        - currently orderable (available, crowdfunding, or stock-only)
        - sorted by recency (campaign start time)

    Optionally limit to ``limit`` projects.
    """
    related = set()
    for item in cart.items:
        related.update(item.product.project.related_projects)
    related_cf = []
    related_noncf = []
    for project in related:
        if project.status in ('crowdfunding', 'available', 'stock-only'):
            if project.start_time:
                related_cf.append(project)
            else:
                related_noncf.append(project)
    related_cf.sort(key=attrgetter('start_time'), reverse=True)
    related = related_cf + related_noncf
    if limit:
        related = related[:limit]
    return related


def associated_products_for_cart(cart, limit=None):
    associated = set()
    for item in cart.items:
        associated.update(item.product.associated_products)
    for item in cart.items:
        associated.discard(item.product)
    associated = list(associated)
    associated.sort(key=attrgetter('gravity'))
    if limit:
        associated = associated[:limit]
    return associated


def available_admin_users_for_select(nullable=True):
    ret = model.Session.query(model.User.id,
                                                model.User.name).\
        filter_by(admin=True).\
        order_by(model.User.name).\
        all()
    if nullable:
        return [('', 'None')] + ret
    else:
        return ret


def available_lead_sources_for_select():
    return model.Session.query(model.LeadSource.id,
                               model.LeadSource.name).\
        order_by(model.LeadSource.name)
