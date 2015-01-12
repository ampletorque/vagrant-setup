from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import hashlib

from six.moves.urllib.parse import urlencode

from webhelpers2.html.tags import HTML, _make_safe_id_component, literal


def grouper(n, iterable):
    """
    Return elements from iterable n items at a time.
    e.g. grouper(3,[1,2,3,4,5,6,7]) -> ([1,2,3], [4,5,6], [7])
    """
    iterable = iter(iterable)
    ret = []
    for item in iterable:
        ret.append(item)
        if len(ret) >= n:
            yield ret
            ret = []
    if len(ret) > 0:
        yield ret


def gravatar_url(email, size=200, default=None, rating='g',
                 force_default=False):
    hash = hashlib.md5(email.encode('utf8').strip().lower()).hexdigest()
    params = {
        's': size,
        'r': rating,
    }
    if default:
        params['d'] = default
    if force_default:
        params['f'] = 'y'
    params = urlencode(params)
    return literal('//www.gravatar.com/avatar/%s?%s' % (hash, params))


def image_or_gravatar(request, obj, chain, title=None, class_=None, id=None,
                      **kwargs):
    img = obj.img(request, chain, class_=class_, id=id)
    if img:
        return img
    else:
        registry = request.registry
        chain, with_themes = registry.image_filter_registry[chain]
        size = max(chain.width, chain.height)
        return HTML.img(src=gravatar_url(obj.email, size=size, **kwargs),
                        alt='', class_=class_, id=id, title=title)


def prettify(name):
    """
    Take a string (or something that can be made into a string), replace
    underscores with spaces, and capitalize the first letter.

    >>> prettify("joe_user")
    'Joe user'
    >>> prettify("foo_bar_baz_quux")
    'Foo bar baz quux'
    >>> prettify(123)
    '123'
    """
    return str(name).replace('_', ' ').capitalize()


def make_id_component(name):
    return _make_safe_id_component(name and name.replace('.', '_'))


def currency(n, show_fractional=True):
    """
    Convert a numeric type into a string formatted for currency display.
    Works as a Mako filter as well.

    >>> currency(1.23, show_fractional=False)
    '$1'
    >>> currency(1.23, show_fractional=True)
    '$1.23'
    >>> currency(1.23, show_fractional='nonzero')
    '$1.23'
    >>> currency(1.00, show_fractional='nonzero')
    '$1'
    """
    if n is None:
        return ''
    frac = n - int(n)
    if (not show_fractional) or (show_fractional == 'nonzero' and frac > 0):
        s = commas(n, decimal=False)
    else:
        s = commas(n, decimal=True)
    return '$' + s


def commas(n, decimal=False):
    """
    Format a numeric type with commas, but no currency symbol. Works as a Mako
    filter as well.
    """
    if n is None:
        return ''

    s = '%d' % n
    pieces = []
    for ii, c in enumerate(reversed(list(s))):
        if ii and ((ii % 3) == 0):
            pieces.append(',')
        pieces.append(c)

    s = ''.join(reversed(pieces))

    if decimal:
        s += ('%0.2f' % n)[-3:]
    return s


def format_percent(percent):
    if percent < 1.0:
        return "%0.1f" % percent
    elif percent < 99:
        return "%d" % round(percent)
    else:
        return commas(percent)
