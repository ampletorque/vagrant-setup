/*globals define*/
define(['jquery'], function ($) {
  // AJAX form validation.
  "use strict";

  function clearErrors($form) {
    $form.find('.form-group').removeClass('has-error').find('ul.error').remove();
  }

  function renderErrors($form, errors) {
    $.each(errors, function(name, error) {
      var
        $input = $form
          .find('input, select, textarea')
          .filter('[name=' + name + ']'),
        $group = $input.closest('.form-group');
      $group.addClass('has-error');
      $group.find('> div').append('<ul class="error"><li>' + error + '</li></ul>');
    });
  }

  function submitHandler(e) {
    e.stopPropagation();
    e.preventDefault();

    var $form = $(this);
    console.log("form is", $form);

    // Submit the form with an ajax request
    $.ajax({
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: $form.serialize(),
      dataType: 'json',
      error: function (request, status, error) {
        alert(request.responseText);
      },
      success: function (data, status, xhr) {
        if(data.status === 'ok') {
          window.location.replace(data.location);
        } else {
          clearErrors($form);
          renderErrors($form, data.errors);
        }
      }
    });
  }

  $(function () {
    $('.js-ajax-validate').on('submit', submitHandler);
  });

});
