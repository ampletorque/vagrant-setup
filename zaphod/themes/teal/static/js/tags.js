/*globals define*/
define(['jquery'], function ($) {
  // This module handles the admin interface's tag association widget.

  "use strict";

  function TagWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('addHandler')
      .proxy('selectHandler')
      .proxy('removeHandler');
    this.init();
  }

  TagWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container
        .on('click', '.js-tag-remove', this.removeHandler)
        .on('click', '.js-tag-add', this.addHandler)
      this.$select = this.$container.find('select')
        .on('change', this.selectHandler);
    },

    removeHandler: function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $row = $(e.target).closest('tr').remove();
    },

    addHandler: function(e) {
      e.preventDefault();
      e.stopPropagation();

      // Hide 'add tag' link

      // Show select widget.
      this.$select.show();
    },

    selectHandler: function(e) {
      // Add tag to list, including hidden field.

      // Hide select widget.

      // Show 'add tag' link
    }

  };

  $(function () {
    $('.js-tag-association').each(function() {
      var d = new TagWidget(this);
    });
  });
});
