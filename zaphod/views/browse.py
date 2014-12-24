from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPNotFound

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
        return model.Session.query(model.Project).\
            filter(model.Project.published == True).\
            filter(model.Project.listed == True)
        # return model.Session.query(model.Project).\
        #     filter(model.Project.suspended_time == None).\
        #     filter(model.Project.published == True).\
        #     filter(model.Project.listed == True).\
        #     order_by(model.Project.gravity)

    def render_html(self):
        q = self.base_q()
        projects = [project for project in q.all() if not project.is_failed()]

        if len(projects) == 2:
            feature_count = 2
        else:
            feature_count = self.feature_count

        browse_tags = model.Session.query(model.Tag).\
            filter_by(published=True, listed=True).\
            order_by(model.Tag.name)

        data = {
            'browse_tags': browse_tags,
            'projects': projects,
            'feature_count': feature_count,
            'stage': self.stage,
            'page_title': self.title(),
        }
        data.update(self.data)
        return render_to_response('browse.html', data, self.request)

    def render_json(self):
        raise NotImplementedError

    def render_csv(self):
        raise NotImplementedError

    def render_rss(self):
        raise NotImplementedError

    def render_atom(self):
        raise NotImplementedError

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
        return ProjectListView.base_q(self).\
            filter(model.Project.stage == model.Project.FUNDRAISING).\
            filter(model.Project.start_time > datetime.utcnow())


class CrowdfundingView(ProjectListView):
    stage = u'Crowdfunding Projects'

    def base_q(self):
        return ProjectListView.base_q(self).\
            filter(model.Project.stage == model.Project.FUNDRAISING).\
            filter(model.Project.start_time <= datetime.utcnow())


class PreorderView(ProjectListView):
    stage = u'Pre-order Projects'

    def base_q(self):
        return ProjectListView.base_q(self).\
            filter(model.Project.stage == model.Project.PREORDER)


class InStockView(ProjectListView):
    stage = 'In Stock Products'

    def base_q(self):
        return ProjectListView.base_q(self).\
            filter(model.Project.stage == model.Project.PRODUCT)


def includeme(config):
    config.add_view(EverythingView, route_name='browse')
    config.add_view(PrelaunchView, route_name='prelaunch')
    config.add_view(CrowdfundingView, route_name='crowdfunding')
    config.add_view(PreorderView, route_name='preorder')
    config.add_view(InStockView, route_name='instock')
