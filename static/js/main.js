// ─── Constants ────────────────────────────────────────────────────

const SEG_COLORS = {
  'Luxury':        '#1e40af',
  'Upper Upscale': '#4f7ef8',
  'Upscale':       '#60a5fa',
  'Midscale':      '#6b7280',
};

const CITY_COORDS = {
  'Casablanca':  [33.573, -7.589],
  'Marrakech':   [31.629, -7.981],
  'Agadir':      [30.427, -9.598],
  'Tanger':      [35.769, -5.800],
  'Tamuda Bay':  [35.690, -5.370],
  'Rabat':       [34.020, -6.841],
  'Fes':         [34.037, -4.998],
};

const MOROCCO_CENTER = [31.5, -7.0];
const MOROCCO_ZOOM   = 7;
const CITY_ZOOM      = 13;

const CHART_ACCENT   = '#4f7ef8';
const CHART_DIM      = 'rgba(79,126,248,0.14)';
const CHART_GRID     = '#3a4258';
const CHART_TICK     = '#6b7894';

const KPI_DELTAS = {
  'kpi-keys':   { text: '+6.2% YoY',    up: true },
  'kpi-occ':    { text: '+3.1 pts YoY', up: true },
  'kpi-adr':    { text: '+8.4% YoY',    up: true },
  'kpi-revpar': { text: '+10.8% YoY',   up: true },
};

Chart.register(ChartDataLabels);

// ─── State & cache (must precede theme setup — swapMapTiles reads leaflet) ──

const state = {
  city:    'all',
  mapSeg:  'all',
};

let apiData  = null;   // /api/data response
let hotels   = null;   // /api/hotels response (flat, merged)
let revChart = null;
let occChart = null;
let leaflet  = null;   // { map, markers, tileLayer }
let brandChart      = null;
let brandHotelsData = [];
const brandState    = { col: 'name', dir: 1 };
const BRAND_STR_COLS = new Set(['name', 'city', 'category', 'owner']);
let tourismInited   = false;

// ─── Theme ────────────────────────────────────────────────────────

const ICON_MOON = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
const ICON_SUN  = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;

function applyTheme(mode) {
  const icon = document.getElementById('theme-icon');
  if (mode === 'light') {
    document.body.classList.add('light');
    icon.innerHTML = ICON_SUN;
  } else {
    document.body.classList.remove('light');
    icon.innerHTML = ICON_MOON;
  }
  swapMapTiles(mode);
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  const next = document.body.classList.contains('light') ? 'dark' : 'light';
  localStorage.setItem('hiq-theme', next);
  applyTheme(next);
});

applyTheme(localStorage.getItem('hiq-theme') || 'dark');

// ─── Formatters ───────────────────────────────────────────────────

const fmt = {
  pct: v  => (v * 100).toFixed(1) + '%',
  num: v  => Math.round(v).toLocaleString('en'),
  mad: v  => Math.round(v).toLocaleString('en'),
  esc: s  => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'),
};

// ─── Aggregation ──────────────────────────────────────────────────

function cityAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.city)) map.set(h.city, []);
    map.get(h.city).push(h);
  });
  return [...map.entries()].map(([city, hs]) => {
    const tk = hs.reduce((s, h) => s + h.keys, 0);
    const ok = hs.reduce((s, h) => s + h.keys * h.occupancy, 0);
    return {
      city,
      hotel_count: hs.length,
      total_keys:  tk,
      occupancy:   ok / tk,
      adr_mad:     hs.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
      revpar_mad:  hs.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
      gop_margin:  hs.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
    };
  });
}

function brandAggs(hotelList) {
  const map = new Map();
  hotelList.forEach(h => {
    if (!map.has(h.brand_group)) map.set(h.brand_group, []);
    map.get(h.brand_group).push(h);
  });
  return [...map.entries()].map(([bg, hs]) => {
    const tk = hs.reduce((s, h) => s + h.keys, 0);
    const ok = hs.reduce((s, h) => s + h.keys * h.occupancy, 0);
    return {
      brand_group:  bg,
      hotel_count:  hs.length,
      total_keys:   tk,
      occupancy:    ok / tk,
      adr_mad:      hs.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
      revpar_mad:   hs.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
      gop_margin:   hs.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
    };
  }).sort((a, b) => b.total_keys - a.total_keys);
}

function nationalKPIs(hotelList) {
  const tk = hotelList.reduce((s, h) => s + h.keys, 0);
  const ok = hotelList.reduce((s, h) => s + h.keys * h.occupancy, 0);
  return {
    total_hotels: hotelList.length,
    total_keys:   tk,
    occupancy:    ok / tk,
    adr_mad:      hotelList.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok,
    revpar_mad:   hotelList.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk,
    gop_margin:   hotelList.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk,
  };
}

function filteredByCity() {
  if (state.city === 'all') return hotels;
  return hotels.filter(h => h.city === state.city);
}

// ─── KPIs ─────────────────────────────────────────────────────────

function renderKPIs() {
  const kpis = nationalKPIs(filteredByCity());

  const set = (id, val, meta) => {
    const el = document.getElementById(id);
    el.querySelector('.kpi-value').textContent = val;
    if (meta !== undefined) {
      const m = document.getElementById(id + '-meta');
      if (m) m.textContent = meta;
    }
    const d = KPI_DELTAS[id];
    if (d) {
      const deltaEl = document.getElementById(id + '-delta');
      if (deltaEl) {
        deltaEl.textContent = d.text;
        deltaEl.className = 'kpi-delta ' + (d.up ? 'up' : 'down');
      }
    }
    el.classList.remove('loading');
  };

  const hotelLabel = kpis.total_hotels + ' hotel' + (kpis.total_hotels !== 1 ? 's' : '');
  set('kpi-keys',   fmt.num(kpis.total_keys), hotelLabel);
  set('kpi-occ',    fmt.pct(kpis.occupancy),  '');
  set('kpi-adr',    fmt.mad(kpis.adr_mad));
  set('kpi-revpar', fmt.mad(kpis.revpar_mad));

  const sub = document.getElementById('dashboard-sub');
  sub.textContent = state.city === 'all'
    ? 'Morocco branded hotel market · 2025 FY estimates'
    : state.city + ' · 2025 FY estimates · ' + hotelLabel;
}

// ─── Charts ───────────────────────────────────────────────────────

function chartConfig(labels, values, tooltipSuffix, bgColors, labelFmt) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: bgColors,
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350 },
      layout: { padding: { right: 72 } },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#2d3449',
          borderColor: '#3a4258',
          borderWidth: 1,
          titleColor: '#eceef4',
          bodyColor: '#8a96b0',
          padding: { top: 8, bottom: 8, left: 12, right: 12 },
          callbacks: {
            label: ctx => '  ' + Math.round(ctx.raw).toLocaleString('en') + tooltipSuffix,
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'right',
          clip: false,
          color: '#8a96b0',
          font: { size: 11, weight: '600' },
          padding: { left: 5 },
          formatter: labelFmt,
        },
      },
      scales: {
        x: {
          min: 0,
          border: { display: false },
          grid:   { color: CHART_GRID },
          ticks:  { color: CHART_TICK, font: { size: 11 } }
        },
        y: {
          border: { display: false },
          grid:   { display: false },
          ticks:  { color: '#c5cbdb', font: { size: 12, weight: '500' } }
        }
      }
    }
  };
}

function barColors(labels) {
  return labels.map(l =>
    state.city === 'all' || l === state.city ? CHART_ACCENT : CHART_DIM
  );
}

function renderCharts() {
  const allCityData = cityAggs(hotels);

  // Set chart container heights based on city count (30px per bar + padding)
  const chartH = Math.max(400, allCityData.length * 30 + 60);
  document.getElementById('chart-revpar').closest('.chart-wrap').style.height = chartH + 'px';
  document.getElementById('chart-occ').closest('.chart-wrap').style.height = chartH + 'px';

  // RevPAR chart — sorted high→low
  const revSorted = [...allCityData].sort((a, b) => b.revpar_mad - a.revpar_mad);
  const revLabels = revSorted.map(c => c.city);
  const revVals   = revSorted.map(c => c.revpar_mad);

  const revLabelFmt = v => Math.round(v).toLocaleString('en');
  if (revChart) {
    revChart.data.labels = revLabels;
    revChart.data.datasets[0].data = revVals;
    revChart.data.datasets[0].backgroundColor = barColors(revLabels);
    revChart.update();
  } else {
    revChart = new Chart(
      document.getElementById('chart-revpar'),
      chartConfig(revLabels, revVals, ' MAD', barColors(revLabels), revLabelFmt)
    );
  }

  // Occupancy chart — sorted high→low
  const occSorted  = [...allCityData].sort((a, b) => b.occupancy - a.occupancy);
  const occLabels  = occSorted.map(c => c.city);
  const occVals    = occSorted.map(c => parseFloat((c.occupancy * 100).toFixed(1)));
  const occLabelFmt = v => v.toFixed(1) + '%';

  if (occChart) {
    occChart.data.labels = occLabels;
    occChart.data.datasets[0].data = occVals;
    occChart.data.datasets[0].backgroundColor = barColors(occLabels);
    occChart.update();
  } else {
    const cfg = chartConfig(occLabels, occVals, '%', barColors(occLabels), occLabelFmt);
    cfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw.toFixed(1) + '%';
    occChart = new Chart(document.getElementById('chart-occ'), cfg);
  }
}

// ─── Brand table ──────────────────────────────────────────────────

function gopClass(v) {
  if (v >= 0.37) return 'gop-high';
  if (v >= 0.30) return 'gop-mid';
  return 'gop-low';
}

function renderBrandTable() {
  const rows = brandAggs(filteredByCity());
  const tbody = document.querySelector('#brand-table tbody');

  tbody.innerHTML = rows.map((r, i) => `
    <tr>
      <td class="rank-cell">${i + 1}</td>
      <td class="brand-link" data-brand="${fmt.esc(r.brand_group)}">${fmt.esc(r.brand_group)}</td>
      <td>${r.hotel_count}</td>
      <td>${fmt.num(r.total_keys)}</td>
      <td>${fmt.pct(r.occupancy)}</td>
      <td>${fmt.mad(r.adr_mad)}</td>
      <td>${fmt.mad(r.revpar_mad)}</td>
      <td class="${gopClass(r.gop_margin)}">${fmt.pct(r.gop_margin)}</td>
    </tr>
  `).join('');

  const sub = document.getElementById('brand-table-sub');
  const dest = state.city === 'all' ? 'All destinations' : state.city;
  sub.textContent = `${dest} · ${rows.length} group${rows.length !== 1 ? 's' : ''}`;
}

// ─── Brand detail ─────────────────────────────────────────────────

function showBrandDetail(brandGroup) {
  brandHotelsData = hotels.filter(h => h.brand_group === brandGroup);

  const tk    = brandHotelsData.reduce((s, h) => s + h.keys, 0);
  const ok    = brandHotelsData.reduce((s, h) => s + h.keys * h.occupancy, 0);
  const occ   = ok / tk;
  const adr   = brandHotelsData.reduce((s, h) => s + h.adr_mad * h.keys * h.occupancy, 0) / ok;
  const revpar= brandHotelsData.reduce((s, h) => s + h.revpar_mad * h.keys, 0) / tk;
  const gop   = brandHotelsData.reduce((s, h) => s + h.gop_margin * h.keys, 0) / tk;

  const cities      = [...new Set(brandHotelsData.map(h => h.city))].sort();
  const ownerValues = [...new Set(brandHotelsData.map(h => h.owner).filter(Boolean))];
  const distinctOwners = ownerValues.filter(o => o !== 'Undisclosed');

  // Header
  document.getElementById('brand-detail-name').textContent = brandGroup;
  document.getElementById('brand-detail-sub').textContent =
    `${brandHotelsData.length} hotel${brandHotelsData.length !== 1 ? 's' : ''} · ${fmt.num(tk)} keys · ${cities.join(', ')}`;

  const ownerBadge = document.getElementById('brand-owner-badge');
  if (distinctOwners.length === 1) {
    ownerBadge.textContent = `Owned by ${distinctOwners[0]}`;
    ownerBadge.style.display = '';
  } else {
    ownerBadge.style.display = 'none';
  }

  // KPI cards
  const setKpi = (id, val) => {
    const el = document.getElementById(id);
    el.querySelector('.kpi-value').textContent = val;
  };
  setKpi('bkpi-keys',   fmt.num(tk));
  setKpi('bkpi-occ',    fmt.pct(occ));
  setKpi('bkpi-adr',    fmt.mad(adr));
  setKpi('bkpi-revpar', fmt.mad(revpar));
  setKpi('bkpi-gop',    fmt.pct(gop));

  // City RevPAR chart
  const cityData = cityAggs(brandHotelsData).sort((a, b) => b.revpar_mad - a.revpar_mad);
  const chartH   = Math.max(240, cityData.length * 38 + 50);
  document.getElementById('brand-chart-wrap').style.height = chartH + 'px';

  const labels = cityData.map(c => c.city);
  const values = cityData.map(c => c.revpar_mad);
  const colors = labels.map(() => CHART_ACCENT);

  if (brandChart) {
    brandChart.data.labels                          = labels;
    brandChart.data.datasets[0].data               = values;
    brandChart.data.datasets[0].backgroundColor    = colors;
    brandChart.update();
  } else {
    brandChart = new Chart(
      document.getElementById('chart-brand-revpar'),
      chartConfig(labels, values, ' MAD', colors, v => Math.round(v).toLocaleString('en'))
    );
  }

  // Hotel table
  document.getElementById('brand-hotels-title').textContent =
    `${brandHotelsData.length} hotel${brandHotelsData.length !== 1 ? 's' : ''}`;
  brandState.col = 'name';
  brandState.dir = 1;
  renderBrandHotelsTable();

  // Switch to brand screen
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-brand').classList.add('active');
}

function renderBrandHotelsTable() {
  const { col, dir } = brandState;
  const sorted = [...brandHotelsData].sort((a, b) => {
    const va = a[col], vb = b[col];
    if (BRAND_STR_COLS.has(col)) return dir * String(va).localeCompare(String(vb));
    return dir * (va - vb);
  });

  document.getElementById('brand-hotels-tbody').innerHTML = sorted.map(h => {
    const segColor = SEG_COLORS[h.category] || '#6b7280';
    return `<tr class="brand-hotel-row">
      <td class="hotel-name-cell">${fmt.esc(h.name)}</td>
      <td>${fmt.esc(h.city)}</td>
      <td><span class="seg-pip" style="background:${segColor};margin-right:7px"></span>${fmt.esc(h.category)}</td>
      <td>${fmt.num(h.keys)}</td>
      <td>${fmt.pct(h.occupancy)}</td>
      <td>${fmt.mad(h.adr_mad)}</td>
      <td>${fmt.mad(h.revpar_mad)}</td>
      <td class="${gopClass(h.gop_margin)}">${fmt.pct(h.gop_margin)}</td>
      <td>${fmt.esc(h.owner || '—')}</td>
    </tr>`;
  }).join('');

  document.querySelectorAll('#brand-hotels-table .sortable-col').forEach(th => {
    const icon = th.querySelector('.sort-icon');
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.bcol === col) {
      th.classList.add(dir === 1 ? 'sort-asc' : 'sort-desc');
      icon.textContent = dir === 1 ? '↑' : '↓';
    } else {
      icon.textContent = '↕';
    }
  });
}

// ─── Map ──────────────────────────────────────────────────────────

function markerRadius(h) {
  return Math.max(8, Math.sqrt(h.keys) * 0.78);
}

function popupHTML(h) {
  return `
    <div class="hiq-popup">
      <div class="hiq-popup-name">${fmt.esc(h.name)}</div>
      <div class="hiq-popup-meta">${fmt.esc(h.brand)} · ${fmt.esc(h.category)} · ${h.year_opened}</div>
      <div class="hiq-popup-grid">
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.num(h.keys)}</div>
          <div class="hiq-popup-stat-lbl">Keys</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.pct(h.occupancy)}</div>
          <div class="hiq-popup-stat-lbl">Occupancy</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.mad(h.adr_mad)}</div>
          <div class="hiq-popup-stat-lbl">ADR MAD</div>
        </div>
        <div class="hiq-popup-stat">
          <div class="hiq-popup-stat-val">${fmt.mad(h.revpar_mad)}</div>
          <div class="hiq-popup-stat-lbl">RevPAR MAD</div>
        </div>
      </div>
    </div>`;
}

const TILE_DARK  = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
const TILE_ATTR  = '&copy; <a href="https://carto.com/">CARTO</a>';

function swapMapTiles(mode) {
  if (!leaflet) return;
  leaflet.tileLayer.remove();
  leaflet.tileLayer = L.tileLayer(mode === 'light' ? TILE_LIGHT : TILE_DARK, {
    attribution: TILE_ATTR, subdomains: 'abcd', maxZoom: 18,
  }).addTo(leaflet.map);
}

function initMap() {
  const map = L.map('map-container', { zoomControl: true }).setView(MOROCCO_CENTER, MOROCCO_ZOOM);
  const isDark = !document.body.classList.contains('light');
  const tileLayer = L.tileLayer(isDark ? TILE_DARK : TILE_LIGHT, {
    attribution: TILE_ATTR, subdomains: 'abcd', maxZoom: 18,
  }).addTo(map);

  const markers = hotels.map(h => {
    const marker = L.circleMarker([h.lat, h.lng], {
      radius:      markerRadius(h),
      fillColor:   SEG_COLORS[h.category] || '#6b7280',
      color:       '#fff',
      weight:      1.2,
      opacity:     0.9,
      fillOpacity: 0.85,
    })
      .addTo(map)
      .bindPopup(popupHTML(h), { maxWidth: 280, minWidth: 240 });

    return { marker, hotel: h };
  });

  leaflet = { map, markers, tileLayer };
  updateMapMarkers();
}

function updateMapMarkers() {
  if (!leaflet) return;
  const { map, markers } = leaflet;
  let visible = 0;

  markers.forEach(({ marker, hotel: h }) => {
    const cityMatch = state.city === 'all' || h.city === state.city;
    const segMatch  = state.mapSeg === 'all' || h.category === state.mapSeg;
    if (cityMatch && segMatch) {
      marker.addTo(map);
      visible++;
    } else {
      marker.remove();
    }
  });

  const countEl = document.getElementById('map-count');
  if (countEl) countEl.textContent = visible + ' hotel' + (visible !== 1 ? 's' : '');
}

function panMap() {
  if (!leaflet) return;
  if (state.city === 'all') {
    leaflet.map.setView(MOROCCO_CENTER, MOROCCO_ZOOM, { animate: true });
  } else {
    const cityHotels = hotels.filter(h => h.city === state.city);
    if (cityHotels.length) {
      const lat = cityHotels.reduce((s, h) => s + h.lat, 0) / cityHotels.length;
      const lng = cityHotels.reduce((s, h) => s + h.lng, 0) / cityHotels.length;
      leaflet.map.setView([lat, lng], CITY_ZOOM, { animate: true });
    }
  }
}

// ─── Hotels screen ────────────────────────────────────────────────

const STRING_COLS = new Set(['name', 'city', 'category', 'brand_group', 'brand']);

const hotelsState = {
  query: '',
  city:  'all',
  seg:   'all',
  col:   'name',
  dir:   1,       // 1 = asc, -1 = desc
};

function filterHotels() {
  const q = hotelsState.query.trim().toLowerCase();
  return (hotels || []).filter(h => {
    if (hotelsState.city !== 'all' && h.city !== hotelsState.city) return false;
    if (hotelsState.seg  !== 'all' && h.category !== hotelsState.seg) return false;
    if (q) {
      const haystack = [h.name, h.city, h.brand, h.brand_group].join(' ').toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });
}

function sortHotels(list) {
  const { col, dir } = hotelsState;
  return [...list].sort((a, b) => {
    const va = a[col], vb = b[col];
    if (STRING_COLS.has(col)) return dir * String(va).localeCompare(String(vb));
    return dir * (va - vb);
  });
}

function syncHotelsSortIcons() {
  document.querySelectorAll('#hotels-table .sortable-col').forEach(th => {
    const icon = th.querySelector('.sort-icon');
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.col === hotelsState.col) {
      th.classList.add(hotelsState.dir === 1 ? 'sort-asc' : 'sort-desc');
      icon.textContent = hotelsState.dir === 1 ? '↑' : '↓';
    } else {
      icon.textContent = '↕';
    }
  });
}

function renderHotelsTable() {
  if (!hotels) return;
  const filtered = filterHotels();
  const sorted   = sortHotels(filtered);
  const total    = hotels.length;

  const tbody = document.getElementById('hotels-tbody');
  tbody.innerHTML = sorted.map(h => {
    const segColor = SEG_COLORS[h.category] || '#6b7280';
    return `<tr>
      <td class="hotel-name-cell">${fmt.esc(h.name)}</td>
      <td>${fmt.esc(h.city)}</td>
      <td><span class="seg-pip" style="background:${segColor};margin-right:7px"></span>${fmt.esc(h.category)}</td>
      <td>${fmt.esc(h.brand_group)}</td>
      <td>${fmt.num(h.keys)}</td>
      <td>${fmt.pct(h.occupancy)}</td>
      <td>${fmt.mad(h.adr_mad)}</td>
      <td>${fmt.mad(h.revpar_mad)}</td>
      <td class="${gopClass(h.gop_margin)}">${fmt.pct(h.gop_margin)}</td>
    </tr>`;
  }).join('');

  document.getElementById('hotels-footer').textContent =
    `Showing ${sorted.length} of ${total} hotel${total !== 1 ? 's' : ''}`;

  syncHotelsSortIcons();
}

// ─── Full render ──────────────────────────────────────────────────

function render() {
  renderKPIs();
  renderCharts();
  renderBrandTable();
  if (leaflet) {
    updateMapMarkers();
    panMap();
  }
}

// ─── Tourism screen ───────────────────────────────────────────────

const TOUR_EVENTS = [
  // Marrakech
  { city:'Marrakech',  name:'Marrakech Marathon',                    date:'January 2026',    attendance:'10,000+ runners',    type:'Sport'     },
  { city:'Marrakech',  name:'Oasis Festival',                        date:'October 2026',    attendance:'25,000',             type:'Music'     },
  { city:'Marrakech',  name:'Atlas Weekend',                         date:'July 2026',        attendance:'30,000',             type:'Music'     },
  { city:'Marrakech',  name:'Marrakech Airshow',                     date:'2026 (TBC)',       attendance:'TBC',                type:'Business'  },
  { city:'Marrakech',  name:'Marrakech International Film Festival', date:'November 2026',   attendance:'50,000+',            type:'Culture'   },
  // Casablanca
  { city:'Casablanca', name:'Morocco Traders Summit',                date:'March 2026',      attendance:'5,000 delegates',    type:'Business'  },
  { city:'Casablanca', name:'Casablanca Finance City Forum',         date:'April 2026',      attendance:'3,000 delegates',    type:'Business'  },
  // Agadir
  { city:'Agadir',     name:'International Agadir Fishing Festival', date:'April 2026',      attendance:'',                   type:'Culture'   },
  { city:'Agadir',     name:'Agadir Beach Soccer World Cup',         date:'May 2026',        attendance:'',                   type:'Sport'     },
  { city:'Agadir',     name:'Timitar Festival',                      date:'July 2026',        attendance:'300,000+',           type:'Music'     },
  // Fes
  { city:'Fes',        name:'Fes Festival of World Sacred Music',    date:'June 2026',       attendance:'80,000',             type:'Music'     },
  { city:'Fes',        name:'SIAM International Agriculture Fair',   date:'April 2026',      attendance:'1M+ visitors',       type:'Business'  },
  // Tanger
  { city:'Tanger',     name:'Tanger International Festival',         date:'August 2026',     attendance:'',                   type:'Culture'   },
  { city:'Tanger',     name:'Tanger Med Business Forum',             date:'September 2026',  attendance:'',                   type:'Business'  },
  // Essaouira
  { city:'Essaouira',  name:'Gnaoua World Music Festival',           date:'June 2026',       attendance:'450,000+ over 4 days', type:'Music'   },
  // Rabat
  { city:'Rabat',      name:'Mawazine Festival',                     date:'May–June 2026',   attendance:'2M+ total',          type:'Music'     },
  { city:'Rabat',      name:'Rabat International Fashion Week',      date:'March 2026',      attendance:'',                   type:'Culture'   },
  // Dakhla
  { city:'Dakhla',     name:'Dakhla Kitesurfing World Cup',          date:'August 2026',     attendance:'5,000+',             type:'Sport'     },
  { city:'Dakhla',     name:'Dakhla Atlantic Festival',              date:'July 2026',        attendance:'',                   type:'Culture'   },
  // National / Religious
  { city:'National',   name:'Eid Al Fitr 2026',                      date:'c. 30 March 2026', attendance:'National',          type:'Religious' },
  { city:'National',   name:'Eid Al Adha 2026',                      date:'c. 6–7 June 2026', attendance:'National',          type:'Religious' },
  { city:'National',   name:'Aid Al Mawlid 2026',                    date:'September 2026',  attendance:'National',           type:'Religious' },
];

const EVENT_TYPE_CLASS = {
  Sport: 'etype-sport', Culture: 'etype-culture', Music: 'etype-music',
  Business: 'etype-business', Religious: 'etype-religious',
};

function renderTourismEvents() {
  const cityOrder = ['Marrakech','Casablanca','Agadir','Fes','Tanger','Essaouira','Rabat','Dakhla','National'];
  const byCity = {};
  TOUR_EVENTS.forEach(ev => {
    if (!byCity[ev.city]) byCity[ev.city] = [];
    byCity[ev.city].push(ev);
  });

  document.getElementById('events-container').innerHTML = cityOrder
    .filter(c => byCity[c])
    .map(city => `
      <div class="events-city-group">
        <div class="events-city-header">${city === 'National' ? 'National / Religious' : city}</div>
        <div class="events-city-cards">
          ${byCity[city].map(ev => `
            <div class="event-card">
              <div class="event-card-top">
                <span class="event-type-pill ${EVENT_TYPE_CLASS[ev.type] || ''}">${fmt.esc(ev.type)}</span>
              </div>
              <div class="event-name">${fmt.esc(ev.name)}</div>
              <div class="event-meta">${fmt.esc(ev.date)}${ev.attendance ? ' · ' + fmt.esc(ev.attendance) : ''}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
}

function initTourismCharts() {
  if (tourismInited) return;

  // Set chart-wrap height: also zeroes min-height so CSS 360px default doesn't interfere
  const setH = (id, h) => {
    const el = document.getElementById(id);
    el.style.minHeight = '0';
    el.style.height = h + 'px';
  };

  const FC = '#f59e0b'; // forecast amber

  // ── Helper for vertical bar charts ──────────────────────────────
  function vBar(labels, values, bgColors, lblFmt, tipFmt) {
    return {
      type: 'bar',
      data: { labels, datasets: [{ data: values, backgroundColor: bgColors, borderRadius: 4, borderSkipped: false }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 28 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#2d3449', borderColor: '#3a4258', borderWidth: 1,
            titleColor: '#eceef4', bodyColor: '#8a96b0',
            padding: { top: 8, bottom: 8, left: 12, right: 12 },
            callbacks: { label: ctx => '  ' + tipFmt(ctx.raw) },
          },
          datalabels: {
            anchor: 'end', align: 'top', clip: false,
            color: '#8a96b0', font: { size: 11, weight: '600' },
            padding: { bottom: 2 }, formatter: lblFmt,
          },
        },
        scales: {
          x: { border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
          y: { border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
        },
      },
    };
  }

  // 1. International Arrivals Trend
  setH('twrap-arrivals', 290);
  const arrLbls = ['2020','2021','2022','2023','2024','2025','2026E'];
  const arrVals = [2.3, 5.2, 11.0, 14.5, 17.4, 20.1, 22.5];
  new Chart(document.getElementById('chart-tour-arrivals'),
    vBar(arrLbls, arrVals, arrLbls.map(l => l.endsWith('E') ? FC : CHART_ACCENT),
      v => v + 'M', v => v + 'M arrivals'));

  // 2. Arrivals by Mode of Transport (grouped)
  setH('twrap-transport', 290);
  new Chart(document.getElementById('chart-tour-transport'), {
    type: 'bar',
    data: {
      labels: ['2022','2023','2024','2025','2026E'],
      datasets: [
        { label: 'Air',  data: [7.2, 9.8, 12.1, 14.2, 15.8], backgroundColor: CHART_ACCENT, borderRadius: 3, borderSkipped: false },
        { label: 'Sea',  data: [2.8, 3.2,  3.8,  4.1,  4.6], backgroundColor: '#22c55e',    borderRadius: 3, borderSkipped: false },
        { label: 'Land', data: [1.0, 1.5,  1.5,  1.8,  2.1], backgroundColor: FC,           borderRadius: 3, borderSkipped: false },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
      layout: { padding: { top: 12 } },
      plugins: {
        legend: { display: true, labels: { color: CHART_TICK, font: { size: 11 }, boxWidth: 10, padding: 14 } },
        datalabels: { display: false },
        tooltip: {
          backgroundColor: '#2d3449', borderColor: '#3a4258', borderWidth: 1,
          titleColor: '#eceef4', bodyColor: '#8a96b0',
          callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}M` },
        },
      },
      scales: {
        x: { border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
        y: { border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
      },
    },
  });

  // 3. Origin Markets (horizontal)
  const origLbls = ['France','MRE','Spain','UK','Germany','Gulf States','USA','Italy','Other'];
  const origVals = [22, 18, 14, 10, 8, 7, 5, 4, 12];
  setH('twrap-origins', Math.max(260, origLbls.length * 34 + 50));
  const origCfg = chartConfig(origLbls, origVals, '%', origLbls.map(() => CHART_ACCENT), v => v + '%');
  origCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + '%';
  new Chart(document.getElementById('chart-tour-origins'), origCfg);

  // 4. Tourist Nights by Destination (horizontal, sorted asc so Marrakech is top)
  const nightsLbls = ['Other','Essaouira','Tanger','Fes','Casablanca','Agadir','Marrakech'];
  const nightsVals = [7.3, 1.6, 2.8, 3.6, 6.2, 12.4, 18.2];
  setH('twrap-nights', Math.max(240, nightsLbls.length * 34 + 50));
  const nightsCfg = chartConfig(nightsLbls, nightsVals, 'M', nightsLbls.map(() => CHART_ACCENT), v => v + 'M');
  nightsCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M nights';
  new Chart(document.getElementById('chart-tour-nights'), nightsCfg);

  // 5. Airport Traffic (horizontal, sorted asc so CMN is top)
  const airLbls = ['Nador NDR','Oujda OUD','Rabat RBA','Fes FEZ','Tanger TNG','Agadir AGA','Marrakech RAK','Casablanca CMN'];
  const airVals  = [0.6, 0.8, 1.1, 1.8, 2.1, 3.4, 6.8, 11.2];
  setH('twrap-airports', Math.max(260, airLbls.length * 34 + 50));
  const airCfg = chartConfig(airLbls, airVals, 'M pax', airLbls.map(() => '#60a5fa'), v => v + 'M');
  airCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M passengers';
  new Chart(document.getElementById('chart-tour-airports'), airCfg);

  // 6. Tourism Revenue Trend
  setH('twrap-revenue', 290);
  const revLbls = ['2020','2021','2022','2023','2024','2025','2026E'];
  const revVals = [34, 44, 76, 89, 105, 118, 132];
  new Chart(document.getElementById('chart-tour-revenue'),
    vBar(revLbls, revVals, revLbls.map(l => l.endsWith('E') ? FC : CHART_ACCENT),
      v => v + 'B', v => 'MAD ' + v + 'B'));

  // 7. Seasonality Index (line)
  setH('twrap-season', 220);
  new Chart(document.getElementById('chart-tour-season'), {
    type: 'line',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
      datasets: [{
        data: [55, 58, 72, 88, 95, 92, 100, 98, 82, 75, 60, 58],
        borderColor: CHART_ACCENT,
        backgroundColor: 'rgba(79,126,248,0.12)',
        fill: true, tension: 0.4,
        pointRadius: 4, pointBackgroundColor: CHART_ACCENT,
        pointBorderColor: '#1a1f2e', pointBorderWidth: 2,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
      layout: { padding: { top: 20 } },
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'top', align: 'top', clip: false,
          color: '#8a96b0', font: { size: 10, weight: '600' },
          formatter: v => v,
        },
        tooltip: {
          backgroundColor: '#2d3449', borderColor: '#3a4258', borderWidth: 1,
          titleColor: '#eceef4', bodyColor: '#8a96b0',
          callbacks: { label: ctx => '  Index: ' + ctx.raw },
        },
      },
      scales: {
        x: { border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
        y: { min: 0, max: 115, border: { display: false }, grid: { color: CHART_GRID }, ticks: { color: CHART_TICK, font: { size: 11 } } },
      },
    },
  });

  renderTourismEvents();
  tourismInited = true;
}

// ─── Events ───────────────────────────────────────────────────────

// Screen nav
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const screen = link.dataset.screen;
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    link.classList.add('active');
    document.getElementById('screen-' + screen).classList.add('active');

    if (screen === 'map') {
      if (!leaflet) {
        initMap();
      } else {
        setTimeout(() => leaflet.map.invalidateSize(), 60);
        updateMapMarkers();
        panMap();
      }
    }
    if (screen === 'hotels')  renderHotelsTable();
    if (screen === 'tourism') initTourismCharts();
  });
});

// City filter (sidebar)
document.getElementById('city-filter').addEventListener('click', e => {
  const item = e.target.closest('.sidebar-item');
  if (!item) return;
  document.querySelectorAll('#city-filter .sidebar-item').forEach(el => el.classList.remove('active'));
  item.classList.add('active');
  state.city = item.dataset.city;
  render();
});

// Map segment filter buttons
document.getElementById('map-seg-bar').addEventListener('click', e => {
  const btn = e.target.closest('.seg-btn');
  if (!btn) return;
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  state.mapSeg = btn.dataset.mapSeg;
  updateMapMarkers();
});

// Sidebar segment filter (mirrors map seg, visual only on dashboard)
document.getElementById('segment-sidebar').addEventListener('click', e => {
  const item = e.target.closest('.sidebar-item');
  if (!item) return;
  document.querySelectorAll('#segment-sidebar .sidebar-item').forEach(el => el.classList.remove('active'));
  item.classList.add('active');
  // Also sync map segment filter
  state.mapSeg = item.dataset.seg;
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.mapSeg === state.mapSeg);
  });
  if (leaflet) updateMapMarkers();
});

// Hotels: search
document.getElementById('hotels-search').addEventListener('input', e => {
  hotelsState.query = e.target.value;
  renderHotelsTable();
});

// Hotels: city pills
document.getElementById('hotels-city-pills').addEventListener('click', e => {
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('#hotels-city-pills .pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  hotelsState.city = pill.dataset.hcity;
  renderHotelsTable();
});

// Hotels: segment pills
document.getElementById('hotels-seg-pills').addEventListener('click', e => {
  const pill = e.target.closest('.pill');
  if (!pill) return;
  document.querySelectorAll('#hotels-seg-pills .pill').forEach(p => p.classList.remove('active'));
  pill.classList.add('active');
  hotelsState.seg = pill.dataset.hseg;
  renderHotelsTable();
});

// Hotels: column sort
document.getElementById('hotels-table').addEventListener('click', e => {
  const th = e.target.closest('.sortable-col');
  if (!th) return;
  const col = th.dataset.col;
  if (col === hotelsState.col) {
    hotelsState.dir *= -1;
  } else {
    hotelsState.col = col;
    hotelsState.dir = STRING_COLS.has(col) ? 1 : -1; // strings default asc, numbers default desc
  }
  renderHotelsTable();
});

// Brand table — click brand group name → brand detail
document.querySelector('#brand-table tbody').addEventListener('click', e => {
  const cell = e.target.closest('.brand-link');
  if (!cell) return;
  showBrandDetail(cell.dataset.brand);
});

// Brand detail — back to dashboard
document.getElementById('brand-back-btn').addEventListener('click', () => {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === 'dashboard')
  );
  document.getElementById('screen-dashboard').classList.add('active');
});

// Brand detail — hotel table column sort
document.getElementById('brand-hotels-table').addEventListener('click', e => {
  const th = e.target.closest('.sortable-col[data-bcol]');
  if (!th) return;
  const col = th.dataset.bcol;
  if (col === brandState.col) {
    brandState.dir *= -1;
  } else {
    brandState.col = col;
    brandState.dir = BRAND_STR_COLS.has(col) ? 1 : -1;
  }
  renderBrandHotelsTable();
});

// ─── AI Chat ──────────────────────────────────────────────────────

const chatHistory = [];   // { role: 'user' | 'assistant', content: string }
let chatBusy = false;

const chatThread  = document.getElementById('chat-thread');
const chatWelcome = document.getElementById('chat-welcome');
const chatTyping  = document.getElementById('chat-typing');
const chatInput   = document.getElementById('chat-input');
const chatSend    = document.getElementById('chat-send');

function mdRender(text) {
  if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') return fmt.esc(text);
  return DOMPurify.sanitize(marked.parse(text));
}

function appendMessage(role, content) {
  // Hide welcome state on first message
  if (chatWelcome) chatWelcome.style.display = 'none';

  const wrap = document.createElement('div');
  wrap.className = `chat-msg chat-msg-${role}`;

  if (role === 'assistant' || role === 'error') {
    const label = document.createElement('div');
    label.className = 'msg-label';
    label.textContent = 'HIQ Analyst';
    wrap.appendChild(label);
  }

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (role === 'user') {
    bubble.textContent = content;
  } else if (role === 'error') {
    wrap.classList.add('chat-msg-error');
    bubble.innerHTML = `<strong>Error:</strong> ${fmt.esc(content)}`;
  } else {
    bubble.innerHTML = mdRender(content);
  }

  wrap.appendChild(bubble);
  chatThread.appendChild(wrap);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function setLoading(on) {
  chatBusy = on;
  chatSend.disabled = on;
  chatInput.disabled = on;
  chatTyping.style.display = on ? 'flex' : 'none';
  if (on) chatThread.scrollTop = chatThread.scrollHeight;
}

async function sendChat(text) {
  text = text.trim();
  if (!text || chatBusy) return;

  chatInput.value = '';
  chatHistory.push({ role: 'user', content: text });
  appendMessage('user', text);
  setLoading(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chatHistory }),
    });
    const data = await res.json();

    if (data.error) {
      appendMessage('error', data.error);
    } else {
      chatHistory.push({ role: 'assistant', content: data.response });
      appendMessage('assistant', data.response);
    }
  } catch (err) {
    appendMessage('error', 'Network error — could not reach the server.');
  } finally {
    setLoading(false);
    chatInput.focus();
  }
}

// Send on button click
chatSend.addEventListener('click', () => sendChat(chatInput.value));

// Send on Enter (Shift+Enter = newline not applicable here since it's an input)
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChat(chatInput.value);
  }
});

// Starter chips
document.getElementById('chat-chips').addEventListener('click', e => {
  const chip = e.target.closest('.chat-chip');
  if (!chip) return;
  sendChat(chip.dataset.q);
});

// ─── Dynamic filters ──────────────────────────────────────────────

function buildCityFilter() {
  const cities = [...new Set(hotels.map(h => h.city))].sort();
  const list = document.getElementById('city-filter');
  list.querySelectorAll('[data-city]:not([data-city="all"])').forEach(el => el.remove());
  cities.forEach(city => {
    const li = document.createElement('li');
    li.className = 'sidebar-item';
    li.dataset.city = city;
    li.textContent = city;
    list.appendChild(li);
  });
}

function buildCityPills() {
  const cities = [...new Set(hotels.map(h => h.city))].sort();
  const bar = document.getElementById('hotels-city-pills');
  bar.querySelectorAll('[data-hcity]:not([data-hcity="all"])').forEach(el => el.remove());
  cities.forEach(city => {
    const btn = document.createElement('button');
    btn.className = 'pill';
    btn.dataset.hcity = city;
    btn.textContent = city;
    bar.appendChild(btn);
  });
}

// ─── Boot ─────────────────────────────────────────────────────────

async function boot() {
  [apiData, hotels] = await Promise.all([
    fetch('/api/data').then(r => r.json()),
    fetch('/api/hotels').then(r => r.json()),
  ]);
  buildCityFilter();
  buildCityPills();
  render();
}

boot();
