/*globals define*/
define(['jquery'], function ($) {
  // This module provides AJAX form validation, so that server-side form
  // validation can be used with client-side error rendering. This avoids
  // issues with data being lost during a page reload.

  // To use this module, set the .js-ajax-validate class on a <form>.

  "use strict";

  function clearErrors($form) {
    // Remove all existing errors that have been rendered in the DOM.
    $form.find('.form-group, td').removeClass('has-error').find('ul.error').remove();
  }

  function renderErrors($form, errors) {
    // Render errors in the DOM based on an error object passed from
    // server-side validation.
    $.each(errors, function(name, error) {
      var
        $input = $form
          .find('input, select, textarea')
          .filter('[name="' + name + '"]'),
        $group = $input.closest('td, .form-group');
      $group.addClass('has-error');
      if($group.prop('tagName') !== 'TD') {
        $group = $group.find('> div');
      }
      $group.append('<ul class="error"><li>' + error + '</li></ul>');
    });
  }

  function ajaxValidate($form) {
    if($form.data('block-submit')) {
      alert('Form submission already in progress.');
      return;
    }
    // Submit the form with an ajax request
    $form.data('block-submit', true);

    $.ajax({
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: $form.serialize(),
      dataType: 'json',
      error: function (request, status, error) {
        $form.data('block-submit', false);
        alert('Server Error');
      },
      success: function (data, status, xhr) {
        if(data.status === 'ok') {
          window.location.replace(data.location);
        } else {
          $form.data('block-submit', false);
          clearErrors($form);
          renderErrors($form, data.errors);
          // Defocus any focused form fields and scroll to the top of the
          // bottom, to try to 'feel' like a page reload.
          $(':focus').blur();
          $(document).scrollTop(0);
        }
      }
    });
  }

  $(function () {
    $('.js-ajax-validate').on('submit', function (e) {
      console.log("ajax validate submit");
      e.stopPropagation();
      e.preventDefault();

      var $form = $(this),
          checkCallback = $form.data('check-callback');
      if(!checkCallback || checkCallback()) {
        ajaxValidate($form);
      }
    });
  });

});
