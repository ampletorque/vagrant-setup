from pyramid.view import view_config


@view_config(route_name='how', renderer='how.html')
def how_view(request):
    return {}


@view_config(route_name='questions', renderer='questions.html')
def questions_view(request):
    return {}


@view_config(route_name='logistics', renderer='logistics.html')
def logistics_view(request):
    return {}


@view_config(route_name='funding', renderer='funding.html')
def funding_view(request):
    return {}


@view_config(route_name='campaign-information',
             renderer='campaign_information.html')
def campaign_information_view(request):
    return {}


@view_config(route_name='user-experience',
             renderer='user_experience.html')
def user_experience_view(request):
    return {}
