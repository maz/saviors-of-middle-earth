// Generated by CoffeeScript 1.4.0
(function() {
  var focused, message_audio, play_message_notification, socket;

  socket = null;

  message_audio = null;

  play_message_notification = function() {
    message_audio.currentTime = 0;
    return message_audio.play();
  };

  focused = true;

  window.addEventListener('focus', function() {
    return focused = true;
  });

  window.addEventListener('blur', function() {
    return focused = false;
  });

  window.addEventListener('load', function() {
    var channel;
    message_audio = new Audio;
    message_audio.src = "/sounds/message.wav";
    channel = new goog.appengine.Channel(document.body.getAttribute('data-channel-token'));
    socket = channel.open();
    socket.onmessage = function(evt) {
      var msg;
      msg = JSON.parse(evt.data);
      if (msg.action === 'new_message') {
        if (!focused) {
          return play_message_notification();
        }
      }
    };
    return socket.onerror = socket.onclose = function() {
      return null;
    };
  }, false);

}).call(this);
