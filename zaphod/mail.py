from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import os.path
import email.utils
from datetime import datetime
from email.mime.text import MIMEText

from pyramid.renderers import render
from pyramid.settings import asbool
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from mako.exceptions import TopLevelLookupException
from premailer import Premailer

from . import model


def process_html(body):
    return Premailer(body,
                     keep_style_tags=True,
                     include_star_selectors=True).transform()


def dump_locally(settings, msg):
    # Don't use UTC, local time is more convenient for debugging.
    now = datetime.now()
    local_dir = settings['mailer.debug_dir']
    base_dir = now.strftime('%Y%m%d-%H%M%S')
    this_dir = os.path.join(local_dir, 'emails', base_dir)
    if not os.path.exists(this_dir):
        os.makedirs(this_dir)

    with open(os.path.join(this_dir, 'headers.txt'), 'w') as f:
        raw_msg = MIMEText('', 'plain', msg.charset)
        msg._set_info(raw_msg)
        f.write(raw_msg.as_string())

    with open(os.path.join(this_dir, 'body.txt'), 'w') as f:
        f.write(msg.body)

    with open(os.path.join(this_dir, 'body.html'), 'w') as f:
        f.write(msg.html)


def send(request, template_name, vars, to=None, from_=None,
         bcc=None, cc=None):
    settings = request.registry.settings

    subject = render('emails/%s.subject.txt' % template_name,
                     vars, request)

    # Strip out any newlines so that we don't cause issues with mangled
    # headers.
    subject = subject.strip().replace('\n', ' ').replace('\r', '')

    recipients = to or [settings['mailer.from']]
    recipients = [recipient
                  if isinstance(recipient, basestring) else
                  email.utils.formataddr(recipient)
                  for recipient in recipients]

    msg = Message(
        subject=subject,
        sender=from_ or settings['mailer.from'],
        recipients=recipients,
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

    if asbool(settings.get('mailer.debug')):
        dump_locally(settings, msg)

    mailer = get_mailer(request)
    mailer.send(msg)


def load_admin_users(template_name):
    # XXX
    return model.Session.query(model.User).filter_by(admin=True).all()


def send_with_admin(request, template_name, vars, to=None, from_=None,
                    bcc=None, cc=None, reply_to=None):
    """
    Wrap the ``mail.send()`` so that emails are bcc'd to any admin users with
    the corresponding setting set.
    """
    admin_emails = [(user.name, user.email) for user in
                    load_admin_users(template_name)]
    bcc.extend(admin_emails)
    return send(request=request, template_name=template_name, vars=vars,
                to=to, from_=from_, bcc=bcc, cc=cc)
