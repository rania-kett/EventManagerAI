/**
 * main.js — Client-side behavior for EventManagerAI platform pages.
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".delete-event-form").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                var title = form.getAttribute("data-event-title") || "cet événement";
                var message =
                    "Supprimer « " + title + " » ?\n\nCette action est irréversible.";
                if (!window.confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    });
})();
