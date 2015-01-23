from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config


class MailTemplateView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:mail_template',
                 match_param='template_name=forgot-password',
                 renderer='emails/forgot_password.html',
                 permission='authenticated')
    def reset_password(self):
        request = self.request
        user = request.user
        token = user.set_reset_password_token()
        link = request.route_url('forgot-reset', _query=dict(
            email=user.email,
            token=token,
        ))
        return dict(user=user, link=link)
