from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config

from .base import BaseReportsView


class LeadsReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:funnel-analysis',
                 renderer='admin/reports/funnel_analysis.html',
                 permission='authenticated')
    def funnel_analysis(self):
        # for a time range

        return {
        }

    @view_config(route_name='admin:reports:lead-activity',
                 renderer='admin/reports/lead_activity.html',
                 permission='authenticated')
    def lead_activity(self):
        # for a time range

        return {
        }

    @view_config(route_name='admin:reports:pipeline',
                 renderer='admin/reports/pipeline.html',
                 permission='authenticated')
    def pipeline(self):
        # as of now

        return {
        }

    @view_config(route_name='admin:reports:lead-sources',
                 renderer='admin/reports/lead_sources.html',
                 permission='authenticated')
    def lead_sources(self):
        # as of now

        return {
        }
