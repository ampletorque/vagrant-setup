from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import logging.handlers
import time
import re
import os.path
import pkg_resources

from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.event import listen
from sqlalchemy.exc import SQLAlchemyError

from pyramid.threadlocal import get_current_request
from pyramid.compat import binary_type, text_type


querylog = logging.getLogger('zaphod.querytimer')


def _log_query_time(total, statement):
    # NOTE: To get other details of the query, use statement and parameters
    # objects.
    if total > 0.2:
        level = querylog.error
        msg = "VERY SLOW QUERY over 200ms"
    elif total > 0.02:
        level = querylog.warn
        msg = "SLOW QUERY over 20ms"
    else:
        level = querylog.debug
        msg = ""

    request = get_current_request()
    level("query time: %0.2fms %s [%s] at %s",
          (total * 1000.), msg, statement,
          request.path if request else '-')

    # Wrap this in a try/except so that it can still be run even when we're not
    # being used inside an actual web request (e.g. during setup-app or
    # maintenance scripts).
    if request:
        env = request.environ
        if 'querytimer.elapsed' not in env:
            env['querytimer.elapsed'] = 0.0
        env['querytimer.elapsed'] += total
        if 'querytimer.num_queries' not in env:
            request.environ['querytimer.num_queries'] = 0
        env['querytimer.num_queries'] += 1


def init_querytimer(engine):
    """
    Use the SQLAlchemy 0.7 event interface to capture basic statistics about
    query performance.
    """
    def before(conn, cursor, statement, parameters, context, executemany):
        context.__querytimer = time.time()

    def after(conn, cursor, statement, parameters, context, executemany):
        now = time.time()
        _log_query_time(now - context.__querytimer, statement)

    listen(engine, "before_cursor_execute", before)
    listen(engine, "after_cursor_execute", after)


def request_log_tween_factory(handler, registry):
    """
    Tween that logs request info.
    """
    log = logging.getLogger('zaphod.requests')

    def tween(request):
        started = time.time()
        try:
            return handler(request)
        finally:
            environ = request.environ

            is_static = any(request.path.startswith(prefix)
                            for prefix in ('/_', '/img/'))
            if is_static:
                level = log.debug
            else:
                level = log.info

            user = '-'
            if request.user:
                try:
                    user = '%d/%s' % (request.user.id, request.user.email)
                except DetachedInstanceError:
                    pass

            level(
                '%8s %8s %3s %15s %4s %s %s',
                '%0.2f' % ((time.time() - started) * 1000.),
                '%0.2f' % (1000. * environ.get('querytimer.elapsed', 0)),
                '%d' % environ.get('querytimer.num_queries', 0),
                request.client_addr,
                request.method,
                request.url,
                user)

    return tween


class ColoredStreamHandler(logging.StreamHandler):
    """
    A subclass of StreamHandler which behaves in the exact same way, but
    colorizes the log level before formatting it.
    """

    COLORS = {'CRITICAL': '[1;31m',
              'ERROR': '[1;31m',
              'WARNING': '[1;33m',
              'INFO': '[1;32m',
              'DEBUG': '[1;37m',
              'reset': '[0m'}

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record, but
        before the formatter is applied the loglevel is colored.
        """
        def _format_levelname(l):
            return self.COLORS[l] + l + self.COLORS['reset']
        record.colored_levelname = _format_levelname(record.levelname)
        logging.StreamHandler.emit(self, record)


class ExceptionSMTPHandler(logging.handlers.SMTPHandler):
    def getSubject(self, record):
        exc = record.exc_info[1]
        exc_name = exc.__class__.__name__
        subject = super(ExceptionSMTPHandler, self).getSubject(record)
        subject = '{0}: {1}: {2}'.format(subject, exc_name, exc)
        return subject


exclog_message = u"""

REQUEST URL
-----------

{url}


USER INFO
---------

{user_info}


URL PARAMETERS
--------------

{get_params}


POST PARAMETERS
---------------

{post_params}


COOKIES
-------

{cookies}


WSGI ENVIRON
------------

{env}


VERSIONS
--------

{versions}


TRACEBACK
---------

"""


exclog_user_info = u"""\
Name: {name}
Email: {email}\
"""


def get_exclog_message(request):
    """
    A custom message generator pyramid_exclog which fills in user info and
    masks sensitive fields.
    """
    env = request.environ.copy()

    # Remove GET and POST params and cookies from environ because they're
    # displayed separately.
    env.pop('webob._parsed_query_vars', None)
    env.pop('webob._parsed_post_vars', None)
    env.pop('webob._parsed_cookies', None)
    env.pop('HTTP_COOKIE', None)
    env = format_dict(env)

    get_params = format_dict(request.GET.copy()) or None

    post_params = request.POST.copy()

    params_to_mask = ['cc.number', 'cc.expires_month', 'cc.expires_year',
                      'cc.code', 'password', 'password2']
    for name in post_params:
        if name in params_to_mask:
            post_params[name] = '*' * len(post_params[name])

    post_params = format_dict(post_params) or None
    cookies = format_dict(request.cookies) or None

    try:
        if request.user:
            name = request.user.name
            email = request.user.email
            user_info = exclog_user_info.format(name=name, email=email)
        else:
            user_info = u'No logged in user'
    except SQLAlchemyError as exc:
        user_info = u'Could not get user info due to SQLAlchemy exc: {}'
        user_info = user_info.format(_as_unicode(exc))

    versions = '\n'.join('%s: %s' % (pkg_name, get_version(pkg_name))
                         for pkg_name in
                          ['zaphod', 'pyramid_frontend', 'pyramid_es',
                           'pyramid_uniform', 'pyramid_cron', 'gimlet'])

    return exclog_message.format(
        url=request.url,
        user_info=user_info,
        env=env,
        get_params=get_params,
        post_params=post_params,
        cookies=cookies,
        versions=versions,
    )


def get_git_version(package):

    def safe_read(path):
        try:
            with open(path) as fp:
                return fp.read().strip()
        except (IOError, OSError) as exc:
            return None

    repo_path = os.path.dirname(pkg_resources.resource_filename(package, ''))
    git_path = os.path.join(repo_path, '.git')
    head_path = os.path.join(git_path, 'HEAD')

    # A ref spec like 'ref: refs/heads/master' or a SHA1
    head = safe_read(head_path)
    ref_match = re.match(r'ref: (?P<ref_path>.+)', head)
    if ref_match:
        ref_path = ref_match.groupdict()['ref_path']
        sha1_path = os.path.join(git_path, ref_path)
        sha1 = safe_read(sha1_path)
    else:
        sha1_match = re.match(r'(?P<sha1>[a-f0-9]{40})', head)
        if sha1_match:
            sha1 = sha1_match.groupdict()['sha1']
        else:
            sha1 = head
    return sha1


def get_version(package):
    git_sha1 = get_git_version(package)
    pkg_version = pkg_resources.get_distribution(package).version
    if git_sha1:
        return '%s - %s' % (pkg_version, git_sha1)
    else:
        return pkg_version


def format_dict(d):
    """Format dict nicely as a unicode string."""
    items = []
    template = u'{}: {}'
    for k, v in sorted(d.items()):
        k = _as_unicode(k)
        v = _as_unicode(v)
        items.append(template.format(k, v))
    return u'\n'.join(items)


def _as_unicode(obj, encoding='utf-8', errors='replace'):
    """Convert an ``obj``ect to a unicode string.

    Assume byte strings are UTF-8 encoded. Call ``str()`` on other objects,
    then convert that string to unicode.

    Be lenient about unknown chars--they will be replaced with the official
    Unicode replacement char.

    """
    if isinstance(obj, text_type):
        return obj
    elif isinstance(obj, binary_type):
        return obj.decode(encoding, errors)
    else:
        return str(obj)
