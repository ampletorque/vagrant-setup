def includeme(config):
    config.add_route('admin:reports', '/list')

    config.add_route('admin:reports:sales', '/sales')
    config.add_route('admin:reports:funding-success', '/funding-success')
    config.add_route('admin:reports:project-launches', '/project-launches')
    config.add_route('admin:reports:user-behavior', '/user-behavior')
    config.add_route('admin:reports:delays', '/delays')
    config.add_route('admin:reports:project-delays', '/project-delays')
    config.add_route('admin:reports:overdue-batches', '/overdue-batches')

    config.add_route('admin:reports:funnel-analysis', '/funnel-analysis')
    config.add_route('admin:reports:lead-activity', '/lead-activity')
    config.add_route('admin:reports:pipeline', '/pipeline')
    config.add_route('admin:reports:lead-sources', '/lead-sources')

    config.add_route('admin:reports:revenue', '/revenue')
    config.add_route('admin:reports:cogs', '/cogs')
    config.add_route('admin:reports:cashflow', '/cashflow')
    config.add_route('admin:reports:inventory', '/inventory')
    config.add_route('admin:reports:payments', '/payments')
    config.add_route('admin:reports:chargebacks', '/chargebacks')

    config.add_route('admin:reports:warehouse-transactions',
                     '/warehouse-transactions')
    config.add_route('admin:reports:project-open-items',
                     '/project-open-items')
