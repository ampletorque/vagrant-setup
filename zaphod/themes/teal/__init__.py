from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import socket

from dogpile.cache import make_region
from dogpile.cache.proxy import ProxyBackend

from pyramid_frontend.images.filters import ThumbFilter, VignetteFilter
from pyramid_frontend.images.chain import FilterChain
from pyramid_frontend.theme import Theme
from pyramid_frontend.assets.less import LessAsset
from pyramid_frontend.assets.requirejs import RequireJSAsset

from .imagefilters import CreatorProfileFilter

log = logging.getLogger(__name__)


if socket.gethostname().startswith('janus.'):
    lessc_path = '/var/sw/less-1.7.0/node_modules/less/bin/lessc'
else:
    lessc_path = 'lessc'


class LoggingProxy(ProxyBackend):
    def set(self, key, value):
        log.debug("cache set: %r -> %r", key, value)
        self.proxied.set(key, value)

    def get(self, key):
        log.debug("cache get: %r", key)
        return self.proxied.get(key)


cache_regions = {
    'default': make_region().configure(
        'dogpile.cache.redis',
        arguments={
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'redis_expiration_time': 60 * 60 * 2,
            'distributed_lock': True,
        },
        # XXX Enable this to log cache accesses.
        # wrap=[LoggingProxy],
    ),
}


class TealTheme(Theme):
    key = 'teal'

    assets = {
        'main-less': LessAsset(
            '/_teal/css/main.less',
            less_path='/_teal/js/vendor/less.js',
            lessc_path=lessc_path,
        ),
        'admin-less': LessAsset(
            '/_teal/css/admin.less',
            less_path='/_teal/js/vendor/less.js',
            lessc_path=lessc_path,
        ),
        'paper-less': LessAsset(
            '/_teal/css/paper.less',
            less_path='/_teal/js/vendor/less.js',
            lessc_path=lessc_path,
        ),
        'main-js': RequireJSAsset(
            '/_teal/js/main.js',
            require_config_path='/_teal/js/require_config.js',
            require_base_url='/_teal/js/vendor/',
        ),
        'admin-js': RequireJSAsset(
            '/_teal/js/admin.js',
            require_config_path='/_teal/js/require_config.js',
            require_base_url='/_teal/js/vendor/',
        ),
    }

    # XXX All of these may need size tweaking
    image_filters = [
        FilterChain(
            'admin-thumb', width=250, height=250,
            crop=False, pad=True,
            extension='jpg', quality=65),

        FilterChain(
            'admin-tiny', width=64, height=64,
            crop=False, pad=True,
            extension='jpg', quality=65),

        FilterChain(
            'project-main', width=749, height=421,
            crop_whitespace=True, pad=True, crop='nonwhite',
            extension='jpg', quality=85),

        # FilterChain(
        #     'project-slider', width=100, height=100,
        #     crop=True, pad=True,
        #     extension='jpg', quality=85),

        FilterChain(
            'product-icon', width=100, height=100,
            crop_whitespace=True, pad=True,
            extension='jpg', quality=85),

        # FilterChain(
        #     'creator-avatar', width=120, height=60,
        #     crop_whitespace=True, pad=True,
        #     extension='png'),

        FilterChain(
            'creator-logo', width=140, height=140,
            crop_whitespace=True, pad=True,
            extension='png'),

        FilterChain(
            'large-avatar', width=120, height=120,
            crop=True, pad=True,
            extension='png'),

        FilterChain(
            'project-mega', width=1200, extension='jpg',
            filters=[
                ThumbFilter((1200, 400), crop_whitespace=True, pad=True,
                            crop='nonwhite'),
                VignetteFilter(),
            ],
            quality=85),

        FilterChain(
            'project-body', width=749, extension='jpg',
            quality=85),

        FilterChain(
            'project-tile', width=749, height=421,
            filters=[
                ThumbFilter((749, 421), crop_whitespace=True, pad=True,
                            crop='nonwhite'),
                VignetteFilter(),
            ],
            extension='jpg', quality=85),

        # FilterChain(
        #     'project-wide', width=1170, height=658,
        #     crop_whitespace=True, pad=True, crop='nonwhite',
        #     extension='jpg', quality=85),

        FilterChain(
            'creator-profile', width=200, height=140,
            filters=[CreatorProfileFilter()],
            pad=True, extension='png'),

        FilterChain(
            'project-avatar', width=72, height=72,
            crop=True, pad=True,
            extension='png'),

        FilterChain(
            'header-avatar', width=34, height=34,
            crop=True, pad=True,
            extension='png'),

        FilterChain(
            'pledge-body', width=150, height=150,
            crop_whitespace=True, pad=True,
            extension='jpg', quality=70),

        # FilterChain(
        #     'hero-wide', width=2000, height=300,
        #     crop=True,
        #     extension='jpg', quality=75),

        FilterChain(
            'press-logo', width=150, height=75,
            crop_whitespace=True, pad=True,
            extension='png'),
    ]

    cache_impl = 'dogpile.cache'
    cache_args = {
        'regions': cache_regions,
    }

    def invalidate_index(self):
        cache = cache_regions['default']
        cache.invalidate('index')

    def invalidate_project(self, project_id):
        cache = cache_regions['default']
        cache.invalidate('project-%d-tile' % project_id)
        cache.invalidate('project-%d-body' % project_id)
        cache.invalidate('project-%d-sidebar' % project_id)
        cache.invalidate('project-%d-leader' % project_id)
        self.invalidate_index()
