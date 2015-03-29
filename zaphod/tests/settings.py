from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


settings = {
    'sqlalchemy.url': 'sqlite:///',

    'elastic.index': 'zaphod-tests',

    'debug': 'true',
    'testing': 'true',

    'pyramid_frontend.compiled_asset_dir': '/tmp/zaphod/compiled',
    'pyramid_frontend.theme': 'teal',

    'payment.mock': 'true',

    'gimlet.secret': 's3krit',
    'cache.backend': 'dogpile.cache.memory',
    'cache.prefix': 'test:',
}
