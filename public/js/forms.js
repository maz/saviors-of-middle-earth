// Generated by CoffeeScript 1.4.0
(function() {

  window.addEventListener('load', function() {
    var form, _i, _len, _ref, _results;
    _ref = document.querySelectorAll('form');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      form = _ref[_i];
      _results.push((function(form) {
        return form.addEventListener('submit', function(evt) {
          var button;
          if ((form.classList.contains('delete-form') && !confirm('Do you really want to delete?')) || (form.getAttribute('data-confirmation-message') && !confirm(form.getAttribute('data-confirmation-message')))) {
            if (evt.stopPropagation) {
              evt.stopPropagation();
            }
            if (evt.preventDefault) {
              evt.preventDefault();
            }
            return false;
          }
          if (form.getAttribute('data-completing-label')) {
            button = form.querySelector('input[type=submit]');
            if (button) {
              button.disabled = true;
              return button.value = form.getAttribute('data-completing-label');
            }
          }
        }, false);
      })(form));
    }
    return _results;
  }, false);

}).call(this);
