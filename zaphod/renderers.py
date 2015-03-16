from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from decimal import Decimal
import csv

from six import StringIO

from pyramid.compat import string_types
from pyramid.renderers import JSON


def htmlstring_renderer_factory(info):
    def _render(value, system):
        if not isinstance(value, string_types):
            value = str(value)
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = b'text/html'
        return value
    return _render


def csv_renderer_factory(info):
    def _render(value, system):
        """
        Returns a plain CSV-encoded string with content-type
        ``text/csv``. The content-type may be overridden by
        setting ``request.response.content_type``.
        """
        request = system.get('request')
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = 'text/csv'

        labels = value.get('labels', [])
        rows = value.get('rows', [])

        fieldnames = [key for key, label in labels]

        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames, dialect=csv.excel)
        writer.writerow(dict(labels))
        writer.writerows(rows)

        return buf.getvalue()
    return _render


def make_json_renderer():
    renderer = JSON(indent=4)
    renderer.add_adapter(Decimal, lambda v, r: str(v))
    return renderer


def includeme(config):
    config.add_renderer(name='htmlstring', factory=htmlstring_renderer_factory)
    config.add_renderer(name='csv', factory=csv_renderer_factory)
    config.add_renderer(name='json', factory=make_json_renderer())
