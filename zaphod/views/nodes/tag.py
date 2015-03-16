from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..browse import ProjectListView
from ... import model


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


def tag_view(tag, system):
    request = system['request']
    return TagListView(request, tag)()


def includeme(config):
    config.add_node_view(tag_view, model.Tag, renderer='browse.html')
