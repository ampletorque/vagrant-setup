from pyramid_frontend.theme import Theme
from pyramid_frontend.assets.less import LessAsset
from pyramid_frontend.assets.requirejs import RequireJSAsset


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
