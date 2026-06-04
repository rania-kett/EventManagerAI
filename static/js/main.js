/**
 * main.js — Client-side behavior for EventManagerAI platform pages.
 */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var modalEl = document.getElementById("deleteEventConfirmModal");
        if (!modalEl) {
            return;
        }

        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        var titleEl = document.getElementById("deleteEventConfirmTitle");
        var confirmBtn = document.getElementById("deleteEventConfirmBtn");
        var pendingForm = null;

        confirmBtn.addEventListener("click", function () {
            if (!pendingForm) {
                return;
            }
            var form = pendingForm;
            pendingForm = null;
            modal.hide();
            form.submit();
        });

        modalEl.addEventListener("hidden.bs.modal", function () {
            pendingForm = null;
        });

        document.querySelectorAll(".delete-event-form").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                var title = form.getAttribute("data-event-title") || "cet événement";
                if (titleEl) {
                    titleEl.textContent = "\u00AB " + title + " \u00BB";
                }
                pendingForm = form;
                modal.show();
            });
        });
    });
})();
