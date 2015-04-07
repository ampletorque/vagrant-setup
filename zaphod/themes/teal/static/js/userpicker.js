/*globals define*/
define(['jquery'], function ($) {
  // This module handles the admin interface's user picker widget.

  "use strict";

  function UserWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('selectHandler')
      .proxy('searchHandler');
    this.init();
  }

  UserWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      console.log("userpicker init");
      this.$search = this.$container.find('input[type=text]')
        .on('keyup', this.searchHandler);
      this.$menu = this.$container.find('.js-user-menu');
      this.$container.on('click', '.js-user-select', this.selectHandler);

      this.activeRequest = null;
      this.lastQuery = null;
    },

    searchHandler: function(e) {
      // When typing, show search results.
      var that = this,
          q = this.$search.val().trim();
      console.log("user search", q);

      if(q === '') {
        this.$menu.hide();
      } else if(q !== this.lastQuery) {
        // This should cancel any currently pending ajax requests.
        if(this.activeRequest) {
          this.activeRequest.abort();
        }
        this.lastQuery = q;
        this.activeRequest = $.ajax({
          type: "GET",
          url: this.$container.data('path') + '?q=' + q,
          error: function (request, status, error) {
            alert('Server Error');
          },
          success: function (data, status, xhr) {
            var user, label;
            that.activeRequest = null;
            console.log("users ajax data", data.users);

            // Populate a menu panel to pick user from
            that.$menu.empty();
            if(data.users.length === 0) {
              that.$menu.append('<li><p>No results.</p></li>');
            }

            for(var ii = 0; ii < data.users.length; ii++) {
              user = data.users[ii];
              label = user.name + ' (' + user.email + ')';
              that.$menu.append('<li><a href="#" class="js-user-select" data-user-id="' + user.id + '" data-user-label="' + label + '">' + label + '</a></li>');
            }
            that.$menu.show();
          },

        });
      }
    },

    selectHandler: function(e) {
      console.log("user select");
      e.preventDefault();
      e.stopPropagation();
      // Add project to list, including hidden field.
      var $el = $(e.target),
          userID = $el.data('user-id'),
          userLabel = $el.data('user-label');

      this.$container.find('input[type=hidden]').val(userID);
      this.$container.find('.input-group-addon').text(userLabel);

      this.$menu.hide();
      this.$search.val('');
      this.lastQuery = null;
    }

  };

  $(function () {
    $('.js-user-picker').each(function() {
      var d = new UserWidget(this);
    });
  });
});
