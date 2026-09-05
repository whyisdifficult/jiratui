function showCopiedState(btn) {
    btn.classList.add("copied");
    setTimeout(function () {
      btn.classList.remove("copied");
    }, 2000);
  }

  function fallbackCopyText(text, btn) {
    var textarea = document.createElement("textarea");
    var copied = false;

    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);

    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);

    try {
      copied = document.execCommand("copy");
    } catch (e) {
      copied = false;
    }

    document.body.removeChild(textarea);

    if (copied) {
      showCopiedState(btn);
      return;
    }

    window.prompt("Copy this command manually:", text);
  }

// handle the copy button for selecting install commands
document.querySelectorAll(".install-cta-copy").forEach(function (btn) {
   btn.addEventListener("click", function () {
      var command = btn.getAttribute("data-command");
      if (!command) return;

      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
         navigator.clipboard.writeText(command).then(function () {
            showCopiedState(btn);
         }).catch(function () {
            fallbackCopyText(command, btn);
         });
         return;
      }

      fallbackCopyText(command, btn);
    });
});

// build and handle the dropdown with the installation comands
document.querySelectorAll(".install-widget").forEach(function (widget) {
   var dropdown = widget.querySelector(".install-method-dropdown");
   if (!dropdown) return;

   var commandEl = widget.querySelector(".install-command");
   var copyBtn = widget.querySelector(".install-cta-copy");
   var label = widget.querySelector(".install-method-label");

   // Command options (buttons with data-command) — show command + Copy
   dropdown.querySelectorAll("button.install-option[data-command]").forEach(function (option) {
      option.addEventListener("click", function (e) {
         e.preventDefault();
         var command = option.getAttribute("data-command");
         console.log(command);
         commandEl.textContent = command;
         commandEl.classList.remove("d-none");
         copyBtn.setAttribute("data-command", command);
         copyBtn.classList.remove("d-none");
         //downloadBtn.classList.add("d-none");
         label.textContent = option.getAttribute("data-label");
         dropdown.removeAttribute("open");
      });
   });
});
