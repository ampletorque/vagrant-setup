/*globals define*/
define(['jquery', 'underscore', 'text!teal/images-row.erb.html'], function ($, _, rowTemplateRaw) {
  // Admin image interface handling.
  "use strict";

  var rowTemplate = _.template(rowTemplateRaw);

  var $movingRow, $helper, $target;

  function makeID() {
    var text = "";
    var possible = "abcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 32; i++ )
      text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
  }

  function loadThumbnail(file, $el) {
    var reader = new FileReader();
    reader.onload = function(e) {
      console.log("setting image", escape(file.name));
      $el.find('.js-image-placeholder').append(
        $('<img>')
          .attr('width', 64)
          .attr('height', 64)
          .attr('src', e.target.result)
      );
    }
    reader.readAsDataURL(file);
  }

  function handleNewFile(file) {
    var uploadPath = $('.js-image-widget').data('upload-path'),
        xsrf = $('#_authentication_token').val();


    if (!!file.type.match(/image.*/)) {
      // Make a new random ID to refer to it.
      var imageID = makeID();

      console.log("counting existing rows");
      var nextIndex = $('.js-image-widget-images > tr').length;

      // Make a new row, passing in the ID
      console.log("making new row", nextIndex);

      var s = rowTemplate({
        idx: nextIndex,
        gravity: nextIndex,
        id: imageID,
        name: file.name
      });
      var $el = $(s);
      $('.js-image-widget-images').append($el);
      loadThumbnail(file, $el);

      var $progress = $el.find('.js-image-progress'),
          $status = $el.find('.js-image-status');

      // Upload the file via ajax, get back an ID reference to it
      var formData = new FormData();
      formData.append("file", file);
      formData.append("id", imageID);
      formData.append("_authentication_token", xsrf);

      console.log("uploading image via ajax");
      // FIXME The form submission should collect these and block if any are not complete
      var xhr = new XMLHttpRequest();
      xhr.open('POST', uploadPath, true);
      xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
          if (e.loaded === e.total) {
            $status.text('Unsaved');
          } else{
            $progress.text(e.loaded / e.total * 100);
          }
        }
      };
      xhr.send(formData);
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

  function handleFileDragOver(e) {
    e.stopPropagation();
    e.preventDefault();
    e.originalEvent.dataTransfer.dropEffect = 'copy';
  }

  function doNothing(e) {
    e.preventDefault();
  }

  function placeTarget(e) {
    var $over = $(e.target).closest('tr'),
        $container = $movingRow.closest('table');

    // If we're not over the container, return.
    if(!($.contains($container[0], $over[0]))) {
      return;
    }

    // If we're over the existing target, return.
    if($over[0] === $target[0]) {
      return;
    }

    $target.remove();

    // If we're over the row being dragged, hide the target.
    if($over[0] === $movingRow[0]) {
      return;
    }

    // Otherwise, place the target either before or after the row we're over.
    var h = $over.height(),
        off = $over.offset();
    if ((e.pageY < (off.top + h / 2)) && ($over.prev()[0] !== $movingRow[0])) {
      $over.before($target);
    } else if ((e.pageY > (off.top + h / 2)) && ($over.next()[0] !== $movingRow[0])) {
      $over.after($target);
    }
  }

  function grabHandler(e) {
    $movingRow = $(this).closest('tr');
    $helper = $('<table>')
      .addClass('table')
      .addClass('table-images')
      .css({
        position: 'absolute',
        width: $movingRow.width()
      })
      .append($movingRow.clone());
    $movingRow.css('opacity', 0.5);

    $target = $('<tr>')
      .addClass('table-drop-target')
      .append('<td colspan="' + $movingRow.find('td').length + '"></td>');

    $('body')
      .on('mousemove', dragHandler)
      .on('selectstart', doNothing)
      .on('mouseup', dropHandler)
      .append($helper);

    dragHandler(e);
  }

  function dragHandler(e) {
    $helper.css({
      top: e.pageY + 10,
      left: e.pageX + 10
    });
    placeTarget(e);
  }

  function dropHandler(e) {
    $('body')
      .off('selectstart', doNothing)
      .off('mousemove', dragHandler)
      .off('mouseup', dropHandler);

    if($target.is(':visible')) {
      // Actually move item and finalize
      $movingRow.css('opacity', 1.0);
      $target.after($movingRow);
      $target.remove();
      setGravity();
    } else {
      $movingRow.css('opacity', 1.0);
    }

    $helper.remove();
  }

  function removeHandler(e) {
    e.preventDefault();
    e.stopPropagation();
    var $row = $(this).closest('tr').remove();
  }

  function setGravity() {
    // Iterate over all rows and set gravity field
    $('.js-image-widget-images > tr').each(function (ii) {
      $(this).find('.js-image-gravity').val(ii);
    });
  }

  $(function () {
    if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
      alert('Browser unsupported!');
    } else {
      $('.js-image-widget')
        .on('dragover', handleFileDragOver)
        .on('drop', handleFileDrop);
      $('.js-image-widget input[type=file]').on('change', handleFileSelect);

      $('.js-image-drag-handle').on('mousedown', grabHandler);
      $('.js-image-remove').on('click', removeHandler);
    }
  });
});
