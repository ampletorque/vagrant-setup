from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from ... import model, mail

from . import NodePredicate


class AskQuestionForm(Schema):
    allow_extra_fields = False
    email = validators.Email(not_empty=True)
    message = validators.UnicodeString(not_empty=True)


def ask_question_view(context, request):
    project = context.node
    form = Form(request, schema=AskQuestionForm)
    if form.validate():
        email = form.data['email']
        message = form.data['message']
        creator_emails = [(owner.user.name, owner.user.email)
                          for owner in project.ownerships
                          if owner.can_receive_questions]

        mail.send_with_admin(
            request,
            'project_question',
            vars=dict(
                email=email,
                message=message,
                project=project,
            ),
            to=creator_emails,
            reply_to=email,
            cc=request.registry.settings['mailer.from'])

        request.flash(
            "Thanks, we'll try to answer your question as soon as "
            "possible.", 'success')

        return HTTPFound(location=request.node_url(project))

    return {
        'renderer': FormRenderer(form),
        'action': 'ask-question',
        'project': project,
    }


def remind_me_view(context, request):
    project = context.node
    if not request.method == 'POST':
        raise HTTPNotFound
    pe = model.ProjectEmail(project=project,
                            email=request.params['email'],
                            source='remind')
    model.Session.add(pe)

    request.flash(
        "Thanks, we'll remind you when this project is nearing the end of its "
        "campaign.", 'success')
    return HTTPFound(location=request.node_url(project))


def prelaunch_signup_view(context, request):
    project = context.node
    if not request.method == 'POST':
        raise HTTPNotFound
    pe = model.ProjectEmail(project=project,
                            email=request.params['email'],
                            source='signup')
    model.Session.add(pe)

    request.flash(
        "Thanks, we'll keep you updated and notify you when this project "
        "campaign launches.", 'success')
    return HTTPFound(location=request.node_url(project))


def updates_view(context, request):
    project = context.node
    return {
        'action': 'updates',
        'project': project,
    }


def backers_view(context, request):
    project = context.node
    q = model.Session.query(model.User).\
        join(model.User.orders).\
        join(model.Order.cart).\
        join(model.Cart.items).\
        join(model.CartItem.product).\
        filter(model.Product.project == project).\
        filter(model.User.show_in_backers == True).\
        order_by(model.Order.id.desc())
    # XXX filter out cancelled orders

    backers = q.all()

    return {
        'action': 'backers',
        'project': project,
        'backers': backers,
    }


def project_base_view(context, request):
    project = context.node
    return {
        'action': None,
        'project': project,
    }


def includeme(config):
    config.add_view(
        project_base_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project)],
        renderer='project.html')
    config.add_view(
        remind_me_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project, suffix='remind-me')])
    config.add_view(
        ask_question_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project,
                                         suffix='ask-question')],
        renderer='ask_question.html')
    config.add_view(
        updates_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project, suffix='updates')],
        renderer='updates.html')
    config.add_view(
        backers_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project, suffix='backers')],
        renderer='backers.html')
    config.add_view(
        prelaunch_signup_view,
        route_name='node',
        custom_predicates=[NodePredicate(model.Project,
                                         suffix='prelaunch-signup')])
