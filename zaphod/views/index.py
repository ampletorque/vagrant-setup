from pyramid.view import view_config


@view_config(route_name='index', renderer='index.html')
def index_view(request):
    def get_groups():
        settings = request.registry.settings
        rows = []
        for ii in range(10):
            key = 'index.row-%d' % ii
            heading_key = key + '.heading'
            if heading_key in settings:
                project_ids = []
                for row_s in settings[key + '.projects'].split('/'):
                    project_ids.append([int(piece) for piece in row_s.split()])
                rows.append((settings[heading_key], project_ids))
        return rows

    return dict(get_groups=get_groups)
