/*globals define*/
define(['jquery'], function ($) {
  // This module handles the admin interface's related project association widget.

  "use strict";

  function RelatedProjectWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('addHandler')
      .proxy('selectHandler')
      .proxy('searchHandler')
      .proxy('removeHandler');
    this.init();
  }

  RelatedProjectWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      console.log("project init");
      this.$container
        .on('click', '.js-project-remove', this.removeHandler)
        .on('click', '.js-project-select', this.selectHandler);
      this.$search = this.$container.find('input[type=text]')
        .on('keyup', this.searchHandler);
      this.$addLink = this.$container.find('.js-project-add')
        .on('click', this.addHandler);
      this.$menu = this.$container.find('.js-project-menu');

      this.activeRequest = null;
      this.lastQuery = null;
    },

    removeHandler: function(e) {
      console.log("project remove");
      e.preventDefault();
      e.stopPropagation();
      var $row = $(e.target).closest('li').remove();
    },

    addHandler: function(e) {
      console.log("project add");
      e.preventDefault();
      e.stopPropagation();
      this.$addLink.hide();
      this.$search.show();
    },

    searchHandler: function(e) {
      // When typing, show search results.
      var that = this,
          q = this.$search.val();
      console.log("project search", q);

      if(q !== this.lastQuery) {
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
            var project;
            that.activeRequest = null;
            console.log("projects ajax data", data.projects);

            var selected = []
            that.$container.find('input[type=hidden]').each(function() {
              selected.push(parseInt($(this).val()));
            });

            // Populate a menu panel to pick project from
            that.$menu.empty();
            if(data.projects.length === 0) {
              that.$menu.append('<li><p>No results.</p></li>');
            }

            for(var ii = 0; ii < data.projects.length; ii++) {
              project = data.projects[ii];
              if($.inArray(project.id, selected) < 0) {
                that.$menu.append('<li><a href="#" class="js-project-select" data-project-id="' + project.id + '" data-project-name="' + project.name + '">' + project.name + '</a></li>');
              } else {
                that.$menu.append('<li><p>' + project.name + '</p></li>');
              }
            }
            that.$menu.show();
          },

        });
      }
    },

    selectHandler: function(e) {
      console.log("project select");
      e.preventDefault();
      e.stopPropagation();
      // Add project to list, including hidden field.
      var $el = $(e.target),
          projectID = $el.data('project-id'),
          projectName = $el.data('project-name'),
          $lastItem = this.$addLink.parent('li');

      $lastItem.before(
        '<li>\n' +
          '<a class="js-project-remove" href="#">' +
            '<i class="fa fa-minus-circle"></i>' +
          '</a>\n' +
          '<input type="hidden" name="related_project_ids" value="' + projectID + '">\n' +
          projectName +
        '\n</li>'
      );

      this.$search.hide();
      this.$search.val('');
      this.$addLink.show();
      this.$menu.hide();
    }

  };

  $(function () {
    $('.js-project-association').each(function() {
      var d = new RelatedProjectWidget(this);
    });
  });
});
