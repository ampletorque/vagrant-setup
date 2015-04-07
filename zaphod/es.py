from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid_es import get_client

from . import model


def hard_reset(registry, doc_types=None):
    client = get_client(registry)
    client.ensure_index(recreate=True)
    client.ensure_all_mappings(model.Base, recreate=True)

    doc_types = doc_types or model.Base._decl_class_registry.values()
    for doc_type in doc_types:
        if hasattr(doc_type, 'elastic_mapping'):
            for obj in model.Session.query(doc_type):
                client.index_object(obj, immediate=True)
