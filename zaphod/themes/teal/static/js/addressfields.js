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

        $stateCA.hide().prop('disabled', 'disabled');
        $stateUS.hide().prop('disabled', 'disabled');
        $stateInt.hide().prop('disabled', 'disabled');

        if(countryCode === 'us') {
          $stateUS.show().removeProp('disabled');
        } else if(countryCode === 'ca') {
          $stateCA.show().removeProp('disabled');
        } else {
          $stateInt.show().removeProp('disabled');
        }
      }

      $countrySelect.change(updateVisibility);
      updateVisibility();

    });
  });
});
