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
  // MEMORY VAULT MANAGEMENT UI LOGIC
  // -------------------------------------------------------------
  var activeCategoryFilter = "All";
  var targetMemoryIdForAction = null;

  async function updateMemoryBadge() {
    if (typeof eel === "undefined" || !eel.getMemoryStats) return;
    try {
      var stats = await eel.getMemoryStats()();
      if (stats && typeof stats.total_memories !== "undefined") {
        $("#memory-counter-badge").text(stats.total_memories);
      }
    } catch (e) {
      console.log("Error updating memory badge:", e);
    }
  }

  async function loadMemoryVault(searchQuery, categoryFilter) {
    if (typeof eel === "undefined" || !eel.getAllMemories) return;

    var cat = categoryFilter || activeCategoryFilter || "All";
    var query = searchQuery || $("#search-memory-vault").val() || "";

    try {
      var memories = await eel.getAllMemories(query, cat)();
      var container = document.getElementById("memory-cards-grid");
      container.innerHTML = "";

      if (!memories || memories.length === 0) {
        container.innerHTML = `
          <div class="col-12 text-center py-4 text-muted">
            <i class="bi bi-cpu fs-2 mb-2 d-block opacity-50"></i>
            <p class="small mb-0">No memory records found in this category.</p>
          </div>
        `;
        return;
      }

      $("#count-cat-all").text(memories.length);

      memories.forEach(function (mem) {
        var card = document.createElement("div");
        card.className = "memory-card";
        card.setAttribute("data-id", mem.id);

        var sensBadge = mem.is_sensitive ? `<span class="badge bg-warning-subtle text-warning border border-warning-subtle small ms-1"><i class="bi bi-lock-fill"></i> Private</span>` : "";
        var timeStr = formatCardTimestamp(mem.updated_at || mem.created_at);

        card.innerHTML = `
          <div class="memory-card-header">
            <div>
              <span class="memory-category-badge badge-cat-${escapeHtml(mem.category)}">${escapeHtml(mem.category)}</span>
              ${sensBadge}
            </div>
            <div class="memory-card-actions">
              <button class="btn-mem-action btn-edit-memory" title="Edit Memory" data-id="${mem.id}" data-cat="${escapeHtml(mem.category)}" data-content="${escapeHtml(mem.content)}" data-sensitive="${mem.is_sensitive}">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn-mem-action btn-mem-delete btn-delete-memory" title="Delete Memory" data-id="${mem.id}">
                <i class="bi bi-trash3"></i>
              </button>
            </div>
          </div>
          <div class="memory-card-content">${escapeHtml(mem.content)}</div>
          <div class="memory-card-footer">
            <span><i class="bi bi-clock me-1"></i> ${timeStr}</span>
            <span class="text-muted">${escapeHtml(mem.source || 'user')}</span>
          </div>
        `;

        container.appendChild(card);
      });
    } catch (e) {
      console.log("Error loading memory vault:", e);
    }
  }

  // Open Memory Vault
  $("#btn-open-memory-vault").click(function () {
    activeCategoryFilter = "All";
    $(".cat-tab").removeClass("active");
    $('.cat-tab[data-cat="All"]').addClass("active");
    $("#search-memory-vault").val("");
    loadMemoryVault();
    $("#memory-vault-modal").fadeIn(150);
  });

  $("#memory-vault-close, #memory-vault-done-btn").click(function () {
    $("#memory-vault-modal").fadeOut(150);
  });

  // Category Tab Filter
  $(document).on("click", ".cat-tab", function () {
    $(".cat-tab").removeClass("active");
    $(this).addClass("active");
    activeCategoryFilter = $(this).data("cat");
    loadMemoryVault(null, activeCategoryFilter);
  });

  // Memory Search Input
  $("#search-memory-vault").on("input", function () {
    var val = $(this).val();
    loadMemoryVault(val, activeCategoryFilter);
  });

  // Open Add Memory Modal
  $("#btn-open-add-memory").click(function () {
    targetMemoryIdForAction = null;
    $("#memory-form-id").val("");
    $("#memory-form-title").html('<i class="bi bi-plus-circle-fill text-info"></i> Add New Memory');
    $("#memory-form-category").val(activeCategoryFilter !== "All" ? activeCategoryFilter : "Profile");
    $("#memory-form-content").val("");
    $("#memory-form-sensitive").prop("checked", false);
    $("#memory-security-warning").hide().text("");
    $("#memory-form-modal").fadeIn(150);
    $("#memory-form-content").focus();
  });

  // Open Edit Memory Modal
  $(document).on("click", ".btn-edit-memory", function () {
    targetMemoryIdForAction = $(this).data("id");
    var cat = $(this).data("cat");
    var content = $(this).data("content");
    var isSensitive = $(this).data("sensitive");

    $("#memory-form-id").val(targetMemoryIdForAction);
    $("#memory-form-title").html('<i class="bi bi-pencil-square text-info"></i> Edit Memory');
    $("#memory-form-category").val(cat);
    $("#memory-form-content").val(content);
    $("#memory-form-sensitive").prop("checked", isSensitive === true || isSensitive === "true");
    $("#memory-security-warning").hide().text("");
    $("#memory-form-modal").fadeIn(150);
    $("#memory-form-content").focus();
  });

  $("#memory-form-close, #memory-form-cancel").click(function () {
    $("#memory-form-modal").fadeOut(150);
    targetMemoryIdForAction = null;
  });

  // Save Memory (Add or Update)
  $("#memory-form-save").click(async function () {
    var memId = $("#memory-form-id").val();
    var cat = $("#memory-form-category").val();
    var content = $("#memory-form-content").val().trim();
    var isSensitive = $("#memory-form-sensitive").is(":checked");

    if (!content) {
      $("#memory-security-warning").text("Please enter memory content.").show();
      return;
    }

    // Client-side quick security warning
    if (/(?:password|otp|pin|cvv|secret\s*key|api\s*key)\s*(?:is|:|=)/i.test(content)) {
      $("#memory-security-warning").text("Security Notice: Passwords, OTPs, and API credentials cannot be stored.").show();
      return;
    }

    if (memId) {
      // Update Memory
      if (typeof eel !== "undefined" && eel.updateMemory) {
        var res = await eel.updateMemory(memId, cat, content, isSensitive)();
        if (res && res.status === "blocked") {
          $("#memory-security-warning").text(res.message).show();
          return;
        }
      }
    } else {
      // Add Memory
      if (typeof eel !== "undefined" && eel.addMemory) {
        var res = await eel.addMemory(cat, content, isSensitive)();
        if (res && res.status === "blocked") {
          $("#memory-security-warning").text(res.message).show();
          return;
        }
      }
    }

    $("#memory-form-modal").fadeOut(150);
    await loadMemoryVault();
    await updateMemoryBadge();
  });

  // Delete Memory Action
  $(document).on("click", ".btn-delete-memory", async function () {
    var memId = $(this).data("id");
    if (!memId) return;

    if (confirm("Are you sure you want to permanently delete this memory record?")) {
      if (typeof eel !== "undefined" && eel.deleteMemory) {
        await eel.deleteMemory(memId)();
        await loadMemoryVault();
        await updateMemoryBadge();
      }
    }
  });

  // Initial memory badge update
  updateMemoryBadge();

  // =============================================================
  // PERSONAL GOAL & PROGRESS TRACKING SYSTEM
  // =============================================================
  var currentGoalsCategoryFilter = "All";
  var currentGoalForAction = null;

  async function updateGoalsBadge() {
    if (typeof eel === "undefined" || !eel.getGoalsStats) return;
    try {
      var stats = await eel.getGoalsStats()();
      if (stats) {
        $("#goals-counter-badge").text(stats.active_goals || 0);
        $("#count-goals-all").text(stats.active_goals + stats.completed_goals || 0);
        $("#stat-active-goals").text(stats.active_goals || 0);
        $("#stat-completed-goals").text(stats.completed_goals || 0);
        $("#stat-avg-progress").text((stats.avg_progress || 0) + "%");
        
        if (stats.closest_goal) {
          $("#stat-closest-goal").text(stats.closest_goal.name + " (" + stats.closest_goal.progress + "%)");
        } else {
          $("#stat-closest-goal").text("None");
        }
      }
    } catch (e) {
      console.log("Error updating goals badge:", e);
    }
  }

  async function loadDailyActionPlan() {
    if (typeof eel === "undefined" || !eel.generateDailyActionPlan) return;
    try {
      var plan = await eel.generateDailyActionPlan()();
      if (!plan) return;

      $("#action-plan-date").text(plan.date || "Today");
      $("#action-plan-summary").text(plan.summary || "Daily action plan based on your active goals.");

      var container = document.getElementById("daily-action-tasks-list");
      container.innerHTML = "";

      if (!plan.tasks || plan.tasks.length === 0) {
        container.innerHTML = '<div class="text-muted small py-2">No pending tasks for today! Great job or create a new goal.</div>';
        return;
      }

      plan.tasks.forEach(function (t) {
        var card = document.createElement("div");
        card.className = "action-task-card priority-" + (t.priority || "Medium");
        card.innerHTML = `
          <div class="action-task-title">${escapeHtml(t.task)}</div>
          <div class="action-task-meta">
            <span class="action-task-goal" title="${escapeHtml(t.goal_name)}"><i class="bi bi-flag-fill"></i> ${escapeHtml(t.goal_name)}</span>
            <span class="action-task-est"><i class="bi bi-stopwatch"></i> ${escapeHtml(t.est_time || "45 mins")}</span>
          </div>
        `;
        container.appendChild(card);
      });
    } catch (e) {
      console.log("Error loading daily action plan:", e);
    }
  }

  async function loadGoalsDashboard(filter, searchQuery) {
    if (typeof eel === "undefined" || !eel.getAllGoals) return;

    var filterVal = filter !== undefined ? filter : currentGoalsCategoryFilter;
    var query = searchQuery !== undefined ? searchQuery : $("#search-goals").val() || "";

    var categoryParam = null;
    var statusParam = null;

    if (filterVal === "Active") {
      statusParam = "Active";
    } else if (filterVal === "Completed") {
      statusParam = "Completed";
    } else if (filterVal !== "All") {
      categoryParam = filterVal;
    }

    try {
      var goals = await eel.getAllGoals(categoryParam, statusParam, query)();
      var grid = document.getElementById("goals-cards-grid");
      grid.innerHTML = "";

      await updateGoalsBadge();

      if (!goals || goals.length === 0) {
        grid.innerHTML = `
          <div class="col-12 text-center py-5 text-muted">
            <i class="bi bi-trophy" style="font-size: 2.5rem; opacity: 0.4;"></i>
            <p class="mt-2 mb-1" style="font-size: 0.9rem;">No goals found matching criteria</p>
            <button class="btn-add-memory mt-2" id="btn-empty-add-goal">
              <i class="bi bi-plus-circle-fill"></i> Create First Goal
            </button>
          </div>
        `;
        $("#btn-empty-add-goal").click(function () {
          $("#btn-open-add-goal").click();
        });
        return;
      }

      goals.forEach(function (g) {
        var card = createGoalCard(g);
        grid.appendChild(card);
      });
    } catch (e) {
      console.log("Error loading goals dashboard:", e);
    }
  }

  function createGoalCard(g) {
    var card = document.createElement("div");
    card.className = "goal-card" + (g.status === "Completed" ? " goal-completed" : "");
    card.id = "goal-card-" + g.id;

    var isHigh = g.priority === "High";
    var isMed = g.priority === "Medium";
    var priorityClass = "priority-" + (g.priority || "Medium");
    var statusClass = "status-" + (g.status === "On Hold" ? "OnHold" : (g.status || "Active"));

    // Deadline badge
    var deadlineHtml = "";
    if (g.deadline) {
      deadlineHtml = `<div class="goal-deadline-chip"><i class="bi bi-calendar-event"></i> Due ${escapeHtml(g.deadline)}</div>`;
    }

    // Milestones list
    var milestones = g.milestones || [];
    var milestonesHtml = "";
    if (milestones.length > 0) {
      var msItems = milestones.map(function (m) {
        var isChecked = m.completed ? "checked" : "";
        var titleClass = m.completed ? "milestone-title-text completed" : "milestone-title-text";
        return `
          <label class="milestone-item">
            <input type="checkbox" class="milestone-chk btn-toggle-milestone" data-goal-id="${g.id}" data-milestone-id="${m.id}" ${isChecked} />
            <span class="${titleClass}">${escapeHtml(m.title)}</span>
          </label>
        `;
      }).join("");

      var completedCount = milestones.filter(function (m) { return m.completed; }).length;
      milestonesHtml = `
        <div class="goal-milestones-box">
          <div class="goal-milestones-header">
            <span>Milestones (${completedCount}/${milestones.length})</span>
            <span class="text-cyan">${Math.round((completedCount/milestones.length)*100)}%</span>
          </div>
          ${msItems}
        </div>
      `;
    }

    // Notes
    var notesHtml = "";
    if (g.notes && g.notes.trim()) {
      notesHtml = `<div class="goal-notes-box"><i class="bi bi-journal-text text-info"></i> ${escapeHtml(g.notes)}</div>`;
    }

    // Progress bar class
    var fillClass = g.progress >= 100 ? "goal-progress-bar-fill fill-100" : "goal-progress-bar-fill";

    card.innerHTML = `
      <div class="goal-card-header">
        <div class="goal-badges-row">
          <div class="goal-badge-group">
            <span class="badge-cat-Profile badge-cat-${g.category || 'General'} memory-category-badge">${escapeHtml(g.category || "General")}</span>
            <span class="badge-priority ${priorityClass}">${escapeHtml(g.priority || "Medium")}</span>
          </div>
          <span class="badge-goal-status ${statusClass}">${escapeHtml(g.status || "Active")}</span>
        </div>
        <div class="goal-title">${escapeHtml(g.name)}</div>
        ${g.description ? `<div class="goal-desc">${escapeHtml(g.description)}</div>` : ""}
        ${deadlineHtml}
      </div>

      <div class="goal-progress-section">
        <div class="goal-progress-header">
          <span class="text-muted">Current Progress</span>
          <span class="prog-pct-label" id="prog-label-${g.id}">${g.progress}%</span>
        </div>
        <div class="goal-progress-bar-bg">
          <div class="${fillClass}" id="prog-bar-${g.id}" style="width: ${g.progress}%;"></div>
        </div>
      </div>

      ${milestonesHtml}
      ${notesHtml}

      <div class="goal-card-footer">
        <span class="text-muted"><i class="bi bi-clock"></i> Updated ${formatCardTimestamp(g.updated_at)}</span>
        <div class="goal-actions-group">
          <button class="btn-goal-action btn-edit-goal" data-goal='${escapeHtml(JSON.stringify(g))}' title="Edit Goal">
            <i class="bi bi-pencil-square"></i> Edit
          </button>
          <button class="btn-goal-action btn-goal-delete btn-delete-goal" data-id="${g.id}" title="Delete Goal">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    `;

    return card;
  }

  // Toggle Milestone Checkbox
  $(document).on("change", ".btn-toggle-milestone", async function () {
    var goalId = $(this).data("goal-id");
    var milestoneId = $(this).data("milestone-id");
    if (!goalId || !milestoneId) return;

    try {
      if (typeof eel !== "undefined" && eel.toggleMilestone) {
        var res = await eel.toggleMilestone(goalId, milestoneId)();
        if (res && res.status === "success") {
          // Refresh goal card and stats
          await loadGoalsDashboard();
          await loadDailyActionPlan();
        }
      }
    } catch (e) {
      console.log("Error toggling milestone:", e);
    }
  });

  // Open / Close Goals Dashboard Modal
  $("#btn-open-goals-vault").click(function () {
    $("#goals-dashboard-modal").fadeIn(200);
    loadDailyActionPlan();
    loadGoalsDashboard();
  });

  $("#goals-dashboard-close, #goals-dashboard-done-btn").click(function () {
    $("#goals-dashboard-modal").fadeOut(150);
  });

  // Toggle Action Plan Banner
  $("#btn-toggle-action-plan").click(function () {
    $("#daily-action-plan-container").slideToggle(200);
  });

  $("#btn-refresh-action-plan").click(function () {
    loadDailyActionPlan();
  });

  // Category & Filter Tabs
  $("#goals-category-tabs .cat-tab").click(function () {
    $("#goals-category-tabs .cat-tab").removeClass("active");
    $(this).addClass("active");
    currentGoalsCategoryFilter = $(this).data("filter");
    loadGoalsDashboard(currentGoalsCategoryFilter);
  });

  // Search Goals
  var searchGoalsTimer = null;
  $("#search-goals").on("input", function () {
    clearTimeout(searchGoalsTimer);
    var query = $(this).val();
    searchGoalsTimer = setTimeout(function () {
      loadGoalsDashboard(currentGoalsCategoryFilter, query);
    }, 250);
  });

  // Open Add Goal Form
  $("#btn-open-add-goal").click(function () {
    $("#goal-form-id").val("");
    $("#goal-form-modal-title").html('<i class="bi bi-trophy-fill text-info"></i> Create New Goal');
    $("#goal-form-name").val("");
    $("#goal-form-category").val("Learning");
    $("#goal-form-description").val("");
    $("#goal-form-deadline").val("");
    $("#goal-form-priority").val("Medium");
    $("#goal-form-status").val("Active");
    $("#goal-form-notes").val("");
    $("#goal-form-warning").hide().text("");

    // Reset milestones container with 2 default starter inputs
    var mlsContainer = document.getElementById("goal-form-milestones-list");
    mlsContainer.innerHTML = "";
    addFormMilestoneRow("Phase 1 - Fundamentals & Setup", false);
    addFormMilestoneRow("Phase 2 - Core Implementation", false);

    $("#goal-form-modal").fadeIn(150);
    $("#goal-form-name").focus();
  });

  // Open Edit Goal Form
  $(document).on("click", ".btn-edit-goal", function () {
    var goalData = $(this).attr("data-goal");
    if (!goalData) return;
    try {
      var g = JSON.parse(goalData);
      $("#goal-form-id").val(g.id);
      $("#goal-form-modal-title").html('<i class="bi bi-pencil-square text-info"></i> Edit Goal');
      $("#goal-form-name").val(g.name || "");
      $("#goal-form-category").val(g.category || "General");
      $("#goal-form-description").val(g.description || "");
      $("#goal-form-deadline").val(g.deadline || "");
      $("#goal-form-priority").val(g.priority || "Medium");
      $("#goal-form-status").val(g.status || "Active");
      $("#goal-form-notes").val(g.notes || "");
      $("#goal-form-warning").hide().text("");

      var mlsContainer = document.getElementById("goal-form-milestones-list");
      mlsContainer.innerHTML = "";
      var milestones = g.milestones || [];
      if (milestones.length > 0) {
        milestones.forEach(function (m) {
          addFormMilestoneRow(m.title, m.completed);
        });
      } else {
        addFormMilestoneRow("", false);
      }

      $("#goal-form-modal").fadeIn(150);
      $("#goal-form-name").focus();
    } catch (e) {
      console.log("Error parsing edit goal data:", e);
    }
  });

  function addFormMilestoneRow(title, isCompleted) {
    var container = document.getElementById("goal-form-milestones-list");
    var row = document.createElement("div");
    row.className = "milestone-form-row";
    row.innerHTML = `
      <input type="checkbox" class="milestone-form-chk" ${isCompleted ? "checked" : ""} title="Mark as completed" />
      <input type="text" class="modal-input milestone-form-input" style="padding: 4px 8px; font-size: 0.78rem;" placeholder="e.g. Complete chapter 1 & coding practice" value="${escapeHtml(title || "")}" />
      <button type="button" class="btn-remove-milestone" title="Remove milestone"><i class="bi bi-x-circle"></i></button>
    `;

    row.querySelector(".btn-remove-milestone").addEventListener("click", function () {
      row.remove();
    });

    container.appendChild(row);
  }

  $("#btn-add-form-milestone").click(function () {
    addFormMilestoneRow("", false);
  });

  $("#goal-form-close, #goal-form-cancel").click(function () {
    $("#goal-form-modal").fadeOut(150);
  });

  // Save Goal (Create or Update)
  $("#goal-form-save").click(async function () {
    var goalId = $("#goal-form-id").val();
    var name = $("#goal-form-name").val().trim();
    var category = $("#goal-form-category").val();
    var description = $("#goal-form-description").val().trim();
    var deadline = $("#goal-form-deadline").val();
    var priority = $("#goal-form-priority").val();
    var status = $("#goal-form-status").val();
    var notes = $("#goal-form-notes").val().trim();

    if (!name) {
      $("#goal-form-warning").text("Please enter a goal name.").show();
      return;
    }

    // Gather milestones
    var milestones = [];
    var rows = document.querySelectorAll("#goal-form-milestones-list .milestone-form-row");
    var idx = 1;
    rows.forEach(function (r) {
      var input = r.querySelector(".milestone-form-input");
      var chk = r.querySelector(".milestone-form-chk");
      var text = input ? input.value.trim() : "";
      if (text) {
        milestones.push({
          id: idx++,
          title: text,
          completed: chk ? chk.checked : false
        });
      }
    });

    var completedCount = milestones.filter(function (m) { return m.completed; }).length;
    var progress = milestones.length > 0 ? Math.round((completedCount / milestones.length) * 100) : 0;

    if (goalId) {
      // Update Goal
      if (typeof eel !== "undefined" && eel.updateGoal) {
        var res = await eel.updateGoal(goalId, name, category, description, deadline, priority, milestones, progress, status, notes)();
      }
    } else {
      // Create Goal
      if (typeof eel !== "undefined" && eel.createGoal) {
        var res = await eel.createGoal(name, category, description, deadline, priority, milestones, progress, status, notes)();
      }
    }

    $("#goal-form-modal").fadeOut(150);
    await loadGoalsDashboard();
    await loadDailyActionPlan();
    await updateGoalsBadge();
  });

  // Delete Goal
  $(document).on("click", ".btn-delete-goal", async function () {
    var goalId = $(this).data("id");
    if (!goalId) return;

    if (confirm("Are you sure you want to delete this goal and its tracking history?")) {
      if (typeof eel !== "undefined" && eel.deleteGoal) {
        await eel.deleteGoal(goalId)();
        await loadGoalsDashboard();
        await loadDailyActionPlan();
        await updateGoalsBadge();
      }
    }
  });

  // Expose methods for Eel to open modals from backend voice commands
  window.openGoalsDashboardModal = function () {
    $("#goals-dashboard-modal").fadeIn(200);
    loadDailyActionPlan();
    loadGoalsDashboard();
  };

  window.openGoalCreateModal = function () {
    $("#btn-open-add-goal").click();
  };

  if (typeof eel !== "undefined") {
    eel.expose(openGoalsDashboardModal, "openGoalsDashboard");
    eel.expose(openGoalCreateModal, "openGoalModal");
  }

  // Initial goals badge update
  updateGoalsBadge();



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
