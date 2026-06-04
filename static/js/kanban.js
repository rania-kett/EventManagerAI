/**
 * kanban.js — Drag & drop + statut API pour le tableau Kanban
 */
(function () {
    "use strict";

    var TOAST_HIDE_MS = 2800;

    var board = document.getElementById("kanbanBoard");
    var toast = document.getElementById("kanbanToast");
    var urlTemplate = window.KANBAN_STATUS_URL_TEMPLATE;

    if (!board || !urlTemplate) {
        return;
    }

    var draggedCard = null;
    var sourceZone = null;

    function statusUrl(eventId) {
        return urlTemplate.replace("/0/", "/" + eventId + "/");
    }

    function showToast(message, isError) {
        if (!toast) return;
        toast.textContent = message;
        toast.classList.toggle("is-error", !!isError);
        toast.classList.add("is-visible");
        clearTimeout(showToast._timer);
        showToast._timer = setTimeout(function () {
            toast.classList.remove("is-visible");
        }, TOAST_HIDE_MS);
    }

    function updateColumnCounts() {
        board.querySelectorAll(".kanban-column").forEach(function (col) {
            var count = col.querySelectorAll(".kanban-card").length;
            var badge = col.querySelector(".kanban-count");
            if (badge) badge.textContent = count;
        });
    }

    function setCardStatusBadge(card, statusKey, statusLabel) {
        var badge = card.querySelector(".kanban-status-badge");
        if (!badge) return;
        badge.className = "kanban-status-badge status-" + statusKey;
        badge.textContent = statusLabel;
        card.setAttribute("data-status", statusKey);
    }

    board.querySelectorAll(".kanban-card").forEach(function (card) {
        card.addEventListener("dragstart", function (e) {
            draggedCard = card;
            sourceZone = card.closest(".kanban-column-body");
            card.classList.add("is-dragging");
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData("text/plain", card.getAttribute("data-event-id"));
        });

        card.addEventListener("dragend", function () {
            card.classList.remove("is-dragging");
            board.querySelectorAll(".kanban-column-body").forEach(function (z) {
                z.classList.remove("is-drag-over");
            });
        });
    });

    board.querySelectorAll(".kanban-column-body").forEach(function (zone) {
        zone.addEventListener("dragover", function (e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            zone.classList.add("is-drag-over");
        });

        zone.addEventListener("dragleave", function () {
            zone.classList.remove("is-drag-over");
        });

        zone.addEventListener("drop", function (e) {
            e.preventDefault();
            zone.classList.remove("is-drag-over");

            if (!draggedCard) return;

            var newStatus = zone.getAttribute("data-drop-zone");
            var eventId = draggedCard.getAttribute("data-event-id");
            var oldStatus = draggedCard.getAttribute("data-status");

            if (newStatus === oldStatus) {
                return;
            }

            zone.appendChild(draggedCard);
            updateColumnCounts();
            draggedCard.classList.add("is-saving");

            fetch(statusUrl(eventId), {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify({ status: newStatus }),
            })
                .then(function (res) {
                    return res.json().then(function (data) {
                        if (!res.ok) throw new Error(data.message || "Update failed");
                        return data;
                    });
                })
                .then(function (data) {
                    setCardStatusBadge(draggedCard, data.status, data.status_label);
                    showToast("Statut mis à jour : " + data.status_label);
                })
                .catch(function () {
                    if (sourceZone) sourceZone.appendChild(draggedCard);
                    updateColumnCounts();
                    showToast("Impossible de mettre à jour le statut.", true);
                })
                .finally(function () {
                    draggedCard.classList.remove("is-saving");
                    draggedCard = null;
                    sourceZone = null;
                });
        });
    });
})();
