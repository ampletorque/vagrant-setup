from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from ... import model, mail


class AskQuestionForm(Schema):
    allow_extra_fields = False
    email = validators.Email(not_empty=True)
    message = validators.UnicodeString(not_empty=True)


def ask_question_view(project, system):
    request = system['request']
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


def remind_me_view(project, system):
    request = system['request']
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


def updates_view(project, system):
    return {
        'action': 'updates',
        'project': project,
    }


def backers_view(project, system):
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


def project_base_view(project, system):
    return {
        'action': None,
        'project': project,
    }


def includeme(config):
    config.add_node_view(project_base_view, model.Project,
                         renderer='project.html')
    config.add_node_view(remind_me_view, model.Project,
                         suffix=['remind-me'])
    config.add_node_view(ask_question_view, model.Project,
                         suffix=['ask-question'],
                         renderer='ask_question.html')
    config.add_node_view(updates_view, model.Project,
                         suffix=['updates'],
                         renderer='updates.html')
    config.add_node_view(backers_view, model.Project,
                         suffix=['backers'],
                         renderer='backers.html')
