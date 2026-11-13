// ═══════════════════════════════════════════════════════════════════
// EVENTS — one feed (/api/events, from events.json + the admin's
// changes) for the Tourism events calendar, the event markers on the
// hotel profile and benchmarking calendars, and the hotel's "Next 90
// days" strip. Loaded after main.js (uses fmt, CalTip, calTipAttrs,
// heatCell, localIsoDate).
// ═══════════════════════════════════════════════════════════════════

const KodoEvents = (() => {
  let feed = null, loading = null;

  // Type → pill family (the platform's colour families, tokens.css)
  const TYPE_FAMILY = {
    holiday: 'violet', religious: 'violet', school_ma: 'grey',
    diaspora: 'grey', music: 'sky', film: 'orange', arts: 'orange', moussem: 'orange', sport: 'green', business: 'blue',
  };
  const IMPACT_RANK = { high: 3, medium: 2, low: 1 };
  const STATUS_FAMILY = { confirmed: 'green', announced: 'blue', estimated: 'orange', moon: 'violet' };
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const esc = s => fmt.esc(s == null ? '' : s);
  const attr = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

  function load() {
    if (feed) return Promise.resolve(feed);
    if (!loading) {
      loading = fetch('/api/events').then(r => r.ok ? r.json() : { events: [], types: {}, labels: {} })
        .catch(() => ({ events: [], types: {}, labels: {} }))
        .then(d => {
          feed = d;
          feed.labelOrder = d.labels || {};     // {field: [[value, label], …]} in display order
          feed.labels = Object.fromEntries(Object.entries(feed.labelOrder).map(([k, pairs]) => [k, Object.fromEntries(pairs)]));
          feed.byId = Object.fromEntries((d.events || []).map(e => [e.id, e])); return feed; });
    }
    return loading;
  }

  // Display labels come from the server (events_db.LABELS), the one place
  // stored values ("high", "moon"…) become what users read
  const label = (field, v) => (feed && feed.labels && feed.labels[field] && feed.labels[field][v]) || v || '';
  const typeLabel = t => label('type', t);
  const impactLabel = v => label('impact', v);                 // "High"
  const impactText = v => `${impactLabel(v)} impact`;          // "High impact"
  const statusLabel = v => label('date_status', v);            // "Moon-dependent"
  const cityLabel = e => e.city === 'National' ? 'Nationwide' : e.city;
  const parse = iso => { const [y, m, d] = iso.split('-').map(Number); return new Date(y, m - 1, d); };
  const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
  const iso = d => localIsoDate(d);

  function dateRange(e) {
    const s = parse(e.start), t = parse(e.end);
    if (e.precision === 'month') return `${MONTH[s.getMonth()]} ${s.getFullYear()} (dates to be announced)`;
    if (e.start === e.end) return `${s.getDate()} ${MON[s.getMonth()]} ${s.getFullYear()}`;
    if (s.getFullYear() !== t.getFullYear()) return `${s.getDate()} ${MON[s.getMonth()]} ${s.getFullYear()} – ${t.getDate()} ${MON[t.getMonth()]} ${t.getFullYear()}`;
    if (s.getMonth() !== t.getMonth()) return `${s.getDate()} ${MON[s.getMonth()]} – ${t.getDate()} ${MON[t.getMonth()]} ${t.getFullYear()}`;
    return `${s.getDate()}–${t.getDate()} ${MON[s.getMonth()]} ${s.getFullYear()}`;
  }
  const shortRange = e => {
    const s = parse(e.start), t = parse(e.end);
    if (e.precision === 'month') return `${MON[s.getMonth()]} (TBA)`;
    if (e.start === e.end) return `${s.getDate()} ${MON[s.getMonth()]}`;
    return s.getMonth() === t.getMonth() ? `${s.getDate()}–${t.getDate()} ${MON[s.getMonth()]}` : `${s.getDate()} ${MON[s.getMonth()]} – ${t.getDate()} ${MON[t.getMonth()]}`;
  };

  // Small pills (tint fill, saturated text, no border)
  const typePill = e => `<span class="pill--${TYPE_FAMILY[e.type] || 'grey'} evc-pill">${esc(typeLabel(e.type))}</span>`;
  const impactBars = v => `<span class="evc-impact evc-impact--${v}"><span class="evc-impact-bars" aria-hidden="true"><i></i><i></i><i></i></span>${esc(impactLabel(v))}</span>`;
  const impactPill = e => impactBars(e.impact).replace('<span class', `<span title="${attr(impactText(e.impact))}" class`);
  const statusBadge = v => `<span class="pill--${STATUS_FAMILY[v] || 'grey'} evc-pill">${esc(statusLabel(v))}</span>`;
  const statusPill = e => statusBadge(e.date_status);
  const cityPill = e => `<span class="pill--grey evc-pill">${esc(cityLabel(e))}</span>`;

  // Events that touch a city (its own, plus nationwide ones)
  function forCity(events, city, { national = true, minNationalRank = 1 } = {}) {
    return events.filter(e => {
      if (city === 'all' || !city) return national || e.city !== 'National';
      if ((e.market || e.city) === city || e.city === city) return true;
      return national && e.city === 'National' && IMPACT_RANK[e.impact] >= minNationalRank;
    });
  }
  const overlaps = (e, a, b) => e.start <= b && e.end >= a;

  // ── Detail panel (one for the whole platform) ─────────────────────
  let panel, backdrop, lastFocus = null;
  function ensurePanel() {
    if (panel) return;
    backdrop = document.createElement('div');
    backdrop.className = 'evc-backdrop'; backdrop.hidden = true;
    panel = document.createElement('aside');
    panel.className = 'evc-panel'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-labelledby', 'evc-panel-title');
    document.body.append(backdrop, panel);
    backdrop.addEventListener('click', close);
    panel.addEventListener('keydown', e => {
      if (e.key === 'Escape') { e.stopPropagation(); close(); }
      if (e.key === 'Tab') {               // keep focus inside the panel
        const f = [...panel.querySelectorAll('a[href], button:not([disabled])')];
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    });
    panel.addEventListener('click', e => {
      const b = e.target.closest('[data-ev-open]');
      if (b) show([b.dataset.evOpen], true);
      else if (e.target.closest('[data-ev-back]')) show(JSON.parse(panel.dataset.list || '[]'), false);
      else if (e.target.closest('.evc-panel-close')) close();
    });
  }
  function nights(e) { return Math.round((parse(e.end) - parse(e.start)) / 864e5) + 1; }
  function detailHtml(e, back) {
    const row = (label, html) => html ? `<div class="evc-d-row"><dt>${label}</dt><dd>${html}</dd></div>` : '';
    return `
      <div class="evc-panel-head">
        ${back ? '<button type="button" class="export-btn" data-ev-back>← All events</button>' : '<span></span>'}
        <button type="button" class="evc-panel-close" aria-label="Close">✕</button>
      </div>
      <h2 class="evc-panel-title" id="evc-panel-title">${esc(e.name)}</h2>
      <div class="evc-panel-pills">${typePill(e)}${impactPill(e)}${statusPill(e)}</div>
      <dl class="evc-d">
        ${row('Dates', esc(dateRange(e)) + (e.precision === 'month' ? '' : ` <span class="evc-muted">· ${nights(e)} ${nights(e) === 1 ? 'day' : 'days'}</span>`))}
        ${row('Date status', esc(statusLabel(e.date_status)) + (e.date_basis ? `<div class="evc-muted">${esc(e.date_basis)}</div>` : ''))}
        ${row('City', esc(cityLabel(e)) + (e.market && e.market !== e.city && e.market !== 'National' ? ` <span class="evc-muted">· hotels in ${esc(e.market)}</span>` : ''))}
        ${row('Venue', esc(e.venue))}
        ${row('Why it matters', esc(e.impact_reason) + (e.effect === 'down' ? '<div class="evc-muted">Lowers hotel demand.</div>' : e.effect === 'mixed' ? '<div class="evc-muted">Business hotels down, leisure up.</div>' : ''))}
        ${row('Expected attendance', esc(e.attendance))}
        ${row('About', esc(e.description))}
        ${row('Recurrence', esc(label('recurrence', e.recurrence)))}
        ${row('Occupancy model', e.model && e.precision !== 'month' ? 'Counted (Kodo Estimates)' : 'Shown only, not counted' + (e.precision === 'month' ? ' (month only)' : ''))}
        ${row('Source', `<a href="${attr(e.source)}" target="_blank" rel="noopener">${esc(e.source.replace(/^https?:\/\/(www\.)?/, '').split('/')[0])} ↗</a>`)}
        ${row('Date last checked', esc(e.checked))}
      </dl>`;
  }
  // ids: one event (detail) or several (a list; picking one shows its detail with a way back)
  function show(ids, fromList) {
    ensurePanel();
    const evs = ids.map(id => feed.byId[id]).filter(Boolean);
    if (!evs.length) return;
    if (panel.hidden) lastFocus = document.activeElement;
    panel.innerHTML = evs.length === 1 ? detailHtml(evs[0], fromList && !!panel.dataset.list) : `
      <div class="evc-panel-head"><span></span><button type="button" class="evc-panel-close" aria-label="Close">✕</button></div>
      <h2 class="evc-panel-title" id="evc-panel-title">${evs.length} events</h2>
      <div class="evc-list">${evs.map(e => agendaRow(e)).join('')}</div>`;
    panel.hidden = backdrop.hidden = false;
    panel.scrollTop = 0;
    (panel.querySelector('.evc-panel-close') || panel).focus();
    CalTip.hide();
  }
  function close() {
    if (!panel || panel.hidden) return;
    panel.hidden = backdrop.hidden = true;
    panel.dataset.list = '';
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
  }
  function openList(ids) {
    ensurePanel();
    panel.dataset.list = ids.length > 1 ? JSON.stringify(ids) : '';
    show(ids, false);
  }

  function agendaRow(e) {
    return `<button type="button" class="evc-row" data-ev-open="${attr(e.id)}" aria-label="${attr(`${e.name}, ${dateRange(e)}, ${cityLabel(e)}, ${impactText(e.impact)}, ${statusLabel(e.date_status)}`)}">
      <span class="evc-row-date">${esc(shortRange(e))}</span>
      <span class="evc-row-main">
        <span class="evc-row-name">${esc(e.name)}</span>
        <span class="evc-row-pills">${typePill(e)}${impactPill(e)}${statusPill(e)}${cityPill(e)}</span>
        <span class="evc-row-why">${esc(e.impact_reason)}</span>
      </span>
    </button>`;
  }

  // ── Exports (the filtered view) ───────────────────────────────────
  function download(name, text, type) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type }));
    a.download = name; document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }
  function exportIcs(events, viewName) {
    const icsEsc = s => String(s || '').replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
    const fold = l => l.length <= 74 ? l : l.match(/.{1,74}/g).join('\r\n ');
    const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Kodo Hospitality//Events//EN', 'CALSCALE:GREGORIAN', `X-WR-CALNAME:${icsEsc('Kodo events · ' + viewName)}`];
    events.forEach(e => {
      lines.push('BEGIN:VEVENT', `UID:${e.id}@kodohospitality.com`, `DTSTAMP:${stamp}`,
        `DTSTART;VALUE=DATE:${e.start.replace(/-/g, '')}`, `DTEND;VALUE=DATE:${iso(addDays(parse(e.end), 1)).replace(/-/g, '')}`,
        fold(`SUMMARY:${icsEsc(e.name + (e.date_status === 'confirmed' ? '' : ` (${statusLabel(e.date_status)})`))}`),
        fold(`LOCATION:${icsEsc([e.venue, cityLabel(e)].filter(Boolean).join(', '))}`),
        fold(`DESCRIPTION:${icsEsc(`${impactText(e.impact)}: ${e.impact_reason}\n${statusLabel(e.date_status)}${e.date_basis ? ': ' + e.date_basis : ''}\nSource: ${e.source} (checked ${e.checked})`)}`),
        fold(`URL:${e.source}`), 'END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    download(`kodo-events-${viewName.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.ics`, lines.join('\r\n') + '\r\n', 'text/calendar');
  }
  function exportCsv(events, viewName) {
    const cols = ['name', 'type', 'city', 'venue', 'start', 'end', 'impact', 'impact_reason', 'date_status', 'date_basis', 'attendance', 'recurrence', 'source', 'checked'];
    const shown = { type: 1, impact: 1, date_status: 1, recurrence: 1 };   // stored value → display label
    const q = v => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`;
    const head = ['Name', 'Type', 'City', 'Venue', 'Start', 'End', 'Impact', 'Why it matters', 'Date status', 'Date basis', 'Attendance', 'Recurrence', 'Source', 'Date last checked'];
    const rows = [head.map(q).join(',')].concat(events.map(e => cols.map(c => q(c === 'city' ? cityLabel(e) : shown[c] ? label(c, e[c]) : e[c])).join(',')));
    download(`kodo-events-${viewName.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.csv`, '\ufeff' + rows.join('\r\n'), 'text/csv;charset=utf-8');
  }

  // ── Markers on the hotel profile and benchmarking calendars ──────
  // Cells carry their date in data-cal-tip (calTipAttrs); a cell with an
  // event in the hotel's city gets a small button that opens the panel.
  async function markCells(container, city) {
    if (!container || !city) return;
    const f = await load();
    const evs = forCity(f.events, city, { minNationalRank: 2 }).filter(e => e.precision !== 'month');
    container.querySelectorAll('[data-cal-tip]').forEach(cell => {
      let tip;
      try { tip = JSON.parse(cell.dataset.calTip); } catch { return; }
      if (!/^\d{4}-\d{2}-\d{2}$/.test(tip.date || '')) return;
      cell.querySelector('.evc-mark')?.remove();
      const hits = evs.filter(e => overlaps(e, tip.date, tip.date))
        .sort((a, b) => IMPACT_RANK[b.impact] - IMPACT_RANK[a.impact]);
      if (!hits.length) return;
      const top = hits[0];
      const b = document.createElement('button');
      b.type = 'button';
      b.className = `evc-mark evc-mark--${top.impact}`;
      b.dataset.evIds = hits.map(e => e.id).join(',');
      b.setAttribute('aria-label', `${hits.length} ${hits.length === 1 ? 'event' : 'events'} on ${tip.date}: ${hits.map(e => e.name).join('; ')}`);
      cell.appendChild(b);
      tip.rows = (tip.rows || []).concat(hits.slice(0, 3).map((e, i) => [i ? '' : (hits.length === 1 ? 'Event' : 'Events'), e.name]));
      if (hits.length > 3) tip.rows.push(['', `+${hits.length - 3} more`]);
      cell.dataset.calTip = JSON.stringify(tip);
    });
  }
  document.addEventListener('click', e => {
    const m = e.target.closest('.evc-mark');
    if (!m) return;
    e.stopPropagation();
    load().then(() => openList(m.dataset.evIds.split(',')));
  }, true);

  // "Next 90 days" strip for a city (hotel profile)
  async function renderNext90(el, city) {
    if (!el) return;
    const f = await load();
    const today = iso(new Date()), until = iso(addDays(new Date(), 90));
    const evs = forCity(f.events, city, { minNationalRank: 2 })
      .filter(e => overlaps(e, today, until))
      .sort((a, b) => a.start.localeCompare(b.start) || IMPACT_RANK[b.impact] - IMPACT_RANK[a.impact]);
    const title = el.querySelector('[data-ev-title]'), list = el.querySelector('[data-ev-list]');
    if (title) title.textContent = `Events in ${city} · next 90 days`;
    list.innerHTML = evs.length ? evs.map(e => `
      <button type="button" class="evc-chip" data-ev-open="${attr(e.id)}" aria-label="${attr(`${e.name}, ${dateRange(e)}, ${impactText(e.impact)}, ${statusLabel(e.date_status)}`)}">
        <span class="evc-chip-date">${esc(shortRange(e))}</span>
        <span class="evc-chip-name">${esc(e.name)}</span>
        <span class="evc-chip-meta">${impactPill(e)}${e.date_status === 'confirmed' ? '' : statusPill(e)}</span>
      </button>`).join('') : `<p class="evc-empty">No events in the next 90 days for ${esc(city)}.</p>`;
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-ev-open]');
    if (!b || (panel && panel.contains(b))) return;
    load().then(() => openList([b.dataset.evOpen]));
  });

  return { load, forCity, overlaps, dateRange, shortRange, typePill, impactPill, impactBars, statusPill, statusBadge, cityPill, agendaRow, open: openList, close,
           exportIcs, exportCsv, markCells, renderNext90, TYPE_FAMILY, IMPACT_RANK, STATUS_FAMILY, MONTH, MON, parse, addDays, iso,
           typeLabel, impactLabel, impactText, statusLabel, cityLabel };
})();

// ═══ Tourism: events calendar ════════════════════════════════════
const EventCalendar = (() => {
  const K = KodoEvents;
  const PREFS_KEY = 'kodo_events_prefs';
  let st = null, root = null;
  const $ = sel => root.querySelector(sel);
  const loadPrefs = () => { try { return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}'); } catch { return {}; } };
  const savePrefs = () => { try { localStorage.setItem(PREFS_KEY, JSON.stringify({ view: st.view, city: st.city, type: st.type, impact: st.impact, national: st.national })); } catch {} };

  async function init() {
    root = document.getElementById('evcal');
    if (!root || st) { if (st) render(); return; }
    const f = await K.load();
    const p = loadPrefs();
    const now = new Date();
    st = {
      view: p.view || (window.matchMedia('(max-width: 640px)').matches ? 'agenda' : 'month'),
      city: p.city || f.home_city || 'all', type: p.type || 'all', impact: p.impact || 'all',
      national: p.national !== false, q: '', y: now.getFullYear(), m: now.getMonth(),
    };
    // City and type options from the data
    const cities = [...new Set(f.events.map(e => e.market || e.city).filter(c => c && c !== 'National'))].sort((a, b) => a.localeCompare(b));
    if (st.city !== 'all' && !cities.includes(st.city)) st.city = 'all';
    $('#evcal-city').innerHTML = '<option value="all">All cities</option>' + cities.map(c => `<option value="${fmt.esc(c)}">${fmt.esc(c)}</option>`).join('');
    const types = Object.keys(f.types).filter(t => f.events.some(e => e.type === t)).sort((a, b) => K.typeLabel(a).localeCompare(K.typeLabel(b)));
    if (st.type !== 'all' && !types.includes(st.type)) st.type = 'all';
    $('#evcal-type').innerHTML = '<option value="all">All types</option>' + types.map(t => `<option value="${t}">${fmt.esc(K.typeLabel(t))}</option>`).join('');
    renderLegend(types);
    $('#evcal-city').value = st.city; $('#evcal-type').value = st.type; $('#evcal-impact').value = st.impact;
    wire();
    render();
  }

  function current() {
    const all = K.forCity(feedEvents(), st.city, { national: st.national });
    const q = st.q.trim().toLowerCase();
    return all.filter(e => (st.type === 'all' || e.type === st.type)
      && (st.impact === 'all' || (st.impact === 'high' ? e.impact === 'high' : e.impact !== 'low'))
      && (!q || [e.name, e.city, e.venue, e.description, e.impact_reason, K.typeLabel(e.type)].join(' ').toLowerCase().includes(q)));
  }
  let _feed = null;
  const feedEvents = () => _feed || [];

  function wire() {
    K.load().then(f => { _feed = f.events; });
    $('#evcal-city').addEventListener('change', e => { st.city = e.target.value; savePrefs(); render(); });
    $('#evcal-type').addEventListener('change', e => { st.type = e.target.value; savePrefs(); render(); });
    $('#evcal-legend').addEventListener('click', e => {      // a type in the legend filters to it; again shows all
      const b = e.target.closest('[data-legtype]');
      if (!b) return;
      st.type = st.type === b.dataset.legtype ? 'all' : b.dataset.legtype;
      $('#evcal-type').value = st.type; savePrefs(); render();
    });
    $('#evcal-legend-toggle').addEventListener('click', e => {
      const open = e.currentTarget.getAttribute('aria-expanded') !== 'true';
      e.currentTarget.setAttribute('aria-expanded', open);
      $('#evcal-legend').classList.toggle('evcal-legend--open', open);
    });
    $('#evcal-impact').addEventListener('change', e => { st.impact = e.target.value; savePrefs(); render(); });
    let t = null;
    $('#evcal-search').addEventListener('input', e => { clearTimeout(t); t = setTimeout(() => { st.q = e.target.value; render(); }, 120); });
    $('#evcal-national').addEventListener('click', () => { st.national = !st.national; savePrefs(); render(); });
    root.querySelectorAll('[data-evview]').forEach(b => b.addEventListener('click', () => { st.view = b.dataset.evview; savePrefs(); render(); }));
    $('#evcal-prev').addEventListener('click', () => step(-1));
    $('#evcal-next').addEventListener('click', () => step(1));
    $('#evcal-today').addEventListener('click', () => { const n = new Date(); st.y = n.getFullYear(); st.m = n.getMonth(); render(); });
    $('#evcal-ics').addEventListener('click', () => K.exportIcs(upcoming(), label()));
    $('#evcal-csv').addEventListener('click', () => K.exportCsv(upcoming(), label()));
    $('#evcal-density').addEventListener('click', e => {
      const w = e.target.closest('[data-week]');
      if (!w) return;
      const d = K.parse(w.dataset.week);
      st.y = d.getFullYear(); st.m = d.getMonth(); st.view = 'month'; savePrefs(); render();
      $('#evcal-grid')?.querySelector(`[data-weekrow="${w.dataset.week}"]`)?.scrollIntoView({ block: 'nearest' });
    });
    $('#evcal-grid').addEventListener('click', e => {
      const more = e.target.closest('[data-day-ids]');
      if (more) K.open(more.dataset.dayIds.split(','));
    });
  }
  const label = () => [st.city === 'all' ? 'All cities' : st.city, st.type === 'all' ? '' : K.typeLabel(st.type),
    st.impact === 'all' ? '' : st.impact === 'high' ? 'High impact' : 'High and medium impact'].filter(Boolean).join(' · ');

  // Legend: one pill per event type (click to filter), the impact bars and the date badges
  function renderLegend(types) {
    $('#evcal-leg-types').innerHTML = types.map(t => `<button type="button" class="pill--${K.TYPE_FAMILY[t] || 'grey'} evc-pill evcal-leg-type" data-legtype="${t}" aria-pressed="false"
      title="Show only ${fmt.esc(K.typeLabel(t))}">${fmt.esc(K.typeLabel(t))}<span class="evcal-leg-x" aria-hidden="true">×</span></button>`).join('');
    $('#evcal-leg-impact').innerHTML = ['high', 'medium', 'low'].map(K.impactBars).join('');
    $('#evcal-leg-status').innerHTML = Object.keys(K.STATUS_FAMILY).map(K.statusBadge).join('')
      + '<span class="evcal-leg-note"><span class="evcal-leg-est" aria-hidden="true">≈ Name</span> Not yet confirmed</span>';
  }
  function syncLegend() {
    root.querySelectorAll('[data-legtype]').forEach(b => {
      const on = b.dataset.legtype === st.type;
      b.setAttribute('aria-pressed', on);
      b.title = on ? 'Show all types' : `Show only ${K.typeLabel(b.dataset.legtype)}`;
    });
    $('#evcal-leg-types').classList.toggle('evcal-leg-types--filtered', st.type !== 'all');
  }
  const todayIso = () => K.iso(new Date());
  const upcoming = () => current().filter(e => e.end >= todayIso()).sort((a, b) => a.start.localeCompare(b.start));
  function bounds() {
    const evs = feedEvents();
    const min = evs.reduce((m, e) => e.start < m ? e.start : m, '9999'), max = evs.reduce((m, e) => e.end > m ? e.end : m, '0000');
    return [K.parse(min.slice(0, 7) + '-01'), K.parse(max.slice(0, 7) + '-01')];
  }
  function step(n) {
    const [lo, hi] = bounds();
    const d = new Date(st.y, st.m + n, 1);
    if (d < lo || d > hi) return;
    st.y = d.getFullYear(); st.m = d.getMonth(); render();
  }

  function render() {
    if (!_feed) { K.load().then(f => { _feed = f.events; render(); }); return; }
    const evs = current();
    root.querySelectorAll('[data-evview]').forEach(b => { b.classList.toggle('active', b.dataset.evview === st.view); b.setAttribute('aria-pressed', b.dataset.evview === st.view); });
    $('#evcal-national').classList.toggle('active', st.national);
    $('#evcal-national').setAttribute('aria-pressed', st.national);
    $('#evcal-month-label').textContent = `${K.MONTH[st.m]} ${st.y}`;
    const [lo, hi] = bounds(), cur = new Date(st.y, st.m, 1);
    $('#evcal-prev').disabled = cur <= lo; $('#evcal-next').disabled = cur >= hi;
    root.querySelector('.evcal-monthnav').hidden = st.view !== 'month';
    syncLegend();
    const n = upcoming().length;
    $('#evcal-count').textContent = `${n} upcoming ${n === 1 ? 'event' : 'events'}`;
    renderDensity(evs);
    $('#evcal-grid').hidden = st.view !== 'month';
    $('#evcal-agenda').hidden = st.view !== 'agenda';
    if (st.view === 'month') renderMonth(evs); else renderAgenda();
  }

  // Weekly heat bar: how busy each week is in the selected city
  function renderDensity(evs) {
    const el = $('#evcal-density');
    const busy = evs.filter(e => e.effect !== 'down' && e.precision !== 'month' && (st.city === 'all' ? e.city !== 'National' || e.impact === 'high' : true));
    const start = (() => { const d = new Date(); d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); return d; })();
    const [, hi] = bounds();
    const last = new Date(hi.getFullYear(), hi.getMonth() + 1, 0);
    let html = '', prevMonth = -1, cells = 0;
    for (let w = new Date(start); w <= last; w = K.addDays(w, 7)) {
      const a = K.iso(w), b = K.iso(K.addDays(w, 6));
      const hits = busy.filter(e => K.overlaps(e, a, b)).sort((x, y) => K.IMPACT_RANK[y.impact] - K.IMPACT_RANK[x.impact]);
      const score = hits.reduce((s, e) => s + K.IMPACT_RANK[e.impact], 0);
      const level = score === 0 ? -1 : score <= 2 ? 0 : score <= 5 ? 1 : score <= 8 ? 2 : 3;
      const cell = level < 0 ? null : heatCell('blue', level, level >= 2 ? '600' : '');
      const label = level < 0 ? 'Quiet week' : ['Light', 'Busy', 'Very busy', 'Peak'][level] + ' week';
      const rows = [[label, `${hits.length} ${hits.length === 1 ? 'event' : 'events'}`]].concat(hits.slice(0, 4).map(e => [K.impactText(e.impact), e.name]));
      if (hits.length > 4) rows.push(['', `+${hits.length - 4} more`]);
      const mo = w.getMonth() !== prevMonth ? `<span class="evcal-dens-month">${K.MON[w.getMonth()]}${w.getMonth() === 0 || prevMonth === -1 ? ' ' + String(w.getFullYear()).slice(2) : ''}</span>` : '';
      prevMonth = w.getMonth();
      html += `<button type="button" class="evcal-dens-week${level >= 0 ? '' : ' evcal-dens-quiet'}" data-week="${a}"
        style="${cell ? `background:${cell.bg};` : ''}"${calTipAttrs(`Week of ${KodoEvents.shortRange({ start: a, end: b })}`, rows)}
        aria-label="${fmt.esc(`Week of ${a}: ${label}, ${hits.length} events`)}">${mo}</button>`;
      cells++;
    }
    el.innerHTML = html;
    el.style.setProperty('--weeks', cells);
  }

  function renderMonth(evs) {
    const el = $('#evcal-grid');
    const first = new Date(st.y, st.m, 1), last = new Date(st.y, st.m + 1, 0);
    let w = K.addDays(first, -((first.getDay() + 6) % 7));
    const narrow = window.matchMedia('(max-width: 640px)').matches, maxLanes = narrow ? 2 : 4;
    const today = todayIso();
    let html = '<div class="bench-cal-dow-row evcal-dow">' + ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => `<div class="bench-cal-dow">${d}</div>`).join('') + '</div>';
    const dayEvs = evs.filter(e => e.precision !== 'month');
    while (w <= last) {
      const days = [...Array(7)].map((_, i) => K.addDays(w, i));
      const a = K.iso(days[0]), b = K.iso(days[6]);
      const inWeek = dayEvs.filter(e => K.overlaps(e, a, b))
        .sort((x, y) => (x.city === 'National') - (y.city === 'National') || K.IMPACT_RANK[y.impact] - K.IMPACT_RANK[x.impact]
          || x.start.localeCompare(y.start) || y.end.localeCompare(x.end));   // the city's own events first
      const lanes = [];   // lanes[i] = last day index used
      const placed = [], hidden = {};
      inWeek.forEach(e => {
        const s = Math.max(0, Math.round((K.parse(e.start) - days[0]) / 864e5)), t = Math.min(6, Math.round((K.parse(e.end) - days[0]) / 864e5));
        let lane = lanes.findIndex(end => end < s);
        if (lane < 0) { lane = lanes.length; lanes.push(-1); }
        if (lane >= maxLanes) { for (let d = s; d <= t; d++) (hidden[d] = hidden[d] || []).push(e.id); return; }
        lanes[lane] = t;
        placed.push({ e, s, t, lane, cutL: e.start < a, cutR: e.end > b });
      });
      const rowsUsed = Math.min(maxLanes, lanes.length);
      html += `<div class="evcal-week" data-weekrow="${a}" style="--lanes:${Math.max(rowsUsed, 1)}">`;
      days.forEach((d, i) => {
        const di = K.iso(d), out = d.getMonth() !== st.m;
        const dayAll = dayEvs.filter(e => K.overlaps(e, di, di));
        html += `<div class="evcal-day${out ? ' evcal-day--out' : ''}${di === today ? ' evcal-day--today' : ''}" style="grid-column:${i + 1}">
          <span class="evcal-daynum"${di === today ? ' aria-current="date"' : ''}>${d.getDate()}</span>
          ${hidden[i] ? `<button type="button" class="evcal-more" data-day-ids="${dayAll.map(e => e.id).join(',')}" aria-label="${fmt.esc(`${dayAll.length} events on ${di}`)}">+${hidden[i].length}</button>` : ''}
        </div>`;
      });
      placed.forEach(({ e, s, t, lane, cutL, cutR }) => {
        const est = e.date_status === 'estimated' || e.date_status === 'moon';
        html += `<button type="button" class="evcal-bar pill--${K.TYPE_FAMILY[e.type] || 'grey'} evcal-bar--${e.impact}${est ? ' evcal-bar--est' : ''}${cutL ? ' evcal-bar--cutl' : ''}${cutR ? ' evcal-bar--cutr' : ''}"
          style="grid-column:${s + 1} / span ${t - s + 1};grid-row:${lane + 2}" data-ev-open="${fmt.esc(e.id)}"
          ${calTipAttrs(e.name, [['Dates', K.dateRange(e)], ['City', K.cityLabel(e)], ['Type', K.typeLabel(e.type)], ['Impact', K.impactLabel(e.impact)], ['Date status', K.statusLabel(e.date_status)]])}
          aria-label="${fmt.esc(`${e.name}, ${K.dateRange(e)}, ${K.cityLabel(e)}, ${K.impactText(e.impact)}, ${K.statusLabel(e.date_status)}`)}">
          <span class="evc-impact-bars evc-impact--${e.impact}" aria-hidden="true"><i></i><i></i><i></i></span><span class="evcal-bar-name">${est ? '≈ ' : ''}${fmt.esc(e.name)}</span></button>`;
      });
      html += '</div>';
      w = K.addDays(w, 7);
    }
    const tba = evs.filter(e => e.precision === 'month' && e.start.slice(0, 7) === `${st.y}-${String(st.m + 1).padStart(2, '0')}`);
    if (tba.length) html += `<div class="evcal-tba"><span class="evc-muted">This month, dates to be announced:</span> ${tba.map(e => `<button type="button" class="export-btn" data-ev-open="${fmt.esc(e.id)}">${fmt.esc(e.name)}</button>`).join(' ')}</div>`;
    el.innerHTML = html;
  }

  function renderAgenda() {
    const el = $('#evcal-agenda');
    const list = upcoming();
    if (!list.length) { el.innerHTML = '<p class="evc-empty">No upcoming events for this selection.</p>'; return; }
    let html = '', key = '';
    list.forEach(e => {
      const d = K.parse(e.start < todayIso() ? todayIso() : e.start);
      const k = `${K.MONTH[d.getMonth()]} ${d.getFullYear()}`;
      if (k !== key) { if (key) html += '</div>'; html += `<h3 class="evcal-agenda-month">${k}</h3><div class="evc-list">`; key = k; }
      html += K.agendaRow(e);
    });
    el.innerHTML = html + '</div>';
  }

  window.addEventListener('resize', () => { if (st && st.view === 'month') { clearTimeout(window._evcalR); window._evcalR = setTimeout(render, 150); } });
  return { init, render };
})();
