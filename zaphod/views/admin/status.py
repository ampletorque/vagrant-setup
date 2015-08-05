import sys
import re
import socket

from pyramid.view import view_config
import redis

from ... import model


@view_config(route_name='admin:status', renderer='admin/status.html',
             permission='admin')
def status_view(request):
    # system uptime
    hostname = socket.gethostname()

    # DB/pool info
    engine = model.Base.metadata.bind
    # Mask password in connection string
    engine_url = re.sub(':[^/].*@', ':****@', str(engine.url))

    # redis stats
    redis_stats = redis.Redis().info()

    return {
        'hostname': hostname,
        'engine': engine,
        'engine_url': engine_url,
        'sys': sys,
        'redis_stats': redis_stats,
    }
