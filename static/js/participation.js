"use strict";
// Polling reads only. No browser persistence, offline queue or automatic POST retry.
(() => {
    const config = document.getElementById("participation-config");
    if (!config) return;
    const status = document.getElementById("refresh-status");
    let timer, controller, countdown, stopped = false;
    const cell = (tag, text) => {
        const element = document.createElement(tag);
        element.textContent = text;
        return element;
    };
    function display(data) {
        if (config.dataset.mode === "requests") {
            const history = document.getElementById("request-history");
            const nodes = data.rows.map(row => {
                const article = cell("article", "");
                article.className = "request-card";
                article.append(cell("h3", `${row.kind} · ${row.author} (${row.username})`),
                    cell("p", `${row.created_at} · Asia/Jerusalem`));
                const text = cell("p", row.text);
                text.className = "request-text";
                text.dir = "auto";
                article.append(text);
                return article;
            });
            history.replaceChildren(...(nodes.length ? nodes : [cell("p", "No requests yet.")]));
        } else {
            const body = document.getElementById("participation-rows");
            body.replaceChildren(...data.rows.map(row => {
                const tr = document.createElement("tr");
                tr.append(...row.map(value => cell("td", value)));
                return tr;
            }));
            const image = document.getElementById("attendance-qr");
            const link = document.getElementById("scan-link");
            const windowStatus = document.getElementById("window-status");
            clearInterval(countdown);
            image.hidden = link.hidden = !data.window;
            if (data.window) {
                image.src = data.window.qr_image;
                link.href = data.window.scan_url;
                const deadline = Date.now() + data.window.remaining * 1000;
                const tick = () => {
                    const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
                    windowStatus.textContent = `${data.window.additional ? "Additional" : "Initial"} window: ${remaining} seconds remaining.`;
                    if (!remaining) { image.hidden = link.hidden = true; clearInterval(countdown); }
                };
                tick(); countdown = setInterval(tick, 1000);
            } else windowStatus.textContent = "Registration window closed.";
        }
        status.textContent = `Updated ${new Date().toLocaleTimeString()}.`;
    }
    async function refresh() {
        if (document.hidden || stopped) return;
        controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 8000);
        let delay = 5000;
        try {
            const response = await fetch(config.dataset.url, {cache: "no-store", signal: controller.signal, headers: {Accept: "application/json"}});
            if (response.redirected || response.status === 403 || response.status === 404) {
                stopped = true;
                throw new Error("Access changed. Reload the page and sign in again if needed.");
            }
            if (!response.ok) throw new Error("Could not refresh. Previously displayed data may be outdated.");
            const data = await response.json();
            display(data);
            if (data.window) delay = Math.min(5000, Math.max(150, data.window.rotation_in * 1000 + 50));
        } catch (error) {
            if (!document.hidden) status.textContent = error.name === "AbortError" ? "Refresh timed out; displayed data may be outdated." : error.message;
        } finally {
            clearTimeout(timeout);
            controller = null;
            if (!document.hidden && !stopped) timer = setTimeout(refresh, delay);
        }
    }
    document.addEventListener("visibilitychange", () => {
        clearTimeout(timer);
        clearInterval(countdown);
        if (document.hidden) { if (controller) controller.abort(); }
        else if (!controller) refresh();
    });
    const initial = document.getElementById("initial-participation");
    if (initial) display(JSON.parse(initial.textContent));
    refresh();
})();
