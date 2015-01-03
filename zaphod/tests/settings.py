from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


settings = {
    'sqlalchemy.url': 'sqlite:///',

    'elastic.index': 'zaphod-tests',

    'debug': 'true',

    'pyramid_frontend.compiled_asset_dir': '/tmp/zaphod/compiled',
    'pyramid_frontend.theme': 'teal',

    'gimlet.secret': 's3krit',
}
