from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import hashlib

from six.moves.urllib.parse import urlencode

from webhelpers2.html.tags import _make_safe_id_component, literal


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
