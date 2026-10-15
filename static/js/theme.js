/* Kodo theme: one choice shared by every page (landing, marketing, platform,
   auth, admin). Load this synchronously in <head>, before any stylesheet, so
   the theme is in place before first paint.

   - Storage key: 'kodo-theme' ('light' | 'dark'). Older keys are migrated once.
   - No saved choice: light, whatever the OS setting.
   - Sets <html data-theme>, which tokens.css reads.
   - KodoTheme.applyBody(cls) mirrors the theme onto <body> for page CSS that
     keys off a body class ('light' on the platform, 'lp-light' on marketing
     pages); call it as the first thing inside <body>.
   - KodoTheme.set(mode) saves the choice, updates the page and fires a
     'kodo:themechange' event on window with detail.mode. */
(function () {
  var KEY = 'kodo-theme';
  var LEGACY_KEYS = ['kodo-lp-theme'];
  var bodyClass = null;

  function valid(v) { return v === 'light' || v === 'dark'; }

  function read() {
    try {
      var v = localStorage.getItem(KEY);
      if (!valid(v)) {
        for (var i = 0; i < LEGACY_KEYS.length; i++) {
          var old = localStorage.getItem(LEGACY_KEYS[i]);
          if (valid(old)) { v = old; localStorage.setItem(KEY, old); break; }
        }
      }
      return v === 'dark' ? 'dark' : 'light';
    } catch (e) {
      return 'light';
    }
  }

  var mode = read();
  document.documentElement.setAttribute('data-theme', mode);

  function syncBody() {
    if (bodyClass && document.body) document.body.classList.toggle(bodyClass, mode === 'light');
  }

  window.KodoTheme = {
    get: function () { return mode; },
    applyBody: function (cls) { bodyClass = cls; syncBody(); },
    set: function (next) {
      if (!valid(next)) return;
      mode = next;
      try { localStorage.setItem(KEY, next); } catch (e) {}
      document.documentElement.setAttribute('data-theme', next);
      syncBody();
      try { window.dispatchEvent(new CustomEvent('kodo:themechange', { detail: { mode: next } })); } catch (e) {}
    },
    toggle: function () { this.set(mode === 'light' ? 'dark' : 'light'); }
  };

  // Another tab changed the theme: follow it.
  window.addEventListener('storage', function (e) {
    if (e.key === KEY && valid(e.newValue) && e.newValue !== mode) window.KodoTheme.set(e.newValue);
  });
})();
