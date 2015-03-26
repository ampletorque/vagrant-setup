from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.sql import func
from pyramid.view import view_config, view_defaults

from .base import BaseReportsView

from .... import model


@view_defaults(permission='admin')
class LeadsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:funnel-analysis',
                 renderer='admin/reports/funnel_analysis.html')
    def funnel_analysis(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:lead-activity',
                 renderer='admin/reports/lead_activity.html')
    def lead_activity(self):
        utcnow, start_date, end_date, start, end = self._range()
        # for a time range

        return {
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:pipeline',
                 renderer='admin/reports/pipeline.html')
    def pipeline(self):
        # as of now

        return {
        }

    @view_config(route_name='admin:reports:lead-sources',
                 renderer='admin/reports/lead_sources.html')
    def lead_sources(self):
        # as of now
        q = model.Session.query(model.LeadSource,
                                func.count('*').label('num_leads')).\
            join(model.LeadSource.leads).\
            group_by(model.LeadSource.id)

        sources = q.all()

        return {
            'sources': sources,
        }
