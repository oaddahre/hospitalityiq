// ─── Constants ────────────────────────────────────────────────────

const SEG_COLORS = {
  'Luxury':        '#7B52CC',
  'Upper Upscale': '#0A4A5A',
  'Upscale':       '#185FA5',
  'Midscale':      '#888580',
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

const CHART_ACCENT   = '#0A4A5A';
const CHART_DIM      = 'rgba(10,74,90,0.15)';
const CHART_GRID     = '#E2E0DA';
const CHART_TICK     = '#888580';

const KPI_DELTAS = {
  'kpi-keys':   { text: '+6.2% YoY',    up: true },
  'kpi-occ':    { text: '+3.1 pts YoY', up: true },
  'kpi-adr':    { text: '+8.4% YoY',    up: true },
  'kpi-revpar': { text: '+10.8% YoY',   up: true },
};

Chart.register(ChartDataLabels);

// Global: no grid lines, tick marks or axis borders on any chart
Chart.defaults.scale.grid.display   = false;
Chart.defaults.scale.grid.drawTicks = false;
Chart.defaults.scale.border.display = false;

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
let pipelineInited  = false;
let pipelineData    = null;
let pipelineLeaflet = null;
const pipelineState = { status: 'all', city: 'all', category: 'all' };
const pipelineSort  = { col: 'expected_opening', dir: 1 };
const PIPE_STR_COLS = new Set(['name', 'city', 'category', 'brand', 'status']);

let hotelDetailPrevScreen = 'hotels';
let hotelCityChart        = null;

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
  localStorage.setItem('kodo-theme', next);
  applyTheme(next);
  redrawChartsForTheme();
});

applyTheme(localStorage.getItem('kodo-theme') || 'light');

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

function getChartColors() {
  const dark = !document.body.classList.contains('light');
  return {
    tick:       dark ? '#6A7A88' : '#888580',
    label:      dark ? '#C8D0D8' : '#111111',
    catLabel:   dark ? '#C8D0D8' : '#111111',
    tooltipBg:  dark ? '#1A2430' : '#FFFFFF',
    tooltipBdr: dark ? '#1E2D3A' : '#E2E0DA',
    tooltipTtl: dark ? '#E8EAE8' : '#111111',
    tooltipBdy: dark ? '#6A7A88' : '#888580',
  };
}

function chartConfig(labels, values, tooltipSuffix, bgColors, labelFmt) {
  const cc = getChartColors();
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
          backgroundColor: cc.tooltipBg,
          borderColor: cc.tooltipBdr,
          borderWidth: 1,
          titleColor: cc.tooltipTtl,
          bodyColor: cc.tooltipBdy,
          padding: { top: 8, bottom: 8, left: 12, right: 12 },
          callbacks: {
            label: ctx => '  ' + Math.round(ctx.raw).toLocaleString('en') + tooltipSuffix,
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'right',
          clip: false,
          color: cc.label,
          font: { size: 11, weight: '600' },
          padding: { left: 5 },
          formatter: labelFmt,
        },
      },
      scales: {
        x: {
          min: 0,
          ticks: { color: cc.tick, font: { size: 11 } }
        },
        y: {
          ticks: { color: cc.catLabel, font: { size: 12, weight: '500' } }
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
      <td><button class="brand-link" data-brand="${fmt.esc(r.brand_group)}" onclick="showBrandDetail(this.dataset.brand)">${fmt.esc(r.brand_group)}</button></td>
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
  console.log('clicked brand:', brandGroup);
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
  setKpi('brand-bkpi-keys',   fmt.num(tk));
  setKpi('brand-bkpi-occ',    fmt.pct(occ));
  setKpi('brand-bkpi-adr',    fmt.mad(adr));
  setKpi('brand-bkpi-revpar', fmt.mad(revpar));
  setKpi('brand-bkpi-gop',    fmt.pct(gop));

  // Switch to brand screen FIRST so the canvas has visible dimensions for Chart.js
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-brand').classList.add('active');
  setSidebar('brand');

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

}

function renderBrandHotelsTable() {
  const { col, dir } = brandState;
  const sorted = [...brandHotelsData].sort((a, b) => {
    const va = a[col], vb = b[col];
    if (BRAND_STR_COLS.has(col)) return dir * String(va).localeCompare(String(vb));
    return dir * (va - vb);
  });

  document.getElementById('brand-hotels-tbody').innerHTML = sorted.map(h => {
    const segColor = SEG_COLORS[h.category] || '#888580';
    return `<tr class="brand-hotel-row">
      <td class="hotel-name-cell"><button class="hotel-name-btn" onclick="showHotelDetail(${h.id})">${fmt.esc(h.name)}</button></td>
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

// ─── Hotel detail ─────────────────────────────────────────────────

const OWNER_CONTEXT = {
  'Risma':        'Accor Morocco listed subsidiary (Bourse de Casablanca)',
  'Madaëf':       'CDG Group hospitality arm',
  'Royal':        'Royal Mansour Collection — Royal hospitality group',
  'Marchica Med': 'State-owned development agency',
  'Club Med':     'Club Med — owned by Fosun International',
};

async function showHotelDetail(id) {
  const h = hotels.find(x => +x.id === +id);
  if (!h) return;

  // Remember which screen we came from
  const active = document.querySelector('.screen.active');
  hotelDetailPrevScreen = active ? active.id.replace('screen-', '') : 'hotels';

  // Switch screen first so Chart.js canvas has visible dimensions
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('screen-hotel').classList.add('active');
  setSidebar('hotel');

  // ── 1. Header ──
  document.getElementById('hotel-hd-name').textContent = h.name;
  document.getElementById('hotel-hd-sub').textContent =
    `${h.brand} · ${h.city} · ${h.category}`;

  const ownerLine = document.getElementById('hotel-hd-owner');
  if (h.owner && h.owner !== 'Undisclosed') {
    ownerLine.textContent = `Owner: ${h.owner}`;
    ownerLine.style.display = '';
  } else {
    ownerLine.style.display = 'none';
  }

  document.getElementById('hotel-hd-year').textContent =
    h.year_opened ? `Opened ${h.year_opened}` : '';

  const dqEl = document.getElementById('hotel-hd-dq');
  if ((h.data_quality || '').toLowerCase().startsWith('verified')) {
    dqEl.textContent = 'Verified';
    dqEl.className   = 'hotel-dq-badge dq-verified';
  } else {
    dqEl.textContent = 'Kōdō Estimate';
    dqEl.className   = 'hotel-dq-badge dq-estimate';
  }

  // ── 2. KPI cards ──
  const setKv = (id, v) => document.getElementById(id).querySelector('.kpi-value').textContent = v;
  setKv('hkpi-keys',   fmt.num(h.keys));
  setKv('hkpi-occ',    fmt.pct(h.occupancy));
  setKv('hkpi-adr',    fmt.mad(h.adr_mad));
  setKv('hkpi-revpar', fmt.mad(h.revpar_mad));
  setKv('hkpi-gop',    fmt.pct(h.gop_margin));

  // ── 3. Estimated financials ──
  const roomsRev = h.adr_mad * h.occupancy * h.keys * 365 / 1e6;
  const totalRev = (h.trevpar_mad || h.revpar_mad / h.occupancy * 1.35) * h.keys * 365 / 1e6;
  const gopMad   = totalRev * h.gop_margin;
  const assetVal = gopMad * 0.85 / 0.072;

  const madM = v => `MAD ${v < 1000 ? v.toFixed(0) : (v / 1000).toFixed(1) + 'B'}M`.replace('BMM', 'B');
  document.getElementById('hfin-rooms').textContent  = `MAD ${roomsRev.toFixed(0)}M`;
  document.getElementById('hfin-total').textContent  = `MAD ${totalRev.toFixed(0)}M`;
  document.getElementById('hfin-gop').textContent    = `MAD ${gopMad.toFixed(0)}M`;
  document.getElementById('hfin-asset').textContent  = assetVal >= 1000
    ? `MAD ${(assetVal / 1000).toFixed(1)}B`
    : `MAD ${assetVal.toFixed(0)}M`;

  // ── 4. Market context chart ──
  document.getElementById('hotel-ctx-city').textContent = h.city;
  renderHotelCityChart(h);

  // ── 5. Segment benchmarks ──
  renderHotelSegBench(h);

  // ── 6. Brand info ──
  const brandCount = hotels.filter(x => x.brand_group === h.brand_group).length;
  document.getElementById('hotel-brand-name').textContent  = h.brand_group;
  document.getElementById('hotel-brand-count').textContent = brandCount;
  const brandBtn = document.getElementById('hotel-brand-link');
  brandBtn.textContent     = `View all ${h.brand_group} properties →`;
  brandBtn.dataset.brand   = h.brand_group;

  // ── 7. Pipeline ──
  document.getElementById('hotel-pipe-city').textContent = h.city;
  await renderHotelPipeline(h);

  // ── 8. Owner section ──
  renderOwnerSection(h);
}

function renderHotelCityChart(h) {
  const cityHotels = hotels
    .filter(x => x.city === h.city)
    .sort((a, b) => b.revpar_mad - a.revpar_mad);

  const labels = cityHotels.map(x =>
    +x.id === +h.id ? `▶ ${x.name}` : x.name
  );
  const values = cityHotels.map(x => x.revpar_mad);
  const colors = cityHotels.map(x => +x.id === +h.id ? CHART_ACCENT : CHART_DIM);

  const chartH = Math.max(200, cityHotels.length * 30 + 50);
  document.getElementById('hotel-city-chart-wrap').style.height = chartH + 'px';

  if (hotelCityChart) {
    hotelCityChart.data.labels                       = labels;
    hotelCityChart.data.datasets[0].data             = values;
    hotelCityChart.data.datasets[0].backgroundColor  = colors;
    hotelCityChart.update();
  } else {
    hotelCityChart = new Chart(
      document.getElementById('chart-hotel-city'),
      chartConfig(labels, values, ' MAD', colors, v => Math.round(v).toLocaleString('en'))
    );
  }
}

function renderHotelSegBench(h) {
  const peers = hotels.filter(x => x.city === h.city && x.category === h.category && +x.id !== +h.id);
  const bench  = document.getElementById('hotel-seg-bench');
  const ctxEl  = document.getElementById('hotel-bench-ctx');

  ctxEl.textContent = `${h.category} · ${h.city} average (${peers.length} peer${peers.length !== 1 ? 's' : ''})`;

  if (!peers.length) {
    bench.innerHTML = `<p class="hbench-no-peers">No comparable ${h.category} hotels in ${h.city}.</p>`;
    return;
  }

  const tk     = peers.reduce((s, x) => s + x.keys, 0);
  const ok     = peers.reduce((s, x) => s + x.keys * x.occupancy, 0);
  const avgOcc = ok / tk;
  const avgAdr = peers.reduce((s, x) => s + x.adr_mad * x.keys * x.occupancy, 0) / ok;
  const avgRev = peers.reduce((s, x) => s + x.revpar_mad * x.keys, 0) / tk;

  const metrics = [
    {
      label: 'Occupancy',
      mine: h.occupancy,     avg: avgOcc,
      fmtVal: v => fmt.pct(v),
      fmtDiff: d => (d >= 0 ? '+' : '') + (d * 100).toFixed(1) + ' pts',
      isPos: h.occupancy >= avgOcc,
    },
    {
      label: 'ADR (MAD)',
      mine: h.adr_mad,       avg: avgAdr,
      fmtVal: v => fmt.mad(v),
      fmtDiff: d => (d >= 0 ? '+' : '−') + 'MAD ' + fmt.mad(Math.abs(d)),
      isPos: h.adr_mad >= avgAdr,
    },
    {
      label: 'RevPAR (MAD)',
      mine: h.revpar_mad,    avg: avgRev,
      fmtVal: v => fmt.mad(v),
      fmtDiff: d => (d >= 0 ? '+' : '−') + 'MAD ' + fmt.mad(Math.abs(d)),
      isPos: h.revpar_mad >= avgRev,
    },
  ];

  bench.innerHTML = metrics.map(m => {
    const top      = Math.max(m.mine, m.avg) * 1.12 || 1;
    const mineW    = Math.round((m.mine / top) * 100);
    const avgW     = Math.round((m.avg  / top) * 100);
    const diff     = m.mine - m.avg;
    return `<div class="hbench-row">
      <div class="hbench-label">${m.label}</div>
      <div class="hbench-bars">
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">This hotel</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill accent" style="width:${mineW}%"></div></div>
          <span class="hbench-val">${m.fmtVal(m.mine)}</span>
        </div>
        <div class="hbench-bar-row">
          <span class="hbench-bar-lbl">Peers avg</span>
          <div class="hbench-bar-track"><div class="hbench-bar-fill muted" style="width:${avgW}%"></div></div>
          <span class="hbench-val">${m.fmtVal(m.avg)}</span>
        </div>
      </div>
      <span class="hbench-diff ${m.isPos ? 'up' : 'down'}">${m.fmtDiff(diff)}</span>
    </div>`;
  }).join('');
}

async function renderHotelPipeline(h) {
  const content = document.getElementById('hotel-pipe-content');
  if (!pipelineData) {
    content.innerHTML = '<p class="hpipe-empty">Loading pipeline data…</p>';
    try {
      pipelineData = await fetch('/api/pipeline').then(r => r.json());
    } catch {
      content.innerHTML = '<p class="hpipe-empty">Pipeline data unavailable.</p>';
      return;
    }
  }

  const cityPipe = pipelineData.filter(p => p.city === h.city);
  if (!cityPipe.length) {
    content.innerHTML = `<p class="hpipe-empty">No confirmed pipeline in ${fmt.esc(h.city)}.</p>`;
    return;
  }

  const totalKeys = cityPipe.reduce((s, p) => s + p.keys, 0);
  const lastYear  = Math.max(...cityPipe.map(p => p.expected_opening));
  const items = cityPipe.map(p => `
    <div class="hpipe-item">
      <div class="hpipe-item-name">${fmt.esc(p.name)}</div>
      <span class="hpipe-item-meta">${fmt.esc(p.brand)} · ${p.keys} keys · ${p.expected_opening}</span>
      <span class="${p.status === 'Under Construction' ? 'pipe-status-uc' : 'pipe-status-pl'}">${fmt.esc(p.status)}</span>
    </div>`).join('');

  content.innerHTML = `
    <p class="hpipe-summary">${totalKeys.toLocaleString('en')} new keys entering ${fmt.esc(h.city)} by ${lastYear}</p>
    <div class="hpipe-list">${items}</div>`;
}

function renderOwnerSection(h) {
  const section = document.getElementById('hotel-owner-section');
  if (!h.owner || h.owner === 'Undisclosed') {
    section.style.display = 'none';
    return;
  }
  section.style.display = '';
  document.getElementById('hotel-owner-name').textContent = h.owner;

  let ctx = '';
  for (const [key, val] of Object.entries(OWNER_CONTEXT)) {
    if (h.owner.includes(key)) { ctx = val; break; }
  }
  const ctxEl = document.getElementById('hotel-owner-ctx');
  if (ctx) {
    ctxEl.textContent     = ctx;
    ctxEl.style.display   = '';
  } else {
    ctxEl.style.display   = 'none';
  }
}

// ─── Map ──────────────────────────────────────────────────────────

function markerRadius(h) {
  return Math.max(8, Math.sqrt(h.keys) * 0.78);
}

function popupHTML(h) {
  return `
    <div class="hiq-popup">
      <button class="hiq-popup-name-btn" onclick="showHotelDetail(${h.id})">${fmt.esc(h.name)}</button>
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
      <button class="hiq-popup-profile-btn" onclick="showHotelDetail(${h.id})">View full profile →</button>
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
  if (pipelineLeaflet) {
    pipelineLeaflet.tileLayer.remove();
    pipelineLeaflet.tileLayer = L.tileLayer(mode === 'light' ? TILE_LIGHT : TILE_DARK, {
      attribution: TILE_ATTR, subdomains: 'abcd', maxZoom: 18,
    }).addTo(pipelineLeaflet.map);
  }
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
      fillColor:   SEG_COLORS[h.category] || '#888580',  // map marker
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

  const filteredCities = new Set(filtered.map(h => h.city)).size;
  document.getElementById('hotels-sub').textContent =
    `${filtered.length} hotel${filtered.length !== 1 ? 's' : ''} · ${filteredCities} ${filteredCities !== 1 ? 'cities' : 'city'} · All performance: Kōdō estimates 2025`;

  const tbody = document.getElementById('hotels-tbody');
  tbody.innerHTML = sorted.map(h => {
    const segColor = SEG_COLORS[h.category] || '#888580';
    return `<tr class="hotel-row-link" onclick="showHotelDetail(${h.id})">
      <td class="hotel-name-cell"><button class="hotel-name-btn">${fmt.esc(h.name)}</button></td>
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

// ─── Redraw all charts on theme change ────────────────────────────

function redrawChartsForTheme() {
  // Dashboard bar charts
  if (revChart) { revChart.destroy(); revChart = null; }
  if (occChart)  { occChart.destroy();  occChart = null; }
  if (hotels) renderCharts();

  // Pipeline charts
  if (pipelineChartProj) { pipelineChartProj.destroy(); pipelineChartProj = null; }
  if (pipelineChartCity) { pipelineChartCity.destroy(); pipelineChartCity = null; }
  if (pipelineInited && pipelineData) renderPipelineCharts();

  // Tourism charts — destroy and reset flag; reinit if screen is active
  if (tourismInited) {
    ['chart-tour-arrivals','chart-tour-transport','chart-tour-origins',
     'chart-tour-nights','chart-tour-airports','chart-tour-revenue','chart-tour-season',
    ].forEach(id => { const c = Chart.getChart(id); if (c) c.destroy(); });
    tourismInited = false;
    const tourismEl = document.getElementById('screen-tourism');
    if (tourismEl && tourismEl.classList.contains('active')) {
      initTourismCharts();
    }
  }

  // Benchmarking trend + DOW charts
  if (benchTrendRevpar) { benchTrendRevpar.destroy(); benchTrendRevpar = null; }
  if (benchTrendOcc)    { benchTrendOcc.destroy();    benchTrendOcc    = null; }
  if (benchDOWChart)    { benchDOWChart.destroy();     benchDOWChart    = null; }
  if (benchmarkInited && benchmarkData) { renderBenchTrends(); renderBenchDOW(); }

  // Brand detail chart — recreate if screen is currently visible
  if (brandChart) { brandChart.destroy(); brandChart = null; }
  const brandScreen = document.getElementById('screen-brand');
  if (brandScreen && brandScreen.classList.contains('active') && brandHotelsData.length) {
    const cityData = cityAggs(brandHotelsData).sort((a, b) => b.revpar_mad - a.revpar_mad);
    const labels = cityData.map(c => c.city);
    const values = cityData.map(c => c.revpar_mad);
    document.getElementById('brand-chart-wrap').style.height = Math.max(240, labels.length * 38 + 50) + 'px';
    brandChart = new Chart(
      document.getElementById('chart-brand-revpar'),
      chartConfig(labels, values, ' MAD', labels.map(() => CHART_ACCENT), v => Math.round(v).toLocaleString('en'))
    );
  }

  // Hotel city chart — recreate if screen is currently visible
  if (hotelCityChart) { hotelCityChart.destroy(); hotelCityChart = null; }
  const hotelScreen = document.getElementById('screen-hotel');
  if (hotelScreen && hotelScreen.classList.contains('active') && hotels) {
    const nameEl = document.getElementById('hotel-hd-name');
    const h = nameEl && hotels.find(x => x.name === nameEl.textContent);
    if (h) renderHotelCityChart(h);
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

const TOUR_NIGHTS_DATA = {
  labels: ['Other','Essaouira','Tanger','Fes','Casablanca','Agadir','Marrakech'],
  years: {
    2021: [2.8, 0.6, 1.1, 1.4, 2.8, 6.2, 8.1],
    2022: [4.8, 1.0, 1.8, 2.2, 4.2, 9.1, 12.4],
    2023: [6.1, 1.2, 2.2, 2.9, 5.1, 10.8, 15.2],
    2024: [6.8, 1.4, 2.5, 3.2, 5.7, 11.6, 16.8],
    2025: [7.3, 1.6, 2.8, 3.6, 6.2, 12.4, 18.2],
  },
};

const TOUR_AIRPORT_DATA = {
  labels: ['Nador NDR','Oujda OUD','Rabat RBA','Fes FEZ','Tanger TNG','Agadir AGA','Marrakech RAK','Casablanca CMN'],
  years: {
    2021: [0.2, 0.3, 0.4, 0.6, 0.8, 1.2, 2.1, 4.2],
    2022: [0.4, 0.5, 0.7, 1.1, 1.4, 2.1, 4.2, 7.8],
    2023: [0.5, 0.6, 0.9, 1.4, 1.7, 2.8, 5.6, 9.4],
    2024: [0.55, 0.7, 1.0, 1.6, 1.9, 3.1, 6.2, 10.6],
    2025: [0.6, 0.8, 1.1, 1.8, 2.1, 3.4, 6.8, 11.2],
  },
};

const TOUR_ORIGINS_DATA = {
  labels: ['France','MRE','Spain','UK','Germany','Gulf States','USA','Italy','Other'],
  years: {
    2021: [24, 20, 12, 9, 7, 5, 4, 3, 16],
    2022: [23, 19, 13, 10, 7, 6, 4, 3, 15],
    2023: [23, 18, 14, 10, 8, 6, 5, 4, 12],
    2024: [22, 18, 14, 10, 8, 7, 5, 4, 12],
    2025: [22, 18, 14, 10, 8, 7, 5, 4, 12],
  },
};

function initTourismCharts() {
  if (tourismInited) return;

  // Set chart-wrap height: also zeroes min-height so CSS 360px default doesn't interfere
  const setH = (id, h) => {
    const el = document.getElementById(id);
    el.style.minHeight = '0';
    el.style.height = h + 'px';
  };

  const FC = '#B8922A'; // forecast amber

  const addYearTabs = (canvasId, data) => {
    const canvas = document.getElementById(canvasId);
    const wrap = canvas.closest('.chart-wrap');
    const tabsDiv = document.createElement('div');
    tabsDiv.className = 'chart-year-tabs';
    [2021, 2022, 2023, 2024, 2025].forEach(yr => {
      const btn = document.createElement('button');
      btn.className = 'chart-year-tab' + (yr === 2025 ? ' active' : '');
      btn.textContent = yr;
      btn.addEventListener('click', () => {
        tabsDiv.querySelectorAll('.chart-year-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const chart = Chart.getChart(canvas);
        if (chart) { chart.data.datasets[0].data = data.years[yr]; chart.update(); }
      });
      tabsDiv.appendChild(btn);
    });
    wrap.parentNode.insertBefore(tabsDiv, wrap);
  };

  // ── Helper for vertical bar charts ──────────────────────────────
  function vBar(labels, values, bgColors, lblFmt, tipFmt) {
    const cc = getChartColors();
    return {
      type: 'bar',
      data: { labels, datasets: [{ data: values, backgroundColor: bgColors, borderRadius: 4, borderSkipped: false }] },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 28 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            padding: { top: 8, bottom: 8, left: 12, right: 12 },
            callbacks: { label: ctx => '  ' + tipFmt(ctx.raw) },
          },
          datalabels: {
            anchor: 'end', align: 'top', clip: false,
            color: cc.label, font: { size: 11, weight: '600' },
            padding: { bottom: 2 }, formatter: lblFmt,
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
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
  {
    const cc = getChartColors();
    new Chart(document.getElementById('chart-tour-transport'), {
      type: 'bar',
      data: {
        labels: ['2022','2023','2024','2025','2026E'],
        datasets: [
          { label: 'Air',  data: [7.2, 9.8, 12.1, 14.2, 15.8], backgroundColor: CHART_ACCENT, borderRadius: 3, borderSkipped: false },
          { label: 'Sea',  data: [2.8, 3.2,  3.8,  4.1,  4.6], backgroundColor: '#1A6B3C',    borderRadius: 3, borderSkipped: false },
          { label: 'Land', data: [1.0, 1.5,  1.5,  1.8,  2.1], backgroundColor: FC,            borderRadius: 3, borderSkipped: false },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 12 } },
        plugins: {
          legend: { display: true, labels: { color: cc.tick, font: { size: 11 }, boxWidth: 10, padding: 14 } },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}M` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }

  // 3. Origin Markets (horizontal, with year tabs)
  const origLbls = TOUR_ORIGINS_DATA.labels;
  const origVals = TOUR_ORIGINS_DATA.years[2025];
  setH('twrap-origins', Math.max(260, origLbls.length * 34 + 50));
  const origCfg = chartConfig(origLbls, origVals, '%', origLbls.map(() => CHART_ACCENT), v => v + '%');
  origCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + '%';
  new Chart(document.getElementById('chart-tour-origins'), origCfg);
  addYearTabs('chart-tour-origins', TOUR_ORIGINS_DATA);

  // 4. Tourist Nights by Destination (horizontal, sorted asc so Marrakech is top, with year tabs)
  const nightsLbls = TOUR_NIGHTS_DATA.labels;
  const nightsVals = TOUR_NIGHTS_DATA.years[2025];
  setH('twrap-nights', Math.max(240, nightsLbls.length * 34 + 50));
  const nightsCfg = chartConfig(nightsLbls, nightsVals, 'M', nightsLbls.map(() => CHART_ACCENT), v => v + 'M');
  nightsCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M nights';
  new Chart(document.getElementById('chart-tour-nights'), nightsCfg);
  addYearTabs('chart-tour-nights', TOUR_NIGHTS_DATA);

  // 5. Airport Traffic (horizontal, sorted asc so CMN is top, with year tabs)
  const airLbls = TOUR_AIRPORT_DATA.labels;
  const airVals  = TOUR_AIRPORT_DATA.years[2025];
  setH('twrap-airports', Math.max(260, airLbls.length * 34 + 50));
  const airCfg = chartConfig(airLbls, airVals, 'M pax', airLbls.map(() => '#185FA5'), v => v + 'M');
  airCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + 'M passengers';
  new Chart(document.getElementById('chart-tour-airports'), airCfg);
  addYearTabs('chart-tour-airports', TOUR_AIRPORT_DATA);

  // 6. Tourism Revenue Trend
  setH('twrap-revenue', 290);
  const revLbls = ['2020','2021','2022','2023','2024','2025','2026E'];
  const revVals = [34, 44, 76, 89, 105, 118, 132];
  new Chart(document.getElementById('chart-tour-revenue'),
    vBar(revLbls, revVals, revLbls.map(l => l.endsWith('E') ? FC : CHART_ACCENT),
      v => v + 'B', v => 'MAD ' + v + 'B'));

  // 7. Seasonality Index (line)
  setH('twrap-season', 220);
  {
    const cc = getChartColors();
    new Chart(document.getElementById('chart-tour-season'), {
      type: 'line',
      data: {
        labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        datasets: [{
          data: [55, 58, 72, 88, 95, 92, 100, 98, 82, 75, 60, 58],
          borderColor: CHART_ACCENT,
          backgroundColor: 'rgba(10,74,90,0.08)',
          fill: false, tension: 0.4,
          pointRadius: 4, pointBackgroundColor: CHART_ACCENT,
          pointBorderColor: '#F4F3F0', pointBorderWidth: 2,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        layout: { padding: { top: 20 } },
        plugins: {
          legend: { display: false },
          datalabels: {
            anchor: 'top', align: 'top', clip: false,
            color: cc.label, font: { size: 10, weight: '600' },
            formatter: v => v,
          },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => '  Index: ' + ctx.raw },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { min: 0, max: 115, ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }

  renderTourismEvents();
  tourismInited = true;
}

// ─── Pipeline screen ──────────────────────────────────────────────

async function initPipeline() {
  if (pipelineInited) {
    if (pipelineLeaflet) setTimeout(() => pipelineLeaflet.map.invalidateSize(), 60);
    return;
  }
  pipelineInited = true;

  const res = await fetch('/api/pipeline');
  if (res.status === 403) {
    const err = await res.json().catch(() => ({}));
    if (err.error === 'upgrade_required') {
      pipelineInited = false;
      if (typeof showUpgradeModal === 'function') showUpgradeModal('Pipeline requires Benchmarker', err.message);
      return;
    }
  }
  pipelineData = await res.json();

  // Populate filter dropdowns
  const cities = [...new Set(pipelineData.map(p => p.city))].sort();
  const cats   = [...new Set(pipelineData.map(p => p.category))].sort();
  const cityEl = document.getElementById('pipe-city-filter');
  const catEl  = document.getElementById('pipe-cat-filter');
  cities.forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; cityEl.appendChild(o); });
  cats.forEach(c   => { const o = document.createElement('option'); o.value = c; o.textContent = c; catEl.appendChild(o); });

  renderPipelineKPIs();
  renderPipelineCards();
  renderPipelineCharts();
  setTimeout(initPipelineMap, 120);
}

function filteredPipeline() {
  return pipelineData.filter(p =>
    (pipelineState.status === 'all'   || p.status   === pipelineState.status) &&
    (pipelineState.city   === 'all'   || p.city     === pipelineState.city)   &&
    (pipelineState.category === 'all' || p.category === pipelineState.category)
  );
}

function renderPipelineKPIs() {
  const all = pipelineData;
  const totalKeys = all.reduce((s, p) => s + p.keys, 0);
  const totalInv  = all.reduce((s, p) => s + p.investment_mad, 0);
  const by2027    = all.filter(p => p.expected_opening <= 2027).length;

  const setKpi = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.querySelector('.kpi-value').textContent = val;
  };
  setKpi('pkpi-total', all.length);
  setKpi('pkpi-keys',  totalKeys.toLocaleString('en'));
  setKpi('pkpi-inv',   (totalInv / 1e9).toFixed(1) + 'B');
  setKpi('pkpi-2027',  by2027);
}

function initPipelineMap() {
  const container = document.getElementById('pipeline-map-container');
  if (!container) return;
  const isDark = !document.body.classList.contains('light');
  const map = L.map('pipeline-map-container', { zoomControl: true }).setView(MOROCCO_CENTER, 6);
  const tileLayer = L.tileLayer(isDark ? TILE_DARK : TILE_LIGHT, {
    attribution: TILE_ATTR, subdomains: 'abcd', maxZoom: 18,
  }).addTo(map);

  const markers = pipelineData.map(p => {
    const color = p.status === 'Under Construction' ? '#B8922A' : '#0A4A5A';
    const radius = Math.max(8, Math.sqrt(p.keys) * 0.85);
    const marker = L.circleMarker([p.lat, p.lng], {
      radius, fillColor: color, color: '#fff',
      weight: 1.5, opacity: 0.9, fillOpacity: 0.85,
    }).addTo(map).bindPopup(pipelinePopupHTML(p), { maxWidth: 280, minWidth: 240 });
    return { marker, project: p };
  });

  pipelineLeaflet = { map, markers, tileLayer };
}

function pipelinePopupHTML(p) {
  const invB = (p.investment_mad / 1e9).toFixed(2);
  const statusPill = p.status === 'Under Construction'
    ? `<span style="background:rgba(184,146,42,0.15);color:#854F0B;border:1px solid rgba(184,146,42,0.4);border-radius:3px;padding:1px 6px;font-size:10px;font-weight:700">${p.status}</span>`
    : `<span style="background:rgba(10,74,90,0.12);color:#0A4A5A;border:1px solid rgba(10,74,90,0.35);border-radius:3px;padding:1px 6px;font-size:10px;font-weight:700">${p.status}</span>`;
  return `<div class="hiq-popup">
    <div class="hiq-popup-name">${fmt.esc(p.name)}</div>
    <div class="hiq-popup-meta">${fmt.esc(p.brand)} · ${fmt.esc(p.category)}</div>
    <div class="hiq-popup-grid">
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${p.keys}</div><div class="hiq-popup-stat-lbl">Keys</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${p.expected_opening}</div><div class="hiq-popup-stat-lbl">Opening</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">MAD ${invB}B</div><div class="hiq-popup-stat-lbl">Investment</div></div>
      <div class="hiq-popup-stat"><div class="hiq-popup-stat-val">${statusPill}</div><div class="hiq-popup-stat-lbl">Status</div></div>
    </div>
  </div>`;
}

let pipelineChartProj = null;
let pipelineChartCity = null;

function renderPipelineCards() {
  const data = filteredPipeline();
  const grid = document.getElementById('pipe-cards-grid');
  const countEl = document.getElementById('pipe-count');
  if (countEl) countEl.textContent = data.length + ' project' + (data.length !== 1 ? 's' : '');

  if (!data.length) {
    grid.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:8px 0">No projects match the selected filters.</p>';
    return;
  }
  grid.innerHTML = data.map(p => {
    const isUC = p.status === 'Under Construction';
    const pill  = isUC ? `<span class="pipe-status-uc">${p.status}</span>` : `<span class="pipe-status-pl">${p.status}</span>`;
    const invM  = Math.round(p.investment_mad / 1e6).toLocaleString('en');
    return `<div class="pipe-card ${isUC ? 'pipe-card-uc' : 'pipe-card-pl'}">
      <div>
        <div class="pipe-card-header-row">
          <div class="pipe-card-name">${fmt.esc(p.name)}</div>
          ${pill}
        </div>
        <div class="pipe-card-location">${fmt.esc(p.city)} · ${fmt.esc(p.category)}</div>
        <div class="pipe-card-brand">${fmt.esc(p.brand)}</div>
      </div>
      <div class="pipe-card-year">${p.expected_opening}</div>
      <div class="pipe-card-metrics">
        <div>
          <div class="pipe-card-metric-val">${p.keys.toLocaleString('en')}</div>
          <div class="pipe-card-metric-lbl">Keys</div>
        </div>
        <div>
          <div class="pipe-card-metric-val">${invM}</div>
          <div class="pipe-card-metric-lbl">MAD M</div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function renderPipelineTableView() {
  const data = filteredPipeline();
  const tbody = document.getElementById('pipeline-tbody');
  data.sort((a, b) => {
    const av = a[pipelineSort.col], bv = b[pipelineSort.col];
    if (PIPE_STR_COLS.has(pipelineSort.col)) return pipelineSort.dir * String(av).localeCompare(String(bv));
    return pipelineSort.dir * (av - bv);
  });
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted)">No projects match filters.</td></tr>';
    return;
  }
  tbody.innerHTML = data.map(p => {
    const pill  = p.status === 'Under Construction' ? `<span class="pipe-status-uc">${p.status}</span>` : `<span class="pipe-status-pl">${p.status}</span>`;
    const invM  = Math.round(p.investment_mad / 1e6).toLocaleString('en');
    return `<tr>
      <td style="font-weight:600">${fmt.esc(p.name)}</td>
      <td>${fmt.esc(p.city)}</td>
      <td>${fmt.esc(p.brand)}</td>
      <td class="num-col">${p.expected_opening}</td>
      <td>${pill}</td>
      <td class="num-col">${p.keys.toLocaleString('en')}</td>
      <td class="num-col">${invM}</td>
    </tr>`;
  }).join('');
}

function togglePipelineTable() {
  const wrap = document.getElementById('pipe-table-wrap');
  const btn  = document.getElementById('pipe-table-toggle');
  const open = wrap.classList.toggle('open');
  btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 9h18M3 15h18M9 3v18M15 3v18" stroke-linecap="round"/></svg> ${open ? 'Hide table view' : 'Show table view'}`;
  if (open) renderPipelineTableView();
}

function renderPipelineCharts() {
  const data = filteredPipeline();

  // Keys by project (horizontal bar, sorted asc so largest at top)
  const sorted = [...data].sort((a, b) => a.keys - b.keys);
  const projLabels = sorted.map(p => p.name);
  const projVals   = sorted.map(p => p.keys);
  const projColors = sorted.map(p => p.status === 'Under Construction' ? '#B8922A' : '#0A4A5A');

  const projWrap = document.getElementById('pwrap-proj');
  if (projWrap) { projWrap.style.minHeight = '0'; projWrap.style.height = Math.max(220, projLabels.length * 36 + 50) + 'px'; }
  if (pipelineChartProj) { pipelineChartProj.destroy(); pipelineChartProj = null; }
  const projCfg = chartConfig(projLabels, projVals, ' keys', projColors, v => v);
  projCfg.options.plugins.tooltip.callbacks.label = ctx => '  ' + ctx.raw + ' keys';
  pipelineChartProj = new Chart(document.getElementById('chart-pipeline-proj'), projCfg);

  // Investment by city (horizontal bar, sorted asc)
  const cityTotals = {};
  data.forEach(p => { cityTotals[p.city] = (cityTotals[p.city] || 0) + p.investment_mad; });
  const cityEntries = Object.entries(cityTotals).sort((a, b) => a[1] - b[1]);
  const cityLabels  = cityEntries.map(e => e[0]);
  const cityVals    = cityEntries.map(e => parseFloat((e[1] / 1e9).toFixed(2)));

  const cityWrap = document.getElementById('pwrap-city');
  if (cityWrap) { cityWrap.style.minHeight = '0'; cityWrap.style.height = Math.max(200, cityLabels.length * 38 + 50) + 'px'; }
  if (pipelineChartCity) { pipelineChartCity.destroy(); pipelineChartCity = null; }
  const cityCfg = chartConfig(cityLabels, cityVals, 'B', cityLabels.map(() => CHART_ACCENT), v => v + 'B');
  cityCfg.options.plugins.tooltip.callbacks.label = ctx => '  MAD ' + ctx.raw + 'B';
  pipelineChartCity = new Chart(document.getElementById('chart-pipeline-city'), cityCfg);
}

function applyPipelineFilter() {
  renderPipelineCards();
  renderPipelineCharts();
  const tableOpen = document.getElementById('pipe-table-wrap').classList.contains('open');
  if (tableOpen) renderPipelineTableView();
  if (pipelineLeaflet) {
    const { map, markers } = pipelineLeaflet;
    markers.forEach(({ marker, project: p }) => {
      const show = (pipelineState.status   === 'all' || p.status   === pipelineState.status) &&
                   (pipelineState.city     === 'all' || p.city     === pipelineState.city)   &&
                   (pipelineState.category === 'all' || p.category === pipelineState.category);
      if (show) marker.addTo(map); else marker.remove();
    });
  }
}

// Pipeline filter events (event delegation on the screen)
document.getElementById('screen-pipeline').addEventListener('click', e => {
  const btn = e.target.closest('[data-pstatus]');
  if (btn) {
    document.querySelectorAll('[data-pstatus]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    pipelineState.status = btn.dataset.pstatus;
    applyPipelineFilter();
  }
  const tBtn = e.target.closest('#pipe-table-toggle');
  if (tBtn) togglePipelineTable();
  const th = e.target.closest('th[data-pcol]');
  if (th) {
    const col = th.dataset.pcol;
    pipelineSort.dir = pipelineSort.col === col ? -pipelineSort.dir : 1;
    pipelineSort.col = col;
    document.querySelectorAll('#pipeline-table th').forEach(t => t.classList.remove('sort-asc', 'sort-desc'));
    th.classList.add(pipelineSort.dir === 1 ? 'sort-asc' : 'sort-desc');
    renderPipelineTableView();
  }
});
document.getElementById('pipe-city-filter').addEventListener('change', e => {
  pipelineState.city = e.target.value;
  applyPipelineFilter();
});
document.getElementById('pipe-cat-filter').addEventListener('change', e => {
  pipelineState.category = e.target.value;
  applyPipelineFilter();
});

// ─── News screen ──────────────────────────────────────────────────
let newsInited = false;

function newsCatClass(cat) {
  return 'news-cat-' + (cat || '').toLowerCase().replace(/\s+/g, '-');
}

function newsDateFmt(d) {
  if (!d) return '';
  const dt = new Date(d + 'T00:00:00');
  return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function toggleArticle(id) {
  const body = document.getElementById('news-body-' + id);
  const btn  = document.getElementById('news-btn-' + id);
  const open = body.classList.toggle('expanded');
  btn.textContent = open ? '← Show less' : 'Read full article →';
}

async function initNews() {
  if (newsInited) return;
  newsInited = true;
  const feed = document.getElementById('news-feed');
  feed.innerHTML = '<p class="news-loading">Loading…</p>';
  try {
    const res = await fetch('/api/news');
    const articles = await res.json();
    if (!articles.length) {
      feed.innerHTML = '<p class="news-loading">No articles published yet.</p>';
      return;
    }
    const shown = articles.slice(0, 7);
    feed.innerHTML = shown.map(a => {
      const bodyBlock = a.body
        ? `<div class="news-body" id="news-body-${a.id}">${a.body}</div>
           <button class="news-read-btn noprint" id="news-btn-${a.id}" onclick="toggleArticle(${a.id})">Read full article →</button>`
        : '';
      return `<div class="news-card">
        <div class="news-card-meta">
          <span class="news-cat ${newsCatClass(a.category)}">${a.category}</span>
          <span class="news-date">${newsDateFmt(a.date)}</span>
          <span class="news-sep">·</span>
          <span class="news-author">${a.author}</span>
        </div>
        <div class="news-headline">${a.headline}</div>
        <div class="news-summary">${a.summary}</div>
        ${bodyBlock}
      </div>`;
    }).join('');
  } catch {
    feed.innerHTML = '<p class="news-loading">Failed to load articles.</p>';
  }
}

// ─── Sidebar visibility ───────────────────────────────────────────

const SIDEBAR_SCREENS = new Set(['dashboard', 'map']);
function setSidebar(screen) {
  document.querySelector('.app-body').classList.toggle('no-sidebar', !SIDEBAR_SCREENS.has(screen));
}

// ─── Mobile nav ───────────────────────────────────────────────────

function closeMobileNav() {
  const overlay = document.getElementById('mobile-nav-overlay');
  const btn     = document.getElementById('hamburger-btn');
  overlay.classList.remove('open');
  btn.textContent = '☰';
  btn.setAttribute('aria-expanded', 'false');
}

function syncMobileNav(screen) {
  document.querySelectorAll('.mobile-nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === screen)
  );
}

document.getElementById('hamburger-btn').addEventListener('click', () => {
  const overlay = document.getElementById('mobile-nav-overlay');
  const btn     = document.getElementById('hamburger-btn');
  const isOpen  = overlay.classList.toggle('open');
  btn.textContent = isOpen ? '✕' : '☰';
  btn.setAttribute('aria-expanded', String(isOpen));
});

// ─── Events ───────────────────────────────────────────────────────

// Screen nav
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const screen = link.dataset.screen;
    closeMobileNav();
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    // Set active on every nav-link (desktop + mobile) matching this screen
    document.querySelectorAll(`.nav-link[data-screen="${screen}"]`).forEach(l => l.classList.add('active'));
    document.getElementById('screen-' + screen).classList.add('active');
    setSidebar(screen);
    syncMobileNav(screen);

    if (screen === 'map') {
      if (!leaflet) {
        initMap();
      } else {
        setTimeout(() => leaflet.map.invalidateSize(), 60);
        updateMapMarkers();
        panMap();
      }
    }
    if (screen === 'hotels')   renderHotelsTable();
    if (screen === 'tourism')  initTourismCharts();
    if (screen === 'pipeline') initPipeline();
    if (screen === 'news')         initNews();
    if (screen === 'benchmarking') {
      initBenchmarking().then(() => {
        if (benchmarkInited && benchmarkData) renderBenchAIInsights();
      });
    }
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
  setSidebar('dashboard');
  syncMobileNav('dashboard');
});

// Hotel detail — back button
document.getElementById('hotel-back-btn').addEventListener('click', () => {
  const prev = hotelDetailPrevScreen;
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l =>
    l.classList.toggle('active', l.dataset.screen === prev)
  );
  const prevScreen = document.getElementById('screen-' + prev);
  if (prevScreen) prevScreen.classList.add('active');
  setSidebar(prev);
  syncMobileNav(prev);
  if (prev === 'map') {
    if (!leaflet) initMap();
    else setTimeout(() => leaflet.map.invalidateSize(), 60);
  }
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
    label.textContent = 'Kōdō Analyst';
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

    if (res.status === 403 && data.error === 'upgrade_required') {
      if (typeof showUpgradeModal === 'function') showUpgradeModal('AI Analyst limit reached', data.message);
    } else if (data.error) {
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

function buildMobileCityPills() {
  const cities = [...new Set(hotels.map(h => h.city))].sort();
  const bar = document.getElementById('mobile-city-pills');
  bar.querySelectorAll('[data-mcity]:not([data-mcity="all"])').forEach(el => el.remove());
  cities.forEach(city => {
    const btn = document.createElement('button');
    btn.className = 'pill';
    btn.dataset.mcity = city;
    btn.textContent = city;
    bar.appendChild(btn);
  });
}

// Mobile city filter
document.getElementById('mobile-city-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-mcity]');
  if (!btn) return;
  document.querySelectorAll('#mobile-city-pills .pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  // Sync sidebar
  state.city = btn.dataset.mcity;
  document.querySelectorAll('#city-filter .sidebar-item').forEach(el =>
    el.classList.toggle('active', el.dataset.city === state.city)
  );
  render();
});

// Mobile segment filter
document.getElementById('mobile-seg-pills').addEventListener('click', e => {
  const btn = e.target.closest('[data-mseg]');
  if (!btn) return;
  document.querySelectorAll('#mobile-seg-pills .pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  state.mapSeg = btn.dataset.mseg;
  document.querySelectorAll('#segment-sidebar .sidebar-item').forEach(el =>
    el.classList.toggle('active', el.dataset.seg === state.mapSeg)
  );
  document.querySelectorAll('#map-seg-bar .seg-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.mapSeg === state.mapSeg)
  );
  if (leaflet) updateMapMarkers();
});

// ─── Benchmarking screen ──────────────────────────────────────────

let benchmarkInited = false;
let benchmarkData   = null;
let benchTrendRevpar = null;
let benchTrendOcc    = null;
let benchDOWChart    = null;

const benchState = {
  myHotelId:  'demo_1',
  compSet:    new Set(['demo_2', 'demo_3', 'demo_4']),
  dateRange:  30,
  adrCalYear: 2026, adrCalMonth: 5, adrCalView: 'mine',
  occCalYear: 2026, occCalMonth: 5, occCalView: 'mine',
};

async function initBenchmarking() {
  if (benchmarkInited) return;
  benchmarkInited = true;
  const res = await fetch('/api/benchmarking');
  if (res.status === 403) {
    const err = await res.json().catch(() => ({}));
    if (err.error === 'upgrade_required') {
      benchmarkInited = false;
      if (typeof showUpgradeModal === 'function') showUpgradeModal('Benchmarking requires Benchmarker', err.message);
      return;
    }
  }
  benchmarkData = await res.json();
  renderBenchPropertySelector();
  renderBenchCompSetBuilder();
  renderBenchAll();
}

// ── Selectors ────────────────────────────────────────────────────

function renderBenchPropertySelector() {
  const sel = document.getElementById('bench-my-hotel');
  sel.innerHTML = benchmarkData.hotels.map(h =>
    `<option value="${h.id}"${h.id === benchState.myHotelId ? ' selected' : ''}>${fmt.esc(h.name)}</option>`
  ).join('');
  updateBenchPropInfo();
  sel.addEventListener('change', () => {
    benchState.myHotelId = sel.value;
    updateBenchPropInfo();
    renderBenchCompSetBuilder();
    renderBenchAll();
  });
}

function updateBenchPropInfo() {
  const h = benchmarkData.hotels.find(x => x.id === benchState.myHotelId);
  if (!h) return;
  document.getElementById('bench-prop-info').innerHTML =
    `<div class="bench-prop-name">${fmt.esc(h.name)}</div>
     <div class="bench-prop-meta">${fmt.esc(h.city)} · ${fmt.esc(h.category)} · ${h.keys} keys</div>`;
}

function renderBenchCompSetBuilder() {
  const container = document.getElementById('bench-comp-checks');
  const others = benchmarkData.hotels.filter(h => h.id !== benchState.myHotelId);
  // remove any comp set entry that is now my property
  benchState.compSet.delete(benchState.myHotelId);

  container.innerHTML = others.map(h => {
    const checked = benchState.compSet.has(h.id);
    return `<label class="bench-comp-check-label${checked ? ' active' : ''}">
      <input type="checkbox" class="bench-comp-cb" value="${h.id}"${checked ? ' checked' : ''}>
      ${fmt.esc(h.name)}<span class="bench-comp-keys">${h.keys} keys</span>
    </label>`;
  }).join('');

  container.querySelectorAll('.bench-comp-cb').forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) benchState.compSet.add(cb.value);
      else benchState.compSet.delete(cb.value);
      cb.closest('.bench-comp-check-label').classList.toggle('active', cb.checked);
      renderCompPills();
      renderBenchAll();
    });
  });

  renderCompPills();
}

function renderCompPills() {
  const c = document.getElementById('bench-comp-pills');
  c.innerHTML = [...benchState.compSet].map(id => {
    const h = benchmarkData.hotels.find(x => x.id === id);
    if (!h) return '';
    return `<span class="bench-comp-pill">${fmt.esc(h.name)}
      <button class="bench-comp-pill-rm" data-compid="${h.id}">×</button></span>`;
  }).join('');
  c.querySelectorAll('.bench-comp-pill-rm').forEach(btn => {
    btn.addEventListener('click', () => {
      benchState.compSet.delete(btn.dataset.compid);
      const cb = document.querySelector(`.bench-comp-cb[value="${btn.dataset.compid}"]`);
      if (cb) { cb.checked = false; cb.closest('.bench-comp-check-label').classList.remove('active'); }
      renderCompPills();
      renderBenchAll();
    });
  });
}

// ── Date range ───────────────────────────────────────────────────

function getBenchDateRange() {
  const end = new Date('2026-06-01');
  const start = new Date(end);
  if (benchState.dateRange === 7)        start.setDate(end.getDate() - 6);
  else if (benchState.dateRange === 30)  start.setDate(end.getDate() - 29);
  else if (benchState.dateRange === 90)  start.setDate(end.getDate() - 89);
  else if (benchState.dateRange === 'ytd') { start.setFullYear(end.getFullYear()); start.setMonth(0); start.setDate(1); }
  return [start, end];
}

function dateInRange(dateStr, start, end) {
  const d = new Date(dateStr + 'T00:00:00');
  return d >= start && d <= end;
}

// ── Data helpers ─────────────────────────────────────────────────

function getMyDaily() {
  const [s, e] = getBenchDateRange();
  return benchmarkData.daily.filter(d =>
    d.hotel_id === benchState.myHotelId && dateInRange(d.date, s, e)
  ).sort((a, b) => a.date.localeCompare(b.date));
}

function getCompDaily() {
  if (!benchState.compSet.size) return [];
  const [s, e] = getBenchDateRange();
  const byDate = {};
  benchmarkData.daily.forEach(d => {
    if (!benchState.compSet.has(d.hotel_id)) return;
    if (!dateInRange(d.date, s, e)) return;
    if (!byDate[d.date]) byDate[d.date] = [];
    byDate[d.date].push(d);
  });
  return Object.entries(byDate).map(([date, recs]) => ({
    date,
    occupancy:     recs.reduce((s, r) => s + r.occupancy, 0) / recs.length,
    adr:           recs.reduce((s, r) => s + r.adr, 0) / recs.length,
    revpar:        recs.reduce((s, r) => s + r.revpar, 0) / recs.length,
    rooms_revenue: recs.reduce((s, r) => s + r.rooms_revenue, 0) / recs.length,
  })).sort((a, b) => a.date.localeCompare(b.date));
}

function aggDaily(records) {
  if (!records.length) return { occupancy: 0, adr: 0, revpar: 0, rooms_revenue: 0 };
  const n = records.length;
  return {
    occupancy:     records.reduce((s, r) => s + r.occupancy, 0) / n,
    adr:           records.reduce((s, r) => s + r.adr, 0) / n,
    revpar:        records.reduce((s, r) => s + r.revpar, 0) / n,
    rooms_revenue: records.reduce((s, r) => s + r.rooms_revenue, 0) / n,
  };
}

// ── Master render ─────────────────────────────────────────────────

function renderBenchAll() {
  renderBenchKPIs();
  renderBenchCalendar('adr');
  renderBenchCalendar('occ');
  renderBenchTrends();
  renderBenchDOW();
  renderBenchMonthlyTable();
}

// ── KPI cards ────────────────────────────────────────────────────

function renderBenchKPIs() {
  const my   = aggDaily(getMyDaily());
  const comp = aggDaily(getCompDaily());

  const noComp = !benchState.compSet.size;

  function setCard(id, myVal, compVal, myFmt, compFmt) {
    const card = document.getElementById(id);
    card.querySelector('.bench-kpi-mine-val').textContent = myFmt(myVal);
    card.querySelector('.bench-kpi-comp-val').textContent = noComp ? '—' : compFmt(compVal);
    const idx = (!noComp && compVal > 0) ? Math.round(myVal / compVal * 100) : null;
    const idxEl   = card.querySelector('.bench-kpi-index');
    const idxVal  = card.querySelector('.bench-kpi-idx-val');
    idxVal.textContent = idx !== null ? idx : '—';
    idxEl.className = 'bench-kpi-index' + (idx === null ? ' bench-idx-neutral' : idx >= 100 ? ' bench-idx-green' : ' bench-idx-red');
  }

  setCard('bkpi-occ',    my.occupancy,     comp.occupancy,     v => (v*100).toFixed(1)+'%',         v => (v*100).toFixed(1)+'%');
  setCard('bkpi-adr',    my.adr,           comp.adr,           v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
  setCard('bkpi-revpar', my.revpar,        comp.revpar,        v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
  setCard('bkpi-rev',    my.rooms_revenue, comp.rooms_revenue, v => 'MAD '+Math.round(v).toLocaleString('en'), v => 'MAD '+Math.round(v).toLocaleString('en'));
}

// ── Calendar ──────────────────────────────────────────────────────

function benchCalDataMap(type, year, month) {
  const prefix = `${year}-${String(month).padStart(2,'0')}`;
  const map = {};

  if (type === 'adr') {
    // buildForHotel (mine) or comp average
    const view = benchState.adrCalView;
    buildCalMap(view, prefix, map);
  } else {
    const view = benchState.occCalView;
    buildCalMap(view, prefix, map);
  }
  return map;
}

function buildCalMap(view, prefix, map) {
  if (view === 'mine') {
    benchmarkData.daily.forEach(d => {
      if (d.hotel_id !== benchState.myHotelId) return;
      if (!d.date.startsWith(prefix)) return;
      map[d.date] = { adr: d.adr, occupancy: d.occupancy, revpar: d.revpar };
    });
  } else {
    const byDate = {};
    benchmarkData.daily.forEach(d => {
      if (!benchState.compSet.has(d.hotel_id)) return;
      if (!d.date.startsWith(prefix)) return;
      if (!byDate[d.date]) byDate[d.date] = [];
      byDate[d.date].push(d);
    });
    Object.entries(byDate).forEach(([date, recs]) => {
      map[date] = {
        adr:       recs.reduce((s, r) => s + r.adr, 0) / recs.length,
        occupancy: recs.reduce((s, r) => s + r.occupancy, 0) / recs.length,
        revpar:    recs.reduce((s, r) => s + r.revpar, 0) / recs.length,
      };
    });
  }
}

function adrCellStyle(adr) {
  const dark = !document.body.classList.contains('light');
  if (adr < 4000) return dark ? {bg:'#0A2030',col:'#0E8FAD'} : {bg:'#D8EEF2',col:'#0A4A5A'};
  if (adr < 6000) return dark ? {bg:'#0A4A5A',col:'#FFFFFF'} : {bg:'#3D7A8A',col:'#FFFFFF'};
  return dark ? {bg:'#0E8FAD',col:'#0A0F14'} : {bg:'#0A4A5A',col:'#FFFFFF'};
}

function occCellStyle(occ) {
  const dark = !document.body.classList.contains('light');
  const p = occ * 100;
  if (p < 60) return dark ? {bg:'#1A0F0F',col:'#E05A5A'} : {bg:'#F0F8F2',col:'#1A6B3C'};
  if (p < 80) return dark ? {bg:'#0F3D22',col:'#4CAF72'} : {bg:'#5A9E6C',col:'#FFFFFF'};
  return dark ? {bg:'#1A6B3C',col:'#FFFFFF'} : {bg:'#1A6B3C',col:'#FFFFFF'};
}

function renderBenchCalendar(calType) {
  const yr  = calType === 'adr' ? benchState.adrCalYear  : benchState.occCalYear;
  const mo  = calType === 'adr' ? benchState.adrCalMonth : benchState.occCalMonth;
  const view = calType === 'adr' ? benchState.adrCalView : benchState.occCalView;

  const MON_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  document.getElementById(`bench-${calType}-month-label`).textContent = `${MON_NAMES[mo-1]} ${yr}`;

  // Update toggle button active state
  document.querySelectorAll(`[data-ctype="${calType}"]`).forEach(btn => {
    btn.classList.toggle('active', btn.dataset.cview === view);
  });

  const dataMap = benchCalDataMap(calType, yr, mo);
  const firstDow = (new Date(yr, mo - 1, 1).getDay() + 6) % 7; // Mon=0
  const totalDays = new Date(yr, mo, 0).getDate();

  let html = '<div class="bench-cal-dow-row">';
  ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].forEach(d => { html += `<div class="bench-cal-dow">${d}</div>`; });
  html += '</div><div class="bench-cal-days">';
  for (let i = 0; i < firstDow; i++) html += '<div class="bench-cal-day bench-cal-empty"></div>';

  for (let day = 1; day <= totalDays; day++) {
    const dateStr = `${yr}-${String(mo).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const isWknd = [0,6].includes((new Date(yr, mo-1, day).getDay()));
    const d = dataMap[dateStr];
    if (d) {
      const sty = calType === 'adr' ? adrCellStyle(d.adr) : occCellStyle(d.occupancy);
      const dispVal = calType === 'adr'
        ? Math.round(d.adr).toLocaleString('en')
        : (d.occupancy * 100).toFixed(0) + '%';
      const tip = `${dateStr}|${Math.round(d.adr)}|${(d.occupancy*100).toFixed(1)}|${Math.round(d.revpar)}`;
      html += `<div class="bench-cal-day${isWknd ? ' bench-cal-weekend' : ''}"
        style="background:${sty.bg};color:${sty.col}"
        data-btip="${tip}">
        <span class="bench-cal-daynum">${day}</span>
        <span class="bench-cal-dayval">${dispVal}</span>
      </div>`;
    } else {
      html += `<div class="bench-cal-day bench-cal-nodata${isWknd ? ' bench-cal-weekend' : ''}">
        <span class="bench-cal-daynum">${day}</span>
      </div>`;
    }
  }
  html += '</div>';
  document.getElementById(`bench-${calType}-grid`).innerHTML = html;
}

// Tooltip shared between both calendars
const benchTip = document.getElementById('bench-cal-tooltip');

document.addEventListener('mousemove', e => {
  if (benchTip && benchTip.style.display !== 'none') {
    benchTip.style.left = (e.clientX + 14) + 'px';
    benchTip.style.top  = (e.clientY - 10) + 'px';
  }
});

document.getElementById('screen-benchmarking').addEventListener('mouseover', e => {
  const cell = e.target.closest('[data-btip]');
  if (!cell) { benchTip.style.display = 'none'; return; }
  const [dt, adr, occ, rev] = cell.dataset.btip.split('|');
  benchTip.innerHTML = `
    <div class="bct-date">${dt}</div>
    <div class="bct-row"><span>ADR</span><span>MAD ${Number(adr).toLocaleString('en')}</span></div>
    <div class="bct-row"><span>Occupancy</span><span>${occ}%</span></div>
    <div class="bct-row"><span>RevPAR</span><span>MAD ${Number(rev).toLocaleString('en')}</span></div>`;
  benchTip.style.display = 'block';
});
document.getElementById('screen-benchmarking').addEventListener('mouseout', e => {
  if (!e.target.closest('[data-btip]')) benchTip.style.display = 'none';
});

// Calendar nav + view toggle events
document.getElementById('bench-adr-prev').addEventListener('click', () => {
  benchState.adrCalMonth--; if (benchState.adrCalMonth < 1) { benchState.adrCalMonth = 12; benchState.adrCalYear--; }
  renderBenchCalendar('adr');
});
document.getElementById('bench-adr-next').addEventListener('click', () => {
  benchState.adrCalMonth++; if (benchState.adrCalMonth > 12) { benchState.adrCalMonth = 1; benchState.adrCalYear++; }
  renderBenchCalendar('adr');
});
document.getElementById('bench-occ-prev').addEventListener('click', () => {
  benchState.occCalMonth--; if (benchState.occCalMonth < 1) { benchState.occCalMonth = 12; benchState.occCalYear--; }
  renderBenchCalendar('occ');
});
document.getElementById('bench-occ-next').addEventListener('click', () => {
  benchState.occCalMonth++; if (benchState.occCalMonth > 12) { benchState.occCalMonth = 1; benchState.occCalYear++; }
  renderBenchCalendar('occ');
});

document.getElementById('screen-benchmarking').addEventListener('click', e => {
  const btn = e.target.closest('.bench-cal-view-btn');
  if (!btn) return;
  const ctype = btn.dataset.ctype;
  const cview = btn.dataset.cview;
  if (ctype === 'adr') benchState.adrCalView = cview;
  else benchState.occCalView = cview;
  renderBenchCalendar(ctype);
});

// ── Trend charts ──────────────────────────────────────────────────

function renderBenchTrends() {
  const myD   = getMyDaily();
  const compD = getCompDaily();

  const labels = myD.map(d => {
    const dt = new Date(d.date + 'T00:00:00');
    return dt.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
  });

  const compByDate = {};
  compD.forEach(d => { compByDate[d.date] = d; });

  const myRevpar  = myD.map(d => Math.round(d.revpar));
  const myOcc     = myD.map(d => parseFloat((d.occupancy * 100).toFixed(1)));
  const cRevpar   = myD.map(d => { const c = compByDate[d.date]; return c ? Math.round(c.revpar) : null; });
  const cOcc      = myD.map(d => { const c = compByDate[d.date]; return c ? parseFloat((c.occupancy * 100).toFixed(1)) : null; });

  const dense = labels.length > 50;

  function mkTrend(myData, compData, suffix) {
    const cc = getChartColors();
    return {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'My Property', data: myData, borderColor: CHART_ACCENT,
            backgroundColor: 'rgba(10,74,90,0.07)', borderWidth: 2, fill: false,
            tension: 0.3, pointRadius: dense ? 0 : 2.5, pointBackgroundColor: CHART_ACCENT },
          { label: 'Comp Set Avg', data: compData, borderColor: '#B8922A',
            borderWidth: 2, borderDash: [5, 4], fill: false, tension: 0.3, pointRadius: 0 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        layout: { padding: { top: 14 } },
        plugins: {
          legend: { display: true, labels: { color: cc.tick, font: { size: 11 }, boxWidth: 22, padding: 14 } },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            mode: 'index', intersect: false,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}${suffix}` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 10 }, maxTicksLimit: 10, maxRotation: 0 } },
          y: { ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    };
  }

  const rWrap = document.getElementById('bench-trend-revpar-wrap');
  rWrap.style.minHeight = '0'; rWrap.style.height = '230px';
  if (benchTrendRevpar) { benchTrendRevpar.destroy(); benchTrendRevpar = null; }
  benchTrendRevpar = new Chart(document.getElementById('bench-trend-revpar'), mkTrend(myRevpar, cRevpar, ' MAD'));

  const oWrap = document.getElementById('bench-trend-occ-wrap');
  oWrap.style.minHeight = '0'; oWrap.style.height = '230px';
  if (benchTrendOcc) { benchTrendOcc.destroy(); benchTrendOcc = null; }
  benchTrendOcc = new Chart(document.getElementById('bench-trend-occ'), mkTrend(myOcc, cOcc, '%'));
}

// ── DOW chart ─────────────────────────────────────────────────────

function renderBenchDOW() {
  const myD   = getMyDaily();
  const compD = getCompDaily();

  const myDOW   = Array(7).fill(null).map(() => []);
  const compDOW = Array(7).fill(null).map(() => []);

  myD.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    myDOW[dow].push(d.occupancy * 100);
  });
  compD.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    compDOW[dow].push(d.occupancy * 100);
  });

  const avg = arr => arr.length ? parseFloat((arr.reduce((s,v) => s+v, 0) / arr.length).toFixed(1)) : 0;

  const dWrap = document.getElementById('bench-dow-wrap');
  dWrap.style.minHeight = '0'; dWrap.style.height = '230px';
  if (benchDOWChart) { benchDOWChart.destroy(); benchDOWChart = null; }

  {
    const cc = getChartColors();
    benchDOWChart = new Chart(document.getElementById('bench-dow-chart'), {
      type: 'bar',
      data: {
        labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        datasets: [
          { label: 'My Property', data: myDOW.map(avg), backgroundColor: CHART_ACCENT, borderRadius: 4, borderSkipped: false },
          { label: 'Comp Set Avg', data: compDOW.map(avg), backgroundColor: 'rgba(184,146,42,0.35)', borderRadius: 4, borderSkipped: false },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 300 },
        layout: { padding: { top: 14 } },
        plugins: {
          legend: { display: true, labels: { color: cc.tick, font: { size: 11 }, boxWidth: 10, padding: 14 } },
          datalabels: { display: false },
          tooltip: {
            backgroundColor: cc.tooltipBg, borderColor: cc.tooltipBdr, borderWidth: 1,
            titleColor: cc.tooltipTtl, bodyColor: cc.tooltipBdy,
            callbacks: { label: ctx => `  ${ctx.dataset.label}: ${ctx.raw}%` },
          },
        },
        scales: {
          x: { ticks: { color: cc.tick, font: { size: 11 } } },
          y: { suggestedMin: 0, suggestedMax: 100, ticks: { color: cc.tick, font: { size: 11 } } },
        },
      },
    });
  }
}

// ── Monthly summary table ─────────────────────────────────────────

function renderBenchMonthlyTable() {
  const months = {};
  benchmarkData.daily.forEach(d => {
    const mk = d.date.substring(0, 7);
    if (!months[mk]) months[mk] = { my: [], compByDate: {} };
    if (d.hotel_id === benchState.myHotelId) {
      months[mk].my.push(d);
    } else if (benchState.compSet.has(d.hotel_id)) {
      if (!months[mk].compByDate[d.date]) months[mk].compByDate[d.date] = [];
      months[mk].compByDate[d.date].push(d);
    }
  });

  const MON_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const tbody = document.getElementById('bench-monthly-tbody');
  tbody.innerHTML = Object.keys(months).sort().map(mk => {
    const { my, compByDate } = months[mk];
    const myAgg = aggDaily(my);
    const compDailyAvg = Object.values(compByDate).map(recs => aggDaily(recs));
    const compAgg = aggDaily(compDailyAvg);
    const noComp = !benchState.compSet.size || !compDailyAvg.length;
    const revIdx = (!noComp && compAgg.revpar > 0) ? Math.round(myAgg.revpar / compAgg.revpar * 100) : null;
    const [yr, mo] = mk.split('-');
    const label = `${MON_NAMES[Number(mo)-1]} ${yr}`;
    const idxCls = revIdx === null ? 'bench-idx-neutral' : revIdx >= 100 ? 'bench-idx-green' : 'bench-idx-red';
    return `<tr>
      <td><strong>${label}</strong></td>
      <td>${(myAgg.occupancy*100).toFixed(1)}%</td>
      <td>${noComp ? '—' : (compAgg.occupancy*100).toFixed(1)+'%'}</td>
      <td>${Math.round(myAgg.adr).toLocaleString('en')}</td>
      <td>${noComp ? '—' : Math.round(compAgg.adr).toLocaleString('en')}</td>
      <td>${Math.round(myAgg.revpar).toLocaleString('en')}</td>
      <td>${noComp ? '—' : Math.round(compAgg.revpar).toLocaleString('en')}</td>
      <td><span class="bench-idx-badge ${idxCls}">${revIdx !== null ? revIdx : '—'}</span></td>
    </tr>`;
  }).join('');
}

// ── AI Insights ───────────────────────────────────────────────────

const DOW_NAMES_FULL = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const DOW_NAMES_SHORT = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

function renderBenchInsightCards() {
  const box    = document.getElementById('bench-ai-insights');
  const my     = aggDaily(getMyDaily());
  const comp   = aggDaily(getCompDaily());
  const noComp = !benchState.compSet.size;
  const myDailyData = getMyDaily();

  // ── Card 1: ADR ──────────────────────────────────────────────
  const adrDiff  = noComp ? 0 : (my.adr - comp.adr) / comp.adr * 100;
  const card1 = {
    icon: '📈',
    headline: noComp ? 'ADR Snapshot' : adrDiff >= 0 ? 'ADR Leadership' : 'ADR Gap',
    body: noComp
      ? `Your ADR stands at MAD ${Math.round(my.adr).toLocaleString('en')}. Select a comp set to benchmark against the market.`
      : adrDiff >= 0
        ? `Your ADR leads the comp set by ${adrDiff.toFixed(1)}% — MAD ${Math.round(my.adr).toLocaleString('en')} vs comp avg MAD ${Math.round(comp.adr).toLocaleString('en')}.`
        : `Your ADR trails the comp set by ${Math.abs(adrDiff).toFixed(1)}% — MAD ${Math.round(my.adr).toLocaleString('en')} vs comp avg MAD ${Math.round(comp.adr).toLocaleString('en')}.`,
    badge: noComp ? `MAD ${Math.round(my.adr).toLocaleString('en')}` : (adrDiff >= 0 ? '+' : '') + adrDiff.toFixed(1) + '% vs comp',
    cls: noComp ? 'bib-amber' : adrDiff >= 2 ? 'bib-green' : adrDiff > -2 ? 'bib-amber' : 'bib-red',
  };

  // ── Card 2: Occupancy ────────────────────────────────────────
  const occDiff = noComp ? 0 : (my.occupancy - comp.occupancy) * 100;
  const card2 = {
    icon: '🏨',
    headline: noComp ? 'Occupancy Snapshot' : occDiff >= 0 ? 'Occupancy Advantage' : 'Occupancy Gap',
    body: noComp
      ? `Running at ${(my.occupancy * 100).toFixed(1)}% occupancy. Add a comp set to see relative performance.`
      : occDiff >= 0
        ? `Occupancy leads comp by ${occDiff.toFixed(1)} pts (${(my.occupancy*100).toFixed(1)}% vs ${(comp.occupancy*100).toFixed(1)}%), indicating stronger demand capture.`
        : `Occupancy trails comp by ${Math.abs(occDiff).toFixed(1)} pts (${(my.occupancy*100).toFixed(1)}% vs ${(comp.occupancy*100).toFixed(1)}%) — review pricing and distribution mix.`,
    badge: noComp ? `${(my.occupancy*100).toFixed(1)}%` : (occDiff >= 0 ? '+' : '') + occDiff.toFixed(1) + ' pts vs comp',
    cls: noComp ? 'bib-amber' : occDiff >= 2 ? 'bib-green' : occDiff > -2 ? 'bib-amber' : 'bib-red',
  };

  // ── Card 3: Best day of week ─────────────────────────────────
  const dowBuckets = Array(7).fill(null).map(() => []);
  myDailyData.forEach(d => {
    const dow = (new Date(d.date + 'T00:00:00').getDay() + 6) % 7;
    dowBuckets[dow].push(d.occupancy * 100);
  });
  const dowAvg     = dowBuckets.map(arr => arr.length ? arr.reduce((s,v)=>s+v,0)/arr.length : 0);
  const validDows  = dowAvg.map((v, i) => ({ v, i })).filter(x => x.v > 0);
  const bestDow    = validDows.reduce((a, b) => b.v > a.v ? b : a, { v: 0, i: 0 });
  const worstDow   = validDows.reduce((a, b) => b.v < a.v ? b : a, { v: 100, i: 0 });
  const spread     = bestDow.v - worstDow.v;
  const isWkndPeak = bestDow.i >= 4;
  const card3 = {
    icon: '📅',
    headline: isWkndPeak ? 'Weekend Strength' : 'Midweek Leader',
    body: `${DOW_NAMES_FULL[bestDow.i]} is your strongest day at ${bestDow.v.toFixed(1)}% vs ${DOW_NAMES_SHORT[worstDow.i]} at ${worstDow.v.toFixed(1)}%. ${spread > 15 ? 'Wide spread — targeted midweek promotions could close the gap.' : 'Consistent demand across the week.'}`,
    badge: `${DOW_NAMES_SHORT[bestDow.i]} peaks at ${bestDow.v.toFixed(0)}%`,
    cls: 'bib-amber',
  };

  // ── Card 4: RevPAR trend ─────────────────────────────────────
  const sorted  = [...myDailyData].sort((a, b) => a.date.localeCompare(b.date));
  const half    = Math.floor(sorted.length / 2);
  const firstH  = sorted.slice(0, half);
  const secondH = sorted.slice(half);
  const rev1    = firstH.length  ? firstH.reduce((s,d)=>s+d.revpar,0)/firstH.length   : 0;
  const rev2    = secondH.length ? secondH.reduce((s,d)=>s+d.revpar,0)/secondH.length  : 0;
  const trendPct = rev1 > 0 ? (rev2 - rev1) / rev1 * 100 : 0;
  const improving = trendPct >= 0;
  const card4 = {
    icon: improving ? '💡' : '⚠️',
    headline: improving ? 'Improving Momentum' : 'Declining Trend',
    body: `RevPAR ${improving ? 'improved' : 'declined'} ${Math.abs(trendPct).toFixed(1)}% from the first to second half of the selected period (MAD ${Math.round(rev1).toLocaleString('en')} → MAD ${Math.round(rev2).toLocaleString('en')}).`,
    badge: (improving ? '+' : '') + trendPct.toFixed(1) + '% vs prior period',
    cls: improving ? 'bib-green' : 'bib-red',
  };

  const cards = [card1, card2, card3, card4];
  box.innerHTML = `
    <div class="bench-insight-grid">
      ${cards.map(c => `
        <div class="bench-insight-card">
          <div class="bench-insight-icon">${c.icon}</div>
          <div class="bench-insight-headline">${fmt.esc(c.headline)}</div>
          <div class="bench-insight-body">${fmt.esc(c.body)}</div>
          <span class="bench-insight-badge ${c.cls}">${fmt.esc(c.badge)}</span>
        </div>`).join('')}
    </div>
    <div id="bench-ai-commentary" class="bench-ai-commentary" style="display:none">
      <div class="bench-ai-commentary-label">✦ AI Commentary</div>
      <div id="bench-ai-commentary-body" class="bench-loading">Generating…</div>
    </div>`;
}

async function fetchBenchAICommentary() {
  const box  = document.getElementById('bench-ai-commentary');
  const body = document.getElementById('bench-ai-commentary-body');
  if (!box || !body) return;
  box.style.display = 'block';

  const myH      = benchmarkData.hotels.find(h => h.id === benchState.myHotelId);
  const compNames = [...benchState.compSet].map(id => benchmarkData.hotels.find(h => h.id === id)?.name).filter(Boolean).join(', ');
  const my   = aggDaily(getMyDaily());
  const comp = aggDaily(getCompDaily());

  const prompt = `Brief strategic commentary on ${myH?.name} vs comp set (${compNames || 'none'}) — Marrakech Luxury, last ${benchState.dateRange} days.
MY: Occ ${(my.occupancy*100).toFixed(1)}% | ADR MAD ${Math.round(my.adr).toLocaleString('en')} | RevPAR MAD ${Math.round(my.revpar).toLocaleString('en')}
COMP AVG: Occ ${(comp.occupancy*100).toFixed(1)}% | ADR MAD ${Math.round(comp.adr).toLocaleString('en')} | RevPAR MAD ${Math.round(comp.revpar).toLocaleString('en')}
2-3 sentences of strategic commentary. Cite specific numbers. Be direct.`;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: prompt }] }),
    });
    const data = await res.json();
    if (data.response) {
      body.className = 'bench-ai-content';
      body.innerHTML = mdRender(data.response);
    } else {
      box.style.display = 'none';
    }
  } catch {
    box.style.display = 'none';
  }
}

function renderBenchAIInsights() {
  renderBenchInsightCards();
  fetchBenchAICommentary();
}

// Date range pill events
document.getElementById('bench-date-bar').addEventListener('click', e => {
  const btn = e.target.closest('.bench-date-pill');
  if (!btn) return;
  document.querySelectorAll('.bench-date-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const v = btn.dataset.brange;
  benchState.dateRange = isNaN(Number(v)) ? v : Number(v);
  renderBenchAll();
});

// AI refresh button
document.getElementById('bench-ai-refresh').addEventListener('click', renderBenchAIInsights);

// ─── Boot ─────────────────────────────────────────────────────────

async function boot() {
  [apiData, hotels] = await Promise.all([
    fetch('/api/data').then(r => r.json()),
    fetch('/api/hotels').then(r => r.json()),
  ]);
  buildCityFilter();
  buildCityPills();
  buildMobileCityPills();
  render();
}

// Fetch current user info and populate tier badge
fetch('/api/me').then(r => r.ok ? r.json() : null).then(me => {
  if (!me) return;
  const badge = document.getElementById('tier-badge');
  if (!badge) return;
  const label = { observer: 'Observer', benchmarker: 'Benchmarker', advisory: 'Advisory' }[me.tier] || me.tier;
  badge.textContent = label;
  badge.className = `tier-badge tier-badge--${me.tier}`;
  badge.style.display = '';
  window._kodoUser = me;
});

boot();
