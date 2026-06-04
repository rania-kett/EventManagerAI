/**
 * ai-generate.js — Gemini description generation (add/edit forms)
 */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var buttons = document.querySelectorAll(".js-generate-description");
        if (!buttons.length) return;

        buttons.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var titleEl = document.getElementById("title");
                var descEl = document.getElementById("description");
                var statusEl = document.getElementById("aiGenerateStatus");
                var url = btn.getAttribute("data-generate-url");

                if (!titleEl || !descEl || !url) return;

                var title = titleEl.value.trim();
                if (!title) {
                    setStatus(statusEl, "Veuillez saisir un titre d'événement.", true);
                    titleEl.focus();
                    return;
                }

                var locationEl = document.getElementById("location");
                var categoryEl = document.getElementById("category");
                var dateEl = document.getElementById("date");

                btn.disabled = true;
                btn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1"></span>Génération…';
                setStatus(statusEl, "Gemini rédige votre description…", false);

                fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: JSON.stringify({
                        title: title,
                        location: locationEl ? locationEl.value.trim() : "",
                        category: categoryEl ? categoryEl.value.trim() : "",
                        date: dateEl ? dateEl.value : "",
                    }),
                })
                    .then(function (res) {
                        return res.json().then(function (data) {
                            if (!res.ok) throw new Error(data.message || "Erreur");
                            return data;
                        });
                    })
                    .then(function (data) {
                        descEl.value = data.description;
                        descEl.dispatchEvent(new Event("input", { bubbles: true }));
                        setStatus(statusEl, "Description générée avec succès.", false, true);
                    })
                    .catch(function (err) {
                        setStatus(
                            statusEl,
                            err.message || "Impossible de générer la description.",
                            true
                        );
                    })
                    .finally(function () {
                        btn.disabled = false;
                        btn.innerHTML =
                            '<i class="bi bi-stars me-1"></i>Générer la description';
                    });
            });
        });
    });

    function setStatus(el, message, isError, isSuccess) {
        if (!el) return;
        el.textContent = message;
        el.className = "ai-generate-status small mt-2";
        if (isError) el.classList.add("text-danger");
        if (isSuccess) el.classList.add("text-success");
    }
})();
