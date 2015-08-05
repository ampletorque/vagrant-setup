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

    'index.row-0.heading': 'Recently Launched',
    'index.row-0.projects': '',
    'index.row-1.heading': 'Recently Funded',
    'index.row-1.projects': '',
    'index.row-2.heading': 'Crowd Favorites',
    'index.row-2.projects': '',
}
