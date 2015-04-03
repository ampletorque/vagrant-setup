/*globals define*/
define(['jquery'], function ($) {
  // This module handles the admin interface's related project association widget.

  "use strict";

  function RelatedProjectWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('addHandler')
      .proxy('selectHandler')
      .proxy('removeHandler');
    this.init();
  }

  RelatedProjectWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container
        .on('click', '.js-project-remove', this.removeHandler)
        .on('click', '.js-project-add', this.addHandler)
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

      // Hide 'add project' link

      // Show select widget.
      this.$select.show();
    },

    selectHandler: function(e) {
      // Add project to list, including hidden field.

      // Hide select widget.

      // Show 'add project' link
    }

  };

  $(function () {
    $('.js-project-association').each(function() {
      var d = new RelatedProjectWidget(this);
    });
  });
});
