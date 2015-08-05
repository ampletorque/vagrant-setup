from pyramid.view import view_config, view_defaults

from .base import BaseReportsView

from .... import model


@view_defaults(permission='admin')
class EmailsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:emails',
                 renderer='admin/reports/emails.html')
    def emails(self):
        q = model.Session.query(model.User.email)
        user_count = q.count()
        q = model.Session.query(model.NewsletterEmail.email)
        newsletter_count = q.count()
        return {
            'user_count': user_count,
            'newsletter_count': newsletter_count,
        }

    @view_config(route_name='admin:reports:emails',
                 request_param='format=csv', renderer='string')
    def emails_csv(self):
        emails = set()

        q = model.Session.query(model.User.email)
        for email, in q:
            emails.add(email)

        q = model.Session.query(model.NewsletterEmail.email)
        for email, in q:
            emails.add(email)

        emails = list(emails)
        emails.sort()
        return '\n'.join(emails)
