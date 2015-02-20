from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid_es import get_client

from . import model


default_doc_types = (
    model.Project,
    model.Order,
    model.User,
)


def hard_reset(registry, doc_types=default_doc_types):
    client = get_client(registry)
    client.ensure_index(recreate=True)
    client.ensure_all_mappings(model.Base, recreate=True)
    for doc_type in doc_types:
        for obj in model.Session.query(doc_type):
            client.index_object(obj, immediate=True)
