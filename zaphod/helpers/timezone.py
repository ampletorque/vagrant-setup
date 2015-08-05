from datetime import datetime

import pytz


def format_datetime(request, dt, format='%m/%d/%Y %I:%M:%S %p %Z',
                    timezone=None):
    """
    Given an offset-unaware UTC datetime object, convert it to the user's local
    timezone, and format it as a string.
    """
    # XXX May want to consider warning about calls to this function that show a
    # full date string but only have a date (non-datetime).

    if isinstance(dt, datetime):
        if not timezone:
            # XXX Get this from settings instead.
            timezone = 'America/Los_Angeles'
        tz = pytz.timezone(timezone)
        dt = pytz.utc.localize(dt).astimezone(tz)

    return dt.strftime(format)


def timezones_for_select():
    return pytz.common_timezones
