from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import datetime

from unidecode import unidecode

from .base import Session


__all__ = ['is_url_name', 'to_url_name', 'utcnow', 'dedupe_name',
           'shipping_day']


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
    s = unidecode(s)
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


def dedupe_name(cls, attr, name, session=Session, max_tries=100):
    """
    Given a SQLAlchemy mapped class, an attribute key, and a base name, find a
    name (which may be just the supplied base name) which is unique for that
    class.  Works by adding an integer suffix which is incremented until a
    unique name was found, e.g.::

        basename
        basename-1
        basename-2
        ...

    :param cls:
        SQLAlchemy mapped class to find a name for.
    :param attr:
        Attribute key.
    :type attr:
        str
    :param name:
        Base for name.
    :type name:
        str
    :return:
        Name which is known to be unique.
    :rtype:
        str
    """
    obj = getattr(cls, attr)
    q = session.query(obj)
    current = name
    for ii in range(1, max_tries):
        if q.filter(obj == current).count() == 0:
            return current
        else:
            current = u"%s-%d" % (name, ii)
    raise ValueError("Failed to find non-duplicate name.")


def shipping_day():
    """
    Calculate the date that an order will be shipped if it is placed now.

    FIXME XXX Implement this
    """
    return utcnow().date()
