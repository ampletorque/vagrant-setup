from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from venusian import lift
from formencode import Schema, validators
from pyramid_es import get_client

from ... import mail, model, custom_validators

from ...admin import BaseEditView, BaseListView, BaseCreateView


@view_defaults(route_name='admin:user', renderer='admin/user.html',
               permission='admin')
@lift()
class UserEditView(BaseEditView):
    cls = model.User

    class UpdateForm(Schema):
        allow_extra_fields = False
        name = validators.String(not_empty=True)
        email = validators.Email(not_empty=True)
        password = validators.String()
        password2 = validators.String()
        enabled = validators.Bool()
        admin = validators.Bool()
        show_admin_bars = validators.Bool()
        show_in_backers = validators.Bool()
        show_location = validators.String()
        show_name = validators.String()
        timezone = validators.String()
        url_path = custom_validators.URLString()
        twitter_username = custom_validators.TwitterUsername()
        chained_validators = [validators.FieldsMatch('password', 'password2')]
        new_comment = custom_validators.CommentBody()

    @view_config(route_name='admin:user:send-password-reset')
    def send_password_reset(self):
        request = self.request
        user = self._get_object()
        token = user.set_reset_password_token()
        mail.send_password_reset(request, user, token)
        request.flash('Sent password reset email to %s.' % user.email,
                      'success')
        return HTTPFound(location=request.route_path('admin:user', id=user.id))

    @view_config(route_name='admin:user:send-welcome-email')
    def send_welcome_email(self):
        request = self.request
        user = self._get_object()
        token = user.set_reset_password_token()
        mail.send_welcome_email(request, user, token)
        request.flash('Sent welcome email to %s.' % user.email, 'success')
        return HTTPFound(location=request.route_path('admin:user', id=user.id))


@view_defaults(route_name='admin:users', renderer='admin/users.html',
               permission='admin')
@lift()
class UserListView(BaseListView):
    cls = model.User
    paginate = True

    @view_config(route_name='admin:users:search', xhr=True, renderer='json')
    def search(self):
        request = self.request
        q = request.params.get('q')

        client = get_client(request)
        results = client.query(model.User, q=q).limit(40).execute()

        return {
            'total': results.total,
            'users': [
                {
                    'id': user._id,
                    'name': user.name,
                    'email': user.email,
                }
                for user in results
            ]
        }


@view_defaults(route_name='admin:users:new',
               renderer='admin/users_new.html', permission='admin')
@lift()
class UserCreateView(BaseCreateView):
    cls = model.User
    obj_route_name = 'admin:user'

    class CreateForm(Schema):
        allow_extra_fields = False
        name = validators.String(not_empty=True)
        email = validators.Email(not_empty=True)
        password = validators.String()
        password2 = validators.String()
        admin = validators.Bool()
        send_welcome_email = validators.Bool()
        chained_validators = [validators.FieldsMatch('password', 'password2')]

    def _create_object(self, form):
        request = self.request
        del form.data['password2']
        send_email = form.data.pop('send_welcome_email')

        existing = model.Session.query(self.cls).\
            filter_by(email=form.data['email']).\
            first()

        if existing:
            request.flash("A user with the specified email address already "
                          "exists. This is the admin page for the existing "
                          "user.", 'error')
            raise HTTPFound(location=request.route_url('admin:user',
                                                       id=existing.id))

        obj = BaseCreateView._create_object(self, form)
        if send_email:
            token = obj.set_reset_password_token()
            mail.send_welcome_email(request, obj, token)
        return obj
