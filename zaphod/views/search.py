from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.httpexceptions import HTTPFound

from pyramid_es import get_client

from .. import model
from .browse import ProjectListView


class ProjectSearchView(ProjectListView):

    @property
    def phrase(self):
        request = self.request
        phrase = request.params.get('q')
        if not phrase:
            raise HTTPFound(location=request.route_url('index'))
        return phrase

    @property
    def stage(self):
        phrase = self.phrase
        return "Search Results for '%s'" % phrase

    def get_project_ids(self):
        phrase = self.phrase

        client = get_client(self.request)
        q = client.query(model.Project, q=phrase).\
            filter_term('published', True)

        result = q.execute()
        project_ids = [int(record._id) for record in result]
        return project_ids


def includeme(config):
    config.add_view(ProjectSearchView, route_name='search',
                    renderer='browse.html')
