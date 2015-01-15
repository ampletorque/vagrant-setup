/*globals define*/
define(['jquery', 'moment'], function ($, moment) {
  // Basic handling of project tile countdowns in javascript.
  "use strict";

  $(function () {
    $('[data-countdown-to]').each(function (ii, el) {
      var
        $el = $(el),
        $val = $el.find('p'),
        $caption = $el.find('span'),
        end = moment.utc($el.data('countdown-to'));

      function updateCountdown() {
        var
          diff = end.diff(moment.utc()),
          remaining = diff / 1000;

        if (remaining > 172800) {
          // More than 2 days, so just show days.
          $val.text(Math.floor(remaining / 86400));
          $caption.text('days left');
        } else if (remaining > 7200) {
          // More than 2 hour, so just show hours.
          $val.text(Math.floor(remaining / 3600));
          $caption.text('hours left');
        } else if (remaining > 120) {
          // More than 2 minutes, so just show minutes.
          $val.text(Math.floor(remaining / 60));
          $caption.text('minutes left');
        } else if (remaining > 1) {
          $val.text(Math.floor(remaining));
          $caption.text('seconds left');
        } else if (remaining > 0) {
          $val.text(Math.floor(remaining));
          $caption.text('second left');
        } else {
          $val.text('-');
          $caption.text('completed');
        }

        if (remaining <= 172800) {
          $val.css({
            'font-weight': 'bold',
            'color': '#bd0000'
          });
        }
      }

      window.setInterval(updateCountdown, 1000);
    });
  });
});
