from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.orm.exc import NoResultFound
from formencode import validators, Schema
from pyramid.httpexceptions import HTTPFound
from pyramid_uniform import Form, FormRenderer
from pyramid.view import view_config

from .. import model


class EmailSignupForm(Schema):
    "Validate email signup submissions."
    allow_extra_fields = False
    email = validators.Email(not_empty=True)


@view_config(route_name='subscribe', renderer='email_signup.html')
def subscribe_view(request):
    form = Form(request, EmailSignupForm)

    # Skip CSRF here, since it's not really a secure resource of any
    # kind, and leaving off the CSRF token means we can happily cache the
    # email signup form everywhere.
    if form.validate(skip_csrf=True):
        q = model.Session.query(model.NewsletterEmail).\
            filter_by(email=form.data['email'])

        try:
            addr = q.one()
        except NoResultFound:
            addr = model.NewsletterEmail(
                email=form.data['email'],
                source='signup',
            )
            model.Session.add(addr)

        request.flash("Thanks for signing up!", 'success')
        return HTTPFound(location=request.route_url('index'))

    return dict(renderer=FormRenderer(form))
