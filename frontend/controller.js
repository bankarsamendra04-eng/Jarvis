// Controller for Eel Exposed Functions & UI Event Bindings
$(document).ready(function () {
  // -------------------------------------------------------------
  // Display Speak / Status Message
  // -------------------------------------------------------------
  eel.expose(DisplayMessage);
  function DisplayMessage(message) {
    if ($(".siri-message li:first").length) {
      $(".siri-message li:first").text(message);
      $(".siri-message").textillate("start");
    } else {
      $(".siri-message").text(message);
    }
  }

  // -------------------------------------------------------------
  // UI State Switchers
  // -------------------------------------------------------------
  eel.expose(ShowHood);
  function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
  }

  eel.expose(openMicUI);
  function openMicUI() {
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
  }

  // -------------------------------------------------------------
  // Dynamic Message Appenders
  // -------------------------------------------------------------
  eel.expose(senderText);
  function senderText(message, timestamp) {
    if (!message || message.trim() === "") return;
    
    // Hide startup placeholder when messages start appearing
    $("#Start").attr("hidden", true);

    var chatBox = document.getElementById("chat-canvas-body");
    var timeStr = timestamp || formatCurrentTime();
    
    var msgHtml = `
      <div class="message-row user-row">
        <div class="message-bubble user-bubble">
          <div class="message-content">${escapeHtml(message)}</div>
          <div class="message-meta">${timeStr}</div>
        </div>
      </div>
    `;
    
    chatBox.innerHTML += msgHtml;
    scrollToBottom();
  }

  eel.expose(receiverText);
  function receiverText(message, timestamp) {
    if (!message || message.trim() === "") return;

    $("#Start").attr("hidden", true);

    var chatBox = document.getElementById("chat-canvas-body");
    var timeStr = timestamp || formatCurrentTime();

    var msgHtml = `
      <div class="message-row assistant-row">
        <div class="message-bubble assistant-bubble">
          <div class="message-content">${escapeHtml(message)}</div>
          <div class="message-meta">
            <i class="bi bi-robot me-1 text-info"></i> ${timeStr}
          </div>
        </div>
      </div>
    `;

    chatBox.innerHTML += msgHtml;
    scrollToBottom();
  }

  // -------------------------------------------------------------
  // Real-time Conversation Refresh Hook (called by backend)
  // -------------------------------------------------------------
  eel.expose(refreshConversations);
  function refreshConversations() {
    if (window.loadConversations) {
      window.loadConversations();
    }
  }

  // -------------------------------------------------------------
  // Biometrics & Startup Animations
  // -------------------------------------------------------------
  eel.expose(hideLoader);
  function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
  }

  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
  }

  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
  }

  eel.expose(hideStart);
  function hideStart() {
    $("#Start").attr("hidden", true);
    setTimeout(function () {
      $("#Oval").addClass("animate__animated animate__zoomIn");
      $("#Oval").attr("hidden", false);
    }, 400);
  }

  // -------------------------------------------------------------
  // Helper Functions
  // -------------------------------------------------------------
  function formatCurrentTime() {
    var d = new Date();
    var hours = d.getHours();
    var minutes = d.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return hours + ':' + minutes + ' ' + ampm;
  }

  function escapeHtml(text) {
    var map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  function scrollToBottom() {
    var viewport = document.getElementById("chat-viewport");
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }

  window.scrollToBottom = scrollToBottom;
  window.escapeHtml = escapeHtml;
  window.formatCurrentTime = formatCurrentTime;
});
