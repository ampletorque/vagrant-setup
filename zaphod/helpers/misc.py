from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import date
from operator import itemgetter
import re
import hashlib
import string
import time

from six.moves.urllib.parse import urlencode

from webhelpers2.html.tags import (HTML, _make_safe_id_component, literal,
                                   select)

from iso3166 import countries


def grouper(n, iterable):
    """
    Return elements from iterable n items at a time.
    e.g. grouper(3,[1,2,3,4,5,6,7]) -> ([1,2,3], [4,5,6], [7])

    :param n: Maximum number of elements in each group
    :type n: int
    :param iterable: Input iterable to regroup
    :returns: Iterator of groups
    :rtype: generator
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
    """
    Return a schemeless URL for the gravatar corresponding to this email
    address.

    :param email: Email address to use for gravatar
    :type email: str
    :param size: Size of resulting image
    :type size: int
    :param default: Default image type to use for emails which are not in the
                    gravatar DB. See
                    https://secure.gravatar.com/site/implement/images/ for
                    choices.
    :type default: str
    :param rating: Appropriateness rating to use for resulting image.
    :type rating: str: g, pg, r, or x
    :param force_default: Force the default image to always load, regardless of
                          whether or not the email exists.
    :type force_default: bool

    :returns: URL to gravatar image
    :rtype: literal
    """
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
    """
    Try to return an image for the specified object. If one does not exist, try
    to return a gravatar using the ``obj.email`` address.
    """
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
    """
    Make the supplied string safe for use as a CSS ID.

    :param name: Input string
    :type name: str
    :returns: ID-safe string
    :rtype: str
    """
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
    """
    Format a numeric type into a human-readable percentage, with an appropriate
    level of precision.
    """
    if percent < 1.0:
        return "%0.1f" % percent
    elif percent < 99:
        return "%d" % round(percent)
    else:
        return commas(percent)


def num_as_word(num):
    """
    Attempts to convert numbers to words -- Only up to 100.
    """
    ones = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
            'eight', 'nine')
    teens = ('ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
             'sixteen', 'seventeen', 'eighteen', 'nineteen')
    tens = ('twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty',
            'ninety')
    try:
        if int(num) != float(num):
            raise ValueError
        num = int(num)
    except (TypeError, ValueError):
        return num

    if num < 10:
        return ones[num]
    elif num < 20:
        return teens[num - 10]
    elif num > 99:
        return num

    for (cap, val) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if val + 10 > num:
            if num % 10:
                return cap + '-' + ones[num % 10]
            return cap


def plural(count, noun, zero_word=False, capitalize=False, with_number=True,
           words=10):
    """
    Return a pluralized version of `noun` if count != 1 else return the
    singular.

    Ex:
    h.plural(5, 'category') => 'five categories'
    h.plural(1, 'category') => 'one category'
    h.plural(0, 'category') => 'zero categories'
    h.plural(-1, 'category', words=10) => '-1 categories'

    :param count: Numeric count of objects
    :type count: int
    :param noun: The singular noun to (potentially) pluralize
    :type noun: str
    :param zero_word: If True, use this instead of 0 for count
    :type zero_word: bool
    :param capitalize: If True, capitalize the returned words
    :type capitalize: bool
    :param with_number: If True, include ``count`` in the returned string
    :type with_number: bool
    :param words:
        If True, always try to convert numbers to words. If False,
        never try to convert numbers to words. If an integer, this acts as a
        threshold for what numbers are converted to words. If the count s less
        than zero, words will always be False.
    :returns: Pluralized string
    :rtype: str
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


def abbreviate_name(name):
    """
    Abbreviate a typical English name to first name and last initial.
    """
    words = string.capwords(name).split()
    if len(words) == 0:
        return u''
    elif len(words) == 1:
        return name
    first = words[0]
    last_initial = words[-1][0]
    return first + ' ' + last_initial


def loaded_time():
    return time.time()


def strip_tags(s):
    "Strip any sgml/xml/html tags from input. Might be a bit reckless."
    return re.sub(r'<.+?>|&\w*?;', u'', s)


def display_url(url):
    """
    Make a URL more human-friendly.
    """
    if not url:
        return
    # Strip off http:// or https://
    url = url.split('//', 1)[-1]
    # Strip off www also
    if url.startswith('www.'):
        url = url[4:]
    # Strip off trailing slash
    url = url.rstrip('/')
    return url


def google_static_map_url(addr, zoom=11, width=200, height=200, scale=1):
    """
    Return the URL for a google static map of the supplied address.
    """
    base_url = '//maps.google.com/maps/api/staticmap'
    params = dict(markers='color:red|%s' % addr.inline,
                  zoom=zoom,
                  size='%dx%d' % (width, height),
                  scale=scale,
                  maptype='roadmap',
                  sensor='false')
    return literal(base_url + '?' + urlencode(params))


def cc_expires_month_select(renderer, name, **kwargs):
    """
    Render an HTML select element for use as a credit card expiration date
    'months' field.
    """
    months = ['%02d' % ii for ii in range(1, 13)]
    if renderer:
        return renderer.select(name, None, months, **kwargs)
    else:
        return select(name, None, months, **kwargs)


def cc_expires_year_select(renderer, name, **kwargs):
    """
    Render an HTML select element for use as a credit card expiration date
    'year' field.
    """
    current_year = date.today().year
    # VISA Gift Cards have very very long expiration times.
    end_year = current_year + 11
    years = range(current_year, end_year)
    if renderer:
        return renderer.select(name, None, years, **kwargs)
    else:
        return select(name, None, years, **kwargs)


def allowed_countries():
    """
    Return a list of countries for use in a shipping or billing address.
    """
    ret = [('us', 'United States'),
           ('ca', 'Canada')]
    ret.extend([(c.alpha2.lower(), c.name) for c in countries
                if (c.alpha2.lower(), c.name) not in ret])
    return ret


def option_value_description(option_value, show_price_changes=True):
    """
    Return a string describing the value of a ProductOptionValue, including
    any price difference.
    """
    price_str = u''
    if show_price_changes and option_value.price_increase != 0:
        price_str = currency(option_value.price_increase)
        if price_str.endswith('00'):
            price_str = price_str[:-3]
        if option_value.price_increase > 0:
            price_str = u" +%s" % price_str
        else:
            price_str = u" %s" % price_str
    return option_value.description + price_str


def variant_list(item, show_defaults=True, show_price_changes=True):
    opts_gravity = []
    for ov in item.option_values:
        opt = ov.option

        if show_defaults or (opt.default_value != ov):
            desc = option_value_description(
                ov, show_price_changes=show_price_changes)
            line = "%s: %s" % (opt.name, desc)
            opts_gravity.append((line, opt.gravity))

    opts_gravity.sort(key=itemgetter(1))
    return [description for description, gravity in opts_gravity]


def variant_string(item, show_price_changes=True):
    """
    Return a human-readable description of an item's variant selections. Works
    on any instance with associated option values.
    """
    return ", ".join(variant_list(item, show_price_changes=show_price_changes))
