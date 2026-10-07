// ─── Kōdō Admin ──────────────────────────────────────────────────────────
// Reaching this page at all already required a logged-in Advisory-tier
// session (admin_page() in app.py). window.__ADMIN_CSRF__ is a per-session
// CSRF token, not a secret — meaningless without the session cookie it's
// paired with. Every state-changing request below sends it back as
// X-CSRF-Token; admin_required (app.py) checks it against the session.
const CSRF = window.__ADMIN_CSRF__;

function escHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function todayStr() { return new Date().toISOString().slice(0, 10); }

function authHeaders(json) {
  const h = { 'X-CSRF-Token': CSRF };
  if (json) h['Content-Type'] = 'application/json';
  return h;
}

// ─── Toasts ──────────────────────────────────────────────────────────────
function toast(text, type) {
  const wrap = document.getElementById('admToastWrap');
  const el = document.createElement('div');
  el.className = 'adm-toast' + (type ? ' ' + type : '');
  el.textContent = text;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ─── Theme toggle (shared 'kodo-lp-theme' key with the rest of the site) ──
function applyAdminTheme(mode) {
  document.body.classList.toggle('light', mode === 'light');
  document.querySelectorAll('.adm-toggle-opt').forEach(opt => {
    opt.classList.toggle('adm-toggle-active', opt.dataset.val === mode);
  });
}
function wireThemeToggle(darkId, lightId) {
  const darkOpt = document.getElementById(darkId);
  const lightOpt = document.getElementById(lightId);
  darkOpt.dataset.val = 'dark';
  lightOpt.dataset.val = 'light';
  [darkOpt, lightOpt].forEach(opt => {
    opt.addEventListener('click', () => {
      const next = opt.dataset.val;
      try { localStorage.setItem('kodo-lp-theme', next); } catch {}
      applyAdminTheme(next);
    });
  });
}
wireThemeToggle('admToggleDark', 'admToggleLight');
wireThemeToggle('admToggleDarkMobile', 'admToggleLightMobile');
(function initTheme() {
  let saved = 'dark';
  try { saved = localStorage.getItem('kodo-lp-theme') || 'dark'; } catch {}
  applyAdminTheme(saved);
})();

// ─── Mobile nav ──────────────────────────────────────────────────────────
const mobileOverlay = document.getElementById('admMobileOverlay');
document.getElementById('admHamburgerBtn').addEventListener('click', () => mobileOverlay.classList.add('open'));
document.getElementById('admMobileClose').addEventListener('click', () => mobileOverlay.classList.remove('open'));
mobileOverlay.addEventListener('click', e => { if (e.target === mobileOverlay) mobileOverlay.classList.remove('open'); });

// ─── Section navigation (last section remembered in localStorage) ────────
const SECTIONS = ['overview', 'users', 'orgs', 'news', 'uploads', 'rates', 'occupancy', 'system'];
const SECTION_LOADERS = {
  overview: loadOverview,
  users: loadUsers,
  orgs: loadOrgs,
  news: loadArticles,
  uploads: () => { loadHotelsForDI(); loadRecentUploads(); },
  rates: () => { loadScraperStatus(); populateHotelSelect(); },
  occupancy: loadOccupancyStatus,
  system: loadSystemInfo,
};
const loadedSections = new Set();

function showSection(name) {
  if (!SECTIONS.includes(name)) name = 'overview';
  SECTIONS.forEach(s => {
    document.getElementById('section-' + s).style.display = s === name ? '' : 'none';
  });
  document.querySelectorAll('#admSectionNav .list-pill').forEach(p => {
    p.classList.toggle('active', p.dataset.section === name);
  });
  try { localStorage.setItem('kodo-admin-section', name); } catch {}
  if (!loadedSections.has(name)) {
    loadedSections.add(name);
    SECTION_LOADERS[name]();
  }
}

document.getElementById('admSectionNav').addEventListener('click', e => {
  const btn = e.target.closest('.list-pill');
  if (!btn) return;
  showSection(btn.dataset.section);
});

(function initSection() {
  let last = 'overview';
  try { last = localStorage.getItem('kodo-admin-section') || 'overview'; } catch {}
  showSection(last);
})();

// Who's signed in — read from /api/me (already exists, used by the rest of
// the platform) rather than guessing a new field shape here.
(async function loadSignedIn() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();
    document.getElementById('admSignedIn').textContent = data.email || '';
  } catch {}
})();

// ─── Slide-in panel ────────────────────────────────────────────────────
const panel = document.getElementById('admPanel');
const panelOverlay = document.getElementById('admPanelOverlay');
const PANEL_TRANSITION_MS = 220; // matches .adm-panel's transition duration in admin.css

function openPanel(title, bodyHtml) {
  document.getElementById('admPanelTitle').textContent = title;
  document.getElementById('admPanelBody').innerHTML = bodyHtml;
  // .visible (display:flex) has to apply and paint *before* .open
  // (the slide transform) for the transition to actually animate —
  // toggling both on the same tick starts already-transformed, so
  // there's nothing to transition from.
  panel.classList.add('visible');
  panelOverlay.classList.add('open');
  requestAnimationFrame(() => requestAnimationFrame(() => panel.classList.add('open')));
}
function closePanel() {
  panel.classList.remove('open');
  panelOverlay.classList.remove('open');
  // Only remove .visible (display:none) once the slide-out transition
  // has actually finished, or the panel would just vanish instantly.
  // Fully removing it from layout when closed (not just off-screen) is
  // what keeps a fixed, positioned-off-screen element from still
  // counting toward document.documentElement.scrollWidth.
  setTimeout(() => panel.classList.remove('visible'), PANEL_TRANSITION_MS);
}
document.getElementById('admPanelClose').addEventListener('click', closePanel);
panelOverlay.addEventListener('click', closePanel);

// ─── Temp-password modal ───────────────────────────────────────────────
function showPwModal(pw, email, label) {
  document.getElementById('admPwModalTitle').textContent = label || 'Temporary Password';
  document.getElementById('admPwModalValue').textContent = pw;
  document.getElementById('admPwModalFor').textContent = email ? `For: ${email}` : '';
  document.getElementById('admPwModal').style.display = 'flex';
}
document.getElementById('admPwDoneBtn').addEventListener('click', () => {
  document.getElementById('admPwModal').style.display = 'none';
});
document.getElementById('admPwCopyBtn').addEventListener('click', async () => {
  const pw = document.getElementById('admPwModalValue').textContent;
  try {
    await navigator.clipboard.writeText(pw);
    toast('Password copied.', 'success');
  } catch { toast('Copy failed — select the password manually.', 'error'); }
});

// ════════════════════════ OVERVIEW ════════════════════════════════════
async function loadOverview() {
  const attnEl = document.getElementById('ov-attention');
  try {
    const [usersRes, orgsRes, newsRes, occRes] = await Promise.all([
      fetch('/admin/users', { headers: authHeaders() }),
      fetch('/admin/organisations', { headers: authHeaders() }),
      fetch('/api/news'),
      fetch('/api/occupancy/status', { headers: authHeaders() }),
    ]);
    const users = await usersRes.json();
    const orgs  = await orgsRes.json();
    const news  = await newsRes.json();
    const occ   = await occRes.json();

    const verified   = users.filter(u => u.email_verified).length;
    const unverified = users.length - verified;
    const byTier = t => users.filter(u => u.tier === t).length;

    document.getElementById('ov-users-total').textContent      = users.length;
    document.getElementById('ov-users-verified').textContent   = verified;
    document.getElementById('ov-users-unverified').textContent = unverified;
    document.getElementById('ov-orgs-total').textContent       = orgs.length;
    document.getElementById('ov-tier-observer').textContent    = byTier('observer');
    document.getElementById('ov-tier-benchmarker').textContent = byTier('benchmarker');
    document.getElementById('ov-tier-advisory').textContent    = byTier('advisory');

    const newsAll = Array.isArray(news) ? news : (news.all || []);
    document.getElementById('ov-news-total').textContent = newsAll.length;

    document.getElementById('ov-occ-last-run').textContent =
      occ.model_run_date ? occ.model_run_date : (occ.has_data ? '—' : 'Not run yet');

    // Needs attention
    const items = [];
    const unverified7d = users.filter(u => u.unverified_7d);
    if (unverified7d.length) {
      items.push(`${unverified7d.length} account${unverified7d.length === 1 ? '' : 's'} unverified for 7+ days`);
    }
    const byName = {};
    orgs.forEach(o => { (byName[o.name] = byName[o.name] || []).push(o); });
    const dupGroups = Object.entries(byName).filter(([, g]) => g.length > 1);
    if (dupGroups.length) {
      items.push(`${dupGroups.length} organisation name${dupGroups.length === 1 ? '' : 's'} with duplicates (${dupGroups.map(([n]) => escHtml(n)).join(', ')})`);
    }
    if (!newsAll.length) {
      items.push('News has zero articles');
    }

    attnEl.innerHTML = items.length
      ? items.map(t => `<div class="adm-row" style="grid-template-columns:1fr"><span class="adm-row-meta" style="color:var(--negative)">${t}</span></div>`).join('')
      : '<p class="adm-empty">Nothing needs attention.</p>';
  } catch (e) {
    attnEl.innerHTML = '<p class="adm-empty adm-error">Could not load overview.</p>';
  }
}

// ════════════════════════ USERS ════════════════════════════════════════
let usersData = [];
let usersFilterState = { tier: 'all', verified: 'all', search: '' };

function buildUsersFilters() {
  const tierEl = document.getElementById('users-tier-filters');
  const verEl  = document.getElementById('users-verified-filters');
  const tiers = ['All', 'Observer', 'Benchmarker', 'Advisory'];
  tierEl.innerHTML = tiers.map((t, i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="tier" data-value="${i === 0 ? 'all' : t.toLowerCase()}">${t}</button>`
  ).join('');
  const vers = [['All', 'all'], ['Verified', 'verified'], ['Unverified', 'unverified']];
  verEl.innerHTML = vers.map(([label, val], i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="verified" data-value="${val}">${label}</button>`
  ).join('');
  [tierEl, verEl].forEach(container => {
    container.addEventListener('click', e => {
      const btn = e.target.closest('.list-pill');
      if (!btn) return;
      container.querySelectorAll('.list-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      usersFilterState[btn.dataset.filter] = btn.dataset.value;
      renderUsers();
    });
  });
}

document.getElementById('users-search').addEventListener('input', e => {
  usersFilterState.search = e.target.value.trim().toLowerCase();
  renderUsers();
});
document.getElementById('users-create-btn').addEventListener('click', openCreateUserPanel);

async function loadUsers() {
  buildUsersFilters();
  const ledger = document.getElementById('users-ledger');
  try {
    const res = await fetch('/admin/users', { headers: authHeaders() });
    if (!res.ok) { ledger.innerHTML = '<p class="adm-empty adm-error">Could not load users.</p>'; return; }
    usersData = await res.json();
    renderUsers();
  } catch { ledger.innerHTML = '<p class="adm-empty adm-error">Error loading users.</p>'; }
}

const TIER_COLOR = { observer: 'var(--text-muted)', benchmarker: 'var(--accent)', advisory: '#F2A33D' };
const STATUS_COLOR = {
  active: 'var(--positive)', pending_approval: '#F2A33D', pending_verification: '#F2A33D',
  pending_payment: '#F2A33D', pending: '#F2A33D', suspended: 'var(--negative)', rejected: 'var(--negative)',
};

function renderUsers() {
  const ledger = document.getElementById('users-ledger');
  const { tier, verified, search } = usersFilterState;
  const filtered = usersData.filter(u => {
    if (tier !== 'all' && u.tier !== tier) return false;
    if (verified === 'verified' && !u.email_verified) return false;
    if (verified === 'unverified' && u.email_verified) return false;
    if (search) {
      const hay = `${u.name || ''} ${u.email || ''}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  });

  const header = `<div class="adm-row-header adm-row-header-users">
    <span>Name / Email</span><span>Organisation</span><span>Tier</span><span>Status</span><span>Verified</span><span></span>
  </div>`;

  if (!filtered.length) {
    ledger.innerHTML = header + '<p class="adm-empty">No users match your filters.</p>';
    return;
  }

  ledger.innerHTML = header + filtered.map(u => {
    const tierColor = TIER_COLOR[u.tier] || 'var(--text-muted)';
    const statusColor = STATUS_COLOR[u.status] || 'var(--text-muted)';
    const verColor = u.unverified_7d ? 'var(--negative)' : (u.email_verified ? 'var(--positive)' : 'var(--text-muted)');
    const verLabel = u.email_verified ? 'Verified' : 'Unverified';
    const isPending = ['pending_approval', 'pending', 'pending_payment'].includes(u.status);
    const actions = [];
    actions.push(`<button class="adm-btn-text" data-act="edit" data-uid="${u.id}">Edit</button>`);
    if (!u.email_verified) {
      actions.push(`<button class="adm-btn-text" data-act="verify" data-uid="${u.id}">Mark verified</button>`);
      actions.push(`<button class="adm-btn-text" data-act="resend" data-uid="${u.id}">Resend verification</button>`);
    }
    actions.push(`<button class="adm-btn-text" data-act="reset-pw" data-uid="${u.id}" data-email="${escHtml(u.email)}">Reset password</button>`);
    if (isPending) actions.push(`<button class="adm-btn-text" data-act="approve" data-uid="${u.id}">Approve</button>`);
    if (u.status === 'active') {
      actions.push(`<button class="adm-btn-text destructive" data-act="disable" data-uid="${u.id}">Disable</button>`);
    } else if (u.status === 'suspended' || u.status === 'rejected') {
      actions.push(`<button class="adm-btn-text" data-act="reactivate" data-uid="${u.id}">Reactivate</button>`);
    }

    return `<div class="adm-row adm-row-users">
      <div class="adm-row-main" data-label="Name / Email">
        <span class="adm-row-name" title="${escHtml(u.name || u.email)}">${escHtml(u.name || '—')}</span>
        <span class="adm-row-sub" title="${escHtml(u.email)}">${escHtml(u.email)}</span>
      </div>
      <span class="adm-row-meta" data-label="Organisation" title="${escHtml(u.organisation || '')}">${escHtml(u.organisation || '—')}</span>
      <span data-label="Tier"><span class="adm-pill" style="color:${tierColor}">${escHtml(u.tier)}</span></span>
      <span data-label="Status"><span class="adm-pill" style="color:${statusColor}">${escHtml((u.status || '').replace(/_/g, ' '))}</span></span>
      <span data-label="Verified"><span class="adm-pill" style="color:${verColor}">${verLabel}</span></span>
      <div class="adm-row-actions" data-label="Actions">${actions.join('')}</div>
    </div>`;
  }).join('');
}

document.getElementById('users-ledger').addEventListener('click', e => {
  const btn = e.target.closest('button[data-act]');
  if (!btn) return;
  const uid = btn.dataset.uid;
  const act = btn.dataset.act;
  if (act === 'edit') return openEditUserPanel(uid);
  if (act === 'verify') return userAction(uid, 'verify');
  if (act === 'resend') return userAction(uid, 'resend-verification');
  if (act === 'reset-pw') return resetPasswordInline(btn, uid, btn.dataset.email);
  if (act === 'approve') return updateUser(uid, { status: 'active' });
  if (act === 'disable') return confirmInline(btn, 'Disable this user?', () => updateUser(uid, { status: 'suspended' }));
  if (act === 'reactivate') return updateUser(uid, { status: 'active' });
});

async function userAction(uid, path) {
  try {
    const res = await fetch(`/admin/users/${uid}/${path}`, { method: 'POST', headers: authHeaders() });
    const data = await res.json();
    if (!res.ok) { toast(data.message || data.error || 'Failed.', 'error'); return; }
    toast(data.message || 'Done.', 'success');
    await loadUsers();
  } catch { toast('Network error.', 'error'); }
}

async function resetPasswordInline(btn, uid, email) {
  confirmInline(btn, `Send a password reset email to ${email}?`, async () => {
    const res = await fetch(`/admin/users/${uid}/reset-password`, { method: 'POST', headers: authHeaders() });
    const data = await res.json();
    toast(data.message || (res.ok ? 'Done.' : 'Failed.'), res.ok ? 'success' : 'error');
  });
}

async function updateUser(uid, changes) {
  try {
    const res = await fetch('/admin/users/' + uid, { method: 'PUT', headers: authHeaders(true), body: JSON.stringify(changes) });
    if (!res.ok) { toast('Update failed.', 'error'); return; }
    await loadUsers();
    toast('Updated.', 'success');
  } catch { toast('Network error.', 'error'); }
}

// Inline Confirm/Cancel — replaces confirm(), appended next to the button
// that triggered it, removed on either choice.
function confirmInline(triggerBtn, message, onConfirm) {
  const existing = triggerBtn.parentElement.querySelector('.adm-confirm-inline');
  if (existing) existing.remove();
  const wrap = document.createElement('span');
  wrap.className = 'adm-confirm-inline';
  wrap.innerHTML = `<span>${escHtml(message)}</span>
    <button class="adm-btn-text destructive" type="button">Confirm</button>
    <button class="adm-btn-text" type="button">Cancel</button>`;
  const [confirmBtn, cancelBtn] = wrap.querySelectorAll('button');
  confirmBtn.addEventListener('click', () => { wrap.remove(); onConfirm(); });
  cancelBtn.addEventListener('click', () => wrap.remove());
  triggerBtn.insertAdjacentElement('afterend', wrap);
}

function openCreateUserPanel() {
  openPanel('New User', `
    <div class="adm-field-group"><label class="adm-label">Full name</label><input class="adm-input" id="uf-name" /></div>
    <div class="adm-field-group"><label class="adm-label">Email</label><input class="adm-input" type="email" id="uf-email" /></div>
    <div class="adm-field-group"><label class="adm-label">Organisation (optional)</label><input class="adm-input" id="uf-org" /></div>
    <div class="adm-field-group"><label class="adm-label">Tier</label>
      <select class="adm-select" id="uf-tier">
        <option value="observer">Observer</option>
        <option value="benchmarker">Benchmarker</option>
        <option value="advisory" selected>Advisory</option>
      </select>
    </div>
    <div class="adm-panel-actions">
      <button class="adm-btn adm-btn-primary" id="uf-submit">Create</button>
      <span class="adm-inline-msg" id="uf-msg"></span>
    </div>
  `);
  document.getElementById('uf-submit').addEventListener('click', async () => {
    const name  = document.getElementById('uf-name').value.trim();
    const email = document.getElementById('uf-email').value.trim();
    const org   = document.getElementById('uf-org').value.trim();
    const tier  = document.getElementById('uf-tier').value;
    const msg   = document.getElementById('uf-msg');
    if (!name || !email) { msg.textContent = 'Name and email are required.'; msg.style.color = 'var(--negative)'; return; }
    const res = await fetch('/admin/users', { method: 'POST', headers: authHeaders(true), body: JSON.stringify({ name, email, organisation: org, tier }) });
    const data = await res.json();
    if (!res.ok) { msg.textContent = data.error || 'Failed.'; msg.style.color = 'var(--negative)'; return; }
    closePanel();
    await loadUsers();
    showPwModal(data.temp_password, email, 'User created');
  });
}

function openEditUserPanel(uid) {
  const u = usersData.find(x => x.id === uid);
  if (!u) return;
  openPanel('Edit ' + (u.name || u.email), `
    <div class="adm-field-group"><label class="adm-label">Tier</label>
      <select class="adm-select" id="ue-tier">
        ${['observer', 'benchmarker', 'advisory'].map(t => `<option value="${t}"${u.tier === t ? ' selected' : ''}>${t}</option>`).join('')}
      </select>
    </div>
    <div class="adm-field-group"><label class="adm-label">Status</label>
      <select class="adm-select" id="ue-status">
        ${['active', 'pending_approval', 'pending_payment', 'pending', 'suspended', 'rejected'].map(s => `<option value="${s}"${u.status === s ? ' selected' : ''}>${s.replace(/_/g, ' ')}</option>`).join('')}
      </select>
    </div>
    <div class="adm-panel-actions">
      <button class="adm-btn adm-btn-primary" id="ue-submit">Save</button>
      <span class="adm-inline-msg" id="ue-msg"></span>
    </div>
  `);
  document.getElementById('ue-submit').addEventListener('click', async () => {
    const tier = document.getElementById('ue-tier').value;
    const status = document.getElementById('ue-status').value;
    await updateUser(uid, { tier, status });
    closePanel();
  });
}

// ════════════════════════ ORGANISATIONS ═══════════════════════════════
let orgsData = [];
let orgsSearch = '';

document.getElementById('orgs-search').addEventListener('input', e => {
  orgsSearch = e.target.value.trim().toLowerCase();
  renderOrgs();
});

async function loadOrgs() {
  const ledger = document.getElementById('orgs-ledger');
  try {
    const res = await fetch('/admin/organisations', { headers: authHeaders() });
    if (!res.ok) { ledger.innerHTML = '<p class="adm-empty adm-error">Could not load organisations.</p>'; return; }
    orgsData = await res.json();
    renderOrgs();
  } catch { ledger.innerHTML = '<p class="adm-empty adm-error">Error loading organisations.</p>'; }
}

function renderOrgs() {
  const ledger = document.getElementById('orgs-ledger');
  const byName = {};
  orgsData.forEach(o => { (byName[o.name] = byName[o.name] || []).push(o); });

  const filtered = orgsData.filter(o => {
    if (!orgsSearch) return true;
    const hay = `${o.name || ''} ${o.owner_email || ''}`.toLowerCase();
    return hay.includes(orgsSearch);
  });

  const header = `<div class="adm-row-header adm-row-header-orgs">
    <span>Name</span><span>Owner</span><span>Seats</span><span>Members</span><span></span>
  </div>`;

  if (!filtered.length) {
    ledger.innerHTML = header + '<p class="adm-empty">No organisations match your search.</p>';
    return;
  }

  ledger.innerHTML = header + filtered.map(o => {
    const isDup = byName[o.name].length > 1;
    const memberCount = o.seats_used || 0;
    const canDelete = memberCount === 0;
    return `<div class="adm-row adm-row-orgs">
      <div class="adm-row-main" data-label="Name">
        <span class="adm-row-name" title="${escHtml(o.name)}">${escHtml(o.name)}${isDup ? ' <span style="color:var(--negative)">(duplicate)</span>' : ''}</span>
        <span class="adm-row-sub">${escHtml(o.plan || '')}</span>
      </div>
      <div class="adm-row-main" data-label="Owner">
        <span class="adm-row-name" style="font-weight:400" title="${escHtml(o.owner_email || '')}">${escHtml(o.owner_name || '—')}</span>
        <span class="adm-row-sub" title="${escHtml(o.owner_email || '')}">${escHtml(o.owner_email || '')}</span>
      </div>
      <span class="adm-row-meta" data-label="Seats">${o.seats_used || 0} / ${o.seats_total || 1}</span>
      <span class="adm-row-meta" data-label="Members">${memberCount}</span>
      <div class="adm-row-actions" data-label="Actions">
        <button class="adm-btn-text" data-act="members" data-oid="${o.id}" data-name="${escHtml(o.name)}">Members</button>
        ${o.status === 'active'
          ? `<button class="adm-btn-text destructive" data-act="suspend" data-oid="${o.id}">Suspend</button>`
          : `<button class="adm-btn-text" data-act="reactivate-org" data-oid="${o.id}">Reactivate</button>`}
        ${canDelete ? `<button class="adm-btn-text destructive" data-act="delete-org" data-oid="${o.id}" data-name="${escHtml(o.name)}">Delete</button>` : ''}
      </div>
    </div>`;
  }).join('');
}

document.getElementById('orgs-ledger').addEventListener('click', e => {
  const btn = e.target.closest('button[data-act]');
  if (!btn) return;
  const oid = btn.dataset.oid;
  const act = btn.dataset.act;
  if (act === 'members') return openOrgMembersPanel(oid, btn.dataset.name);
  if (act === 'suspend') return updateOrg(oid, { status: 'suspended' });
  if (act === 'reactivate-org') return updateOrg(oid, { status: 'active' });
  if (act === 'delete-org') {
    confirmInline(btn, `Delete "${btn.dataset.name}"? This cannot be undone.`, () => deleteOrg(oid));
  }
});

async function updateOrg(orgId, changes) {
  try {
    const res = await fetch(`/admin/organisations/${orgId}`, { method: 'PUT', headers: authHeaders(true), body: JSON.stringify(changes) });
    const data = await res.json();
    if (!res.ok) { toast(data.error || 'Update failed.', 'error'); return; }
    await loadOrgs();
    toast('Updated.', 'success');
  } catch { toast('Network error.', 'error'); }
}

async function deleteOrg(orgId) {
  try {
    const res = await fetch(`/admin/organisations/${orgId}`, { method: 'DELETE', headers: authHeaders() });
    const data = await res.json();
    if (!res.ok) { toast(data.error || 'Delete failed.', 'error'); return; }
    await loadOrgs();
    toast('Organisation deleted.', 'success');
  } catch { toast('Network error.', 'error'); }
}

function openOrgMembersPanel(orgId, orgName) {
  openPanel(orgName + ' — Members', '<p class="adm-loading">Loading…</p>');
  fetch(`/admin/organisations/${orgId}/members`, { headers: authHeaders() })
    .then(r => r.json())
    .then(members => {
      const body = document.getElementById('admPanelBody');
      if (!members.length) { body.innerHTML = '<p class="adm-empty">No members.</p>'; return; }
      body.innerHTML = members.map(m => `
        <div class="adm-row" style="grid-template-columns:1fr auto">
          <div class="adm-row-main">
            <span class="adm-row-name">${escHtml(m.name || '—')}</span>
            <span class="adm-row-sub">${escHtml(m.email)} · ${escHtml(m.role || 'member')}</span>
          </div>
          <span class="adm-pill" style="color:${STATUS_COLOR[m.status] || 'var(--text-muted)'}">${escHtml((m.status || '').replace(/_/g, ' '))}</span>
        </div>
      `).join('');
    })
    .catch(() => { document.getElementById('admPanelBody').innerHTML = '<p class="adm-empty adm-error">Error loading members.</p>'; });
}

// ════════════════════════ NEWS ══════════════════════════════════════════
let articles = [];
let newsSearch = '';
const CATS = ['Market Intelligence', 'Pipeline', 'Openings', 'Interviews', 'Sponsored', 'Partner Feature'];

document.getElementById('news-search').addEventListener('input', e => {
  newsSearch = e.target.value.trim().toLowerCase();
  renderArticles();
});
document.getElementById('news-create-btn').addEventListener('click', () => openArticlePanel(null));

async function loadArticles() {
  try {
    const res = await fetch('/api/news');
    const data = await res.json();
    articles = Array.isArray(data) ? data : (data.all || []);
  } catch { articles = []; }
  renderArticles();
}

function artTitle(a) { return a.title || a.headline || '(untitled)'; }
function artStatus(a) { return a.status === 'published' || a.published ? 'published' : 'draft'; }

function renderArticles() {
  const ledger = document.getElementById('news-ledger');
  const filtered = articles.filter(a => !newsSearch || artTitle(a).toLowerCase().includes(newsSearch));
  const header = `<div class="adm-row-header adm-row-header-news">
    <span>Title</span><span>Category</span><span>Type</span><span>Date</span><span>Views</span><span></span>
  </div>`;
  if (!filtered.length) {
    ledger.innerHTML = header + '<p class="adm-empty">No articles match your search.</p>';
    return;
  }
  ledger.innerHTML = header + filtered.map(a => {
    const status = artStatus(a);
    const statusColor = status === 'published' ? 'var(--positive)' : 'var(--text-muted)';
    return `<div class="adm-row adm-row-news">
      <div class="adm-row-main" data-label="Title">
        <span class="adm-row-name" title="${escHtml(artTitle(a))}">${escHtml(artTitle(a))}</span>
        ${a.featured ? '<span class="adm-row-sub" style="color:#4A7FA5">Featured</span>' : ''}
      </div>
      <span class="adm-row-meta" data-label="Category">${escHtml(a.category || '—')}</span>
      <span class="adm-row-meta" data-label="Type">${escHtml(a.type || '—')}</span>
      <span class="adm-row-meta" data-label="Date">${escHtml(a.date || '—')}</span>
      <span class="adm-row-meta" data-label="Views">${a.views || 0}</span>
      <div class="adm-row-actions" data-label="Actions">
        <button class="adm-btn-text" data-act="edit-art" data-id="${a.id}">Edit</button>
        <button class="adm-btn-text" data-act="toggle-pub" data-id="${a.id}">${status === 'published' ? 'Unpublish' : 'Publish'}</button>
        <button class="adm-btn-text destructive" data-act="delete-art" data-id="${a.id}">Delete</button>
      </div>
    </div>`;
  }).join('');
}

document.getElementById('news-ledger').addEventListener('click', e => {
  const btn = e.target.closest('button[data-act]');
  if (!btn) return;
  const id = parseInt(btn.dataset.id, 10);
  if (btn.dataset.act === 'edit-art') return openArticlePanel(id);
  if (btn.dataset.act === 'toggle-pub') return togglePublish(id);
  if (btn.dataset.act === 'delete-art') {
    confirmInline(btn, `Delete "${artTitle(articles.find(a => a.id === id))}"?`, () => deleteArticle(id));
  }
});

function openArticlePanel(id) {
  const a = id ? articles.find(x => x.id === id) : null;
  const isSponsorType = a && (a.type === 'sponsored' || a.type === 'partner');
  openPanel(a ? 'Edit Article' : 'New Article', `
    <div class="adm-field-group"><label class="adm-label">Title</label><input class="adm-input" id="f-title" value="${escHtml(a ? artTitle(a) : '')}" /></div>
    <div class="adm-field-group"><label class="adm-label">Category</label>
      <select class="adm-select" id="f-category">${CATS.map(c => `<option${a && a.category === c ? ' selected' : ''}>${c}</option>`).join('')}</select>
    </div>
    <div class="adm-field-group"><label class="adm-label">Type</label>
      <select class="adm-select" id="f-type">
        <option value="editorial"${!a || a.type === 'editorial' ? ' selected' : ''}>Editorial</option>
        <option value="sponsored"${a && a.type === 'sponsored' ? ' selected' : ''}>Sponsored</option>
        <option value="partner"${a && a.type === 'partner' ? ' selected' : ''}>Partner Feature</option>
      </select>
    </div>
    <div class="adm-field-group"><label class="adm-label">Author</label><input class="adm-input" id="f-author" value="${escHtml(a ? a.author : 'Kōdō Editorial') || 'Kōdō Editorial'}" /></div>
    <div class="adm-field-group"><label class="adm-label">Read time</label><input class="adm-input" id="f-read-time" value="${escHtml(a ? a.read_time : '5 min read') || '5 min read'}" /></div>
    <div class="adm-field-group"><label class="adm-label">Date</label><input class="adm-input" type="date" id="f-date" value="${escHtml(a ? (a.date || '') : todayStr())}" /></div>
    <div class="adm-field-group"><label class="adm-label">Cover image query</label><input class="adm-input" id="f-cover-query" value="${escHtml(a ? a.cover_image_query : '')}" /></div>
    <div class="adm-field-group"><label class="adm-label">Tags (comma-separated)</label><input class="adm-input" id="f-tags" value="${a && Array.isArray(a.tags) ? escHtml(a.tags.join(', ')) : ''}" /></div>
    <div class="adm-field-group">
      <label class="adm-label"><input type="checkbox" id="f-published" ${a && artStatus(a) === 'published' ? 'checked' : ''} /> Published</label>
    </div>
    <div class="adm-field-group">
      <label class="adm-label"><input type="checkbox" id="f-featured" ${a && a.featured ? 'checked' : ''} /> Featured (hero)</label>
    </div>
    <div class="adm-field-group"><label class="adm-label">Excerpt</label><textarea class="adm-textarea" id="f-excerpt" rows="3">${escHtml(a ? (a.excerpt || a.summary) : '')}</textarea></div>
    <div class="adm-field-group"><label class="adm-label">Content (HTML)</label><textarea class="adm-textarea" id="f-content" rows="10">${escHtml(a ? (a.content || a.body) : '')}</textarea></div>
    <div id="sponsored-fields" style="display:${isSponsorType ? 'block' : 'none'}">
      <div class="adm-field-group"><label class="adm-label">Sponsor name</label><input class="adm-input" id="f-sponsor-name" value="${escHtml(a ? a.sponsor_name : '')}" /></div>
      <div class="adm-field-group"><label class="adm-label">Sponsor logo domain</label><input class="adm-input" id="f-sponsor-domain" value="${escHtml(a ? a.sponsor_logo_domain : '')}" /></div>
      <div class="adm-field-group"><label class="adm-label">CTA text</label><input class="adm-input" id="f-sponsor-cta-text" value="${escHtml(a ? a.sponsor_cta_text : '')}" /></div>
      <div class="adm-field-group"><label class="adm-label">CTA URL</label><input class="adm-input" id="f-sponsor-cta-url" value="${escHtml(a ? a.sponsor_cta_url : '')}" /></div>
    </div>
    <input type="hidden" id="form-id" value="${a ? a.id : ''}" />
    <div class="adm-panel-actions">
      <button class="adm-btn adm-btn-primary" id="f-submit">Save</button>
      <span class="adm-inline-msg" id="f-msg"></span>
    </div>
  `);
  document.getElementById('f-type').addEventListener('change', e => {
    document.getElementById('sponsored-fields').style.display =
      (e.target.value === 'sponsored' || e.target.value === 'partner') ? 'block' : 'none';
  });
  document.getElementById('f-submit').addEventListener('click', saveArticle);
}

async function saveArticle() {
  const id = document.getElementById('form-id').value;
  const tagsRaw = document.getElementById('f-tags').value;
  const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [];
  const payload = {
    title: document.getElementById('f-title').value.trim(),
    category: document.getElementById('f-category').value,
    type: document.getElementById('f-type').value,
    author: document.getElementById('f-author').value.trim() || 'Kōdō Editorial',
    read_time: document.getElementById('f-read-time').value.trim(),
    date: document.getElementById('f-date').value,
    cover_image_query: document.getElementById('f-cover-query').value.trim(),
    tags,
    published: document.getElementById('f-published').checked,
    featured: document.getElementById('f-featured').checked,
    excerpt: document.getElementById('f-excerpt').value.trim(),
    content: document.getElementById('f-content').value.trim(),
    sponsor_name: document.getElementById('f-sponsor-name')?.value.trim() || null,
    sponsor_logo_domain: document.getElementById('f-sponsor-domain')?.value.trim() || null,
    sponsor_cta_text: document.getElementById('f-sponsor-cta-text')?.value.trim() || null,
    sponsor_cta_url: document.getElementById('f-sponsor-cta-url')?.value.trim() || null,
  };
  const msg = document.getElementById('f-msg');
  if (!payload.title) { msg.textContent = 'Title is required.'; msg.style.color = 'var(--negative)'; return; }
  const url = id ? '/admin/news/' + id : '/admin/news';
  const method = id ? 'PUT' : 'POST';
  const res = await fetch(url, { method, headers: authHeaders(true), body: JSON.stringify(payload) });
  if (!res.ok) { msg.textContent = 'Save failed.'; msg.style.color = 'var(--negative)'; return; }
  closePanel();
  toast('Article saved.', 'success');
  await loadArticles();
}

async function togglePublish(id) {
  const a = articles.find(x => x.id === id);
  if (!a) return;
  const newStatus = artStatus(a) === 'published' ? 'draft' : 'published';
  const res = await fetch('/admin/news/' + id, {
    method: 'PUT', headers: authHeaders(true),
    body: JSON.stringify({ status: newStatus, published: newStatus === 'published' }),
  });
  if (!res.ok) { toast('Failed.', 'error'); return; }
  await loadArticles();
}

async function deleteArticle(id) {
  const res = await fetch('/admin/news/' + id, { method: 'DELETE', headers: authHeaders() });
  if (!res.ok) { toast('Delete failed.', 'error'); return; }
  toast('Article deleted.', 'success');
  await loadArticles();
}

// ════════════════════════ UPLOADS ══════════════════════════════════════
let diParsed = [];

async function loadHotelsForDI() {
  try {
    const res = await fetch('/api/hotels');
    const hs = await res.json();
    const sel = document.getElementById('di-hotel');
    const uniq = []; const seen = new Set();
    hs.forEach(h => { if (!seen.has(h.id)) { seen.add(h.id); uniq.push(h); } });
    sel.innerHTML = '<option value="">Select hotel…</option>' +
      uniq.map(h => `<option value="${escHtml(h.id)}" data-name="${escHtml(h.name)}">${escHtml(h.name)} (${escHtml(h.city)})</option>`).join('');
  } catch {}
}

const dz = document.getElementById('di-dropzone');
const finp = document.getElementById('di-file');
dz.addEventListener('click', () => finp.click());
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag-over'); });
dz.addEventListener('dragleave', () => dz.classList.remove('drag-over'));
dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('drag-over'); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
finp.addEventListener('change', () => { if (finp.files[0]) handleFile(finp.files[0]); });

function handleFile(file) {
  const reader = new FileReader();
  reader.onload = ev => parseCSV(ev.target.result, file.name);
  reader.readAsText(file);
}

function diMsg(text, isError) {
  const el = document.getElementById('di-msg');
  el.textContent = text;
  el.style.color = isError ? 'var(--negative)' : 'var(--positive)';
}

function parseCSV(text, filename) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  if (!lines.length) { diMsg('Empty file.', true); return; }
  const header = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/"/g, ''));
  const required = ['date', 'occupancy', 'adr', 'rooms_sold', 'rooms_revenue'];
  const missing = required.filter(c => !header.includes(c));
  if (missing.length) { diMsg('Missing columns: ' + missing.join(', '), true); return; }

  diParsed = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
    const row = {};
    header.forEach((h, j) => { row[h] = vals[j] ?? ''; });
    if (row.date) diParsed.push(row);
  }

  const cols = ['date', 'occupancy', 'adr', 'rooms_sold', 'rooms_revenue'];
  document.getElementById('di-preview-table').innerHTML =
    `<div class="adm-row" style="grid-template-columns:repeat(5,1fr);border-top:none">${cols.map(c => `<span class="adm-row-meta" style="text-transform:uppercase;font-size:10px">${c}</span>`).join('')}</div>` +
    diParsed.slice(0, 5).map(r => `<div class="adm-row" style="grid-template-columns:repeat(5,1fr)">${cols.map(c => `<span class="adm-row-meta">${escHtml(r[c] || '')}</span>`).join('')}</div>`).join('');
  document.getElementById('di-preview').style.display = 'block';

  const dates = diParsed.map(r => r.date).sort();
  if (dates.length) {
    document.getElementById('di-from').value = dates[0];
    document.getElementById('di-to').value = dates[dates.length - 1];
  }

  dz.querySelector('.adm-dropzone-main').textContent = `${filename} · ${diParsed.length} rows`;
  document.getElementById('di-submit').disabled = false;
  diMsg(`${diParsed.length} rows parsed from ${filename}`, false);
}

document.getElementById('di-submit').addEventListener('click', async () => {
  const sel = document.getElementById('di-hotel');
  const hotelId = sel.value;
  const hotelName = sel.options[sel.selectedIndex]?.dataset?.name || hotelId;
  if (!hotelId) { diMsg('Select a hotel.', true); return; }
  if (!diParsed.length) { diMsg('No data to upload.', true); return; }

  document.getElementById('di-submit').disabled = true;
  diMsg('Uploading…', false);

  const res = await fetch('/admin/upload-performance', {
    method: 'POST', headers: authHeaders(true),
    body: JSON.stringify({ hotel_id: hotelId, hotel_name: hotelName, rows: diParsed }),
  });
  const data = await res.json();
  if (!res.ok) { diMsg(data.error || 'Upload failed.', true); document.getElementById('di-submit').disabled = false; return; }
  diMsg(`${data.rows_ingested} rows ingested · ${data.date_range}`, false);
  document.getElementById('di-submit').disabled = false;
  diParsed = [];
  document.getElementById('di-preview').style.display = 'none';
  dz.querySelector('.adm-dropzone-main').textContent = 'Drag & drop CSV file here';
  loadRecentUploads();
});

async function loadRecentUploads() {
  const container = document.getElementById('di-recent');
  const header = `<div class="adm-row-header adm-row-header-uploads">
    <span>Hotel</span><span>Date range</span><span>Rows</span>
  </div>`;
  try {
    const res = await fetch('/admin/recent-uploads', { headers: authHeaders() });
    const logs = await res.json();
    if (!logs.length) { container.innerHTML = header + '<p class="adm-empty">No uploads yet.</p>'; return; }
    container.innerHTML = header + logs.map(l => `
      <div class="adm-row adm-row-uploads">
        <span class="adm-row-meta" data-label="Hotel" title="${escHtml(l.hotel_name || l.hotel_id)}">${escHtml(l.hotel_name || l.hotel_id)}</span>
        <span class="adm-row-meta" data-label="Date range">${escHtml(l.date_from)} – ${escHtml(l.date_to)}</span>
        <span class="adm-row-meta" data-label="Rows">${l.rows}</span>
      </div>
    `).join('');
  } catch { container.innerHTML = '<p class="adm-empty adm-error">Could not load.</p>'; }
}

// ════════════════════════ RATES / SCRAPER ══════════════════════════════
async function loadScraperStatus() {
  try {
    const res = await fetch('/api/scraper/status', { headers: authHeaders() });
    const data = await res.json();
    const statusEl = document.getElementById('ri-status');
    statusEl.textContent = data.scheduler_running ? 'Scheduler Active' : 'Scheduler Off';
    statusEl.style.color = data.scheduler_running ? 'var(--positive)' : '#F2A33D';
    document.getElementById('ri-last-run').textContent = data.last_run
      ? `Last run: ${data.last_run.replace('T', ' ').slice(0, 19)}` : 'Never run';
    document.getElementById('ri-live-count').textContent = data.hotels_with_live ?? '—';
    document.getElementById('ri-est-count').textContent = data.hotels_estimated ?? '—';
    const src = data.source_breakdown || {};
    document.getElementById('ri-sources').textContent = Object.entries(src).map(([k, v]) => `${k}: ${v}`).join('  ·  ') || '—';
    document.getElementById('ri-log').textContent = data.log_tail || '(no log yet)';
  } catch {
    document.getElementById('ri-log').textContent = 'Error loading status';
  }
}

async function populateHotelSelect() {
  try {
    const res = await fetch('/api/hotels', { headers: authHeaders() });
    const hotels = await res.json();
    const sel = document.getElementById('ri-hotel-sel');
    if (sel.dataset.populated) return;
    (hotels.hotels || hotels).forEach(h => {
      const opt = document.createElement('option');
      opt.value = h.id;
      opt.textContent = `${h.name} (${h.city})`;
      sel.appendChild(opt);
    });
    sel.dataset.populated = '1';
  } catch {}
}

document.getElementById('run-scraper-btn').addEventListener('click', async () => {
  const btn = document.getElementById('run-scraper-btn');
  btn.disabled = true;
  btn.textContent = 'Starting…';
  try {
    const res = await fetch('/api/scraper/run', { method: 'POST', headers: authHeaders() });
    const data = await res.json();
    toast(data.status === 'started' ? 'Scraper started.' : (data.error || 'Error'), data.status === 'started' ? 'success' : 'error');
  } catch { toast('Network error.', 'error'); }
  setTimeout(() => { btn.disabled = false; btn.textContent = 'Run Scraper Now'; }, 2500);
});

document.getElementById('ri-save-btn').addEventListener('click', async () => {
  const hotelId = document.getElementById('ri-hotel-sel').value;
  const stayDate = document.getElementById('ri-stay-date').value;
  const rateMad = document.getElementById('ri-rate-mad').value;
  const note = document.getElementById('ri-note').value;
  const msgEl = document.getElementById('ri-override-msg');
  if (!hotelId || !stayDate || !rateMad) {
    msgEl.textContent = 'Hotel, date and rate are required.'; msgEl.style.color = 'var(--negative)'; return;
  }
  try {
    const res = await fetch('/api/scraper/override', {
      method: 'POST', headers: authHeaders(true),
      body: JSON.stringify({ hotel_id: hotelId, stay_date: stayDate, rate_mad: +rateMad, note }),
    });
    const data = await res.json();
    if (data.status === 'saved') {
      msgEl.textContent = `Saved — MAD ${rateMad} on ${stayDate}`; msgEl.style.color = 'var(--positive)';
      document.getElementById('ri-rate-mad').value = '';
      document.getElementById('ri-note').value = '';
    } else {
      msgEl.textContent = data.error || 'Error saving override'; msgEl.style.color = 'var(--negative)';
    }
  } catch { msgEl.textContent = 'Network error'; msgEl.style.color = 'var(--negative)'; }
});

// ════════════════════════ OCCUPANCY ════════════════════════════════════
async function loadOccupancyStatus() {
  try {
    const res = await fetch('/api/occupancy/status', { headers: authHeaders() });
    const data = await res.json();
    document.getElementById('occ-last-run').textContent = data.model_run_date ? data.model_run_date : (data.has_data ? '—' : 'Not run yet');
    document.getElementById('occ-high').textContent = data.high_confidence ?? '—';
    document.getElementById('occ-medium').textContent = data.medium_confidence ?? '—';
    document.getElementById('occ-low').textContent = data.low_confidence ?? '—';
  } catch {}
}

document.getElementById('run-occ-btn').addEventListener('click', async () => {
  const btn = document.getElementById('run-occ-btn');
  btn.disabled = true;
  btn.textContent = 'Starting…';
  try {
    const res = await fetch('/api/occupancy/run', { method: 'POST', headers: authHeaders() });
    const data = await res.json();
    toast(data.status === 'started' ? 'Occupancy model started.' : (data.error || 'Error'), data.status === 'started' ? 'success' : 'error');
  } catch { toast('Network error.', 'error'); }
  setTimeout(() => { btn.disabled = false; btn.textContent = 'Run Model Now'; loadOccupancyStatus(); }, 2500);
});

// ════════════════════════ DATA & SYSTEM ════════════════════════════════
async function loadSystemInfo() {
  const el = document.getElementById('sys-info');
  const header = `<div class="adm-row-header adm-row-header-system">
    <span>File</span><span>Exists</span><span>Size</span><span>Modified</span>
  </div>`;
  try {
    const res = await fetch('/admin/system-info', { headers: authHeaders() });
    if (!res.ok) { el.innerHTML = '<p class="adm-empty adm-error">Could not load system info.</p>'; return; }
    const data = await res.json();
    const rows = Object.entries(data.files).map(([name, info]) => `
      <div class="adm-row adm-row-system">
        <span class="adm-row-meta" data-label="File">${escHtml(name)}</span>
        <span class="adm-row-meta" data-label="Exists" style="color:${info.exists ? 'var(--positive)' : 'var(--negative)'}">${info.exists ? 'Yes' : 'No'}</span>
        <span class="adm-row-meta" data-label="Size">${info.size_bytes != null ? info.size_bytes + ' B' : '—'}</span>
        <span class="adm-row-meta" data-label="Modified" title="${escHtml(info.modified_at || '')}">${escHtml(info.modified_at || '—')}</span>
      </div>
    `).join('');
    el.innerHTML = `
      <p class="adm-row-meta" style="margin-bottom:4px;word-break:break-all"><strong>DATA_DIR:</strong> ${escHtml(data.data_dir)}</p>
      <p class="adm-row-meta" style="margin-bottom:16px;word-break:break-all"><strong>APP_DIR:</strong> ${escHtml(data.app_dir)}</p>
      <p class="adm-row-meta" style="margin-bottom:16px">${data.user_count} user(s) · ${data.org_count} organisation(s)</p>
      ${header}${rows}
    `;
  } catch { el.innerHTML = '<p class="adm-empty adm-error">Error loading system info.</p>'; }
}
