General Conventions
===================

Dates and Times
---------------

All dates should be persisted in UTC only. Timezone localization should be done
at the presentation layer. The only exception to this is logging, which may be
timestamped using the system clock.

Always include the timezone when shwoing a time, even if that timezone is UTC.

Dates shown to the user should always be shown in ISO-8601 format (YYYY-MM-DD).

Date entry should include time where possible (e.g. make it clear when something is timed at 12:01am, 11:59pm, etc).
