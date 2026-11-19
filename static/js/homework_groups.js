/* Status-only reads; no generation, edit or publication requests. */
(function () {
  'use strict';
  const config = document.getElementById('group-config');
  if (!config) return;
  let pending = config.dataset.pending === 'true', timer = null, request = null;
  function text(id, value) { const node = document.getElementById(id); if (node) node.textContent = String(value); }
  function cancel() { clearTimeout(timer); if (request) request.abort(); }
  async function refresh() {
    if (!pending || document.hidden || request) return;
    const controller = new AbortController(); request = controller;
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(config.dataset.url, {credentials: 'same-origin', signal: controller.signal});
      if (!response.ok || response.redirected) {
        if (response.status === 403 || response.status === 404 || response.redirected) pending = false;
        throw new Error('Status unavailable');
      }
      const state = await response.json();
      for (const row of state.rows) {
        text('group-status-' + row.id, row.label); text('group-comparison-' + row.id, row.comparison);
        text('group-reason-' + row.id, row.reason); text('group-elapsed-' + row.id, row.elapsed);
      }
      text('group-progress', `${state.finished} / ${state.total} processed. ${state.ready} drafts produced, including ${state.partial} with failed comparison. ${state.failed} failed.`);
      pending = state.pending;
      text('group-refresh', pending ? 'Updates every 5 seconds while this page is visible.' : 'Processing finished. Review and publish each draft separately.');
    } catch (_) {
      if (!document.hidden) text('group-refresh', 'Status could not be refreshed. No new processing was requested. Refresh the page if needed.');
    } finally {
      clearTimeout(timeout); request = null;
      if (pending && !document.hidden) timer = setTimeout(refresh, 5000);
    }
  }
  document.addEventListener('visibilitychange', () => { cancel(); if (!document.hidden) refresh(); });
  if (pending) refresh();
}());
