from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid.renderers import render
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from mako.exceptions import TopLevelLookupException
from premailer import Premailer


def process_html(body):
    return Premailer(body,
                     keep_style_tags=True,
                     include_star_selectors=True).transform()


def send(request, template_name, vars, to=None, from_=None,
         bcc=None, cc=None):
    settings = request.registry.settings

    subject = render('emails/%s.subject.txt' % template_name,
                     vars, request)
    subject = subject.strip()

    msg = Message(
        subject=subject,
        sender=from_ or settings['mailer.from'],
        recipients=to or [settings['mailer.from']],
    )

    try:
        html_body = render('emails/%s.html' % template_name,
                           vars, request)
    except TopLevelLookupException:
        pass
    else:
        msg.html = process_html(html_body)

    msg.body = render('emails/%s.txt' % template_name,
                      vars, request)

    mailer = get_mailer(request)
    mailer.send(msg)
