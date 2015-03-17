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


  function initBillingSameAsShipping() {
    var $checkbox = $("#billing_same_as_shipping");

    function updateBillingVisibility(e) {
      var same = $checkbox.attr('checked') || ($checkbox.attr('type') === 'hidden');
      $('.billing-fields').toggle(!same);
    }

    $checkbox
      .change(updateBillingVisibility)
      .click(updateBillingVisibility)
      .trigger('change');
  }

  $(function () {
    $('.js-ccfield').on('cctype', function (e, ccType) {
      updateCardType(ccType);
    });

    initBillingSameAsShipping();
    initCCForm();
  });
});
