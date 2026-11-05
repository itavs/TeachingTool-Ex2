// Logic-only tests: no browser, network, third-party package or DOM renderer.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function harness(mode = 'requests') {
    class Element {
        constructor() { this.children = []; this.textContent = ''; this.hidden = false; }
        append(...nodes) { this.children.push(...nodes); }
        replaceChildren(...nodes) { this.children = nodes; }
    }
    const elements = new Map();
    for (const id of ['refresh-status', 'request-history', 'participation-rows', 'attendance-qr', 'scan-link', 'window-status']) elements.set(id, new Element());
    elements.set('participation-config', {dataset: {mode, url: '/fake-feed/'}});
    const listeners = {}, timers = new Map();
    let serial = 0, calls = 0, response = {rows: [{kind: 'Comment', author: 'Example', username: 'student', created_at: 'now', text: '<script>unsafe</script>'}]};
    const document = {hidden: false, getElementById: id => elements.get(id), createElement: () => new Element(), addEventListener: (event, fn) => listeners[event] = fn};
    const context = {document, Date, JSON, Math, AbortController,
        setTimeout: (fn, delay) => { const id = ++serial; timers.set(id, {fn, delay}); return id; },
        clearTimeout: id => timers.delete(id), setInterval: () => ++serial, clearInterval: () => {},
        fetch: async () => { calls++; return {ok: true, redirected: false, status: 200, json: async () => response}; }};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/js/participation.js'), 'utf8'), context);
    return {document, elements, listeners, timers, calls: () => calls, setResponse: value => response = value,
        settle: () => new Promise(resolve => setImmediate(resolve))};
}

test('lecturer polling uses text nodes, schedules 5s, pauses hidden and resumes visible', async () => {
    const h = harness();
    await h.settle();
    assert.equal(h.calls(), 1);
    const text = h.elements.get('request-history').children[0].children[2];
    assert.equal(text.textContent, '<script>unsafe</script>');
    assert.equal(text.children.length, 0);
    assert.equal([...h.timers.values()][0].delay, 5000);
    h.document.hidden = true;
    h.listeners.visibilitychange();
    assert.equal(h.timers.size, 0);
    assert.equal(h.calls(), 1);
    h.document.hidden = false;
    h.listeners.visibilitychange();
    await h.settle();
    assert.equal(h.calls(), 2);
});

test('attendance polling displays QR and refreshes at the next rotation boundary', async () => {
    const h = harness('attendance');
    h.setResponse({rows: [['student', 'Present']], window: {additional: true, remaining: 90, rotation_in: 1,
        qr_image: 'data:image/svg+xml;base64,example', scan_url: '/scan/example/'}});
    await h.settle();
    assert.equal(h.elements.get('attendance-qr').hidden, false);
    assert.equal(h.elements.get('scan-link').href, '/scan/example/');
    assert.match(h.elements.get('window-status').textContent, /Additional/);
    assert.equal([...h.timers.values()][0].delay, 1050);
});

test('scan script submits a form, rather than making a GET registration request', () => {
    let posts = 0;
    const progress = {};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/js/register.js'), 'utf8'), {
        document: {getElementById: id => id === 'attendance-registration' ? {requestSubmit: () => posts++} : progress}});
    assert.equal(posts, 1);
    assert.match(progress.textContent, /Submitting/);
});
