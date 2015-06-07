/*globals define*/
define([
  'jquery',
  'tpl!teal/templates/options-row.erb.html',
  'tpl!teal/templates/options-value-row.erb.html'
], function ($, optionRowTemplate, valueRowTemplate) {
  // This module handles the product options admin interface.

  "use strict";

  function OptionWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('optionAddHandler')
      .proxy('valueAddHandler')
      .proxy('optionRemoveHandler')
      .proxy('valueRemoveHandler')
      .proxy('optionGrabHandler')
      .proxy('valueGrabHandler')
      .proxy('optionDragHandler')
      .proxy('valueDragHandler')
      .proxy('optionDropHandler')
      .proxy('valueDropHandler')
      .proxy('optionPlaceTarget')
      .proxy('valuePlaceTarget')
      .proxy('setGravity')
      .proxy('resetHandler');
    this.init();
  }

  OptionWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container
        .on('click', '.js-option-remove', this.optionRemoveHandler)
        .on('click', '.js-value-remove', this.valueRemoveHandler)
        .on('click', '.js-option-add', this.optionAddHandler)
        .on('click', '.js-value-add', this.valueAddHandler)
        .on('mousedown', '.js-option-drag-handle', this.optionGrabHandler)
        .on('mousedown', '.js-value-drag-handle', this.valueGrabHandler);

      this.$optionsBody = this.$container.find('> tbody');

      this.$optionsBackup = this.$optionsBody.find('> tr').clone();

      this.$form = this.$container.closest('form')
        .on('reset', this.resetHandler);

      this.indexCounter = this.$optionsBody.find('.js-value-drag-handle').length;
    },

    optionAddHandler: function(e) {
      console.log("option add");
      e.preventDefault();
      e.stopPropagation();

      var $optionsBody = this.$container.find('> tbody'),
          $options = $optionsBody.find('> tr'),
          newID = 'new-' + this.indexCounter;

      // Make a new row, passing in the ID
      var $el = $(optionRowTemplate({
        idx: this.indexCounter,
        gravity: this.indexCounter,
        id: newID
      }));
      $optionsBody.append($el);

      var $optionEl = $(valueRowTemplate({
        optionIdx: this.indexCounter,
        valueIdx: 0,
        gravity: 0,
        id: 'new-0'
      }));
      $el.find('table > tbody').append($optionEl);
      $optionEl.find('input[type=radio]').prop('checked', 'checked');

      this.indexCounter++;
    },

    optionRemoveHandler: function(e) {
      console.log("option remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('tr').remove();
    },

    doNothing: function(e) {
      e.preventDefault();
    },

    optionGrabHandler: function(e) {
      console.log("option grab");
      this.$movingRow = $(e.target).closest('tr');
      this.$helper = $('<table>')
        .addClass('table')
        .css({
          position: 'absolute',
          width: this.$movingRow.width()
        })
        .append(this.$movingRow.clone());
      this.$movingRow.css('opacity', 0.5);

      $('body')
        .on('mousemove', this.optionDragHandler)
        .on('selectstart', this.doNothing)
        .on('mouseup', this.optionDropHandler)
        .append(this.$helper);

      this.$target = $('<tr>')
        .addClass('table-drop-target')
        .append('<td colspan="4"></td>');

      this.optionDragHandler(e);
    },

    optionDragHandler: function(e) {
      console.log("option drag");
      this.$helper.css({
        top: e.pageY + 10,
        left: e.pageX + 10
      });
      this.optionPlaceTarget(e);
    },

    optionDropHandler: function(e) {
      console.log("option drop");
      $('body')
        .off('selectstart', this.doNothing)
        .off('mousemove', this.optionDragHandler)
        .off('mouseup', this.optionDropHandler);

      if(this.$target.is(':visible')) {
        // Actually move item and finalize
        this.$movingRow.css('opacity', 1.0);
        this.$target.after(this.$movingRow);
        this.$target.detach();
        this.setGravity();
      } else {
        this.$movingRow.css('opacity', 1.0);
      }

      this.$helper.remove();
    },

    optionPlaceTarget: function(e) {
      console.log("option place target");
      var $over = $(e.target).closest('tr');

      // If we're not over the container, return.
      if(!($.contains(this.$optionsBody[0], $over[0]))) {
        return;
      }

      // If we're over the existing target, return.
      if($over[0] === this.$target[0]) {
        return;
      }

      this.$target.detach();

      // If we're over the row being dragged, hide the target.
      if($over[0] === this.$movingRow[0]) {
        return;
      }

      // Otherwise, place the target either before or after the row we're over.
      var h = $over.height(),
          off = $over.offset();
      if ((e.pageY < (off.top + h / 2)) && ($over.prev()[0] !== this.$movingRow[0])) {
        $over.before(this.$target);
      } else if ((e.pageY > (off.top + h / 2)) && ($over.next()[0] !== this.$movingRow[0])) {
        $over.after(this.$target);
      }
    },

    valueAddHandler: function(e) {
      console.log("value add");
      e.preventDefault();
      e.stopPropagation();

      var $el = $(e.target),
          $thisOption = $el.closest('table').closest('tr');

      var $optionsBody = this.$container.find('> tbody'),
          $options = $optionsBody.find('> tr'),
          optionIdx = $thisOption.data('index');

      var $valuesBody = $el.closest('table').find('> tbody'),
          $values = $valuesBody.find('> tr'),
          newID = 'new-' + this.indexCounter;

      $valuesBody.append(valueRowTemplate({
        optionIdx: optionIdx,
        valueIdx: this.indexCounter,
        gravity: this.indexCounter,
        id: newID
      }));

      this.indexCounter++;
    },

    valueRemoveHandler: function(e) {
      console.log("value remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('tr').remove();

      // XXX Ideally this should update the option's default to a new value.
    },

    valueGrabHandler: function(e) {
      console.log("value grab");
      this.$movingRow = $(e.target).closest('tr');
      this.$movingBody = this.$movingRow.closest('tbody');
      this.$helper = $('<table>')
        .addClass('table')
        .css({
          position: 'absolute',
          width: this.$movingRow.width()
        })
        .append(this.$movingRow.clone());
      this.$movingRow.css('opacity', 0.5);

      $('body')
        .on('mousemove', this.valueDragHandler)
        .on('selectstart', this.doNothing)
        .on('mouseup', this.valueDropHandler)
        .append(this.$helper);

      this.$target = $('<tr>')
        .addClass('table-drop-target')
        .append('<td colspan="6"></td>');

      this.valueDragHandler(e);
    },

    valueDragHandler: function(e) {
      console.log("value drag");
      this.$helper.css({
        top: e.pageY + 10,
        left: e.pageX + 10
      });
      this.valuePlaceTarget(e);
    },

    valueDropHandler: function(e) {
      console.log("value drop");
      $('body')
        .off('selectstart', this.doNothing)
        .off('mousemove', this.valueDragHandler)
        .off('mouseup', this.valueDropHandler);

      if(this.$target.is(':visible')) {
        // Actually move item and finalize
        this.$movingRow.css('opacity', 1.0);
        this.$target.after(this.$movingRow);
        this.$target.detach();
        this.setGravity();
      } else {
        this.$movingRow.css('opacity', 1.0);
      }

      this.$helper.remove();
    },

    valuePlaceTarget: function(e) {
      console.log("value place target");
      var $over = $(e.target).closest('tr');

      // If we're not over the container, return.
      if(!($.contains(this.$movingBody[0], $over[0]))) {
        return;
      }

      // If we're over the existing target, return.
      if($over[0] === this.$target[0]) {
        return;
      }

      this.$target.detach();

      // If we're over the row being dragged, hide the target.
      if($over[0] === this.$movingRow[0]) {
        return;
      }

      // Otherwise, place the target either before or after the row we're over.
      var h = $over.height(),
          off = $over.offset();
      if ((e.pageY < (off.top + h / 2)) && ($over.prev()[0] !== this.$movingRow[0])) {
        $over.before(this.$target);
      } else if ((e.pageY > (off.top + h / 2)) && ($over.next()[0] !== this.$movingRow[0])) {
        $over.after(this.$target);
      }
    },

    setGravity: function(e) {
      console.log("set gravity");
      this.$container.find('.js-option-gravity, .js-value-gravity').each(function (ii) {
        $(this).val(ii);
      });

    },

    resetHandler: function(e) {
      console.log("options reset");
      this.$optionsBody.empty();
      this.$optionsBody.append(this.$optionsBackup.clone());
    }
  };

  $(function () {
    $('.js-option-widget').each(function() {
      var d = new OptionWidget(this);
    });
  });
});
