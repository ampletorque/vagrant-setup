from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from .. import mail


class ContactForm(Schema):
    "Validates contact form submissions."
    allow_extra_fields = False
    email = validators.Email(not_empty=True)
    subject = validators.UnicodeString()
    message = validators.UnicodeString(not_empty=True)


@view_config(route_name='contact', renderer='contact.html')
def contact_view(request):
    form = Form(request, schema=ContactForm)

    if form.validate():
        vars = dict(
            body=form.data['message'],
            user_agent=request.user_agent,
        )
        mail.send_with_admin(request, 'contact', vars,
                             to=form.data['email'],
                             reply_to=form.data['email'])

        request.flash(
            "Thank you for your inquiry. Your message has been received. "
            "We make every effort to respond to customer requests as "
            "quickly as possible.", 'success')

        raise HTTPFound(location=request.url)

    return dict(renderer=FormRenderer(form))
