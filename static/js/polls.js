"use strict";
// Lecturer-only read polling. No vote retries or generation/provider calls.
(() => {
    const config = document.getElementById("poll-config");
    if (!config) return;
    const status = document.getElementById("poll-refresh-status");
    let timer, controller, stopped = false;
    const text = (tag, value) => { const node = document.createElement(tag); node.textContent = value; return node; };
    async function refresh() {
        if (document.hidden || stopped || controller) return;
        controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 8000);
        try {
            const response = await fetch(config.dataset.url, {cache:"no-store", signal:controller.signal});
            if (response.redirected || response.status === 403 || response.status === 404) {
                stopped = true;
                throw new Error("Access changed. Reload and sign in again if needed.");
            }
            if (!response.ok) throw new Error("Could not refresh; displayed results may be outdated.");
            const data = await response.json();
            if (document.getElementById("poll-status").textContent !== data.status) {
                status.textContent = "Poll status changed. Reload to update the available actions.";
                stopped = true;
                return;
            }
            const body = document.getElementById("poll-results");
            if (body && data.show_results) {
                document.getElementById("poll-respondents").textContent = `Responses: ${data.respondent_count}`;
                body.replaceChildren(...data.results.map(row => {
                    const tr = document.createElement("tr");
                    const label = text("td", row.text); label.dir = "auto";
                    tr.append(label, text("td", row.count), text("td", `${row.percent}%`)); return tr;
                }));
            }
            status.textContent = `Updated ${new Date().toLocaleTimeString()}.`;
        } catch (error) {
            if (!document.hidden) status.textContent = error.name === "AbortError" ? "Refresh timed out; results may be outdated." : error.message;
        } finally {
            clearTimeout(timeout); controller = null;
            if (!document.hidden && !stopped) timer = setTimeout(refresh, 5000);
        }
    }
    document.addEventListener("visibilitychange", () => {
        clearTimeout(timer);
        if (document.hidden) { if (controller) controller.abort(); }
        else refresh();
    });
    refresh();
})();
