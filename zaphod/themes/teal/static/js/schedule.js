/*globals define*/
define([
  'jquery',
  'moment',
  'tpl!teal/templates/schedule-row.erb.html',
], function ($, moment, rowTemplate) {
  // This module handles the product schedule admin interface.

  "use strict";

  function ScheduleWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('addHandler')
      .proxy('removeHandler');
    this.init();
  }

  ScheduleWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      console.log("schedule init");
      this.$container
        .on('click', '.js-batch-remove', this.removeHandler)
        .on('click', '.js-batch-add', this.addHandler);
    },

    addHandler: function(e) {
      console.log("batch add");
      e.preventDefault();
      e.stopPropagation();

      var $batchesBody = this.$container.find('> tbody'),
          $batches = $batchesBody.find('> tr'),
          nextIndex = $batches.length,
          newID = 'new-' + nextIndex;

      var $last = $batches.last();

      // Calculate new date string that is 1 month after current last ship time
      var lastShipTime = moment($last.find('.js-datepicker').val(), 'YYYY-MM-DD'),
          nextShipTime = lastShipTime.add(1, 'months').format('YYYY-MM-DD');

      // Update last current batch to not have empty qty, if it does
      var $lastQty = $last.find('[name$=qty]');
      if($lastQty.val() === '') {
        $lastQty.val(1);
      }

      // Make a new row, passing in the ID
      $batchesBody.append(rowTemplate({
        qty: "",
        idx: nextIndex,
        id: newID,
        shipTime: nextShipTime
      }));
    },

    removeHandler: function(e) {
      console.log("batch remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('tr').remove();
    },

  };

  $(function () {
    $('.js-schedule-widget').each(function() {
      var d = new ScheduleWidget(this);
    });
  });
});
