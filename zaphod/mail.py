from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import os
import os.path
import email.utils
import textwrap
from datetime import datetime

import six

from pyramid.renderers import render
from pyramid.settings import asbool
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from mako.exceptions import TopLevelLookupException
from premailer import Premailer

from . import model

log = logging.getLogger(__name__)


def process_html(body):
    return Premailer(body,
                     keep_style_tags=True,
                     include_star_selectors=True).transform()


def process_text(body):
    out_lines = []
    for line in body.split('\n'):
        if line:
            out_lines.extend(textwrap.wrap(line, 79,
                                           break_long_words=False,
                                           break_on_hyphens=False))
        else:
            out_lines.append('')
    return '\n'.join(out_lines)


def dump_locally(settings, msg):
    # Don't use UTC, local time is more convenient for debugging.
    now = datetime.now()
    local_dir = settings['mailer.debug_dir']
    base_dir = now.strftime('%Y%m%d-%H%M%S')
    this_dir = os.path.join(local_dir, base_dir)
    if not os.path.exists(this_dir):
        os.makedirs(this_dir)

    with open(os.path.join(this_dir, 'raw.txt'), 'w') as f:
        raw_msg = msg.to_message()
        f.write(raw_msg.as_string())

    with open(os.path.join(this_dir, 'body.txt'), 'w') as f:
        f.write(msg.body)

    if msg.html:
        with open(os.path.join(this_dir, 'body.html'), 'w') as f:
            f.write(msg.html)


def format_address_list(addrs):
    return [addr if isinstance(addr, six.string_types) else
            email.utils.formataddr(addr) for addr in addrs]


def send(request, template_name, vars, to=None, from_=None,
         bcc=None, cc=None, reply_to=None):
    settings = request.registry.settings

    subject = render('emails/%s.subject.txt' % template_name,
                     vars, request)

    # Strip out any newlines so that we don't cause issues with mangled
    # headers.
    subject = subject.strip().replace('\n', ' ').replace('\r', '')

    recipients = format_address_list(to or [settings['mailer.from']])

    extra_headers = {}
    if reply_to:
        extra_headers['Reply-To'] = reply_to

    msg = Message(
        subject=subject,
        sender=from_ or settings['mailer.from'],
        recipients=recipients,
        cc=cc and format_address_list(cc),
        bcc=bcc and format_address_list(bcc),
        extra_headers=extra_headers,
    )

    try:
        html_body = render('emails/%s.html' % template_name,
                           vars, request)
    except TopLevelLookupException:
        pass
    else:
        msg.html = process_html(html_body)

    msg.body = process_text(render('emails/%s.txt' % template_name,
                                   vars, request))

    log.info("enqueueing %s to:%r subject:%r", template_name, to, subject)
    if asbool(settings.get('mailer.debug')):
        dump_locally(settings, msg)
    else:
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
    bcc = bcc or []
    bcc.extend(admin_emails)
    return send(request=request, template_name=template_name,
                vars=vars,
                to=to, from_=from_, bcc=bcc, cc=cc, reply_to=reply_to)


def send_order_confirmation(request, order):
    recipient = [(order.shipping.full_name,
                  order.user.email)]
    items_by_project = {}
    for item in order.cart.items:
        this_project = items_by_project.setdefault(item.product.project, [])
        this_project.append(item)
    vars = {
        'order': order,
        'items_by_project': items_by_project,
    }
    send_with_admin(request, 'order_confirmation', vars=vars, to=recipient)
