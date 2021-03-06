// Generated by CoffeeScript 1.6.3
(function() {
  window.addEventListener('load', function() {
    var MARGIN, form, input, mtxt, recalc_width;
    form = document.getElementById('nickname-form');
    form.addEventListener('submit', function(evt) {
      if (input.value.trim() === "") {
        evt.preventDefault();
        return evt.stopPropagation();
      }
    }, false);
    input = form.querySelector('input[type=text]');
    input.addEventListener('blur', function() {
      if (input.value.trim() !== "") {
        return form.submit();
      }
    }, false);
    mtxt = document.createElement('span');
    mtxt.style.position = 'absolute';
    mtxt.style.opacity = 0;
    mtxt.style.left = "-6666px";
    mtxt.style.top = "-6666px";
    mtxt.style.font = window.getComputedStyle(input).font;
    document.body.insertBefore(mtxt, document.body.children[0]);
    MARGIN = 10;
    recalc_width = function() {
      mtxt.textContent = input.value;
      return input.style.width = "" + (mtxt.offsetWidth + MARGIN) + "px";
    };
    recalc_width();
    return input.addEventListener('keypress', function() {
      return setTimeout(recalc_width, 0);
    }, false);
  }, false);

}).call(this);
