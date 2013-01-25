// Generated by CoffeeScript 1.4.0
(function() {

  window.addEventListener('load', function() {
    var confirm_field, delete_button;
    confirm_field = document.getElementById('confirm-field');
    delete_button = document.getElementById('delete-button');
    return confirm_field.addEventListener('keydown', function(evt) {
      if (evt.keyCode === 13) {
        if (evt.stopPropagation) {
          evt.stopPropagation();
        }
        if (evt.preventDefault) {
          evt.preventDefault();
        }
      }
      return setTimeout(function() {
        return delete_button.disabled = confirm_field.value !== "unrecoverable";
      }, 10);
    }, false);
  }, false);

}).call(this);
