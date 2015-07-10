/*globals define*/
define(['jquery'], function ($) {
  // This module handles address fields interactivity.

  "use strict";

  $(function () {
    $('.address-fields').each(function() {
      var $fields = $(this),
          $countrySelect = $fields.find('select[name$="country_code"]'),
          $stateCA = $fields.find('.state-field-ca'),
          $stateUS = $fields.find('.state-field-us'),
          $stateInt = $fields.find('.state-field-int');

      function updateVisibility() {
        var countryCode = $countrySelect.val();

        $stateCA.hide().attr('disabled', 'disabled');
        $stateUS.hide().attr('disabled', 'disabled');
        $stateInt.hide().attr('disabled', 'disabled');

        if(countryCode === 'us') {
          $stateUS.show().removeAttr('disabled');
        } else if(countryCode === 'ca') {
          $stateCA.show().removeAttr('disabled');
        } else {
          $stateInt.show().removeAttr('disabled');
        }
      }

      $countrySelect.change(updateVisibility);
      updateVisibility();

    });
  });
});
