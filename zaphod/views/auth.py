from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging

from datetime import datetime, timedelta

from formencode import Schema, NestedVariables, validators

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.security import forget, remember

from pyramid_uniform import Form, FormRenderer

from .. import mail, model, custom_validators


log = logging.getLogger(__name__)


class LoginForm(Schema):
    """
    Schema for validating login attempts.
    """
    allow_extra_fields = False
    email = validators.UnicodeString(not_empty=False, strip=True)
    password = validators.UnicodeString(not_empty=False, strip=True)
    remember_me = validators.Bool()


class SettingsForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    name = validators.UnicodeString(not_empty=True, strip=True)
    email = validators.UnicodeString(not_empty=True, strip=True)
    password = validators.UnicodeString(not_empty=False, min=4, strip=True)
    password2 = validators.UnicodeString(not_empty=False, strip=True)

    url_path = custom_validators.URLString()
    twitter_username = validators.UnicodeString()

    show_in_backers = validators.Bool()
    show_name = validators.UnicodeString()
    show_location = validators.UnicodeString()

    chained_validators = [validators.FieldsMatch('password', 'password2')]


class ForgotPasswordForm(Schema):
    allow_extra_fields = False
    email = validators.UnicodeString(not_empty=True, strip=True)


class ForgotResetForm(Schema):
    allow_extra_fields = False
    password = validators.UnicodeString(not_empty=False, min=4, strip=True)
    password2 = validators.UnicodeString(not_empty=False, strip=True)
    chained_validators = [validators.FieldsMatch('password', 'password2')]


def constant_time_compare(a, b):
    "Compare two strings with constant time. Used to prevent timing attacks."
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


class UserView(object):
    def __init__(self, request):
        self.request = request

    def _do_login(self, email, password, remember_me):
        request = self.request

        user = model.Session.query(model.User).\
            filter_by(email=email).\
            first()
        if user and user.check_password(password):
            # Set auth token.
            remember(request, user.id, user=user, remember=remember_me)
            request.flash('Login successful.', 'success')
            raise HTTPFound(location=request.route_url('account'))
        else:
            request.flash('Email or password incorrect.', 'error')

    @view_config(route_name='account', renderer='account.html',
                 permission='authenticated')
    def account(self):
        return {}

    @view_config(route_name='order', renderer='order.html',
                 permission='authenticated')
    def order(self):
        request = self.request
        order_id = request.matchdict['id']
        order = model.Order.get(order_id)
        return {'order': order}

    @view_config(route_name='settings', renderer='settings.html',
                 permission='authenticated')
    def settings(self):
        request = self.request

        form = Form(request, schema=SettingsForm)
        if form.validate():
            password = form.data.pop('password')
            del form.data['password2']
            form.bind(request.user)
            request.flash('Saved settings.', 'success')

            if password:
                request.user.update_password(password)
                request.flash('Updated password.', 'success')

            return HTTPFound(location=request.route_url('account'))

        return dict(renderer=FormRenderer(form))

    @view_config(route_name='login', renderer='login.html')
    def login(self):
        """
        In a GET, just show the login form.
        In a POST, accept params and try to authenticate the user.
        """
        request = self.request

        form = Form(request, schema=LoginForm, skip_csrf=True)
        if form.validate():
            email = form.data['email']
            password = form.data['password']
            remember_me = form.data['remember_me']
            self._do_login(email, password, remember_me)

        return dict(renderer=FormRenderer(form))

    @view_config(route_name='logout')
    def logout(self):
        """
        Log the user out.
        """
        request = self.request
        if request.user:
            request.flash('You have been logged out.', 'info')
        forget(request)
        raise HTTPFound(location=request.route_url('login'))
        return {}

    def _get_user(self, email):
        return model.Session.query(model.User).\
            filter_by(email=email).\
            first()

    def _validate_reset_token(self):
        """
        Check forgotten password reset token and grab account.

        This will raise a ``400 Bad Request`` if all of the following
        conditions aren't met::

            - an ``email`` param must be present
            - a ``token`` param must be present
            - an active account must be associated with the ``email`` param
            - the ``token`` param must match the account's password reset
              token
        """
        request = self.request
        params = request.GET

        params_present = 'email' in params and 'token' in params
        user = None
        tokens_match = False

        if params_present:
            email = params['email']
            token = params['token']
            user = self._get_user(email)
            if user:
                expected_token = user.password_reset_token
                tokens_match = constant_time_compare(expected_token, token)

        if not (params_present and user and tokens_match):
            log.warn('invalid_reset_token email:%s token:%s',
                     params.get('email'), params.get('token'))
            raise HTTPBadRequest

        now = datetime.utcnow()
        expiration_time = user.password_reset_time + timedelta(days=1)
        if now > expiration_time:
            request.flash('Password reset email has expired.', 'error')
            raise HTTPFound(location=request.route_url('forgot-password'))

        return user

    @view_config(route_name='forgot-password', renderer='forgot_password.html')
    def forgot_password(self):
        request = self.request
        form = Form(request, schema=ForgotPasswordForm)

        if form.validate():
            user = self._get_user(form.data['email'])

            if not user:
                request.flash("No user with that email address "
                              "exists. Please double check it.", 'error')
                raise HTTPFound(location=request.current_route_url())

            token = user.set_reset_password_token()

            link = request.route_url('forgot-reset', _query=dict(
                email=user.email,
                token=token,
            ))
            vars = dict(user=user, link=link)

            mail.send(request, 'reset_password', vars, to=[(user.name,
                                                            user.email)])

            request.flash("An email has been sent with "
                          "instructions to reset your password.", 'error')
            return HTTPFound(location=request.route_url('login'))

        return dict(renderer=FormRenderer(form))

    @view_config(route_name='forgot-reset', renderer='forgot_reset.html')
    def forgot_reset(self):
        request = self.request
        user = self._validate_reset_token()
        form = Form(request, schema=ForgotResetForm)

        if form.validate():
            user.update_password(form.data['password'])
            request.flash("Password has been updated.", 'success')
            return HTTPFound(location=request.route_url('login'))

        return dict(renderer=FormRenderer(form))
