from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid_frontend.images.filters import ThumbFilter, VignetteFilter
from pyramid_frontend.images.chain import FilterChain
from pyramid_frontend.theme import Theme
from pyramid_frontend.assets.less import LessAsset
from pyramid_frontend.assets.requirejs import RequireJSAsset

from .imagefilters import CreatorProfileFilter


class TealTheme(Theme):
    key = 'teal'

    assets = {
        'main-less': LessAsset(
            '/_teal/css/main.less',
            less_path='/_teal/js/vendor/less.js',
            lessc_path='/var/sw/less-1.7.0/node_modules/less/bin/lessc',
        ),
        'main-js': RequireJSAsset(
            '/_teal/js/main.js',
            require_config_path='/_teal/js/require_config.js',
            require_base_url='/_teal/js/vendor/',
        ),
    }

    image_filters = [
        # FilterChain(
        #     'project-main', width=749, height=421,
        #     crop_whitespace=True, pad=True, crop='nonwhite',
        #     extension='jpg', quality=85),

        # FilterChain(
        #     'project-slider', width=100, height=100,
        #     crop=True, pad=True,
        #     extension='jpg', quality=85),

        FilterChain(
            'pledge-icon', width=100, height=100,
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

        # FilterChain(
        #     'account-avatar', width=120, height=120,
        #     crop=True, pad=True,
        #     extension='png'),

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

        # FilterChain(
        #     'project-avatar', width=72, height=72,
        #     crop=True, pad=True,
        #     extension='png'),

        # FilterChain(
        #     'header-avatar', width=34, height=34,
        #     crop=True, pad=True,
        #     extension='png'),

        # FilterChain(
        #     'pledge-body', width=150, height=150,
        #     crop_whitespace=True, pad=True,
        #     extension='jpg', quality=70),

        # FilterChain(
        #     'hero-wide', width=2000, height=300,
        #     crop=True,
        #     extension='jpg', quality=75),

        FilterChain(
            'press-logo', width=150, height=75,
            crop_whitespace=True, pad=True,
            extension='png'),
    ]
