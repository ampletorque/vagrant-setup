/*globals define*/
define(['jquery'], function ($) {
  // This module handles the admin interface's tag association widget.

  // TODO
  // - Support form resets
  // - Add loading spinner when getting tag data via AJAX

  "use strict";

  function TagWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('addHandler')
      .proxy('populateOptions')
      .proxy('selectHandler')
      .proxy('removeHandler');
    this.init();
  }

  TagWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container.on('click', '.js-tag-remove', this.removeHandler);
      this.$addLink = this.$container.find('.js-tag-add')
        .on('click', this.addHandler);
      this.$select = this.$container.find('select')
        .on('change', this.selectHandler);

      this.allTags = [];
    },

    removeHandler: function(e) {
      console.log("tag remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('li').remove();
    },

    populateOptions: function() {
      // Use cached tag data to repopulate select field. Disable tags which are
      // already associated.
      var tag, s;

      var selected = []
      this.$container.find('input[type=hidden]').each(function() {
        selected.push(parseInt($(this).val()));
      });

      this.$select.empty();
      this.$select.append('<option>Select Tag</option>');

      for(var ii = 0; ii < this.allTags.length; ii++) {
        tag = this.allTags[ii];
        if($.inArray(tag.id, selected) < 0) {
          s = '<option value="' + tag.id + '">' + tag.name + '</option>';
        } else {
          // Already selected, disable it
          s = '<option disabled>' + tag.name + '</option>';
        }
        this.$select.append(s);
      }
      this.$select.show();
    },

    addHandler: function(e) {
      console.log("tag add");
      e.preventDefault();
      e.stopPropagation();
      var that = this;

      this.$addLink.hide();

      if(this.allTags.length > 0) {
        this.populateOptions();
      } else {
        console.log("tag ajax request");
        // Load tags via AJAX and populate the select menu.
        $.ajax({
          type: "GET",
          url: this.$container.data('path'),
          error: function (request, status, error) {
            alert('Server Error');
          },
          success: function (data, status, xhr) {
            console.log("tag ajax success");
            that.allTags = data.tags;
            that.populateOptions();
          },
        });
      }
    },

    selectHandler: function(e) {
      console.log("tag select");
      var $selected = this.$select.find('option:selected'),
          tagID = $selected.val(),
          tagName = $selected.text(),
          $lastItem = this.$addLink.parent('li');

      console.log("selected", $selected);
      console.log("tag id", tagID);
      console.log("tag name", tagName);

      $selected.removeProp('selected');

      $lastItem.before(
        '<li>\n' +
          '<a class="js-tag-remove" href="#">' +
            '<i class="fa fa-minus-circle"></i>' +
          '</a>\n' +
          '<input type="hidden" name="tag_ids" value="' + tagID + '">\n' +
          tagName +
        '\n</li>'
      );

      this.$select.hide();
      this.$addLink.show();
    }

  };

  $(function () {
    $('.js-tag-association').each(function() {
      var d = new TagWidget(this);
    });
  });
});
