// Generated by CoffeeScript 1.4.0
(function() {
  var $, Communique, communique_cache, focused, loading, message_audio, overlay, play_message_notification, sidebar, socket;

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

  $ = function(id) {
    return document.getElementById(id);
  };

  overlay = null;

  loading = null;

  sidebar = null;

  overlay.show = function() {
    return overlay.style.display = 'block';
  };

  overlay.hide = function() {
    return overlay.style.display = 'none';
  };

  loading.show = function() {
    overlay.show();
    return loading.style.display = 'block';
  };

  loading.hide = function() {
    return loading.style.display = 'none';
  };

  communique_cache = null;

  Communique = (function() {

    function Communique(data) {
      communique_cache[data.id] = this;
      this.unread = data.unread;
      this.id = data.id;
      this.users = data.users;
      this.dom = document.createElement('div');
      this.dom.setAttribute('data-id', data.id);
      this.dom.classList.add('communique');
      if (data.unread) {
        this.dom.classList.add('unread');
      }
      this.dom.textContent = data.users.join(', ');
      if (sidebar.childNodes[0]) {
        sidebar.insertBefore(this.dom, sidebar.childNodes[0]);
      } else {
        sidebar.appendChild(this.dom);
      }
    }

    return Communique;

  })();

  window.addEventListener('load', function() {
    var channel, messages_opener, messages_panel;
    message_audio = new Audio;
    message_audio.src = "/sounds/message.wav";
    message_audio.load();
    channel = new goog.appengine.Channel(document.body.getAttribute('data-channel-token'));
    socket = channel.open();
    socket.onmessage = function(evt) {
      var msg;
      msg = JSON.parse(evt.data);
      if (msg.action === 'new_message') {
        if (!focused) {
          play_message_notification();
        }
        if (messages_panel.classList.contains('active')) {
          return null;
        } else {
          return messages_opener.classList.add('attn');
        }
      }
    };
    socket.onerror = socket.onclose = function() {
      return null;
    };
    messages_panel = $('messages-panel');
    messages_opener = messages_panel.querySelector('.messages-opener');
    messages_opener.addEventListener('click', function() {
      var op;
      messages_panel.classList.toggle('active');
      messages_opener.textContent = messages_panel.classList.contains('active') ? "Close" : "Messages";
      messages_opener.classList.remove('attn');
      if (messages_panel.classList.contains('active') && !communique_cache) {
        communique_cache = {};
        loading.show();
        op = new XMLHttpRequest;
        op.open('get', '/messaging/list', true);
        op.responeType = 'json';
        return op.onload = function() {
          var communique, _i, _len, _ref;
          _ref = op.response;
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            communique = _ref[_i];
            create_communique_dom(communique);
          }
          return loading.hide();
        };
      }
    }, false);
    overlay = messages_panel.querySelector('.overlay');
    loading = messages_panel.querySelector('.loading');
    return sidebar = messages_panel.querySelector('.sidebar');
  }, false);

}).call(this);
