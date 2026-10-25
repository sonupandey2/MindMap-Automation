/**
 * app.js — Shared client-side utilities.
 */

// ── Delete Confirmation & Flash Dismiss ────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Attach confirmation to any form or link with data-confirm
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            var message = el.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-dismiss flash alerts after 5 seconds
    document.querySelectorAll('.flash-container .alert').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

});


// ── Schedule Field Toggle ──────────────────────────────────
function initScheduleFields() {
    var select = document.getElementById('schedule_type');
    if (!select) return;

    function toggle() {
        var selected = select.value;
        document.querySelectorAll('.schedule-group').forEach(function (group) {
            var match = group.getAttribute('data-schedule') === selected;
            group.style.display = match ? 'block' : 'none';

            // Disable hidden inputs so they don't submit stale values
            group.querySelectorAll('input, select').forEach(function (input) {
                input.disabled = !match;
            });
        });
    }

    select.addEventListener('change', toggle);
    toggle(); // run on page load to show the right group
}
