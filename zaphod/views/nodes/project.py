from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config
from formencode import Schema, validators
from pyramid_uniform import Form, FormRenderer

from ... import model, mail

from . import NodePredicate


class AskQuestionForm(Schema):
    allow_extra_fields = False
    email = validators.Email(not_empty=True)
    message = validators.UnicodeString(not_empty=True)


class ProjectView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='node', renderer='ask_question.html',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='ask-question')])
    def ask_question(self):
        request = self.request
        project = self.context.node
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

    @view_config(route_name='node', request_method='POST',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='remind-me')])
    def remind_me(self):
        request = self.request
        project = self.context.node
        pe = model.ProjectEmail(project=project,
                                email=request.params['email'],
                                source='remind')
        model.Session.add(pe)

        request.flash(
            "Thanks, we'll remind you when this project is nearing the end "
            "of its campaign.", 'success')
        return HTTPFound(location=request.node_url(project))

    @view_config(route_name='node', request_method='POST',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='prelaunch-signup')])
    def prelaunch_signup(self):
        request = self.request
        project = self.context.node
        pe = model.ProjectEmail(project=project,
                                email=request.params['email'],
                                source='signup')
        model.Session.add(pe)

        request.flash(
            "Thanks, we'll keep you updated and notify you when this project "
            "campaign launches.", 'success')
        return HTTPFound(location=request.node_url(project))

    @view_config(route_name='node', renderer='updates.html',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='updates')])
    def updates_view(self):
        project = self.context.node
        return {
            'action': 'updates',
            'project': project,
        }

    @view_config(route_name='node', renderer='backers.html',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='backers')])
    def backers_view(self):
        project = self.context.node
        q = model.Session.query(model.User).\
            join(model.User.orders).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            filter(model.Product.project == project).\
            filter(model.CartItem.status != 'cancelled').\
            filter(model.User.show_in_backers == True).\
            order_by(model.Order.id.desc())
        backers = q.all()
        return {
            'action': 'backers',
            'project': project,
            'backers': backers,
        }

    @view_config(route_name='node', renderer='project.html',
                 custom_predicates=[NodePredicate(model.Project)])
    def project_base(self):
        project = self.context.node
        return {
            'action': None,
            'project': project,
        }

    def _verify_owner(self):
        request = self.request
        project = self.context.node
        if not (request.user and (request.user.admin or
                project.check_owner(request.user))):
            raise HTTPForbidden

    @view_config(route_name='node', renderer='project_crowdfunding.html',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='crowdfunding')])
    def crowdfunding(self):
        request = self.request
        project = self.context.node
        if project.status == 'crowdfunding':
            raise HTTPFound(location=request.node_url(project))
        elif project.status == 'prelaunch':
            self._verify_owner()
        return {
            'action': 'crowdfunding',
            'project': project,
        }

    @view_config(route_name='node', renderer='project_available.html',
                 custom_predicates=[NodePredicate(model.Project,
                                                  suffix='available')])
    def available(self):
        request = self.request
        project = self.context.node
        if project.status == 'available':
            raise HTTPFound(location=request.node_url(project))
        self._verify_owner()
        return {
            'action': 'available',
            'project': project,
        }
