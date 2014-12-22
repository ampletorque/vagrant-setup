def includeme(config):
    config.add_route('admin', '/')

    config.add_route('admin:creators', '/creators')
    config.add_route('admin:projects', '/projects')
    config.add_route('admin:users', '/users')
