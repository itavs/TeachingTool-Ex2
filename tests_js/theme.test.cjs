// Appearance logic checks with the existing Node harness; not visual browser tests.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/theme.js'), 'utf8');

function harness({stored = null, dark = false, blocked = false} = {}) {
  const root = {dataset: {}}, docEvents = {}, winEvents = {}, selectEvents = {};
  const select = {value: 'system', addEventListener: (event, fn) => selectEvents[event] = fn};
  const media = {matches: dark, addEventListener: (_, fn) => media.changed = fn};
  let saved = stored;
  const document = {documentElement: root, getElementById: () => select,
    addEventListener: (event, fn) => docEvents[event] = fn};
  const window = {matchMedia: () => media, addEventListener: (event, fn) => winEvents[event] = fn,
    localStorage: {
      getItem: () => {if (blocked) throw Error('Storage blocked'); return saved;},
      setItem: (_, value) => {if (blocked) throw Error('Storage blocked'); saved = value;}
    }};
  vm.runInNewContext(source, {document, window});
  return {root, media, select, winEvents, saved: () => saved,
    ready: () => docEvents.DOMContentLoaded(),
    choose: value => {select.value = value; selectEvents.change();}};
}

test('system default applies before DOM ready and tracks OS changes', () => {
  const h = harness({dark: true});
  assert.equal(h.root.dataset.theme, 'dark');
  h.ready(); assert.equal(h.select.value, 'system');
  h.media.matches = false; h.media.changed();
  assert.equal(h.root.dataset.theme, 'light');
});
test('explicit preference survives navigation/reload and ignores OS changes', () => {
  const h = harness({dark: false}); h.ready(); h.choose('dark');
  assert.equal(h.saved(), 'dark');
  h.media.changed(); assert.equal(h.root.dataset.theme, 'dark');
  const next = harness({stored: h.saved()});
  assert.equal(next.root.dataset.theme, 'dark');
  next.ready(); assert.equal(next.select.value, 'dark');
  next.choose('light'); assert.equal(next.root.dataset.theme, 'light');
  next.choose('system'); assert.equal(next.saved(), 'system');
});
test('blocked storage still permits in-page selection without throwing', () => {
  const h = harness({blocked: true}); h.ready(); h.choose('dark');
  assert.equal(h.root.dataset.theme, 'dark');
});
test('invalid saved preference falls back to system', () => {
  const h = harness({stored: 'invalid', dark: true});
  assert.equal(h.root.dataset.theme, 'dark'); h.ready();
  assert.equal(h.select.value, 'system');
});
test('storage changes sync tabs, including clearing preferences', () => {
  const h = harness({stored: 'light', dark: true}); h.ready();
  h.winEvents.storage({key: 'teachingtool.appearance', newValue: 'dark'});
  assert.equal(h.select.value, 'dark');
  h.winEvents.storage({key: null, newValue: null});
  assert.equal(h.select.value, 'system');
  assert.equal(h.root.dataset.theme, 'dark');
});
