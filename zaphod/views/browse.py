from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.sql import or_

from .. import model


class ProjectListView(object):
    stage = u'Browse Projects'
    feature_count = 0

    def __init__(self, request):
        self.request = request
        self.data = {}

    def title(self):
        return self.stage

    def base_q(self):
        utcnow = datetime.utcnow()
        return model.Session.query(model.Project.id).\
            filter(model.Project.suspended_time == None).\
            filter(model.Project.published == True).\
            filter(model.Project.listed == True).\
            filter(or_(model.Project.end_time >= utcnow,
                       model.Project.successful == True)).\
            order_by(model.Project.gravity)

    def get_project_ids(self):
        return self.base_q().all()

    def render_html(self):
        project_ids = self.get_project_ids()

        if len(project_ids) == 2:
            feature_count = 2
        else:
            feature_count = self.feature_count

        browse_tags = model.Session.query(model.Tag).\
            filter_by(published=True, listed=True).\
            order_by(model.Tag.name)

        data = {
            'browse_tags': browse_tags,
            'projects': project_ids,
            'feature_count': feature_count,
            'stage': self.stage,
            'page_title': self.title(),
        }
        data.update(self.data)
        return data

    def render_json(self):
        raise HTTPNotFound

    def render_csv(self):
        raise HTTPNotFound

    def render_rss(self):
        raise HTTPNotFound

    def render_atom(self):
        raise HTTPNotFound

    def __call__(self):
        format = self.request.params.get('format', 'html')
        if format in ('html', 'json', 'csv', 'rss', 'atom'):
            return getattr(self, 'render_%s' % format)()
        else:
            raise HTTPNotFound()


class EverythingView(ProjectListView):
    feature_count = 2


class PrelaunchView(ProjectListView):
    stage = u'Pre-launch Projects'

    def base_q(self):
        utcnow = datetime.utcnow()
        return ProjectListView.base_q(self).\
            filter(utcnow < model.Project.start_time)


class CrowdfundingView(ProjectListView):
    stage = u'Crowdfunding Projects'

    def base_q(self):
        utcnow = datetime.utcnow()
        return ProjectListView.base_q(self).\
            filter(utcnow >= model.Project.start_time,
                   utcnow < model.Project.end_time)


class AvailableView(ProjectListView):
    stage = u'Funded & Available Projects'

    def base_q(self):
        utcnow = datetime.utcnow()
        return ProjectListView.base_q(self).\
            filter(utcnow >= model.Project.end_time).\
            filter(model.Project.accepts_preorders == True)


class ArchiveView(ProjectListView):
    stage = 'Project Archive'

    def base_q(self):
        utcnow = datetime.utcnow()
        return ProjectListView.base_q(self).\
            filter(utcnow >= model.Project.end_time).\
            filter(model.Project.accepts_preorders == False)


def includeme(config):
    config.add_view(EverythingView, route_name='browse',
                    renderer='browse.html')
    config.add_view(PrelaunchView, route_name='prelaunch',
                    renderer='browse.html')
    config.add_view(CrowdfundingView, route_name='crowdfunding',
                    renderer='browse.html')
    config.add_view(AvailableView, route_name='available',
                    renderer='browse.html')
    config.add_view(ArchiveView, route_name='archive', renderer='browse.html')
