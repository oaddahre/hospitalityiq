/* Kodo palette for charts and the map, read from tokens.css for the current
   theme. Usage:
     const p = KodoPalette.get();      // { series: [...6], text, grid, ... }
     KodoPalette.onChange(p => redraw(p));
   Values are re-read whenever the theme changes. */
(function () {
  var cache = null;
  var listeners = [];

  function v(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function family(n) {
    return { dot: v('--cat-' + n + '-dot'), text: v('--cat-' + n + '-text'), tint: v('--cat-' + n + '-tint') };
  }

  function read() {
    var fam = { blue: family(1), green: family(2), orange: family(3), violet: family(4), sky: family(5), grey: family(6), red: family(7) };
    return {
      theme: document.documentElement.getAttribute('data-theme') || 'light',
      // Chart series order: blue, green, orange, violet, sky, grey (dot colours)
      series: [fam.blue.dot, fam.green.dot, fam.orange.dot, fam.violet.dot, fam.sky.dot, fam.grey.dot],
      families: fam,
      bg: v('--bg'),
      bgAlt: v('--bg-alt'),
      border: v('--border'),
      grid: v('--border'),
      text: v('--text'),
      text2: v('--text-2'),
      text3: v('--text-3'),
      axis: v('--text-3'),
      tooltipBg: v('--bg-alt'),
      tooltipBorder: v('--border'),
      action: v('--action'),
      onAction: v('--on-action'),
      positive: fam.green,
      negative: fam.red,
      warning: fam.orange,
      owners: { State: fam.grey, Listed: fam.blue, Private: fam.green, Family: fam.orange }
    };
  }

  window.KodoPalette = {
    get: function () { return cache || (cache = read()); },
    refresh: function () { cache = read(); return cache; },
    onChange: function (fn) { listeners.push(fn); }
  };

  window.addEventListener('kodo:themechange', function () {
    var p = window.KodoPalette.refresh();
    listeners.forEach(function (fn) { try { fn(p); } catch (e) { console.error(e); } });
  });
})();
