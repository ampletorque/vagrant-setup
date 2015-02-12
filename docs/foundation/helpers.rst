Template Helpers
================

These functions are available to templates under the ``h.`` namespace, and provide general utilities for use in templates. Add more template utilities here, but obey these rules:

1. No import dependencies on other parts of ``zaphod`` are allowed inside of ``zaphod.helpers``. This ensure that it will always be possible to import ``zaphod.helpers`` from anywhere, and that template helpers will be usable without any prepared DB or module state, which is useful for testing and developing new themes.
2. Helper modules and functions should be entirely stateless, and their import dependencies should be similarly stateless. For example, do not use ``locale.setlocale()``.
3. The ``h.`` namespace also exposes functions from `WebHelpers2 <https://webhelpers2.readthedocs.org/en/latest/>`_. These functions may be used in templates, and should not be shadowed by newly implemented functions, except where the shadowing function is an extension which provides a backward compatible interface to the shadowed function.


Miscellaneous
-------------

.. automodule:: zaphod.helpers.misc
    :members:
    :undoc-members:


Pagination
----------

.. automodule:: zaphod.helpers.paginate
    :members:
    :undoc-members:


Social
------

.. automodule:: zaphod.helpers.social
    :members:
    :undoc-members:


Timezone
--------

.. automodule:: zaphod.helpers.timezone
    :members:
    :undoc-members:


XSRF
----

.. automodule:: zaphod.helpers.xsrf
    :members:
    :undoc-members:
