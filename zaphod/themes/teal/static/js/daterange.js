define(['jquery', 'moment', 'teal/datepicker'], function ($, moment) {
  function formatDate(d) {
    return moment(d).format('MM/DD/YYYY');
  }

  function formatDateLabel(d) {
    return moment(d).format('MMM D, YYYY');
  }

  var ranges = [
    'today',
    'yesterday',
    'this-week-sun',
    'this-week-mon',
    'last-7-days',
    'last-week-sun',
    'last-week-mon',
    'last-business-week',
    'last-14-days',
    'this-month',
    'last-30-days',
    'last-month',
    'this-year',
    'last-year',
    'a-while',
  ];

  function DateRange(element, options) {
    this.$el = $(element);
    this.init();
  }

  DateRange.prototype = {
    infoFor: function(range) {
      var start = new Date(),
          end = new Date();

      switch(range) {
        case 'today':
          label = 'Today';
          break;
        case 'yesterday':
          start.setDate(start.getDate() - 1);
          end = start;
          label = 'Yesterday';
          break;
        case 'last-7-days':
          end.setDate(start.getDate() - 1);
          start.setDate(start.getDate() - 7);
          label = 'Last 7 Days';
          break;
        case 'this-week-sun':
          start.setDate(start.getDate() - start.getDay());
          label = 'This Week (Sun - Today)';
          break;
        case 'this-week-mon':
          start.setDate(start.getDate() - start.getDay() + 1);
          label = 'This Week (Mon - Today)';
          break;
        case 'last-week-sun':
          start.setDate(start.getDate() - start.getDay() - 7);
          end = new Date(start.getTime());
          end.setDate(start.getDate() + 6);
          label = 'Last Week (Sun - Sat)';
          break;
        case 'last-week-mon':
          start.setDate(start.getDate() - start.getDay() - 6);
          end = new Date(start.getTime());
          end.setDate(start.getDate() + 6);
          label = 'Last Week (Mon - Sun)';
          break;
        case 'last-business-week':
          start.setDate(start.getDate() - start.getDay() - 6);
          end = new Date(start.getTime());
          end.setDate(start.getDate() + 4);
          label = 'Last Business Week';
          break;
        case 'last-14-days':
          end.setDate(start.getDate() - 1);
          start.setDate(start.getDate() - 14);
          label = 'Last 14 Days';
          break;
        case 'this-month':
          start.setDate(1);
          label = 'This Month';
          break;
        case 'last-30-days':
          end.setDate(start.getDate() - 1);
          start.setDate(start.getDate() - 30);
          label = 'Last 30 Days';
          break;
        case 'last-month':
          start.setDate(1);
          start.setMonth(start.getMonth() - 1);
          end.setDate(0);
          label = 'Last Month';
          break;
        case 'this-year':
          start.setDate(1);
          start.setMonth(0);
          label = 'This Year';
          break;
        case 'last-year':
          start.setDate(1);
          start.setMonth(0);
          start.setFullYear(start.getFullYear() - 1);
          end.setMonth(0);
          end.setDate(0);
          label = 'Last Year';
          break;
        case 'a-while':
          start.setDate(1);
          start.setMonth(0);
          start.setFullYear(start.getFullYear() - 10);
          label = 'A While';
          break;
        default:
          console.log('Invalid date range.', range);
      }

      var date_label;
      if (start === end) {
        date_label = formatDateLabel(start);
      } else {
        date_label = formatDateLabel(start) + " - " + formatDateLabel(end);
      }

      return {
        start: start,
        end: end,
        range_label: label,
        date_label: date_label,
      };
    },

    changeRange: function(info, trigger) {
      this.$range_label.html(info.range_label);
      this.$date_label.html(info.date_label);

      this.$start_el.val(formatDate(info.start));
      this.$end_el.val(formatDate(info.end));

      if(trigger) {
        this.$el.trigger('daterange.change');
      }
    },

    init: function() {

      var that = this;

      this.$dropdown = this.$el.find('.dropdown-menu');
      this.$pickers = this.$el.find('.js-date-range-pickers');
      this.$range_label = this.$el.find('.js-date-range-current');
      this.$date_label = this.$el.find('.js-date-range-text');
      this.$start_el = this.$el.find('.js-date-range-start');
      this.$end_el = this.$el.find('.js-date-range-end');

      this.$dropdown.on('click', '.js-custom-range', function(e) {
        that.$range_label.hide();
        that.$date_label.hide();
        that.$pickers.show();
      });

      this.$dropdown.on('click', '.js-date-range', function(e) {
        that.$pickers.hide();
        that.$range_label.show();
        that.$date_label.show();

        var range_key = $(this).data('range'),
            info = that.infoFor(range_key);

        that.changeRange(info, true);
      });

      this.$pickers.find('button').click(function(e) {
        that.$el.trigger('daterange.change');
        e.preventDefault();
        e.stopPropagation();
      });

      var found_named_range = false;

      for (ii = 0; ii < ranges.length; ii++) {
        var rr = ranges[ii],
            info = this.infoFor(rr);
        this.$dropdown.append($('<li><a href="#" class="js-date-range" data-range="' + rr + '">' + info.range_label + '</a></li>'));

        if((this.$start_el.val() === formatDate(info.start)) && (this.$end_el.val() === formatDate(info.end))) {
          found_named_range = true;
          this.changeRange(info, false);
        }
      }

      if(!found_named_range) {
        this.$range_label.hide();
        this.$date_label.hide();
        this.$pickers.show();
      }
    },
  };

  $.fn.daterange = function(options) {
    return this.each(function() { var d = new DateRange(this, options); });
  };

  $.fn.daterange.DateRange = DateRange;

  $(function () {
    $('.js-date-range-friendly').daterange();

    $('.js-date-range-form').on('daterange.change', function(e) {
      $(this).submit();
    });
  });
});
