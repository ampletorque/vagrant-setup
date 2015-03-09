/*globals define*/
define(['jquery', 'underscore', 'text!teal/images-row.erb.html'], function ($, _, rowTemplateRaw) {
  // Admin image interface handling.
  "use strict";

  var rowTemplate = _.template(rowTemplateRaw);

  function makeID() {
    var text = "";
    var possible = "abcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 32; i++ )
      text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
  }

  function handleNewFile(file) {
    var uploadPath = $('.js-image-widget').data('upload-path'),
        xsrf = $('#_authentication_token').val();


    if (!!file.type.match(/image.*/)) {
      // Make a new random ID to refer to it.
      var imageID = makeID();

      // Upload the file via ajax, get back an ID reference to it
      var formData = new FormData();
      formData.append("file", file);
      formData.append("id", imageID);
      formData.append("_authentication_token", xsrf);

      $.ajax({
        type: 'POST',
        contentType: false,
        processData: false,
        url: uploadPath,
        data: formData,
        error: function (request, status, error) {
          alert(request.responseText);
        }
      });

      nextIndex = $('.js-image-widget-images > tr').length;

      // Make a new row, passing in the ID

      var s = rowTemplate({
        idx: nextIndex,
        gravity: nextIndex,
        id: imageID,
        name: file.name
      });
      $('.js-image-widget-images').append(s);

    }
  }

  function handleNewFiles(files) {
    console.log("new files", files);
    for(var ii = 0; ii < files.length; ii++) {
      handleNewFile(files[ii]);
    }
  }

  function handleFileSelect(e) {
    handleNewFiles(e.target.files);
  }

  function handleFileDrop(e) {
    e.stopPropagation();
    e.preventDefault();
    handleNewFiles(e.originalEvent.dataTransfer.files);
  }

  function handleDragOver(e) {
    e.stopPropagation();
    e.preventDefault();
    e.originalEvent.dataTransfer.dropEffect = 'copy';
  }

  function dragStartHandler(e) {

  }

  function removeHandler(e) {
    e.preventDefault();
    e.stopPropagation();
    var $row = $(this).closest('tr').remove();
  }

  $(function () {
    console.log("setting up image admin handlers");
    $('.js-image-widget')
      .on('dragover', handleDragOver)
      .on('drop', handleFileDrop);
    $('.js-image-widget input[type=file]').on('change', handleFileSelect);

    $('.js-image-drag-handle').on('mousedown', dragStartHandler);
    $('.js-image-remove').on('click', removeHandler);
  });
});
