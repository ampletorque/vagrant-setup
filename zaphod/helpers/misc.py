from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
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


def plural(count, noun, zero_word=False, capitalize=False, with_number=True,
           words=10):
    """
    Return a pluralized version of `noun` if count != 1 else return the
    singular.

    kwargs:
      `zero_word`: If truthy value, use this instead of 0 for count
      `capitalize`: If True, capitalize the returned words
      `with_number`: If True, display `count` in the returned string
      `words`: If True, always try to convert numbers to words
               If False, never try to convert numbers to words
               If an integer, this acts as a threshold for what numbers are
               converted to words.
               If count is less than zero, words will always be False.

    Ex:
    h.plural(5, 'category') => 'five categories'
    h.plural(1, 'category') => 'one category'
    h.plural(0, 'category') => 'zero categories'
    h.plural(-1, 'category', words=10) => '-1 categories'
    """
    noun = pluralize(noun) if count != 1 else noun

    if count < 0:
        words = False
    count = count or zero_word

    if words is not False and (words is True or words >= count):
        count = num_as_word(count)
    count = str(count)

    if with_number:
        return "%s %s" % (count.capitalize() if capitalize else count,
                          noun.capitalize() if capitalize else noun)
    return "%s" % noun.capitalize() if capitalize else noun


def pluralize(noun):
    """
    Super janky pluralization function. That's how we roll.
    """
    for pattern, search, replace in (('[ml]ouse$', '([ml])ouse$', '\\1ice'),
                                     ('child$', '(child)$', '\\1ren'),
                                     ('booth$', '(booth)$', '\\1s'),
                                     ('foot$', '(f)oot$', '\\1eet'),
                                     ('ooth$', 'ooth$', 'eeth'),
                                     ('l[eo]af$', '(l)([eo])af$',
                                      '\\1\\2aves'),
                                     ('sis$', 'sis$', 'ses'),
                                     ('human$', '(h)uman$', '\\1umans'),
                                     ('man$', '(m)an$', '\\1en'),
                                     ('person$', '(p)erson', '\\1eople'),
                                     ('ife$', 'ife$', 'ives'),
                                     ('eau$', 'eau$', 'eaux'),
                                     ('lf$', 'lf$', 'lves'),
                                     ('[sxz]$', '$', 'es'),
                                     ('[^aeioudgkprt]h$', '$', 'es'),
                                     ('(qu|[^aeiou])y$', 'y$', 'ies'),
                                     ('$', '$', 's')):
        if re.search(pattern, noun, flags=re.I):
            return re.sub(search, replace, noun, flags=re.I)
