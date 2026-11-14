/* Search entries for the tourism Outlook (2026E estimate, 2027F forecast).
   Usage:
     KodoOutlookSearch.match('2027f')   // [{ year: 2027, name: '2027F · Tourism outlook (Kodo forecast)', ... }]
   A query matches when every word is a year (2026 or 2027, with or without
   E or F), one of estimate / forecast / outlook (or their first four or more
   letters), or tourism / kodo / morocco, and at least one word is a year or
   one of those three. Any capitalisation. Tested in tests/test_tourism_search.py. */
(function (root) {
  var ENTRIES = {
    2026: { year: 2026, label: '2026E', name: '2026E · Tourism estimate', tag: 'est.', kind: 'est',
            meta: 'Official months so far plus Kodo’s model for the rest of 2026' },
    2027: { year: 2027, label: '2027F', name: '2027F · Tourism outlook (Kodo forecast)', tag: 'fcst.', kind: 'fc',
            meta: 'Base case and range for arrivals, nights, occupancy, receipts and airports' },
  };
  // Which entry comes first for each word
  var WORDS = { estimate: [2026, 2027], forecast: [2027, 2026], outlook: [2027, 2026] };
  var CONTEXT = ['tourism', 'kodo', 'morocco'];

  function word(t) {
    for (var w in WORDS) {
      if (t === w || t === w + 's' || (t.length >= 4 && w.indexOf(t) === 0)) return w;
    }
    return null;
  }

  function match(query) {
    var tokens = String(query || '').toLowerCase().split(/[\s,;·/+()-]+/).filter(Boolean);
    if (!tokens.length) return [];
    var year = null, order = null;
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i], y = /^(2026|2027)[ef]?$/.exec(t), w = word(t);
      if (y) {
        if (year && year !== +y[1]) return [];
        year = +y[1];
      } else if (w) {
        order = order || WORDS[w];
      } else if (!CONTEXT.some(function (c) { return t.length >= 4 && c.indexOf(t) === 0; })) {
        return [];
      }
    }
    if (year) return [ENTRIES[year]];
    return order ? order.map(function (y) { return ENTRIES[y]; }) : [];
  }

  var api = { match: match, entries: ENTRIES };
  root.KodoOutlookSearch = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
