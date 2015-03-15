from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import time

from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.event import listen
from pyramid.threadlocal import get_current_request


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

    level("Query Time: %0.2fms %s [%s]", (total * 1000.), msg, statement)

    # Wrap this in a try/except so that it can still be run even when we're not
    # being used inside an actual web request (e.g. during setup-app or
    # maintenance scripts).
    request = get_current_request()
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
        _log_query_time(now - context.__querytimer, statement % parameters)

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
                request.remote_addr,
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
