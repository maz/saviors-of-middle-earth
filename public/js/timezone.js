// Generated by CoffeeScript 1.6.3
(function() {
  var future, offset_in_seconds;

  offset_in_seconds = function() {
    return Math.round((new Date()).getTimezoneOffset() * 100) / -100;
  };

  future = new Date();

  future.setYear(future.getYear() + 5);

  document.cookie = "gmt_offset=" + offset_in_seconds() / 60 + (";expires=" + (future.toGMTString()));

}).call(this);
