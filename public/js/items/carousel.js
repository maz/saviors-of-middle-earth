// Generated by CoffeeScript 1.6.3
(function() {
  window.addEventListener('load', function() {
    var container, _i, _len, _ref, _results;
    _ref = document.querySelectorAll('.carousel-container');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      container = _ref[_i];
      _results.push((function(container) {
        var LEFT_SPEED, RIGHT_SPEED, carousel, contents, extreme_width, frame, left, right, speed, start_timer, stop_timer, timer;
        left = container.querySelector('.left-arrow');
        right = container.querySelector('.right-arrow');
        contents = container.querySelector('.carousel-contents');
        carousel = container.querySelector('.carousel');
        if (contents.children.length <= 1) {
          return;
        }
        extreme_width = contents.children[contents.children.length - 2].offsetLeft;
        RIGHT_SPEED = 5;
        LEFT_SPEED = -RIGHT_SPEED;
        speed = RIGHT_SPEED;
        frame = function() {
          return carousel.scrollLeft = Math.max(Math.min(carousel.scrollLeft + speed, extreme_width - carousel.offsetWidth), 0);
        };
        timer = null;
        stop_timer = function() {
          document.body.removeEventListener('mouseup', stop_timer, false);
          return clearInterval(timer);
        };
        start_timer = function() {
          timer = setInterval(frame, 10);
          frame();
          return document.body.addEventListener('mouseup', stop_timer, false);
        };
        right.addEventListener('mousedown', function() {
          speed = RIGHT_SPEED;
          return start_timer();
        }, false);
        return left.addEventListener('mousedown', function() {
          speed = LEFT_SPEED;
          return start_timer();
        }, false);
      })(container));
    }
    return _results;
  }, false);

}).call(this);
