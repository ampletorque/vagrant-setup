Python Style Guide and Tips
===========================

Not all of these are Python-specific, but they're all good suggestions.

Static Checking
---------------

Always use ``flake8``. Some PEP8 errors may need to be ignored to support SQLAlchemy constructs: those are enumerated in ``setup.cfg``, so if you call ``flake8`` with no arguments in the root of the repository, it will ignore the right errors.

Style
-----

Avoid using variable names that also belong to builtins, packages, or std lib packages (aka "shadowing").

On comment lines, keep a space between the "#" and the comment text.

Don't put whitespace between a function name and a paren when making a call.

Don't use things like ``each`` for loop variables.

For integer iterators, use a doubled character (e.g. ``ii``) instead of a single character (``i``) so that it can be grepped for or replaced.

If you have a comment on the first line of a function, consider if it should be a doctoring.

Use docstrings to describe the basic purpose of a function, use comments for implementation. docstrings are for the user (or caller), comments are for author/editor.

Watch out for meaningless function names.

Watch out for code duplication. If you see a lot of chunks of code that look similar, think about what they have in common and how you can factor that out.

Decompose very long functions into component parts. This does two things:

* It keeps individual pieces of code shorter and easier to reason about. So the short function is likely to have fewer bugs and will be easier to read in the future.
* It improves the narrative quality of the original function.

.. code-block:: python

    def foo():
        do_bar()
        do_baz()

is more clear than:

.. code-block:: python

    def foo():
        < 10 lines from do_bar >
        < 10 lines from do_baz >

Split large files into different files in the same module.

In the same vein, keep utility functions like "title_case_test" in their own module.

No magic numbers.  It's difficult to read things like,:

.. code-block:: python

    ... filter(and_(model.DataIntegrity.id >= 4,
                    model.DataIntegrity.id <= 12)) ...

because "4" and "12" don't have any intrinsic meaning.

Imports
-------

General imports:

* Use relative imports inside packages where possible.
* Put multiple imports from the same file on the same line.
* Put ``import <foo>" before "from <foo> import``
* Similarly, Import from submodules in order of depth, e.g.:
    * ``from zaphod imports helpers`` before
    * ``from zaphod.lib.base import render`` before 
    * ``from zaphod.views.admin.base import AdminHandler``

Also, follow this ordering for the header strictly:

1. Module-level docstring.
2. ``__future__`` imports.
3. Python stdlib imports.
4. Non-standard imports (e.g. ``sqlalchemy``, ``webob``, etc).
5. Local project common imports (e.g. ``model``, ``request``, etc).
6. Other local project imports.
7. Relative package imports.
8. Log instantiations (e.g. ``logging.getLogger(__name__)``).
9. Module-level variables and constants.

Here's an example:

.. code-block:: python

    """
    Management of frobozz interfaces.
    """
    from __future__ import absolute_import

    import logging
    import json
    from datetime import datetime

    from webob import Request

    from zaphod import model

    from zaphod import mail
    from zaphod.themes import teal

    from . import interfaces

    log = logging.getLogger(__name__)

    _registry = {}


File and Network Handling
-------------------------

Where possible, use shared network interface components: e.g. global zmq context, global mailer, etc.
Use the ``tempfile`` module for temporary files, always.

Models / DB
-----------

Use nouns for SQLAlchemy class names.  e.g. "Dismissal" instead of "Dismiss".

Query.filter_by(...) can substantially shorten queries vs. Query.filter(...).  E.g.:

.. code-block:: python

    meta.Session.query(model.ContentIntegrityDismiss).\
        filter(and_(model.ContentIntegrityDismiss.warning_id == warning_id,
                    model.ContentIntegrityDismiss.product_id == id,
                    model.ContentIntegrityDismiss.dup_id == dup_id)).\
                    first()

can be written as:

.. code-block:: python

    meta.Session.query(model.ContentIntegrityDismiss).\
        filter_by(warning_id=warning_id, product_id=id, dup_id=dup_id)).\
        first()

SQLAlchemy declarative constructors accept keyword arguments for properties.  If the property values are available at instantiation time, you should prefer:

.. code-block:: python

    c = ModelClass(property="foo")

over:

.. code-block:: python

    c = ModelClass()
    c.property = "foo"

If you're setting a foreign key in the SQLAlchemy object, e.g.:

.. code-block:: python

    Foo(other_object_id=123)

and you already have `other_object` loaded, it's usually better to do:

.. code-block:: python

    Foo(other_object=other_object)

The main reason not to do that is that it's a little faster to set the `id` column directly.

Multiple calls to Query.filter are ANDed together.  If the filter conditions are moderately complicated (i.e. they take up a lot of space), it's usually better to do:

.. code-block:: python

    q = meta.Session.query().filter().filter()...

instead of:

.. code-block:: python

    q = meta.Session.query().filter(and_(..., ...))

SQLAlchemy will generally handle the polymorphic column for you.  If you create a new instance of a polymorphic subclass, the discriminator will automatically be filled in.

Also, if you filter against a subclass using a superclass field, it will handle the join to the parent class. For example, you don't need an explicit join to Node when doing:

.. code-block:: python

    meta.Sesson.query(model.ProductSiteVariant).filter_by(name=...)

If you're using ORM inheritance and have a bunch of columns that play the same role in different subclasses, use ``orm.synonym()`` to simplify queries.  See ProductSpecValue.value for an example.

By and large, you really shouldn’t have to deal with discriminator columns explicitly.  When it seems like it’s necessary, it’s usually a sign that the code needs to be restructured.

If you're grabbing a database parameter out of request.params, you need to check the database result before doing anything with it. E.g. deleting an object by id should check to make sure that id exists.

General Architecture
--------------------

For trying a list of defaults (e.g. for imports, config paths, file locations) use a loop through a list rather than nested try blocks. The latter makes diagnosing exceptions more difficult and the code less extensible.

Don't try to write files to cwd. Odds of a server environment supporting this are slim.

Try to avoid formatting strings before it's really necessary. Functions should return highly structured objects where possible (e.g. return a time delta instead of returning a string with "2 days ago")

Don't use ``time.sleep()`` in a network read loop.  use poller / timeout.

Try not to use functions with side effects, particularly those that are web context aware, in functions outside of a controller method. Using these prevents the function from being used in a different context, which is usually undesirable.
