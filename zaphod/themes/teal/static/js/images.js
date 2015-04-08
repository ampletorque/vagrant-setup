/*globals define*/
define(['jquery',
        'tpl!teal/templates/images-row-existing.erb.html',
        'tpl!teal/templates/images-row-new.erb.html',
        'tpl!teal/templates/images-result.erb.html'],
        function ($, existingRowTemplate, newRowTemplate, resultTemplate) {
  // This module handles the admin interface's image association widget.

  "use strict";

  function ImageWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('handleNewFile')
      .proxy('handleNewFiles')
      .proxy('handleFileDrop')
      .proxy('handleFileDragOver')
      .proxy('handleFileSelect')
      .proxy('placeTarget')
      .proxy('grabHandler')
      .proxy('dragHandler')
      .proxy('dropHandler')
      .proxy('removeHandler')
      .proxy('setGravity')
      .proxy('searchHandler')
      .proxy('selectHandler')
      .proxy('resetHandler')
      .proxy('ajaxValidateCheck');
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
        .on('click', '.js-image-select', this.selectHandler)
        .find('input[type=file]')
          .on('change', this.handleFileSelect);

      this.$search = this.$container.find('.js-image-search')
        .on('keyup', this.searchHandler);
      this.$results = this.$container.find('.js-image-search-results');
      this.$imagesBody = this.$container.find('> tbody');

      this.$imagesBodyBackup = this.$imagesBody.clone();

      this.$target = $('<tr>')
        .addClass('table-drop-target')
        .append('<td colspan="6"></td>');

      this.$form = this.$container.closest('form')
        .on('reset', this.resetHandler);

      this.$form.data('check-callback', this.ajaxValidateCheck);

      this.indexCounter = this.$imagesBody.find('> tr').length;

      this.activeSearchRequest = null;
      this.lastSearchQuery = null;

      this.pendingUploads = [];
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
          xsrf = $('#_authentication_token').val(),
          that = this;

      if (!!file.type.match(/image.*/)) {
        // Make a new random ID to refer to it.
        var imageID = this.makeID();

        // Make a new row, passing in the ID
        var $el = $(newRowTemplate({
          idx: this.indexCounter,
          gravity: this.indexCounter,
          id: imageID,
          name: file.name
        }));
        if(this.$target.is(':visible')) {
          this.$target.after($el);
        } else {
          $('.js-image-widget-images').append($el);
        }

        this.indexCounter++;

        this.loadThumbnail(file, $el);

        var $progress = $el.find('.js-image-progress'),
            $status = $el.find('.js-image-status');

        // Upload the file via ajax, get back an ID reference to it
        var formData = new FormData();
        formData.append("file", file);
        formData.append("id", imageID);
        formData.append("_authentication_token", xsrf);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', uploadPath, true);
        xhr.upload.onprogress = function (e) {
          if (e.lengthComputable) {
            if (e.loaded === e.total) {
              $status.text('Unsaved');
            } else{
              $progress.text((e.loaded / e.total * 100).toFixed(0));
            }
          }
        };
        xhr.send(formData);
        xhr.onreadystatechange = function(e) {
          // Remove this from the pending uploads once it's complete.
          var idx = that.pendingUploads.indexOf(xhr);
          if(idx != -1) {
            that.pendingUploads.splice(idx, 1);
          }
        };

        this.pendingUploads.push(xhr);
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
      this.$target.detach();
      this.setGravity();
    },

    handleFileDragOver: function(e) {
      e.stopPropagation();
      e.preventDefault();
      e.originalEvent.dataTransfer.dropEffect = 'copy';
      this.placeFileTarget(e);
    },

    doNothing: function(e) {
      e.preventDefault();
    },

    placeFileTarget: function(e) {
      var $over = $(e.target).closest('tr');

      // If we're not over the container, return.
      if(!($.contains(this.$imagesBody[0], $over[0]))) {
        return;
      }

      // If we're over the existing target, return.
      if($over[0] === this.$target[0]) {
        return;
      }

      this.$target.detach();

      // Otherwise, place the target either before or after the row we're over.
      var h = $over.height(),
          off = $over.offset(),
          threshold = off.top + h / 2;
      if (e.pageY < threshold) {
        $over.before(this.$target);
      } else  {
        $over.after(this.$target);
      }
    },

    placeTarget: function(e) {
      var $over = $(e.target).closest('tr');

      // If we're not over the container, return.
      if(!($.contains(this.$imagesBody[0], $over[0]))) {
        return;
      }

      // If we're over the existing target, return.
      if($over[0] === this.$target[0]) {
        return;
      }

      this.$target.detach();

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
        this.$target.detach();
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
    },

    searchHandler: function(e) {
      var that = this,
          q = this.$search.val().trim();
      console.log("image search", q);

      if(q !== this.lastSearchQuery) {
        // This should cancel any currently pending ajax requests.
        if(this.activeSearchRequest) {
          this.activeSearchRequest.abort();
        }
        this.lastSearchQuery = q;
        this.activeSearchRequest = $.ajax({
          type: "GET",
          url: this.$container.data('search-path') + '?filter=admin-tiny&q=' + q,
          error: function (request, status, error) {
            alert('Server Error');
          },
          success: function (data, status, xhr) {
            var image, label;
            that.activeSearchRequest = null;
            console.log("images ajax data", data.images);

            // Populate a menu panel to pick user from
            that.$results.empty();
            if(data.images.length === 0) {
              that.$results.append('<p>No results.</p>');
            }

            for(var ii = 0; ii < data.images.length; ii++) {
              image = data.images[ii];
              that.$results.append(resultTemplate({
                image: image
              }));
            }
            that.$results.show();
          },

        });
      }

    },

    selectHandler: function(e) {
      console.log("image select");
      e.preventDefault();
      e.stopPropagation();
      // Add project to list, including hidden field.
      var $el = $(e.target).closest('a'),
          imageID = $el.data('image-id'),
          imageName = $el.data('image-name'),
          imageAlt = $el.data('image-alt'),
          imageTitle = $el.data('image-title');

      $('.js-image-widget-images').append(existingRowTemplate({
        idx: this.indexCounter,
        gravity: this.indexCounter,
        id: $el.data('image-id'),
        name: $el.data('image-name'),
        alt: $el.data('image-alt'),
        title: $el.data('image-title'),
        width: $el.data('image-width'),
        height: $el.data('image-height'),
        path: $el.data('image-path'),
        originalPath: $el.data('image-original-path'),
      }));

      $el.closest('.modal').modal('hide');

      this.indexCounter++;

      this.$search.val('');
      this.lastSearchQuery = null;

    },

    resetHandler: function(e) {
      console.log("image form reset");
      // Restore initial image state.
      this.$imagesBody.replaceWith(this.$imagesBodyBackup.clone());
      this.pendingUploads = [];
    },

    ajaxValidateCheck: function() {
      console.log("image form ajax validate check");
      if(this.pendingUploads.length > 0) {
        alert("Image uploads are still in progress.");
        return false;
      } else {
        return true;
      }
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
