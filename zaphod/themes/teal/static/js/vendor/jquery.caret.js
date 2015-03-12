/*
 *
 * Copyright (c) 2010 C. F., Wong (<a href="http://cloudgen.w0ng.hk">Cloudgen Examplet Store</a>)
 * Licensed under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 *
 */
(function ($, len, createRange, duplicate) {
  $.fn.caret = function (options, opt2) {
    var
    t = this[0],
    msie = $.browser.msie,
    start, end, re,
    range, stored_range, s, e, val, selection, te;

    if (typeof options === "object" && typeof options.start === "number" && typeof options.end === "number") {
      start = options.start;
      end = options.end;
    } else if (typeof options === "number" && typeof opt2 === "number") {
      start = options;
      end = opt2;
    } else if (typeof options === "number" && opt2 === undefined) {
      start = end = options;
    } else if (typeof options === "string") {
      if ((start = t.value.indexOf(options)) > -1) {
        end = start + options[len];
      } else {
        start = null;
      }
    } else if (Object.prototype.toString.call(options) === "[object RegExp]") {
      re = options.exec(t.value);
      if (re != null) {
        start = re.index;
        end = start + re[0][len];
      }
    }

    if (end && end > this[0].value.length) {
      if (start === end) {
        start = end = this[0].value.length;
      } else {
        end = this[0].value.length;
      }
    }

    if (typeof start !== "undefined") {
      if (msie) {
        range = this[0].createTextRange();
        range.collapse(true);
        range.moveStart('character', start);
        range.moveEnd('character', end - start);
        range.select();
      } else {
        this[0].selectionStart = start;
        this[0].selectionEnd = end;
      }

      this[0].focus();
      return this;
    }

    if (msie && this[0].tagName.toLowerCase() !== "textarea") {
      val = this.val();

      range = document.selection[createRange]()[duplicate]();
      range.moveEnd("character", val[len]);
      s = (range.text ? val.lastIndexOf(range.text) : val[len]);

      range = document.selection[createRange]()[duplicate]();
      range.moveStart("character", -val[len]);
      e = range.text[len];
    } else if (msie) {
      range = document.selection[createRange]();

      stored_range = range[duplicate]();
      stored_range.moveToElementText(this[0]);
      stored_range.setEndPoint('EndToEnd', range);

      s = stored_range.text[len] - range.text[len];
      e = s + range.text[len];
    } else {
      try {
        s = t.selectionStart;
        e = t.selectionEnd;
      } catch (ex) {
        s = 0;
        e = 0;
      }
    }

    te = t.value.substring(s, e);
    return {start: s, end: e, text: te, replace: function (st) {
      return t.value.substring(0, s) + st + t.value.substring(e, t.value[len]);
    }};
  };
}(jQuery, "length", "createRange", "duplicate"));
