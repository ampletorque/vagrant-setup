import logging

import os
import os.path
import email.utils
import textwrap
from datetime import datetime, date, timedelta

from pyramid.renderers import render
from pyramid.settings import asbool
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from mako.exceptions import TopLevelLookupException
from premailer import Premailer

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
    return [addr if isinstance(addr, str) else
            email.utils.formataddr(addr) for addr in addrs]


def send(request, template_name, vars, to=None, from_=None,
         bcc=None, cc=None, reply_to=None, immediately=False):
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
        log.info("debug: dumping %s", template_name)
        dump_locally(settings, msg)
        debug_addr = settings.get('mailer.debug_addr')
        if debug_addr:
            log.info("debug: sending %s to %s", template_name, debug_addr)
            subject += ' [was to %s]' % \
                ', '.join(email.utils.parseaddr(addr)[1]
                          for addr in msg.recipients)
            msg.subject = subject
            msg.recipients = [debug_addr]
            msg.cc = []
            msg.bcc = []
            mailer = get_mailer(request)
            mailer.send(msg)
    else:
        mailer = get_mailer(request)
        if immediately:
            mailer.send_immediately(msg)
        else:
            mailer.send(msg)


def send_with_admin(request, template_name, vars, to=None, from_=None,
                    bcc=None, cc=None, reply_to=None, immediately=False):
    """
    Wrap the ``mail.send()`` so that emails are bcc'd to any admin users with
    the corresponding setting set.
    """
    bcc = bcc or []
    bcc.append(request.registry.settings['mailer.admins'])
    return send(request=request, template_name=template_name,
                vars=vars,
                to=to, from_=from_, bcc=bcc, cc=cc, reply_to=reply_to,
                immediately=immediately)


def send_order_confirmation(request, order):
    recipient = [(order.user.name, order.user.email)]
    items_by_project = {}
    for item in order.cart.items:
        this_project = items_by_project.setdefault(item.product.project, [])
        this_project.append(item)
    vars = {
        'order': order,
        'items_by_project': items_by_project,
    }
    send_with_admin(request, 'order_confirmation', vars=vars, to=recipient)


def send_cancellation_confirmation(request, order):
    recipient = [(order.user.name, order.user.email)]
    # XXX
    vars = {
        'order': order,
    }
    send_with_admin(request, 'cancellation_confirmation', vars=vars,
                    to=recipient)


def send_shipping_confirmation(request, order):
    recipient = [(order.user.name, order.user.email)]
    unshipped_items = [item for item in order.cart.items
                       if item.status.key not in ('cancelled', 'shipped')]
    for shipment in order.shipments:
        shipment.tracking_email_sent = True
    vars = {
        'order': order,
        'unshipped_items': unshipped_items,
    }
    send_with_admin(request, 'shipping_confirmation', vars=vars, to=recipient)


def send_update_payment(request, project, order, due_date, link):
    recipient = [(order.user.name, order.user.email)]
    vars = {
        'order': order,
        'project': project,
        'link': link,
        'due_date': due_date,
    }
    send_with_admin(request, 'update_payment', vars=vars, to=recipient)


def send_payment_confirmation(request, project, order, amount):
    recipient = [(order.user.name, order.user.email)]
    vars = {
        'project': project,
        'order': order,
        'amount': amount,
    }
    send_with_admin(request, 'payment_confirmation', vars=vars, to=recipient)


def _send_reset_email(request, user, token, template_name):
    recipient = [(user.name, user.email)]
    link = request.route_url('forgot-reset', _query=dict(
        email=user.email,
        token=token,
    ))
    vars = {
        'link': link,
        'user': user,
    }
    send(request, template_name, vars, to=recipient)


def send_password_reset(request, user, token):
    _send_reset_email(request, user, token, 'reset_password')


def send_welcome_email(request, user, token):
    _send_reset_email(request, user, token, 'welcome_email')


def send_update_payment_email(request, order, link):
    recipient = [(order.user.name, order.user.email)]
    due_date = date.today() + timedelta(days=7)
    vars = {
        'order': order,
        'link': link,
        'due_date': due_date,
    }
    send_with_admin(request, 'update_payment', vars=vars, to=recipient)
