from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render

from .. import model


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
        elif action == 'updates':
            return updates_handler(project, request)
        elif action == 'backers':
            return backers_handler(project, request)
        else:
            raise HTTPNotFound

        raise NotImplementedError

    return render('project.html', dict(project=project), request)


def includeme(config):
    config.add_node_renderer(project_renderer, model.Project, accept_suffix=True)
