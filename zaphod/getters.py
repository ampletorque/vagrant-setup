from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from . import model


def get_project(project_id):
    return model.Project.get(project_id)


def creators_for_select():
    return model.Session.query(model.Creator.id, model.Creator.name).\
        order_by(model.Creator.name)


def provider_types_for_select():
    return model.Session.query(model.ProviderType.id,
                               model.ProviderType.name).\
        order_by(model.ProviderType.name)
