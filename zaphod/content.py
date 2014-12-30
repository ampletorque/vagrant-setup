from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

from webhelpers2.html.tags import literal
from markdown import markdown
from pyramid_frontend.images.files import filter_sep, prefix_for_name


def _images_html_filter_replace(m):
    initial_part, path = m.group("initial"), m.group("path")
    pm = re.match("/img/"
                  "(?P<name>[^./%s]+)"
                  "(?P<rest>.*)" % filter_sep,
                  path, re.X)
    if path.count("/") == 2 and pm:
        prefix = prefix_for_name(pm.group("name"))
        return "%ssrc=\"/img/%s/%s%s\"" % (
            initial_part, prefix, pm.group("name"), pm.group("rest"))
    return m.group(0)


def images_html_filter(s):
    """
    Input filter to add an appropriate directory prefix to images in templates.
    """
    r = r'''
    (?P<initial>
    <img\s+[^>]*)
    src=
    ["']*
    (?P<path>/img/[^"']+)
    ["']*'''
    return re.compile(r, re.I | re.X).sub(_images_html_filter_replace, s)


def render_markdown(request, obj, s, safe=False):
    extensions = [
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
    ]
    if safe:
        s = markdown(s, extensions=extensions, safe_mode='escape')
    else:
        s = markdown(s, extensions=extensions)
    s = images_html_filter(s)
    return literal(s)
