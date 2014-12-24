from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def includeme(config):
    config.include('.article')
    config.include('.creator')
    config.include('.project')
    config.include('.update')
    config.include('.tag')
    config.include('.provider')
    config.include('.provider_type')
