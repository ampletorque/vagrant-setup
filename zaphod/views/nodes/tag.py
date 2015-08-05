from pyramid.view import view_config

from ..browse import ProjectListView
from ... import model

from . import NodePredicate


class TagListView(ProjectListView):

    def __init__(self, request, tag):
        ProjectListView.__init__(self, request)
        self.tag = tag
        self.data['tag'] = tag

    def title(self):
        return self.tag.name

    def base_q(self):
        return ProjectListView.base_q(self).\
            filter(model.Project.tags.contains(self.tag))


@view_config(route_name='node', renderer='browse.html',
             custom_predicates=[NodePredicate(model.Tag)])
def tag_view(context, request):
    tag = context.node
    return TagListView(request, tag)()
