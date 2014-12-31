from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import locale
import hashlib

from six.moves.urllib.parse import urlencode

from webhelpers2.html.tags import _make_safe_id_component, literal


# def localeconv():
#     "Manually install en_US for systems that don't have it."
#     d = {'currency_symbol': '$',
#          'decimal_point': '.',
#          'frac_digits': 2,
#          'grouping': [3, 3, 0],
#          'int_curr_symbol': 'USD ',
#          'int_frac_digits': 2,
#          'mon_decimal_point': '.',
#          'mon_grouping': [3, 3, 0],
#          'mon_thousands_sep': ',',
#          'n_cs_precedes': 1,
#          'n_sep_by_space': 0,
#          'n_sign_posn': 1,
#          'negative_sign': '-',
#          'p_cs_precedes': 1,
#          'p_sep_by_space': 0,
#          'p_sign_posn': 1,
#          'positive_sign': '',
#          'thousands_sep': ','}
#     return d
# locale.setlocale(locale.LC_ALL, 'C')
# locale.localeconv = localeconv


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
    s = locale.currency(n, grouping=True)
    frac = n - int(n)
    if (not show_fractional) or (show_fractional == 'nonzero' and frac > 0):
        s = s[:-3]
    return s


def commas(n, decimal=False):
    """
    Format a numeric type with commas, but no currency symbol. Works as a Mako
    filter as well.
    """
    if n is None:
        return ''
    return locale.format('%.2f' if decimal else '%d', n, grouping=True)


def format_percent(percent):
    if percent < 1.0:
        return "%0.1f" % percent
    elif percent < 99:
        return "%d" % round(percent)
    else:
        return commas(percent)
