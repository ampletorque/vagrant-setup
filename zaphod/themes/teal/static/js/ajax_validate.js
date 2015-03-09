/*globals define*/
define(['jquery'], function ($) {
  // AJAX form validation.
  "use strict";

  function submitHandler(e) {
    e.stopPropagation();
    e.preventDefault();
    alert('blocked');

    var $form = $(this);

    // Serialize the form data

    // Make an ajax POST request to the form action

    // Check status

    // If status is ok, redirect to supplied location

    // If status is fail, collect errors from response and render them

  }

  $(function () {
    console.log("initialized");
    $('.js-ajax-validate').on('submit', submitHandler);
  });

});
