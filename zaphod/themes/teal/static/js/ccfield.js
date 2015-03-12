define(['jquery', 'jquery.caret'], function ($) {
  var ccTypes = {
    "visa": {
      'mask': "---- ---- ---- ----",
      'iin': ["4"]
    },
    "mastercard": {
      'mask': "---- ---- ---- ----",
      'iin': ["51", "52", "53", "54", "55"]
    },
    "discover": {
      'mask': "---- ---- ---- ----",
      'iin': ["6011"]
    },
    "amex": {
      'mask': "---- ------ -----",
      'iin': ["34", "37"]
    },
    "unknown": {
      'mask': "---- ---- ---- ----",
      'iin': []
    }
  };

  function detectCardType(cc_num) {
    var ccType, iin, i;
    for (ccType in ccTypes) {
      if(ccTypes.hasOwnProperty(ccType)) {
        for (i = 0; ccTypes[ccType].iin[i]; i++) {
          iin = ccTypes[ccType].iin[i];
          if (cc_num.substr(0, iin.length) === iin) {
            return ccType;
          }
        }
      }
    }
    return "unknown";
  }

  function isPrintable(keycode) {
    return (keycode >= 32 && keycode < 127);
  }

  function redistribute(num, mask) {
    function reSegment(m) {
      return "(.{0," + m.length + "})";
    }

    var
    segs = mask.split(/\s+/).length,
    maskRe = new RegExp("^" + mask.replace(/\S+/g, reSegment).replace(/\s/g, "")),
    maskSub = "$1 $2 $3 $4 $5 $6 $7".substring(0, segs * 2 + segs - 1);

    return num.replace(/\s/g, "")
      .replace(maskRe, maskSub)
      .replace(/\s*$/, '');
  }

  function checkCardType() {
    var
      last_type = $(this).data('ccfield.cctype'),
      type = detectCardType($(this).val()),
      caret = $(this).caret();

    if (last_type !== type) {
      $(this)
        .data('ccfield.cctype', type)
        .trigger("cctype", type)
        .val(redistribute($(this).val(), ccTypes[type].mask));

      if (caret.start > 0 || caret.end > 0) {
        $(this).caret(caret.start);
      }
    }
  }

  $(function () {
    var $el = $('.js-ccfield');
    console.log("cc field", $el);

    $el.each(checkCardType);

    $el.on('keypress', function (e) {
      if (isPrintable(e.which)) { 
        var
          meta_key = e.metaKey || e.ctrlKey || e.altKey,
          chr = String.fromCharCode(e.which),
          val = $(this).val(),
          caret = $(this).caret(),
          mask, caretOffset;

        // No text selected
        if (caret.start === caret.end && !meta_key) {
          e.preventDefault();

          mask = ccTypes[detectCardType(val)].mask;
          if (/\d/.test(chr) && val.length < mask.length) {
            val = redistribute(val.substr(0, caret.start) + chr +
                               val.substr(caret.start, val.length), mask);
            caretOffset = val.charAt(caret.start) === " " ? 2 : 1;
            $(this).val(val).caret(caret.start + caretOffset);
          }
        }
      }
    });

    $el.on('keydown', function (e) {
      var
        val = $(this).val(),
        len = val.length,
        caret = $(this).caret(),
        caretOffset, mask;

      mask = ccTypes[detectCardType(val)].mask;

      // Backspace
      if (e.which === 8 && caret.start === caret.end) {
        e.preventDefault();
        caretOffset = val.charAt(caret.start - 1) === " " ? 2 : 1;
        val = val.substr(0, caret.start - caretOffset) + val.substr(caret.start, len);
        $(this).val(redistribute(val, mask)).caret(caret.start - caretOffset);
      }

      // Delete
      else if (e.which === 46 && caret.start === caret.end) {
        e.preventDefault();
        caretOffset = val.charAt(caret.start) === " " ? 2 : 1;
        val = val.substr(0, caret.start) + val.substr(caret.start + caretOffset, len);
        $(this).val(redistribute(val, mask)).caret(caret.start);
      }

      // Backspace or delete with selection
      else if (e.which === 46 || e.which === 8) {
        e.preventDefault();
        val = val.substr(0, caret.start) + val.substr(caret.end, len);
        $(this).val(redistribute(val, mask)).caret(caret.start);
      }
    });

    $el.on('keyup', checkCardType);
  });
});
