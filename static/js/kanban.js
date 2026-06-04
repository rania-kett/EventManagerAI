(function () {
    "use strict";
    var board = document.getElementById("kanbanBoard");
    var toast = document.getElementById("kanbanToast");
    var urlTemplate = window.KANBAN_STATUS_URL_TEMPLATE;
    if (!board || !urlTemplate) return;

    var draggedCard = null;
    var sourceZone = null;

    function statusUrl(id) { return urlTemplate.replace("/0/", "/" + id + "/"); }
    function showToast(msg, err) {
        if (!toast) return;
        toast.textContent = msg;
        toast.className = "kanban-toast is-visible" + (err ? " is-error" : "");
        clearTimeout(showToast._t);
        showToast._t = setTimeout(function () { toast.classList.remove("is-visible"); }, 2800);
    }
    function updateCounts() {
        board.querySelectorAll(".kanban-column").forEach(function (col) {
            var b = col.querySelector(".kanban-count");
            if (b) b.textContent = col.querySelectorAll(".kanban-card").length;
        });
    }

    board.querySelectorAll(".kanban-card").forEach(function (card) {
        card.addEventListener("dragstart", function (e) {
            draggedCard = card;
            sourceZone = card.closest(".kanban-column-body");
            card.classList.add("is-dragging");
            e.dataTransfer.setData("text/plain", card.getAttribute("data-event-id"));
        });
        card.addEventListener("dragend", function () {
            card.classList.remove("is-dragging");
            board.querySelectorAll(".kanban-column-body").forEach(function (z) { z.classList.remove("is-drag-over"); });
        });
    });

    board.querySelectorAll(".kanban-column-body").forEach(function (zone) {
        zone.addEventListener("dragover", function (e) { e.preventDefault(); zone.classList.add("is-drag-over"); });
        zone.addEventListener("dragleave", function () { zone.classList.remove("is-drag-over"); });
        zone.addEventListener("drop", function (e) {
            e.preventDefault();
            zone.classList.remove("is-drag-over");
            if (!draggedCard) return;
            var newStatus = zone.getAttribute("data-drop-zone");
            if (newStatus === draggedCard.getAttribute("data-status")) return;
            var eventId = draggedCard.getAttribute("data-event-id");
            zone.appendChild(draggedCard);
            updateCounts();
            draggedCard.classList.add("is-saving");
            fetch(statusUrl(eventId), {
                method: "PATCH",
                headers: { "Content-Type": "application/json", Accept: "application/json" },
                body: JSON.stringify({ status: newStatus }),
            })
                .then(function (r) { return r.json().then(function (d) { if (!r.ok) throw new Error(d.message); return d; }); })
                .then(function (d) {
                    var badge = draggedCard.querySelector(".kanban-status-badge");
                    if (badge) { badge.className = "kanban-status-badge status-" + d.status; badge.textContent = d.status_label; }
                    draggedCard.setAttribute("data-status", d.status);
                    showToast("Statut mis à jour : " + d.status_label, false);
                })
                .catch(function () {
                    if (sourceZone) sourceZone.appendChild(draggedCard);
                    updateCounts();
                    showToast("Impossible de mettre à jour le statut.", true);
                })
                .finally(function () { draggedCard.classList.remove("is-saving"); draggedCard = null; sourceZone = null; });
        });
    });
})();
