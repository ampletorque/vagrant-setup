from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from formencode import Schema, validators
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_uniform import Form, FormRenderer

from .. import mail


class LaunchForm(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString()
    description = validators.UnicodeString()
    email = validators.Email()
    goal = validators.Number()
    allocation = validators.UnicodeString()
    country = validators.UnicodeString()


templ = '''%(description)s

From: %(email)s
Project Name: %(name)s
Funding Goal: %(goal)s
Allocation: %(allocation)s
Country: %(country)s'''


@view_config(route_name='launch', renderer='launch.html')
def launch_view(request):
    form = Form(request, schema=LaunchForm)

    if form.validate():
        vars = dict(
            body=templ % form.data,
            user_agent=request.user_agent,
            subject=form.data['name'],
            email=form.data['email'],
        )
        mail.send_with_admin(request, 'contact', vars,
                             to='projects+inbound@crowdsupply.com',
                             reply_to=form.data['email'])
        request.flash(
            "Thanks! We'll contact you within 24-48 hours with further "
            "instructions.", 'success')
        return HTTPFound(location=request.route_url('index'))

    return dict(renderer=FormRenderer(form))
