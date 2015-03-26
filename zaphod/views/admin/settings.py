from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer


class SettingsForm(Schema):
    allow_extra_fields = False
    show_admin_bars = validators.Bool()


@view_config(route_name='admin:settings', renderer='admin/settings.html',
             permission='admin')
def settings_view(request):
    form = Form(request, schema=SettingsForm)
    if form.validate():
        form.bind(request.user)
        request.flash('Saved changes.', 'success')
        return HTTPFound(location=request.current_route_url())
    return dict(renderer=FormRenderer(form))
