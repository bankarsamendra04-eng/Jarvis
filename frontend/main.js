$(document).ready(function () {
  if (typeof eel !== "undefined" && eel.init) {
    try {
      eel.init()();
    } catch (err) {
      console.log("Eel init notice:", err);
    }
  }
  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

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

  function doc_keyUp(e) {
    if (e.key === "j" && e.metaKey) {
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
    if (message != "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      if (typeof eel !== "undefined" && eel.takeAllCommands) {
        eel.takeAllCommands(message);
      }
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  function ShowHideButton(message) {
    if (message.length == 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    console.log("Current chatbox input: ", message); // Log input value for debugging
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    key = e.which;
    if (key == 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });
});
