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

        $stateCA.hide().prop('disabled', true);
        $stateUS.hide().prop('disabled', true);
        $stateInt.hide().prop('disabled', true);

        if(countryCode === 'us') {
          $stateUS.show().prop('disabled', false);
        } else if(countryCode === 'ca') {
          $stateCA.show().prop('disabled', false);
        } else {
          $stateInt.show().prop('disabled', false);
        }
      }

      $countrySelect.change(updateVisibility);
      updateVisibility();

    });
  });
});
