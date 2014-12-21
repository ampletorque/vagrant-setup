from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import re
import datetime


__all__ = ['utcnow']


def is_url_name(s):
    """
    Test if a string is a legal URL name. E.g.  all lowercase, only
    alphanumeric characters, separated by hyphens.
    """
    return re.compile('^[a-z0-9\-\/]+$').search(s) is not None


def to_url_name(s, convert_camel_case=False):
    """
    Convert a string to a legal URL name.
    """
    if not isinstance(s, six.text_type):
        raise ValueError("Need to be called with a unicode string!")
    # Transliterate accented unicode characters to the base character.  Not all
    # characters can be transliterated, so fallback to simple replacement.
    try:
        s = s.encode('ascii', 'transliterate')
    except UnicodeEncodeError:
        s = s.encode('ascii', 'replace')
    if convert_camel_case:
        # Convert CamelCaseStrings to Camel Case Strings.
        s = re.sub(r'([a-z])([A-Z])', '\g<1> \g<2>', s)
    # Just eliminate apostrophes.
    s = re.sub(r'\'', '', s)
    # Convert & to and.
    s = re.sub(r'&', ' and ', s)
    # Convert + to plus.
    s = re.sub(r'\+', ' plus ', s)
    # Convert @ to at.
    s = re.sub(r'\@', ' at ', s)
    # Make lowercase and convert non-URLString chars to spaces.
    s = re.sub(r'[^a-z0-9\ ]', ' ', s.lower())
    # Strip and convert whitespace blocks to hyphens.
    s = re.sub(r'\s+', '-', s.strip())
    return s


def utcnow():
    """
    Wraps the ``datetime.utcnow()`` function for use inside the model. Provides
    a convenient access point for mocking all ``utcnow()`` calls.
    """
    return datetime.datetime.utcnow()
