Bug and Feature Ticket Tracking
===============================

Feature development and bug fixes on Zaphod are tracked in a ticket tracker
residing on GitHub::

http://github.com/crowdsupply/zaphod/issues

It is not necessary for every piece of development to correspond to a ticket:
it simply serves as a helpful clearinghouse for long-term planning and
information gathering. In general, it is better to err on the side of filing
*more* tickets for bugs, and *fewer* tickets for new features. In other words,
if you have identified something as a bug, you should nearly always file a
ticket for it unless it can be fixed immediately, but if you have identified
something as a feature, you should exercise more caution.

Filing "good" tickets can help speed up development, so let's summarize some of
the important parts of a good ticket.

Title & Body
------------

The title of a ticket should be a concise explanation of the work needs to be
done. In some cases this will be a bit unknown, because the fix for a bug is
not necessarily definite. As such, it is helpful to use the imperative tense
for titles of enhancement tickets, like "Make the blazorp machine respect the
FTD decoder format", and the declarative tense for titles of bug tickets, like
"The blazorp machine crashes every 2nd Tuesday".

The body of a ticket should contain a sufficient enough explanation that
someone without first-hand knowledge of the bug or feature can begin work
immediately. For bug, this usually includes step-by-step instructions to
replicate the bug.

Tags
----

All tickets should have at least one of the following tags. Additional
topic-specific tags may be added to this to provide further sorting abilities.

**Bug** - (Synonym for *defect*.) When a piece of functionality is not working
as it was originally intended and specified to, it is a bug. This tag should
*not* be used for extensions of functionality.

**Enhancement** - To be used for new features, or extending the scope or
robustness of existing features.

Note that the usage of the word 'enhancement' as opposed to 'feature' or
'change' adds some implicit restriction here. You might ask, "what about
changes to the way features work which are just a change, and don't necessarily
enhance anything?" Excellent question. The implication--which should be
respected--is that those changes don't belong in the ticket tracker, because
they shouldn't exist.

**Refactoring** - To be used for architectural or implementation changes which
are internal to the codebase only, and don't represent a bug or new
user-facing functionality, but which are nonetheless good things to do.

**Data** - To be used for problems with just the stored data on the live
production deployment of the app, and not actual code.

Sometimes it is advisable to combine the **data** tag with one of the other
three, such as a situation where a particular bug caused some amount of data to
be corrupted. However, the other three tags should never be combined, because
it does not make sense to do so.


Some Examples
~~~~~~~~~~~~~

* An upstream API begins returning a previously nonexistent error flag when a
  certain action is performed. We want to be able to catch this flag and notify
  the user. This is an **enhancement**.
* A form submitted by a user causes a 500 error when the data in a certain
  field is too long. We want to catch that error, and instead show a
  notification to the user. This is an **enhancement**.
* When a user of a specific supported browser submits a form correctly, they
  see a 500 error. Users of other supported browsers do not. This is a **bug**.


A Quick Note on Browser Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a browser-specific distinction is found, it is only considered a bug if
that browser is "supported". Due to time and cost constraints, it is not
practical or desirable to support all browsers, and the list of browsers that
should be supported is a constantly moving target.

As of **June 2015**, the list of supported browsers is as follows:

* Internet Explorer 8 and newer.
* Firefox 37 and newer
* Google Chrome "Stable" (specifying a version requirement for Google Chrome is
  not sensible, because users are automatically upgraded)
* Google Chrome on Android and iOS
* iOS Safari 7.1 and newer

Browsers which are notably absent from this list are:

* Opera, including Opera Mini
* Windows Phone
* Blackberry

This isn't intended to serve as an authoritative list, because the support
goals can vary based on specific cases, day-to-day business requirements, etc.
It is only intended to serve as a baseline guide.

Assignees
---------

Avoid changing the *assignee* on a ticket without explicitly talking to that
user first. Better yet, just let them change the assignee themselves. It is not
useful to do things like "assign all tickets of a certain type to Person X".
There are two reasons for this approach::

1. If a new contributor (e.g. a new developer, designer, or support team
   member) joins the tracker, they have no way of knowing what tickets are
   actually specifically claimed and being worked on, and which ones are still
   outstanding.
2. Similarly, assigning a ticket without dialogue removes information about
   whether or not it is being worked on actively.
