from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime, timedelta, date, time

import pytz
from formencode import Schema, validators

from pyramid_uniform import Form


class ReportRangeSchema(Schema):
    allow_extra_fields = True
    start_date = validators.DateConverter(if_missing=None, if_empty=None)
    end_date = validators.DateConverter(if_missing=None, if_empty=None)


class BaseReportsView(object):
    def __init__(self, request):
        self.request = request

    def _range(self, default='mtd'):
        request = self.request

        form = Form(request, schema=ReportRangeSchema(), method='GET')
        form.assert_valid(skip_csrf=True)

        now = datetime.utcnow()
        report_tz = pytz.timezone('America/Los_Angeles')

        def utcize(dt_local):
            dt_local = report_tz.localize(datetime.combine(dt_local, time()))
            return dt_local.astimezone(pytz.utc).replace(tzinfo=None)

        if (form.data.get('start_date') and form.data.get('end_date')):

            start_local = form.data.get('start_date')
            end_local = form.data.get('end_date')

            start = start_local
            end = end_local

        else:
            now_local = pytz.utc.localize(now).astimezone(report_tz)
            today_local = now_local.date()
            if default == 'mtd':
                month_begin_local = date(today_local.year,
                                         today_local.month,
                                         1)

                start = month_begin_local
                end = now_local
            elif default == 'ytd':
                year_begin_local = date(today_local.year, 1, 1)

                start = year_begin_local
                end = now_local

        start_date = datetime.combine(start, time())
        end_date = datetime.combine(end, time())

        start_utc = utcize(start_date)
        end_utc = utcize(end_date) + timedelta(days=1)

        return now, start_date, end_date, start_utc, end_utc
