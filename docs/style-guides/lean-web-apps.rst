Principles of Lean Web Apps
===========================

This is intended to be a set of guidelines, not hard-and-fast rules. The goal
of this list, at its core, is to spend less money and time on software.

* Make everything happen in the scope of a web request. No extra processes or
  scripts.
* Data models should be time-invariant. If behavior needs to change as of a
  specific time, that change shouldn’t occur in the data, it should occur in
  the view servicing a given request. This prevents the need for synchronous
  “servicing” tasks.
* All app state should be contained in the data model or request session. No
  app-global variables.
* Try to avoid the need to pass lots of non-permanent state around between
  requests, either by limiting the state to a single request, or keeping the
  state in the browser, using AJAX requests from there to service additional
  data manipulation. As an exception, passing around a CSRF token is a
  necessary evil.
* Use the framework for as much as possible, especially URL dispatch,
  rendering, and containerization. Resist the urge to roll your own scripts or
  techniques and never be more than one abstraction layer above the framework.
* If you can’t do what you need in the framework, change the feature rather
  than introduce a new layer.
* In Pyramid, e.g. develop new renderers rather than returning a ‘raw’ response
  from a view. This will be much more testable, etc.

Pyramid-specific concerns:

* New views are generally preferable to making existing views more complex.
* Keep dependencies simple:
* Model should not depend on other parts of the app.
* Helpers should not depend on other parts of the app.
* Views should depend on other things, but nothing should depend on views.
* Use builtin view predicates whenever possible instead of checking for
  conditions within the view (e.g. ``xhr=True, request_method=‘POST’``, etc).
