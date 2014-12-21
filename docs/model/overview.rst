Model Overview
==============

The Zaphod data model is encapsulated in the ``zaphod.model`` module and submodules. The goals of the model are to:

* Provide a clean abstraction layer over relational data.
* Be completely usable outside of the Pyramid context and web stack. E.g. you should be able to do ``import zaphod.model`` from other Python apps and do stuff useful.
* Do not expose data manipulation methods which make it easy to create invalid database states.

All canonical non-media data should be stored in a SQL DB, as structured by this model.

.. seealso::

    * :doc:`/testing/model`
