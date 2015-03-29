from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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


def tag_view(context, request):
    tag = context.node
    return TagListView(request, tag)()


def includeme(config):
    config.add_view(tag_view,
                    route_name='node',
                    custom_predicates=[NodePredicate(model.Tag)],
                    renderer='browse.html')
