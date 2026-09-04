// Main Frontend Application Logic & Conversation History Management
$(document).ready(function () {
  var activeConversationId = null;
  var targetConversationIdForAction = null;
  var siriWave = null;

  // Initialize Eel backend
  if (typeof eel !== "undefined" && eel.init) {
    try {
      eel.init()();
    } catch (err) {
      console.log("Eel init notice:", err);
    }
  }

  // Initialize Animations
  try {
    $(".text").textillate({
      loop: true,
      speed: 1500,
      sync: true,
      in: { effect: "bounceIn" },
      out: { effect: "bounceOut" }
    });

    $(".siri-message").textillate({
      loop: true,
      sync: true,
      in: { effect: "fadeInUp", sync: true },
      out: { effect: "fadeOutUp", sync: true }
    });

    siriWave = new SiriWave({
      container: document.getElementById("siri-container"),
      width: 600,
      style: "ios9",
      amplitude: "1",
      speed: "0.30",
      height: 160,
      autostart: true,
      waveColor: "#00d2ff",
      waveOffset: 0,
      rippleEffect: true,
      rippleColor: "#ffffff"
    });
  } catch (e) {
    console.log("Animation init notice:", e);
  }

  // -------------------------------------------------------------
  // Load Initial Conversation & History
  // -------------------------------------------------------------
  async function initializeConversationState() {
    try {
      if (typeof eel !== "undefined" && eel.getActiveConversationId) {
        activeConversationId = await eel.getActiveConversationId()();
      }
    } catch (e) {
      console.log("Error getting active conv ID:", e);
    }
    await loadConversations();
    if (activeConversationId) {
      loadConversationMessages(activeConversationId);
    }
  }

  initializeConversationState();

  // -------------------------------------------------------------
  // Load Conversations List from SQLite
  // -------------------------------------------------------------
  async function loadConversations(searchQuery) {
    if (typeof eel === "undefined" || !eel.getConversations) return;

    try {
      var query = searchQuery || $("#search-conversations").val() || "";
      var conversations = await eel.getConversations(query)();

      var pinnedList = document.getElementById("pinned-list");
      var recentList = document.getElementById("recent-list");
      var pinnedSection = document.getElementById("pinned-section");
      var noConvState = document.getElementById("no-conversations-state");

      pinnedList.innerHTML = "";
      recentList.innerHTML = "";

      if (!conversations || conversations.length === 0) {
        pinnedSection.style.display = "none";
        noConvState.style.display = "block";
        return;
      }

      noConvState.style.display = "none";
      var hasPinned = false;

      conversations.forEach(function (conv) {
        var card = createConversationCard(conv);
        if (conv.is_pinned) {
          hasPinned = true;
          pinnedList.appendChild(card);
        } else {
          recentList.appendChild(card);
        }
      });

      pinnedSection.style.display = hasPinned ? "block" : "none";
    } catch (err) {
      console.log("Error loading conversations:", err);
    }
  }

  window.loadConversations = loadConversations;

  // -------------------------------------------------------------
  // Create Conversation Card Element
  // -------------------------------------------------------------
  function createConversationCard(conv) {
    var card = document.createElement("div");
    card.className = "conv-card" + (conv.id === activeConversationId ? " active" : "");
    card.setAttribute("data-id", conv.id);

    var pinBadge = conv.is_pinned ? `<i class="bi bi-pin-angle-fill conv-pin-badge" title="Pinned"></i>` : "";
    var formattedTime = formatCardTimestamp(conv.last_message_time || conv.updated_at);
    var previewText = conv.last_message || "No messages yet";

    card.innerHTML = `
      <div class="conv-card-header">
        <div class="conv-card-title-group">
          <i class="bi bi-chat-text-fill conv-chat-icon"></i>
          <span class="conv-title" title="${escapeHtml(conv.title)}">${escapeHtml(conv.title)}</span>
          ${pinBadge}
        </div>
        <button class="conv-menu-btn" title="Options" data-id="${conv.id}">
          <i class="bi bi-three-dots-vertical"></i>
        </button>
      </div>
      <div class="conv-card-meta">
        <div class="conv-preview">${escapeHtml(previewText)}</div>
        <div class="conv-time">${formattedTime}</div>
      </div>
      <div class="conv-dropdown-menu" id="menu-${conv.id}">
        <div class="conv-menu-item btn-pin-conv" data-id="${conv.id}">
          <i class="bi ${conv.is_pinned ? "bi-pin-angle" : "bi-pin-angle-fill"}"></i>
          <span>${conv.is_pinned ? "Unpin Chat" : "Pin to Top"}</span>
        </div>
        <div class="conv-menu-item btn-rename-conv" data-id="${conv.id}" data-title="${escapeHtml(conv.title)}">
          <i class="bi bi-pencil-square"></i>
          <span>Rename</span>
        </div>
        <div class="conv-menu-item danger-item btn-delete-conv" data-id="${conv.id}" data-title="${escapeHtml(conv.title)}">
          <i class="bi bi-trash3"></i>
          <span>Delete</span>
        </div>
      </div>
    `;

    // Click Card to Select Conversation
    card.addEventListener("click", function (e) {
      if ($(e.target).closest(".conv-menu-btn").length || $(e.target).closest(".conv-dropdown-menu").length) {
        return;
      }
      switchActiveConversation(conv.id, conv.title);
    });

    // Options Menu Button Click
    var menuBtn = card.querySelector(".conv-menu-btn");
    menuBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      $(".conv-dropdown-menu").not(`#menu-${conv.id}`).removeClass("show");
      $(`#menu-${conv.id}`).toggleClass("show");
    });

    return card;
  }

  // Close dropdowns on outside click
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".conv-menu-btn").length && !$(e.target).closest(".conv-dropdown-menu").length) {
      $(".conv-dropdown-menu").removeClass("show");
    }
  });

  // -------------------------------------------------------------
  // Switch Active Conversation
  // -------------------------------------------------------------
  async function switchActiveConversation(convId, convTitle) {
    if (activeConversationId === convId) return;

    activeConversationId = convId;
    $(".conv-card").removeClass("active");
    $(`.conv-card[data-id="${convId}"]`).addClass("active");

    if (convTitle) {
      $("#active-conv-title").text(convTitle);
    }

    try {
      if (typeof eel !== "undefined" && eel.setActiveConversation) {
        await eel.setActiveConversation(convId)();
      }
    } catch (e) {
      console.log("Error setting active conv:", e);
    }

    await loadConversationMessages(convId);

    // Close mobile drawer if open
    $("#sidebar").removeClass("open");
    $("#sidebar-backdrop").removeClass("show");
  }

  // -------------------------------------------------------------
  // Load Messages for a Specific Conversation
  // -------------------------------------------------------------
  async function loadConversationMessages(convId) {
    var chatBox = document.getElementById("chat-canvas-body");
    chatBox.innerHTML = "";

    if (typeof eel === "undefined" || !eel.getMessages) return;

    try {
      var messages = await eel.getMessages(convId)();

      if (!messages || messages.length === 0) {
        // Show idle visual orb if empty
        $("#Oval").attr("hidden", false);
        return;
      }

      // Hide idle orb when chat has active history
      $("#Oval").attr("hidden", true);
      $("#Start").attr("hidden", true);

      messages.forEach(function (msg) {
        var isUser = msg.sender === "user";
        var timeStr = formatMessageTimestamp(msg.timestamp);

        var msgHtml = `
          <div class="message-row ${isUser ? "user-row" : "assistant-row"}">
            <div class="message-bubble ${isUser ? "user-bubble" : "assistant-bubble"}">
              <div class="message-content">${escapeHtml(msg.transcription)}</div>
              <div class="message-meta">
                ${!isUser ? '<i class="bi bi-robot me-1 text-info"></i>' : ''}
                ${msg.is_priority_memory ? '<span class="memory-tag"><i class="bi bi-star-fill"></i> Saved</span>' : ''}
                ${timeStr}
              </div>
            </div>
          </div>
        `;
        chatBox.innerHTML += msgHtml;
      });

      scrollToBottom();
    } catch (err) {
      console.log("Error loading messages:", err);
    }
  }

  // -------------------------------------------------------------
  // Create New Chat (+ New Chat Button)
  // -------------------------------------------------------------
  $("#btn-new-chat").click(async function () {
    if (typeof eel === "undefined" || !eel.createConversation) return;

    try {
      var res = await eel.createConversation("New Conversation")();
      if (res && res.id) {
        activeConversationId = res.id;
        $("#active-conv-title").text("New Conversation");
        $("#chat-canvas-body").html("");
        $("#Oval").attr("hidden", false);
        await loadConversations();
        $("#chatbox").val("").focus();
        
        // Close mobile sidebar
        $("#sidebar").removeClass("open");
        $("#sidebar-backdrop").removeClass("show");
      }
    } catch (e) {
      console.log("Error creating new chat:", e);
    }
  });

  // Shortcut Ctrl+N / Cmd+N for New Chat
  $(document).keydown(function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "n") {
      e.preventDefault();
      $("#btn-new-chat").click();
    }
  });

  // -------------------------------------------------------------
  // Search Filter
  // -------------------------------------------------------------
  $("#search-conversations").on("input", function () {
    var val = $(this).val();
    if (val.length > 0) {
      $("#clear-search-btn").show();
    } else {
      $("#clear-search-btn").hide();
    }
    loadConversations(val);
  });

  $("#clear-search-btn").click(function () {
    $("#search-conversations").val("");
    $(this).hide();
    loadConversations("");
  });

  // -------------------------------------------------------------
  // Pin / Unpin Conversation
  // -------------------------------------------------------------
  $(document).on("click", ".btn-pin-conv", async function (e) {
    e.stopPropagation();
    var convId = $(this).data("id");
    $(".conv-dropdown-menu").removeClass("show");
    if (typeof eel !== "undefined" && eel.togglePinConversation) {
      await eel.togglePinConversation(convId)();
      await loadConversations();
    }
  });

  // -------------------------------------------------------------
  // Rename Conversation Modal & Action
  // -------------------------------------------------------------
  $(document).on("click", ".btn-rename-conv", function (e) {
    e.stopPropagation();
    targetConversationIdForAction = $(this).data("id");
    var currentTitle = $(this).data("title") || "";
    $(".conv-dropdown-menu").removeClass("show");

    $("#rename-input").val(currentTitle);
    $("#rename-modal").fadeIn(150);
    $("#rename-input").focus().select();
  });

  $("#rename-modal-close, #rename-cancel-btn").click(function () {
    $("#rename-modal").fadeOut(150);
    targetConversationIdForAction = null;
  });

  $("#rename-save-btn").click(async function () {
    var newTitle = $("#rename-input").val().trim();
    if (!newTitle || !targetConversationIdForAction) return;

    if (typeof eel !== "undefined" && eel.renameConversation) {
      await eel.renameConversation(targetConversationIdForAction, newTitle)();
      if (activeConversationId === targetConversationIdForAction) {
        $("#active-conv-title").text(newTitle);
      }
      await loadConversations();
    }
    $("#rename-modal").fadeOut(150);
    targetConversationIdForAction = null;
  });

  $("#rename-input").keypress(function (e) {
    if (e.which === 13) {
      $("#rename-save-btn").click();
    }
  });

  // -------------------------------------------------------------
  // Delete Conversation Modal & Action
  // -------------------------------------------------------------
  $(document).on("click", ".btn-delete-conv", function (e) {
    e.stopPropagation();
    targetConversationIdForAction = $(this).data("id");
    var currentTitle = $(this).data("title") || "this conversation";
    $(".conv-dropdown-menu").removeClass("show");

    $("#delete-conv-title-preview").text(`"${currentTitle}"`);
    $("#delete-modal").fadeIn(150);
  });

  $("#delete-modal-close, #delete-cancel-btn").click(function () {
    $("#delete-modal").fadeOut(150);
    targetConversationIdForAction = null;
  });

  $("#delete-confirm-btn").click(async function () {
    if (!targetConversationIdForAction) return;

    if (typeof eel !== "undefined" && eel.deleteConversation) {
      var res = await eel.deleteConversation(targetConversationIdForAction)();
      if (res && res.active_id) {
        activeConversationId = res.active_id;
      }
      await loadConversations();
      if (activeConversationId) {
        await loadConversationMessages(activeConversationId);
      } else {
        $("#chat-canvas-body").html("");
        $("#Oval").attr("hidden", false);
      }
    }
    $("#delete-modal").fadeOut(150);
    targetConversationIdForAction = null;
  });

  // -------------------------------------------------------------
  // Top Navbar Action: Clear Current View
  // -------------------------------------------------------------
  $("#btn-clear-chat").click(function () {
    $("#btn-new-chat").click();
  });

  // -------------------------------------------------------------
  // Sidebar Responsive Drawer Toggle
  // -------------------------------------------------------------
  $("#sidebar-toggle").click(function () {
    $("#sidebar").toggleClass("open");
    $("#sidebar-backdrop").toggleClass("show");
  });

  $("#close-sidebar-btn, #sidebar-backdrop").click(function () {
    $("#sidebar").removeClass("open");
    $("#sidebar-backdrop").removeClass("show");
  });

  // -------------------------------------------------------------
  // Voice Command & Text Input Handlers
  // -------------------------------------------------------------
  $("#MicBtn").click(function () {
    if (typeof eel !== "undefined") {
      eel.play_assistant_sound();
    }
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);

    if (typeof eel !== "undefined" && eel.takeAllCommands) {
      eel.takeAllCommands()();
    }
  });

  // Shortcut Win+J / Meta+J for Voice Command
  function doc_keyUp(e) {
    if (e.key === "j" && (e.metaKey || e.altKey)) {
      if (typeof eel !== "undefined") {
        eel.play_assistant_sound();
      }
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      if (typeof eel !== "undefined" && eel.takeAllCommands) {
        eel.takeAllCommands()();
      }
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  function PlayAssistant(message) {
    if (message && message.trim() !== "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);

      if (typeof eel !== "undefined" && eel.takeAllCommands) {
        eel.takeAllCommands(message);
      }
      $("#chatbox").val("");
      ShowHideButton("");
    }
  }

  function ShowHideButton(message) {
    if (!message || message.length === 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").on("input keyup", function () {
    var message = $(this).val().trim();
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    var message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    if (e.which === 13) {
      var message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });

  // -------------------------------------------------------------
  // Date/Time Formatting Utilities
  // -------------------------------------------------------------
  function formatCardTimestamp(dateStr) {
    if (!dateStr) return "";
    try {
      var d = new Date(dateStr.replace(/-/g, "/"));
      var now = new Date();
      if (isNaN(d.getTime())) return dateStr;

      var isToday = d.toDateString() === now.toDateString();
      if (isToday) {
        var hrs = d.getHours();
        var mins = d.getMinutes();
        var ampm = hrs >= 12 ? "PM" : "AM";
        hrs = hrs % 12 || 12;
        mins = mins < 10 ? "0" + mins : mins;
        return hrs + ":" + mins + " " + ampm;
      }

      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      return months[d.getMonth()] + " " + d.getDate();
    } catch (e) {
      return dateStr;
    }
  }

  function formatMessageTimestamp(dateStr) {
    if (!dateStr) return window.formatCurrentTime ? window.formatCurrentTime() : "";
    try {
      var d = new Date(dateStr.replace(/-/g, "/"));
      if (isNaN(d.getTime())) return dateStr;
      var hrs = d.getHours();
      var mins = d.getMinutes();
      var ampm = hrs >= 12 ? "PM" : "AM";
      hrs = hrs % 12 || 12;
      mins = mins < 10 ? "0" + mins : mins;
      return hrs + ":" + mins + " " + ampm;
    } catch (e) {
      return dateStr;
    }
  }

  function escapeHtml(text) {
    var map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text || "").replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  function scrollToBottom() {
    var viewport = document.getElementById("chat-viewport");
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }
});
