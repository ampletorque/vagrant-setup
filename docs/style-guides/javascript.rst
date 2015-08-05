JavaScript Style Guide
======================


This page describes conventions for JavaScript and plugins.

Indents
-------

Use two spaces for indents, never ``\t``.

Comments
--------

All comments should be on their own lines. Don't share a line between code and comment. Multi-line comments should look like:

.. code-block:: javascript

    // When called on a form field, set val as the label value, so that
    // when the field is clicked, it is emptied, but if it is blurred
    // with no value the default is restored. Also, make it so that when
    // the default value is filled in, the text is a lighter shade.

Don't use ``/* this format. */``

jQuery Plugins
--------------

jQuery plugins should be named like ``jquery.myplugin.js``, and should have this structure:

.. code-block:: javascript

    (function ($) {
      $.fn.myplugin = function (opts) {
        // This block should have a comment (wrapped to 80 lines) describing
        // what the plugin does. Use the $.each function so you don't break the
        // chain. 
        return this.each(function () {
          console.log('hello');
        });
      };
    }(jQuery));

Associated CSS files or image files can be called ``jquery.myplugin.css``, ``jquery.myplugin.png``, etc.

jQuery Style
------------

When chaining in jQuery, put a newline and indent before the dot. When reducing the set of the jQuery object (e.g. with a ``find()``, ``parent()``, or similar), indent an additional level. When discarding the reductions (e.g. with ``end()``), reduce the indent level. E.g.:

.. code-block:: javascript

    $('div')
      .show()
      .find('a')
        .fadeOut()
        .end()
      .click(function () { });
