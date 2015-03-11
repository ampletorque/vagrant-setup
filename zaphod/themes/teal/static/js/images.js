/*globals define*/
define(['jquery', 'underscore', 'text!teal/images-row.erb.html'], function ($, _, rowTemplateRaw) {
  // This module handles the admin interface's image association widget.

  // TODO:
  // - Block form submission until all image uploads have completed.
  // - Listen for form resets and reset image data back to the original
  // (requires storing the original data).
  // - Don't allow dragging images 'out of position' (outside the main tbody
  // for images).
  // Improve performmance, particularly of progress indicator updates and
  // thumbnail showing.
  // Highlight rows somehow if they're still unsaved.

  "use strict";

  var rowTemplate = _.template(rowTemplateRaw);

  function ImageWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('handleNewFile')
      .proxy('handleNewFiles')
      .proxy('handleFileDrop')
      .proxy('handleFileSelect')
      .proxy('placeTarget')
      .proxy('grabHandler')
      .proxy('dragHandler')
      .proxy('dropHandler')
      .proxy('removeHandler')
      .proxy('setGravity');
    this.init();
  }

  ImageWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container
        .on('dragover', this.handleFileDragOver)
        .on('drop', this.handleFileDrop)
        .on('mousedown', '.js-image-drag-handle', this.grabHandler)
        .on('click', '.js-image-remove', this.removeHandler)
        .find('input[type=file]')
          .on('change', this.handleFileSelect);
    },

    makeID: function() {
      // Return a randomly-generated ID to pass to use to refer to a newly
      // added image.
      var text = "", possible = "abcdefghijklmnopqrstuvwxyz0123456789";
      for( var i=0; i < 32; i++ ) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
      }
      return text;
    },

    loadThumbnail: function(file, $row) {
      // Load the actual image data from a newly added image file, and show it
      // in a scaled image element in the corresponding row.
      var reader = new FileReader();
      reader.onload = function(e) {
        $row.find('.js-image-placeholder').append(
          $('<img>')
            .attr('width', 64)
            .attr('height', 64)
            .attr('src', e.target.result)
        );
      };
      reader.readAsDataURL(file);
    },

    handleNewFile: function(file) {
      var uploadPath = this.$container.data('upload-path'),
          xsrf = $('#_authentication_token').val();

      if (!!file.type.match(/image.*/)) {
        // Make a new random ID to refer to it.
        var imageID = this.makeID(),
            nextIndex = this.$container.find('.js-image-widget-images > tr').length;

        // Make a new row, passing in the ID
        var $el = $(rowTemplate({
          idx: nextIndex,
          gravity: nextIndex,
          id: imageID,
          name: file.name
        }));
        $('.js-image-widget-images').append($el);

        this.loadThumbnail(file, $el);

        var $progress = $el.find('.js-image-progress'),
            $status = $el.find('.js-image-status');

        // Upload the file via ajax, get back an ID reference to it
        var formData = new FormData();
        formData.append("file", file);
        formData.append("id", imageID);
        formData.append("_authentication_token", xsrf);

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
    },

    handleNewFiles: function(files) {
      for(var ii = 0; ii < files.length; ii++) {
        this.handleNewFile(files[ii]);
      }
    },

    handleFileSelect: function(e) {
      this.handleNewFiles(e.target.files);
    },

    handleFileDrop: function(e) {
      e.stopPropagation();
      e.preventDefault();
      this.handleNewFiles(e.originalEvent.dataTransfer.files);
    },

    handleFileDragOver: function(e) {
      e.stopPropagation();
      e.preventDefault();
      e.originalEvent.dataTransfer.dropEffect = 'copy';
    },

    doNothing: function(e) {
      e.preventDefault();
    },

    placeTarget: function(e) {
      var $over = $(e.target).closest('tr');

      // If we're not over the container, return.
      if(!($.contains(this.$container[0], $over[0]))) {
        return;
      }

      // If we're over the existing target, return.
      if($over[0] === this.$target[0]) {
        return;
      }

      this.$target.remove();

      // If we're over the row being dragged, hide the target.
      if($over[0] === this.$movingRow[0]) {
        return;
      }

      // Otherwise, place the target either before or after the row we're over.
      var h = $over.height(),
          off = $over.offset();
      if ((e.pageY < (off.top + h / 2)) && ($over.prev()[0] !== this.$movingRow[0])) {
        $over.before(this.$target);
      } else if ((e.pageY > (off.top + h / 2)) && ($over.next()[0] !== this.$movingRow[0])) {
        $over.after(this.$target);
      }
    },

    grabHandler: function(e) {
      this.$movingRow = $(e.target).closest('tr');
      this.$helper = $('<table>')
        .addClass('table')
        .addClass('table-images')
        .css({
          position: 'absolute',
          width: this.$movingRow.width()
        })
        .append(this.$movingRow.clone());
      this.$movingRow.css('opacity', 0.5);

      this.$target = $('<tr>')
        .addClass('table-drop-target')
        .append('<td colspan="' + this.$movingRow.find('td').length + '"></td>');

      $('body')
        .on('mousemove', this.dragHandler)
        .on('selectstart', this.doNothing)
        .on('mouseup', this.dropHandler)
        .append(this.$helper);

      this.dragHandler(e);
    },

    dragHandler: function(e) {
      this.$helper.css({
        top: e.pageY + 10,
        left: e.pageX + 10
      });
      this.placeTarget(e);
    },

    dropHandler: function(e) {
      $('body')
        .off('selectstart', this.doNothing)
        .off('mousemove', this.dragHandler)
        .off('mouseup', this.dropHandler);

      if(this.$target.is(':visible')) {
        // Actually move item and finalize
        this.$movingRow.css('opacity', 1.0);
        this.$target.after(this.$movingRow);
        this.$target.remove();
        this.setGravity();
      } else {
        this.$movingRow.css('opacity', 1.0);
      }

      this.$helper.remove();
    },

    removeHandler: function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $row = $(e.target).closest('tr').remove();
    },

    setGravity: function() {
      // Iterate over all rows and set gravity field
      this.$container.find('.js-image-widget-images > tr').each(function (ii) {
        $(this).find('.js-image-gravity').val(ii);
      });
    }

  };

  $(function () {
    if (!(window.File && window.FileReader)) {
      alert('Browser unsupported!');
    } else {
      $('.js-image-widget').each(function() {
        var d = new ImageWidget(this);
      });
    }
  });
});
