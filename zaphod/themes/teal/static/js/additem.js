/*globals define*/
define([
  'jquery',
  'tpl!teal/templates/additem-result.erb.html',
  'tpl!teal/templates/additem-form.erb.html',
  'tpl!teal/templates/additem-option.erb.html'
], function ($, resultTemplate, formTemplate, optionTemplate) {
  // This module handles the 'item adder' widget.

  "use strict";

  function AddItemWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('searchHandler')
      .proxy('pickHandler');
    this.init();
  }

  AddItemWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      console.log("additem init");
      this.$container
        .on('keypress', '.js-product-search', this.searchHandler)
        .on('click', '.js-product-select', this.pickHandler);
    },

    searchHandler: function(e) {
      console.log("additem search keypress");

      var $field = $(e.target),
          $results = this.$container.find('.js-product-results'),
          path = this.$container.data('search-path');

      // XXX Cancel any existing pending ajax requests

      $.ajax({
        type: "GET",
        url: path + "?q=" + $field.val(),
        success: function (data, status, xhr) {
          console.log("additem search results", data);
          var products = data.products;
          console.log("additem emptying");
          $results.empty();
          for(var ii = 0; ii < products.length; ii++) {
            console.log("additem result", products[ii]);
            $results.append(resultTemplate({product: products[ii]}));
          }
        }
      });
    },

    pickHandler: function(e) {
      console.log("additem product pick");
      e.preventDefault();
      e.stopPropagation();

      var $el = $(e.target).closest('.js-product-select'),
          $form = this.$container.find('.js-product-form');

      // Remove all the other result items
      $el.parent().siblings().remove();

      // Execute ajax request for product info
      console.log("el is", $el);
      console.log("info path is", $el.data('info-path'));
      $.ajax({
        type: "GET",
        url: $el.data('info-path'),
        success: function (data, status, xhr) {
          console.log("additem info result", data);
          $form.html(formTemplate({
            info: data,
            optionTemplate: optionTemplate
          }));
        }
      });

      // Render form
    }
  };

  $(function () {
    $('.js-additem-widget').each(function() {
      var d = new AddItemWidget(this);
    });
  });
});
