from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from .. import model, helpers as h


class AskQuestionForm(Schema):
    allow_extra_fields = False
    email = validators.Email(not_empty=True)
    message = validators.UnicodeString(not_empty=True)


def ask_question_handler(project, request):
    form = Form(request, schema=AskQuestionForm)
    if form.validate():
        email = form.data['email']
        message = form.data['message']
        # creator_emails = [owner.account.email
        #                  for owner in project.ownerships
        #                  if owner.can_receive_questions]

        subject = h.truncate(message, 30).\
            replace('\n', ' ').replace('\r', '')

        # send_with_admin('project_question',
        #                '[Campaign Question] %s' % subject,
        #                email=email,
        #                message=message,
        #                project=project,
        #                to=creator_emails,
        #                reply_to=email,
        #                cc='support@crowdsupply.com')

        request.flash(
            "Thanks, we'll try to answer your question as soon as "
            "possible.", 'success')

        return HTTPFound(location=request.node_url(project))

    return render('ask_question.html', {
        'renderer': FormRenderer(form),
        'action': 'ask-question',
        'project': project,
    }, request)


def remind_me_handler(project, request):
    if not request.method == 'POST':
        raise HTTPNotFound
    pe = model.ProjectEmail(project=project,
                            email=request.params['email'],
                            source='remind')
    model.Session.add(pe)
    model.Session.commit()

    request.flash(
        "Thanks, we'll remind you when this project is nearing the end of its "
        "campaign.", 'success')
    raise HTTPFound(location=request.node_url(project))


def updates_handler(project, request):
    return render('updates.html', {
        'action': 'updates',
        'project': project,
    }, request)


def backers_handler(project, request):
    q = model.Session.query(model.User).\
        join(model.User.orders).\
        join(model.Order.cart).\
        join(model.Cart.items).\
        join(model.CartItem.pledge_level).\
        filter(model.PledgeLevel.project == project).\
        filter(model.User.show_in_backers == True)
    # XXX filter out cancelled orders

    backers = q.all()

    return render('backers.html', {
        'action': 'backers',
        'project': project,
        'backers': backers,
    }, request)


def project_renderer(project, system):
    request = system['request']
    suffix = system['suffix']

    if suffix:
        if len(suffix) != 1:
            raise HTTPNotFound
        action = suffix[0]
        if action == 'remind-me':
            return remind_me_handler(project, request)
        elif action == 'ask-question':
            return ask_question_handler(project, request)
        elif action == 'updates':
            return updates_handler(project, request)
        elif action == 'backers':
            return backers_handler(project, request)
        else:
            raise HTTPNotFound

        raise NotImplementedError

    return render('project.html', {
        'action': None,
        'project': project,
    }, request)


def includeme(config):
    config.add_node_renderer(project_renderer, model.Project,
                             accept_suffix=True)
