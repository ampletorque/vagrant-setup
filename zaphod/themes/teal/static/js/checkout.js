define(['jquery', 'teal/ccfield'], function ($) {
  "use strict";

  var $icons = $('.credit-card-icons');

  function updateCardType(ccType) {
    if (ccType === "unknown") {
      $icons.find('.cc-icon').removeClass('disabled');
    } else {
      $icons.find('.cc-icon').addClass('disabled');
      $icons.find('.cc-icon-' + ccType).removeClass('disabled');
    }
  }

  $('.js-ccfield').on('cctype', function (e, ccType) {
    updateCardType(ccType);
  });


});
