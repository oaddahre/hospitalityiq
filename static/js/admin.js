// ─── Kodo Admin ──────────────────────────────────────────────────────────
// Reaching this page at all already required a logged-in Advisory-tier
// session (admin_page() in app.py). window.__ADMIN_CSRF__ is a per-session
// CSRF token, not a secret — meaningless without the session cookie it's
// paired with. Every state-changing request below sends it back as
// X-CSRF-Token; admin_required (app.py) checks it against the session.
// Read live (not cached into a const at load time) — admin.html sets this
// global in its own <script> tag, and reading it fresh here means the
// order of that tag relative to this file's <script src> can never
// silently send the literal string "undefined" as the token again.
function csrfToken() { return window.__ADMIN_CSRF__; }

function escHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function todayStr() { return new Date().toISOString().slice(0, 10); }

function authHeaders(json) {
  const h = { 'X-CSRF-Token': csrfToken() };
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

// ─── Theme toggle (shared site-wide theme, see static/js/theme.js) ──
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
      KodoTheme.set(next);
      applyAdminTheme(next);
    });
  });
}
wireThemeToggle('admToggleDark', 'admToggleLight');
wireThemeToggle('admToggleDarkMobile', 'admToggleLightMobile');
(function initTheme() {
  applyAdminTheme(KodoTheme.get());
})();

// ─── Mobile nav ──────────────────────────────────────────────────────────
const mobileOverlay = document.getElementById('admMobileOverlay');
document.getElementById('admHamburgerBtn').addEventListener('click', () => mobileOverlay.classList.add('open'));
document.getElementById('admMobileClose').addEventListener('click', () => mobileOverlay.classList.remove('open'));
mobileOverlay.addEventListener('click', e => { if (e.target === mobileOverlay) mobileOverlay.classList.remove('open'); });

// ─── Section navigation (last section remembered in localStorage) ────────
const SECTIONS = ['overview', 'users', 'orgs', 'news', 'uploads', 'rates', 'occupancy', 'events', 'coverage', 'health', 'system'];
const SECTION_LOADERS = {
  overview: loadOverview,
  users: loadUsers,
  orgs: loadOrgs,
  news: loadArticles,
  uploads: () => { loadHotelsForDI(); loadRecentUploads(); loadFiguresLoaded(); },
  rates: () => { loadScraperStatus(); loadScrapeCoverage(); populateHotelSelect(); loadIdOverrides(); loadCoordHistory(); loadRatesStore(false); },
  occupancy: () => { loadOccupancyStatus(); loadSideBySide(); loadSwitch(); },
  events: loadEvents,
  coverage: loadPriceCoverage,
  health: () => loadDataHealth(false),
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
  if (location.hash !== '#' + name) history.replaceState(null, '', '#' + name);
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
  const fromHash = location.hash.slice(1);          // /admin#coverage opens that section
  showSection(SECTIONS.includes(fromHash) ? fromHash : last);
})();
window.addEventListener('hashchange', () => { const s = location.hash.slice(1); if (SECTIONS.includes(s)) showSection(s); });

// Who's signed in — read from /api/me (already exists, used by the rest of
// the platform) rather than guessing a new field shape here.
(async function loadSignedIn() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();
    document.getElementById('admUserMenuEmail').textContent = data.email || '';
  } catch {}
})();

// ─── Nav user menu (top right: email → Back to platform / Log out) ───────
(function wireUserMenu() {
  const btn = document.getElementById('admUserMenuBtn');
  const dropdown = document.getElementById('admUserMenuDropdown');
  btn.addEventListener('click', e => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
  });
  document.addEventListener('click', e => {
    if (!dropdown.contains(e.target) && e.target !== btn) dropdown.classList.remove('open');
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') dropdown.classList.remove('open');
  });
})();

// ─── Generic per-row "⋯" menu — one #admRowMenu element, repositioned
// under whichever trigger button opened it. Shared by Users and (later)
// every other section's row actions, so there's one menu implementation
// to get right instead of one per section. ──────────────────────────────
const rowMenu = document.getElementById('admRowMenu');
let rowMenuCleanup = [];

function closeRowMenu() {
  rowMenu.classList.remove('open');
  rowMenu._trigger = null;
  rowMenuCleanup.forEach(fn => fn());
  rowMenuCleanup = [];
}

// Repositions the (already-rendered) menu under triggerBtn, clamped to the
// viewport. Called on open and again after swapping in a confirm prompt,
// since that changes the menu's size.
function positionRowMenu(triggerBtn) {
  const trigRect = triggerBtn.getBoundingClientRect();
  const menuRect = rowMenu.getBoundingClientRect();
  let left = trigRect.right - menuRect.width;
  let top = trigRect.bottom + 6;
  left = Math.max(8, Math.min(left, window.innerWidth - menuRect.width - 8));
  if (top + menuRect.height > window.innerHeight - 8) top = trigRect.top - menuRect.height - 6;
  rowMenu.style.left = left + 'px';
  rowMenu.style.top = top + 'px';
}

function renderRowMenuItems(triggerBtn, items) {
  rowMenu.innerHTML = items.map((it, i) =>
    `<button type="button" class="adm-row-menu-item${it.destructive ? ' destructive' : ''}" data-i="${i}">${escHtml(it.label)}</button>`
  ).join('');
  rowMenu.querySelectorAll('button').forEach((btn, i) => {
    btn.addEventListener('click', () => {
      const item = items[i];
      if (item.confirmMessage) {
        renderRowMenuConfirm(triggerBtn, item.confirmMessage, item.onConfirm);
      } else {
        closeRowMenu();
        item.onClick && item.onClick(triggerBtn);
      }
    });
  });
  positionRowMenu(triggerBtn);
}

// Confirm/Cancel swapped into the SAME floating menu — not inserted next
// to the tiny "⋯" button, which sits in a ~40px Actions column far too
// narrow for a "Delete this user? Confirm Cancel" prompt to expand into
// without overflowing the row. This is the "existing inline confirm UI"
// (same Confirm/Cancel look used throughout this file), just anchored to
// the menu popover
// instead of the table cell.
function renderRowMenuConfirm(triggerBtn, message, onConfirm) {
  rowMenu.innerHTML = `
    <div class="adm-row-menu-confirm">
      <span>${escHtml(message)}</span>
      <div class="adm-row-menu-confirm-actions">
        <button type="button" class="adm-btn-text destructive" id="rmConfirmYes">Confirm</button>
        <button type="button" class="adm-btn-text" id="rmConfirmNo">Cancel</button>
      </div>
    </div>`;
  document.getElementById('rmConfirmYes').addEventListener('click', () => { closeRowMenu(); onConfirm(); });
  document.getElementById('rmConfirmNo').addEventListener('click', () => closeRowMenu());
  positionRowMenu(triggerBtn);
}

function openRowMenu(triggerBtn, items) {
  const reopening = rowMenu._trigger === triggerBtn;
  closeRowMenu();
  if (reopening) return;

  rowMenu._trigger = triggerBtn;
  // Measure off-screen first (visibility:hidden, already display:flex via
  // .open) so position is computed from the menu's real size, then reveal.
  rowMenu.style.left = '-9999px';
  rowMenu.style.top = '-9999px';
  rowMenu.classList.add('open');
  renderRowMenuItems(triggerBtn, items);

  const onDocClick = e => {
    if (!rowMenu.contains(e.target) && e.target !== triggerBtn && !triggerBtn.contains(e.target)) closeRowMenu();
  };
  const onKey = e => { if (e.key === 'Escape') closeRowMenu(); };
  // capture:true so this runs before the trigger's own click handler could
  // re-open a different menu while this one is still wired up.
  document.addEventListener('click', onDocClick, true);
  document.addEventListener('keydown', onKey);
  rowMenuCleanup.push(() => document.removeEventListener('click', onDocClick, true));
  rowMenuCleanup.push(() => document.removeEventListener('keydown', onKey));
}

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
let usersFilterState = { tier: 'all', status: 'all', search: '' };
let usersSort = { field: 'created_at', dir: 'desc' };
let usersPage = 1;
const USERS_PAGE_SIZE = 25;

// The server has more status values than we want to show (pending_approval,
// pending_verification, pending_payment, pending, suspended, rejected…).
// This is the one place that collapses them into the three buckets the
// redesigned Status column actually shows — mirrors "Active = verified and
// enabled" in spirit: in this app "active" already implies verified+approved,
// so anything that isn't active or disabled reads as Pending.
function statusBucket(u) {
  if (u.status === 'suspended' || u.status === 'rejected') return 'disabled';
  if (u.status === 'active') return 'active';
  return 'pending';
}
const STATUS_META = {
  active:   { label: 'Active',   family: 'green'  },
  pending:  { label: 'Pending',  family: 'orange' },
  disabled: { label: 'Disabled', family: 'grey'   },
};
// Status pills use the colour families (tokens.css): Active green, Pending
// orange, Disabled grey. Tier pills take their colour from data-plan (the
// plan mapping in tokens.css); being an admin is called out separately by
// .adm-admin-tag (data-plan="admin", the ink pill).
const TIER_META = {
  observer:    { label: 'Observer' },
  benchmarker: { label: 'Benchmarker' },
  advisory:    { label: 'Advisory' },
};

function shortDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function buildUsersFilters() {
  const tierEl   = document.getElementById('users-tier-filters');
  const statusEl = document.getElementById('users-status-filters');
  const tiers = [['All', 'all'], ['Observer', 'observer'], ['Benchmarker', 'benchmarker'], ['Advisory', 'advisory']];
  tierEl.innerHTML = tiers.map(([label, val], i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="tier" data-value="${val}">${label}</button>`
  ).join('');
  const statuses = [['All', 'all'], ['Active', 'active'], ['Pending', 'pending'], ['Disabled', 'disabled']];
  statusEl.innerHTML = statuses.map(([label, val], i) =>
    `<button class="list-pill${i === 0 ? ' active' : ''}" data-filter="status" data-value="${val}">${label}</button>`
  ).join('');
  [tierEl, statusEl].forEach(container => {
    container.addEventListener('click', e => {
      const btn = e.target.closest('.list-pill');
      if (!btn) return;
      container.querySelectorAll('.list-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      usersFilterState[btn.dataset.filter] = btn.dataset.value;
      usersPage = 1;
      renderUsers();
    });
  });
}

document.getElementById('users-search').addEventListener('input', e => {
  usersFilterState.search = e.target.value.trim().toLowerCase();
  usersPage = 1;
  renderUsers();
});
document.getElementById('users-create-btn').addEventListener('click', openCreateUserPanel);

document.getElementById('users-header').addEventListener('click', e => {
  const th = e.target.closest('[data-sort]');
  if (!th) return;
  if (usersSort.field === th.dataset.sort) {
    usersSort.dir = usersSort.dir === 'asc' ? 'desc' : 'asc';
  } else {
    usersSort.field = th.dataset.sort;
    usersSort.dir = 'asc';
  }
  renderUsers();
});

function sortUsers(list) {
  const { field, dir } = usersSort;
  const mul = dir === 'asc' ? 1 : -1;
  return [...list].sort((a, b) => {
    let av, bv;
    if (field === 'status') { av = statusBucket(a); bv = statusBucket(b); }
    else { av = a[field]; bv = b[field]; }
    av = (av || '').toString().toLowerCase();
    bv = (bv || '').toString().toLowerCase();
    if (av < bv) return -1 * mul;
    if (av > bv) return 1 * mul;
    return 0;
  });
}

function updateUsersSortIndicator() {
  document.querySelectorAll('#users-header [data-sort]').forEach(el => {
    const active = el.dataset.sort === usersSort.field;
    el.classList.toggle('adm-sort-active', active);
    if (active) el.dataset.sortDir = usersSort.dir; else el.removeAttribute('data-sort-dir');
  });
}

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

function renderUsers() {
  const ledger = document.getElementById('users-ledger');
  const { tier, status, search } = usersFilterState;
  let filtered = usersData.filter(u => {
    if (tier !== 'all' && u.tier !== tier) return false;
    if (status !== 'all' && statusBucket(u) !== status) return false;
    if (search) {
      const hay = `${u.name || ''} ${u.email || ''}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  });

  document.getElementById('users-count').textContent = `${filtered.length} user${filtered.length === 1 ? '' : 's'}`;
  filtered = sortUsers(filtered);

  const totalPages = Math.max(1, Math.ceil(filtered.length / USERS_PAGE_SIZE));
  if (usersPage > totalPages) usersPage = totalPages;
  const pageItems = filtered.slice((usersPage - 1) * USERS_PAGE_SIZE, usersPage * USERS_PAGE_SIZE);

  if (!filtered.length) {
    ledger.innerHTML = '<p class="adm-empty">No users match your filters.</p>';
  } else {
    ledger.innerHTML = pageItems.map(u => {
      const planKey = TIER_META[u.tier] ? u.tier : 'observer';
      const tierMeta = TIER_META[planKey];
      const statusMeta = STATUS_META[statusBucket(u)];
      return `<div class="adm-row adm-row-users">
        <div class="adm-row-main" data-label="Name" style="flex-direction:row;align-items:center;gap:6px">
          <span class="adm-row-name" title="${escHtml(u.name || u.email)}">${escHtml(u.name || '—')}</span>
          ${u.is_admin ? '<span class="adm-admin-tag" data-plan="admin">Admin</span>' : ''}
        </div>
        <span class="adm-row-email" data-label="Email" title="${escHtml(u.email)}">${escHtml(u.email)}</span>
        <span data-label="Tier"><span class="adm-pill pill--plan" data-plan="${planKey}">${tierMeta.label}</span></span>
        <span data-label="Status"><span class="adm-pill pill--${statusMeta.family}">${statusMeta.label}</span></span>
        <span class="adm-row-meta" data-label="Joined">${shortDate(u.created_at)}</span>
        <span class="adm-row-meta" data-label="Last login">${u.last_login ? shortDate(u.last_login) : 'Never'}</span>
        <div class="adm-row-actions" data-label="Actions">
          <button class="adm-row-menu-btn" type="button" data-uid="${u.id}" aria-label="Actions for ${escHtml(u.name || u.email)}">⋯</button>
        </div>
      </div>`;
    }).join('');
  }

  renderUsersPagination(totalPages);
  updateUsersSortIndicator();
}

function renderUsersPagination(totalPages) {
  const el = document.getElementById('users-pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }
  el.innerHTML = `
    <button class="adm-btn-text" id="users-prev-page" type="button"${usersPage === 1 ? ' disabled' : ''}>‹ Prev</button>
    <span class="adm-pagination-label">Page ${usersPage} of ${totalPages}</span>
    <button class="adm-btn-text" id="users-next-page" type="button"${usersPage === totalPages ? ' disabled' : ''}>Next ›</button>
  `;
  document.getElementById('users-prev-page').addEventListener('click', () => { if (usersPage > 1) { usersPage--; renderUsers(); } });
  document.getElementById('users-next-page').addEventListener('click', () => { if (usersPage < totalPages) { usersPage++; renderUsers(); } });
}

// Builds this row's "⋯" menu items. Disable/Delete are left out entirely
// for the signed-in admin's own row — mirrors the 400 app.py already
// returns if either were attempted anyway (admin_users_update /
// admin_users_delete), so the UI never offers what the API would refuse.
function buildUserMenuItems(u) {
  const bucket = statusBucket(u);
  const items = [];
  items.push({ label: 'Edit', onClick: () => openEditUserPanel(u.id) });
  items.push({
    label: 'Reset password',
    confirmMessage: `Send a password reset email to ${u.email}?`,
    onConfirm: () => resetPassword(u.id),
  });
  if (!u.email_verified) {
    items.push({
      label: 'Mark verified',
      confirmMessage: 'This skips the email check. Only do this if you know this person.',
      onConfirm: () => userAction(u.id, 'verify'),
    });
    items.push({ label: 'Resend confirmation', onClick: () => userAction(u.id, 'resend-verification') });
  }
  if (!u.is_self && bucket !== 'disabled') {
    items.push({
      label: 'Disable', destructive: true,
      confirmMessage: 'Disable this user?',
      onConfirm: () => updateUser(u.id, { status: 'suspended' }),
    });
  }
  if (bucket !== 'active') {
    items.push({ label: 'Enable', onClick: () => updateUser(u.id, { status: 'active' }) });
  }
  if (!u.is_self) {
    items.push({
      label: 'Delete', destructive: true,
      confirmMessage: `Delete ${u.name || u.email}? This can't be undone.`,
      onConfirm: () => deleteUser(u.id),
    });
  }
  return items;
}

document.getElementById('users-ledger').addEventListener('click', e => {
  const btn = e.target.closest('.adm-row-menu-btn');
  if (!btn) return;
  const u = usersData.find(x => x.id === btn.dataset.uid);
  if (!u) return;
  openRowMenu(btn, buildUserMenuItems(u));
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

async function resetPassword(uid) {
  try {
    const res = await fetch(`/admin/users/${uid}/reset-password`, { method: 'POST', headers: authHeaders() });
    const data = await res.json();
    toast(data.message || (res.ok ? 'Done.' : 'Failed.'), res.ok ? 'success' : 'error');
  } catch { toast('Network error.', 'error'); }
}

async function updateUser(uid, changes) {
  try {
    const res = await fetch('/admin/users/' + uid, { method: 'PUT', headers: authHeaders(true), body: JSON.stringify(changes) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { toast(data.error || 'Update failed.', 'error'); return; }
    await loadUsers();
    toast('Updated.', 'success');
  } catch { toast('Network error.', 'error'); }
}

async function deleteUser(uid) {
  try {
    const res = await fetch('/admin/users/' + uid, { method: 'DELETE', headers: authHeaders() });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) { toast(data.error || 'Delete failed.', 'error'); return; }
    await loadUsers();
    toast('User deleted.', 'success');
  } catch { toast('Network error.', 'error'); }
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
    <div class="adm-field-group"><label class="adm-label">Full name</label><input class="adm-input" id="ue-name" value="${escHtml(u.name || '')}" /></div>
    <div class="adm-field-group"><label class="adm-label">Email</label><input class="adm-input" value="${escHtml(u.email)}" disabled /></div>
    <div class="adm-field-group"><label class="adm-label">Organisation</label><input class="adm-input" id="ue-org" value="${escHtml(u.organisation || '')}" /></div>
    <div class="adm-field-group"><label class="adm-label">Tier</label>
      <select class="adm-select" id="ue-tier">
        ${['observer', 'benchmarker', 'advisory'].map(t => `<option value="${t}"${u.tier === t ? ' selected' : ''}>${t[0].toUpperCase() + t.slice(1)}</option>`).join('')}
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
    const name = document.getElementById('ue-name').value.trim();
    const org = document.getElementById('ue-org').value.trim();
    const tier = document.getElementById('ue-tier').value;
    const status = document.getElementById('ue-status').value;
    await updateUser(uid, { name, organisation: org, tier, status });
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
    <span>Name</span><span>Owner</span><span>Seats</span><span>Members</span><span>Actions</span>
  </div>`;

  if (!filtered.length) {
    ledger.innerHTML = header + '<p class="adm-empty">No organisations match your search.</p>';
    return;
  }

  ledger.innerHTML = header + filtered.map(o => {
    const isDup = byName[o.name].length > 1;
    const memberCount = o.seats_used || 0;
    return `<div class="adm-row adm-row-orgs">
      <div class="adm-row-main" data-label="Name">
        <span class="adm-row-name" title="${escHtml(o.name)}">${escHtml(o.name)}${isDup ? ' <span class="adm-pill pill--red">duplicate</span>' : ''}</span>
        <span class="adm-row-sub">${escHtml(o.plan || '')}</span>
      </div>
      <div class="adm-row-main" data-label="Owner">
        <span class="adm-row-name" style="font-weight:400" title="${escHtml(o.owner_email || '')}">${escHtml(o.owner_name || '—')}</span>
        <span class="adm-row-sub" title="${escHtml(o.owner_email || '')}">${escHtml(o.owner_email || '')}</span>
      </div>
      <span class="adm-row-meta" data-label="Seats">${o.seats_used || 0} / ${o.seats_total || 1}</span>
      <span class="adm-row-meta" data-label="Members">${memberCount}</span>
      <div class="adm-row-actions" data-label="Actions">
        <button class="adm-row-menu-btn" type="button" data-oid="${o.id}" aria-label="Actions for ${escHtml(o.name)}">⋯</button>
      </div>
    </div>`;
  }).join('');
}

// Builds this org row's "⋯" menu — Delete only offered once it has no
// members, same guard the old inline Delete link used (canDelete above).
function buildOrgMenuItems(o) {
  const items = [{ label: 'Members', onClick: () => openOrgMembersPanel(o.id, o.name) }];
  if (o.status === 'active') {
    items.push({ label: 'Suspend', destructive: true, onClick: () => updateOrg(o.id, { status: 'suspended' }) });
  } else {
    items.push({ label: 'Reactivate', onClick: () => updateOrg(o.id, { status: 'active' }) });
  }
  if ((o.seats_used || 0) === 0) {
    items.push({
      label: 'Delete', destructive: true,
      confirmMessage: `Delete "${o.name}"? This cannot be undone.`,
      onConfirm: () => deleteOrg(o.id),
    });
  }
  return items;
}

document.getElementById('orgs-ledger').addEventListener('click', e => {
  const btn = e.target.closest('.adm-row-menu-btn');
  if (!btn) return;
  const o = orgsData.find(x => x.id === btn.dataset.oid);
  if (!o) return;
  openRowMenu(btn, buildOrgMenuItems(o));
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
          <span class="adm-pill pill--${STATUS_META[statusBucket(m)].family}">${escHtml((m.status || '').replace(/_/g, ' '))}</span>
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
    <span>Title</span><span>Category</span><span>Type</span><span>Date</span><span>Views</span><span>Actions</span>
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
        ${a.featured ? '<span class="adm-pill pill--solid">Featured</span>' : ''}
      </div>
      <span class="adm-row-meta" data-label="Category">${escHtml(a.category || '—')}</span>
      <span class="adm-row-meta" data-label="Type">${escHtml(a.type || '—')}</span>
      <span class="adm-row-meta" data-label="Date">${escHtml(a.date || '—')}</span>
      <span class="adm-row-meta" data-label="Views">${a.views || 0}</span>
      <div class="adm-row-actions" data-label="Actions">
        <button class="adm-row-menu-btn" type="button" data-id="${a.id}" aria-label="Actions for ${escHtml(artTitle(a))}">⋯</button>
      </div>
    </div>`;
  }).join('');
}

function buildArticleMenuItems(a) {
  const status = artStatus(a);
  return [
    { label: 'Edit', onClick: () => openArticlePanel(a.id) },
    { label: status === 'published' ? 'Unpublish' : 'Publish', onClick: () => togglePublish(a.id) },
    {
      label: 'Delete', destructive: true,
      confirmMessage: `Delete "${artTitle(a)}"?`,
      onConfirm: () => deleteArticle(a.id),
    },
  ];
}

document.getElementById('news-ledger').addEventListener('click', e => {
  const btn = e.target.closest('.adm-row-menu-btn');
  if (!btn) return;
  const id = parseInt(btn.dataset.id, 10);
  const a = articles.find(x => x.id === id);
  if (!a) return;
  openRowMenu(btn, buildArticleMenuItems(a));
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
    <div class="adm-field-group"><label class="adm-label">Author</label><input class="adm-input" id="f-author" value="${escHtml(a ? a.author : 'Kodo Editorial') || 'Kodo Editorial'}" /></div>
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
    author: document.getElementById('f-author').value.trim() || 'Kodo Editorial',
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

// A CSV (commas or semicolons, quoted fields) or the first sheet of an Excel
// file -> rows keyed by their header. The server checks every value
// (hotel_figures.py) and answers with one line per problem.
function handleFile(file) {
  const reader = new FileReader();
  if (/\.xlsx?$/i.test(file.name)) {
    reader.onload = ev => {
      if (!window.XLSX) { diMsg('The Excel reader did not load: save the file as CSV and try again.', true); return; }
      try {
        const wb = XLSX.read(new Uint8Array(ev.target.result), { type: 'array', cellDates: false });
        const ws = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json(ws, { header: 1, raw: false, defval: '' });
        showParsed(rows, file.name);
      } catch (e) { diMsg('Could not read this Excel file: ' + e.message, true); }
    };
    reader.readAsArrayBuffer(file);
  } else {
    reader.onload = ev => showParsed(parseDelimited(ev.target.result), file.name);
    reader.readAsText(file);
  }
}

function parseDelimited(text) {
  text = String(text).replace(/^﻿/, '');
  const first = text.split(/\r?\n/, 1)[0] || '';
  const delim = (first.match(/;/g) || []).length > (first.match(/,/g) || []).length ? ';' : ',';
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') quoted = false;
      else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === delim) { row.push(cell); cell = ''; }
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); rows.push(row); row = []; cell = '';
    } else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter(r => r.some(c => String(c).trim()));
}

function showParsed(grid, filename) {
  const errBox = document.getElementById('di-errors');
  errBox.style.display = 'none';
  if (!grid.length) { diMsg('Empty file.', true); return; }
  const header = grid[0].map(h => String(h).trim());
  diParsed = grid.slice(1).map(r => Object.fromEntries(header.map((h, j) => [h, r[j] ?? ''])));
  dz.querySelector('.adm-dropzone-main').textContent = `${filename} · ${diParsed.length} rows`;
  diCheck(filename);
}

// The server checks every row (hotel_figures.py) and sends back the rows as
// they would be saved; nothing is saved until "Save these figures", and a
// file with any row in error can't be saved at all.
async function diCheck(filename) {
  const sel = document.getElementById('di-hotel');
  const submit = document.getElementById('di-submit');
  submit.disabled = true;
  diMsg(`Checking ${diParsed.length} rows…`, false);
  let res, data;
  try {
    res = await fetch('/admin/upload-figures', { method: 'POST', headers: authHeaders(true),
      body: JSON.stringify({ hotel_id: sel.value, rows: diParsed, preview: true }) });
    data = await res.json();
  } catch { diMsg('Could not check the file.', true); return; }
  diShowResult(data);
  const rows = data.rows || [];
  document.getElementById('di-preview-table').innerHTML = rows.length
    ? `<div class="dh-scroll"><table class="adm-table"><thead><tr><th>Hotel</th><th>Month or night</th><th>Type</th><th>Occupancy</th><th>ADR (MAD)</th><th>Rooms RevPAR</th><th>Rooms available</th><th></th></tr></thead><tbody>`
      + rows.map(r => `<tr><td>${escHtml(r.hotel)} <span class="adm-hint">${escHtml(r.city)}</span></td><td>${escHtml(r.period)}</td><td>${escHtml(DI_TYPE[r.data_type] || r.data_type)}</td><td>${r.occupancy}%</td>`
        + `<td>${Number(r.adr).toLocaleString('en')}</td><td>${r.revpar === '' ? '—' : Number(r.revpar).toLocaleString('en')}</td>`
        + `<td>${r.rooms_available === '' ? '—' : Number(r.rooms_available).toLocaleString('en')}</td><td>${r.replaces ? 'replaces the stored figure' : 'new'}</td></tr>`).join('')
      + '</tbody></table></div>'
    : '<p class="adm-hint">No row passed the checks.</p>';
  document.getElementById('di-preview').style.display = 'block';
  if (res.ok) {
    submit.disabled = false;
    diMsg(`All ${rows.length} rows pass the checks (${data.months} months, ${data.nights} nights${data.replaces ? `, ${data.replaces} replace stored figures` : ''}). Nothing is saved until you press Save.`, false);
  } else {
    diMsg(data.error || 'The file has problems: nothing can be saved.', true);
  }
}

function diShowResult(data) {
  const errBox = document.getElementById('di-errors');
  const errs = data.details || [], notes = data.notes || [];
  errBox.style.display = errs.length || notes.length ? '' : 'none';
  errBox.innerHTML = (errs.length ? `<strong>${errs.length} problem${errs.length === 1 ? '' : 's'}: fix ${errs.length === 1 ? 'it' : 'them'} in the file, then load it again.</strong><br>` + errs.map(escHtml).join('<br>') : '')
    + (notes.length ? `${errs.length ? '<br>' : ''}<strong>${notes.length} note${notes.length === 1 ? '' : 's'} (kept):</strong><br>` + notes.map(escHtml).join('<br>') : '');
}

function diMsg(text, isError) {
  const el = document.getElementById('di-msg');
  el.textContent = text;
  el.style.color = isError ? 'var(--negative)' : 'var(--positive)';
}

document.getElementById('di-hotel').addEventListener('change', () => { if (diParsed.length) diCheck(''); });

document.getElementById('di-submit').addEventListener('click', async () => {
  const sel = document.getElementById('di-hotel');
  const hotelId = sel.value;
  const hotelName = sel.options[sel.selectedIndex]?.dataset?.name || '';
  if (!diParsed.length) { diMsg('No data to upload.', true); return; }
  document.getElementById('di-submit').disabled = true;
  diMsg('Saving…', false);
  const res = await fetch('/admin/upload-figures', {
    method: 'POST', headers: authHeaders(true),
    body: JSON.stringify({ hotel_id: hotelId, hotel_name: hotelName, rows: diParsed }),
  });
  const data = await res.json().catch(() => ({}));
  diShowResult(data);
  if (!res.ok) { diMsg(data.error || 'Upload failed.', true); return; }
  diMsg(`${data.rows_ingested} saved (${data.months} months, ${data.nights} nights${data.replaced ? `, ${data.replaced} replaced` : ''}) · ${data.date_range}`, false);
  diParsed = [];
  document.getElementById('di-preview').style.display = 'none';
  dz.querySelector('.adm-dropzone-main').textContent = 'Drag & drop a CSV or Excel file here';
  loadRecentUploads();
  loadFiguresLoaded();
});

const DI_TYPE = { actual: 'Actual', prior_year: 'Prior year (actual)', reforecast: 'Reforecast: not used to score the model' };
async function loadFiguresLoaded() {
  const t = document.getElementById('di-loaded');
  try {
    const res = await fetch('/admin/figures-loaded', { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) throw new Error();
    t.innerHTML = d.months.length
      ? '<thead><tr><th>Hotel</th><th>Month</th><th>Type</th><th>Occupancy</th><th>ADR (MAD)</th><th>Rooms available</th><th>Loaded</th></tr></thead><tbody>'
        + d.months.map(r => `<tr><td>${escHtml(r.hotel)} <span class="adm-hint">${escHtml(r.city)}</span></td><td>${escHtml(r.month)}</td><td>${escHtml(DI_TYPE[r.data_type] || r.data_type)}</td><td>${escHtml(r.occupancy)}%</td>`
          + `<td>${Number(r.adr).toLocaleString('en')}</td><td>${r.rooms_available ? Number(r.rooms_available).toLocaleString('en') : '—'}</td><td>${escHtml((r.uploaded_at || '').slice(0, 10))}</td></tr>`).join('') + '</tbody>'
        + (d.hotels.some(h => h.nights) ? `<tfoot><tr><td colspan="7" class="adm-hint">Daily figures: ${d.hotels.filter(h => h.nights).map(h => `${escHtml(h.name)} ${h.nights} nights`).join(' · ')}</td></tr></tfoot>` : '')
      : '<tbody><tr><td class="adm-hint">No data: no hotel figures have been loaded.</td></tr></tbody>';
  } catch { t.innerHTML = '<tbody><tr><td class="adm-hint">Could not load.</td></tr></tbody>'; }
}

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
// Last scraper run (scrape_coverage.csv): hotels per outcome, the hotels
// that did not get prices, nights priced out of the nights possible
async function loadScrapeCoverage() {
  const stats = document.getElementById('ri-cov-stats'), sum = document.getElementById('ri-cov-summary'),
    list = document.getElementById('ri-cov-list');
  try {
    const res = await fetch('/api/admin/scraper/coverage', { headers: authHeaders() });
    const d = await res.json();
    stats.replaceChildren(); list.replaceChildren();
    if (!res.ok || !d.has_data) { sum.textContent = d.message || d.error || 'No data'; return; }
    d.counts.forEach(([k, v]) => {   // in outcome order: ok first
      const box = document.createElement('div'); box.className = 'adm-stat';
      const val = document.createElement('span'); val.className = 'adm-stat-val'; val.textContent = v;
      const lab = document.createElement('span'); lab.className = 'adm-stat-label'; lab.textContent = k;
      box.append(val, lab); stats.appendChild(box);
    });
    const pct = d.nights_possible ? Math.round(100 * d.nights_priced / d.nights_possible) : 0;
    sum.textContent = `Run of ${d.scrape_date} · ${d.hotels} hotels · nights priced ${d.nights_priced.toLocaleString('en')} of `
      + `${d.nights_possible.toLocaleString('en')} possible (${pct}%) · nights ${d.window[0]} to ${d.window[1]}`;
    if (!d.problems.length) { list.textContent = 'Every hotel got prices (ok).'; return; }
    const t = document.createElement('table'); t.className = 'adm-table';
    t.innerHTML = '<thead><tr><th>Hotel</th><th>City</th><th>Outcome</th><th>Nights priced</th></tr></thead>';
    const tb = document.createElement('tbody');
    d.problems.forEach(p => {
      const tr = document.createElement('tr');
      [p.name, p.city || '–', p.outcome, String(p.nights)].forEach(v => { const td = document.createElement('td'); td.textContent = v; tr.appendChild(td); });
      tb.appendChild(tr);
    });
    t.appendChild(tb); list.appendChild(t);
  } catch { sum.textContent = 'Error loading the last run'; }
}

async function loadScraperStatus() {
  try {
    const res = await fetch('/api/scraper/status', { headers: authHeaders() });
    const data = await res.json();
    const statusEl = document.getElementById('ri-status');
    statusEl.textContent = data.running ? 'Running Now' : (data.scheduler_running ? 'Scheduler Active' : 'Scheduler Off');
    statusEl.classList.remove('pill--green', 'pill--orange');
    statusEl.classList.add(data.scheduler_running ? 'pill--green' : 'pill--orange');
    document.getElementById('ri-last-run').textContent = data.last_run
      ? `Last run: ${data.last_run.replace('T', ' ').slice(0, 19)}` : 'Never run';
    document.getElementById('ri-live-count').textContent = data.hotels_with_live ?? '—';
    document.getElementById('ri-est-count').textContent = data.hotels_estimated ?? '—';
    const src = data.source_breakdown || {};
    document.getElementById('ri-sources').textContent = Object.entries(src).map(([k, v]) => `${k}: ${v}`).join('  ·  ') || '—';
    document.getElementById('ri-log').textContent = data.log_tail || '(no log yet)';

    // DataForSEO (main price source): login and balance now, last run's cost
    const df = data.dataforseo || {};
    const dr = df.last_run || {};
    const money = v => v == null ? '' : `$${Number(v).toFixed(2)}`;
    document.getElementById('ri-dataforseo').textContent = 'DataForSEO: ' + ([
      { ok: 'OK', missing_credentials: 'Login not set', bad_login: 'Login rejected', no_balance: 'No balance', paused: 'Account paused', no_access: 'No access', error: 'Error' }[df.status] || '—',
      df.status !== 'ok' && df.message ? df.message : '',
      df.balance != null ? `balance ${money(df.balance)}${df.balance < df.min_balance ? ` (under ${money(df.min_balance)})` : ''}` : '',
      dr.cost != null ? `last run cost ${money(dr.cost)} · ${dr.price_calls || 0} price calls, ${dr.id_lookups || 0} ID lookups, ${dr.matched || 0} hotels matched` : '',
      dr.status && dr.status !== 'ok' && dr.message ? `last run: ${dr.message}` : '',
      (dr.errors || []).length ? `last error: ${dr.errors[dr.errors.length - 1]}` : '',
    ].filter(Boolean).join(' · '));

    const h = data.health || {};
    document.getElementById('ri-health').textContent = 'Data health: ' + (h.status === 'ok'
      ? `OK · last live price ${h.last_live_price} · ${h.nights_found} of ${h.nights_checked} nights found in the last run (${h.nights_found_pct}%)`
      : `Stale · ${(h.problems || []).join(' ')}`);
    document.getElementById('ri-cities').textContent = `Cities scraped: ${data.cities === 'all' ? 'all (SCRAPER_CITIES not set)' : data.cities}`
      + (data.limit ? ` · first ${data.limit} hotels (SCRAPER_LIMIT)` : '')
      + ` · browser steps (brand sites, Booking.com) ${data.browser_steps ? 'on' : 'off'}`;
    const st = data.store || {};
    if (st.data_dir) document.getElementById('ri-cities').textContent += ` · data folder ${st.data_dir}`
      + (st.on_railway ? (st.persistent ? ' (Railway volume: kept across deploys)' : ' (NOT the Railway volume: lost at every deploy)') : '')
      + ` · Google IDs cached ${st.google_ids_cached || 0}, not found ${st.google_ids_not_found || 0}`;
    if ((h.account_problems || []).length) document.getElementById('ri-health').textContent += ' · ' + h.account_problems.join(' ');
  } catch {
    document.getElementById('ri-log').textContent = 'Error loading status';
  }
}

// Occupancy model: v1 against v2 for one hotel, and the last calibration
document.getElementById('ri-occ-compare').addEventListener('click', async () => {
  const hid = document.getElementById('ri-occ-hotel').value, msg = document.getElementById('ri-occ-msg'),
    out = document.getElementById('ri-occ-result');
  if (!hid) { msg.textContent = 'Choose a hotel'; return; }
  msg.textContent = 'Loading…';
  try {
    const res = await fetch(`/api/admin/occupancy/compare?hotel_id=${encodeURIComponent(hid)}`, { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) { msg.textContent = d.error || 'Failed'; return; }
    document.getElementById('ri-occ-shown').textContent = (d.shown_model || 'v1').toUpperCase();
    msg.textContent = `Average next 30 nights: v1 ${d.avg_v1 ?? '–'}% · v2 ${d.avg_v2 ?? '–'}%`
      + (d.model_run_date ? ` · model run ${d.model_run_date}` : '') + (d.v2_computed_live ? ' · v2 computed now (not in the last run)' : '');
    const t = document.createElement('table');
    t.className = 'adm-table';
    t.innerHTML = '<thead><tr><th>Night</th><th>v1 low–mid–high</th><th>v2 low–mid–high</th><th>Published rate</th><th>Price coverage</th><th>v2 signals</th></tr></thead>';
    const tb = document.createElement('tbody');
    (d.nights || []).forEach(n => {
      const tr = document.createElement('tr');
      [n.night, n.v1 != null ? (n.v1_low != null ? `${n.v1_low}–${Math.round(n.v1)}–${n.v1_high}%` : `${Math.round(n.v1)}%`) : '–',
       n.v2_mid != null ? `${n.v2_low}–${n.v2_mid}–${n.v2_high}%` : '–',
       n.price != null ? `MAD ${Math.round(n.price).toLocaleString('en')}` : '–', n.price_coverage || '–',
       (n.signals || '').split(';').join(' · ')].forEach(v => { const td = document.createElement('td'); td.textContent = v; tr.appendChild(td); });
      tb.appendChild(tr);
    });
    t.appendChild(tb);
    out.replaceChildren(t);
  } catch { msg.textContent = 'Failed'; }
});

async function loadCalibration() {
  const el = document.getElementById('ri-occ-calib');
  try {
    const res = await fetch('/api/admin/occupancy/calibration', { headers: authHeaders() });
    const c = await res.json();
    el.replaceChildren();
    const line = t => { const d = document.createElement('div'); d.textContent = t; el.appendChild(d); };
    line(`${c.message || c.status}${c.run_at ? ' · run ' + c.run_at : ''}`);
    if (c.status !== 'ok') return;
    const fmt = (k, s) => `${k}: ${s.n} nights · average error v1 ${s.v1_mae_pts ?? '–'} pts, v2 ${s.v2_mae_pts ?? '–'} pts`
      + ` · bias v1 ${s.v1_bias_pts ?? '–'}, v2 ${s.v2_bias_pts ?? '–'}` + (s.v2_inside_range_pct != null ? ` · inside v2 range ${s.v2_inside_range_pct}%` : '');
    line(fmt('All', c.overall));
    Object.entries(c.by_city || {}).forEach(([k, s]) => line(fmt(k, s)));
    Object.entries(c.by_hotel_type || {}).forEach(([k, s]) => line(fmt(k.replace('_', ' '), s)));
    const ab = c.abroad_holidays;
    if (ab) {            // visitors' home-country school holidays (internal list): with and without
      line(`School holidays abroad (internal list): ${ab.nights_in_periods} of ${ab.nights_compared} real nights fall in them · ${ab.verdict}`);
      const row = (k, t) => line(`${k}: v2 error with ${t.with.v2 ?? '–'} pts, without ${t.without_all.v2 ?? '–'} pts · ` +
        ab.countries.map(cc => `without ${cc} ${t['without_' + cc].v2 ?? '–'}`).join(', '));
      if (ab.nights_in_periods) {
        row('All', ab.overall);
        Object.entries(ab.by_city || {}).forEach(([k, t]) => row(k, t));
        Object.entries(ab.by_month || {}).forEach(([k, t]) => row(k, t));
      }
    }
  } catch { el.textContent = '—'; }
}
loadCalibration();

async function populateHotelSelect() {
  try {
    const res = await fetch('/api/hotels', { headers: authHeaders() });
    const hotels = await res.json();
    ['ri-hotel-sel', 'ri-gid-hotel', 'ri-occ-hotel'].forEach(selId => {
      const sel = document.getElementById(selId);
      if (!sel || sel.dataset.populated) return;
      (hotels.hotels || hotels).forEach(h => {
        const opt = document.createElement('option');
        opt.value = h.id;
        opt.textContent = `${h.name} (${h.city})`;
        sel.appendChild(opt);
      });
      sel.dataset.populated = '1';
    });
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
  setTimeout(() => { btn.disabled = false; btn.textContent = 'Run Scraper Now'; loadScraperStatus(); loadScrapeCoverage(); }, 2500);
});

// Google hotel ID overrides, and the loose matches to review
function renderIdOverrides(data) {
  const ov = data.overrides || {};
  const list = document.getElementById('ri-gid-list');
  list.replaceChildren();
  const ids = Object.keys(ov);
  if (!ids.length) { list.textContent = 'No overrides.'; }
  ids.forEach(hid => {
    const row = document.createElement('div');
    row.textContent = `${ov[hid].hotel_name || hid}: ${ov[hid].identifier} (set ${String(ov[hid].set_at || '').slice(0, 10)}) `;
    const rm = document.createElement('button');
    rm.className = 'adm-btn adm-btn-secondary'; rm.textContent = 'Remove'; rm.style.marginLeft = '6px';
    rm.addEventListener('click', () => saveIdOverride(hid, ''));
    row.appendChild(rm); list.appendChild(row);
  });
  const lm = data.loose_matches || {};
  const ll = document.getElementById('ri-loose-list');
  ll.replaceChildren();
  const lk = Object.keys(lm);
  if (!lk.length) { ll.textContent = 'None so far.'; return; }
  lk.forEach(hid => {
    const m = lm[hid], row = document.createElement('div');
    row.textContent = `Our "${m.our_name}" ↔ Google "${m.google_name}" · ${m.distance_m} m apart · ${m.stage} · last seen ${String(m.last_seen || '').slice(0, 10)}`;
    ll.appendChild(row);
  });
}
async function loadIdOverrides() {
  try {
    const res = await fetch('/api/scraper/id-overrides', { headers: authHeaders() });
    if (res.ok) renderIdOverrides(await res.json());
  } catch {}
}
async function saveIdOverride(hotelId, identifier) {
  const msgEl = document.getElementById('ri-gid-msg');
  try {
    const res = await fetch('/api/scraper/id-overrides', { method: 'POST', headers: authHeaders(true),
      body: JSON.stringify({ hotel_id: hotelId, identifier }) });
    const data = await res.json();
    if (res.ok) {
      msgEl.textContent = identifier ? 'Saved: used from the next scraper run.' : 'Override removed.';
      msgEl.style.color = 'var(--positive)';
      document.getElementById('ri-gid-value').value = '';
      loadIdOverrides();
    } else { msgEl.textContent = data.error || 'Error saving'; msgEl.style.color = 'var(--negative)'; }
  } catch { msgEl.textContent = 'Network error'; msgEl.style.color = 'var(--negative)'; }
}
document.getElementById('ri-gid-save').addEventListener('click', () => {
  const hotelId = document.getElementById('ri-gid-hotel').value;
  const msgEl = document.getElementById('ri-gid-msg');
  if (!hotelId) { msgEl.textContent = 'Choose a hotel.'; msgEl.style.color = 'var(--negative)'; return; }
  saveIdOverride(hotelId, document.getElementById('ri-gid-value').value.trim());
});

// Coordinate corrections: preview, apply, undo (this server's hotels.csv)
let coordCsv = '';
function coordRows(el, rows) {
  rows.slice(0, 60).forEach(r => {
    const d = document.createElement('div');
    d.textContent = `${r.status}: ${r.hotel || r.hotel_id} · ${(r.current || []).join(', ') || '—'} → ${r.new.join(', ')} (${r.approve})`;
    el.appendChild(d);
  });
}
async function coordPost(url, body) {
  const res = await fetch(url, { method: 'POST', headers: authHeaders(true), body: JSON.stringify(body) });
  return [res.ok, await res.json().catch(() => ({}))];
}
document.getElementById('ri-coord-file').addEventListener('change', async e => {
  const f = e.target.files[0];
  coordCsv = f ? await f.text() : '';
  document.getElementById('ri-coord-apply').disabled = true;
  document.getElementById('ri-coord-result').replaceChildren();
});
document.getElementById('ri-coord-preview').addEventListener('click', async () => {
  const msg = document.getElementById('ri-coord-msg'), out = document.getElementById('ri-coord-result');
  out.replaceChildren();
  const [ok, data] = await coordPost('/api/admin/coordinates/preview', { csv: coordCsv });
  if (!ok) { msg.textContent = data.error || 'Preview failed'; msg.style.color = 'var(--negative)'; return; }
  const c = data.counts || {};
  msg.textContent = `Would apply ${c.apply || 0} · already applied ${c.already || 0} · changed since the audit ${c.conflict || 0} · not approved ${c['not approved'] || 0} · not found ${c['not found'] || 0}`;
  msg.style.color = '';
  coordRows(out, data.rows || []);
  document.getElementById('ri-coord-apply').disabled = !(c.apply > 0);
});
document.getElementById('ri-coord-apply').addEventListener('click', async () => {
  if (!confirm('Apply the approved coordinate changes to this server\'s hotels.csv? A backup is made first.')) return;
  const msg = document.getElementById('ri-coord-msg');
  const [ok, data] = await coordPost('/api/admin/coordinates/apply', { csv: coordCsv, confirm: true });
  msg.textContent = ok ? `Applied ${data.applied} changes · backup ${data.backup || '—'}` : (data.error || 'Apply failed');
  msg.style.color = ok ? 'var(--positive)' : 'var(--negative)';
  document.getElementById('ri-coord-apply').disabled = true;
  loadCoordHistory();
});
let idsJson = '';
document.getElementById('ri-ids-file').addEventListener('change', async e => {
  const f = e.target.files[0];
  idsJson = f ? await f.text() : '';
  document.getElementById('ri-ids-import').disabled = true;
  document.getElementById('ri-ids-result').replaceChildren();
});
function idsCounts(c) { return Object.entries(c || {}).map(([k, v]) => `${k} ${v}`).join(' · ') || 'nothing to import'; }
function idsRows(rows) {
  const out = document.getElementById('ri-ids-result');
  out.replaceChildren();
  (rows || []).forEach(r => {
    const d = document.createElement('div');
    d.textContent = `${r.status}: hotel ${r.hotel_id} ${r.name} · file ${r.identifier}` + (r.server_identifier ? ` · server ${r.server_identifier}` : '');
    out.appendChild(d);
  });
}
document.getElementById('ri-ids-preview').addEventListener('click', async () => {
  const msg = document.getElementById('ri-ids-msg');
  const [ok, data] = await coordPost('/api/admin/google-ids/preview', { json: idsJson });
  if (!ok) { msg.textContent = data.error || 'Preview failed'; msg.style.color = 'var(--negative)'; return; }
  msg.textContent = idsCounts(data.counts); msg.style.color = '';
  idsRows(data.rows);
  document.getElementById('ri-ids-import').disabled = !Object.keys(data.counts || {}).some(k => k.endsWith(': import') || k.endsWith(': reject'));
});
document.getElementById('ri-ids-import').addEventListener('click', async () => {
  if (!confirm('Import these Google IDs into this server? Both ID files are backed up first.')) return;
  const msg = document.getElementById('ri-ids-msg');
  const [ok, data] = await coordPost('/api/admin/google-ids/import', { json: idsJson, confirm: true });
  msg.textContent = ok ? `Imported ${data.imported} · backups ${(data.backups || []).join(', ') || '—'}` : (data.error || 'Import failed');
  msg.style.color = ok ? 'var(--positive)' : 'var(--negative)';
  document.getElementById('ri-ids-import').disabled = true;
  loadCoordHistory(); loadIdOverrides();
});

// Approve Google ID candidates, and hide or remove hotels (same flow)
function csvSection(prefix, urls, describe, confirmText, done) {
  let text = '';
  const btn = document.getElementById(`ri-${prefix}-apply`), msg = document.getElementById(`ri-${prefix}-msg`),
    out = document.getElementById(`ri-${prefix}-result`);
  const show = data => {
    out.replaceChildren();
    (data.rows || []).forEach(r => { const d = document.createElement('div'); d.textContent = describe(r); out.appendChild(d); });
  };
  const counts = c => Object.entries(c || {}).map(([k, v]) => `${k} ${v}`).join(' · ') || 'nothing in the file';
  document.getElementById(`ri-${prefix}-file`).addEventListener('change', async e => {
    const f = e.target.files[0];
    text = f ? await f.text() : '';
    btn.disabled = true; out.replaceChildren(); msg.textContent = '';
  });
  document.getElementById(`ri-${prefix}-preview`).addEventListener('click', async () => {
    const [ok, data] = await coordPost(urls[0], { csv: text });
    if (!ok) { msg.textContent = data.error || 'Preview failed'; msg.style.color = 'var(--negative)'; return; }
    msg.textContent = counts(data.counts); msg.style.color = '';
    show(data);
    btn.disabled = !done.some(s => (data.counts || {})[s] > 0);
  });
  btn.addEventListener('click', async () => {
    if (!confirm(confirmText)) return;
    const [ok, data] = await coordPost(urls[1], { csv: text, confirm: true });
    msg.textContent = ok ? `Done: ${data.approved ?? data.changed} · backup ${(data.backups || [data.backup]).filter(Boolean).join(', ') || '—'}`
      : (data.error || 'Failed');
    msg.style.color = ok ? 'var(--positive)' : 'var(--negative)';
    if (ok) show(data);
    btn.disabled = true;
    loadCoordHistory(); loadIdOverrides();
  });
}
csvSection('cand', ['/api/admin/candidates/preview', '/api/admin/candidates/approve'],
  r => `${r.status}: ${r.hotel || r.hotel_id} → "${r.google_name}" (${r.confidence || '—'}) · ${(r.current || []).join(', ') || '—'} → ${(r.new || []).join(', ')}`
    + (r.server_identifier && r.status === 'conflict' ? ` · this server has ${r.server_identifier}` : '')
    + (r.other_hotels ? ` · same Google hotel as ${r.other_hotels.join(', ')}` : '') + (r.unreject ? ' · un-rejects this ID' : ''),
  'Set the approved Google IDs and move those hotels to Google\'s position? Both files are backed up first.', ['approve']);
csvSection('hl', ['/api/admin/hotels-list/preview', '/api/admin/hotels-list/apply'],
  r => `${r.status}: ${r.hotel || r.hotel_id} (${r.action})` + (r.current_name ? ` · this server calls it "${r.current_name}"` : '')
    + (r.new_status ? ` · back to ${r.new_status}` : '') + (r.new_name ? ` · → "${r.new_name}"` : '')
    + (r.action === 'add' ? ` · new hotel ${r.hotel_id} in ${r.new_city || '?'}${r.new_owner ? ', owner ' + r.new_owner : ''}`
      : r.new_city ? ` · ${r.old_city || '?'} → ${r.new_city}${r.new_region ? ' (' + r.new_region + ')' : ''}` : '')
    + (r.action === 'owner' && r.new_owner ? ` · owner ${r.old_owner || '?'} → ${r.new_owner}` : '')
    + (r.action === 'rooms' && r.new_rooms ? ` · rooms ${r.old_rooms || '?'} → ${r.new_rooms}` : '')
    + (r.action === 'brand' && r.new_brand ? ` · brand ${r.old_brand || '?'} → ${r.new_brand} (${r.new_brand_group || '?'})` : '')
    + (r.action === 'merge' && r.into ? ` · merged into hotel ${r.into}${r.into_name ? ' "' + r.into_name + '"' : ''}` : '')
    + (r.action === 'pipeline_add' ? ` · new pipeline project ${r.pipeline_id || '?'} in ${r.new_city || '?'}${r.new_owner ? ', owner ' + r.new_owner : ''}` : '')
    + (r.pipeline_name ? ` · pipeline project ${r.pipeline_id} "${r.pipeline_name}"${r.pipeline_new ? ' (new)' : ''}` : '')
    + (r.new && r.action === 'pipeline_position' ? ` · ${(r.old || []).join(', ')} → ${r.new.join(', ')}${r.approximate ? ' (approximate)' : ''}` : '')
    + (r.action === 'pipeline_update' && r.pipeline_fields ? ' · ' + Object.entries(r.pipeline_fields).map(([k, v]) =>
        `${k} ${(r.old_fields || {})[k] || '—'} → ${k === 'notes' ? '(new notes)' : v}`).join(', ') : '')
    + (r.action === 'pipeline_remove' ? ` · removed from the pipeline${r.into_hotel_id ? ', now operating hotel ' + r.into_hotel_id : ''}` : '')
    + (r.note ? ` · ${r.note}` : '') + (r.reason ? ` · ${r.reason}` : ''),
  'Change this server\'s hotel list as previewed? hotels.csv (and pipeline.csv for a pipeline move, performance.csv for an added hotel) is backed up first.',
  ['hide', 'unhide', 'remove', 'rename', 'city', 'owner', 'rooms', 'brand', 'notes', 'merge', 'add', 'to_pipeline', 'pipeline_position', 'pipeline_add', 'pipeline_update', 'pipeline_remove']);
csvSection('own', ['/api/admin/owners/preview', '/api/admin/owners/apply'],
  r => `${r.status}: ${r.name || r.id} (${r.id})` + (r.hotels != null ? ` · ${r.hotels} hotels` : '')
    + (r.old_hotels != null ? ` (was ${r.old_hotels})` : '') + ((r.changed || []).length ? ` · changes ${r.changed.join(', ')}` : '')
    + (r.note ? ` · ${r.note}` : ''),
  'Add or replace these owner profiles on this server? owners.json is backed up first.', ['add', 'replace']);

const BACKUP_GROUPS = {
  'hotels.csv': 'Hotel list (hotels.csv)',
  'pipeline.csv': 'Pipeline (pipeline.csv)',
  'performance.csv': 'Performance estimates (performance.csv)',
  'owners.json': 'Owner profiles (owners.json)',
  'dataforseo_hotel_ids.json': 'Google IDs (dataforseo_hotel_ids.json)',
  'hotel_id_overrides.json': 'Manual Google IDs (hotel_id_overrides.json)',
};

// "hotels.csv.20261102-112609-123456" → "2026-11-02 11:26:09"
function backupTime(name) {
  const m = name.match(/\.(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-\d+$/);
  return m ? `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}` : '';
}

function backupRow(b) {
  const row = document.createElement('div');
  row.className = 'adm-backup-row';
  const name = document.createElement('span');
  name.className = 'adm-backup-name';
  name.textContent = b; name.title = b;
  const when = document.createElement('span');
  when.className = 'adm-backup-time';
  when.textContent = backupTime(b);
  row.append(name, when, restoreButton(b));
  return row;
}

function restoreButton(b, label = 'Restore') {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'adm-btn adm-btn-secondary adm-btn-sm';
  btn.textContent = 'Restore';
  btn.title = `Restore this backup (${b})`;
  btn.setAttribute('aria-label', `Restore this backup: ${b}`);
  btn.addEventListener('click', async () => {
    if (!confirm(`Put the backup ${b} back? The current file is backed up first.`)) return;
    const [ok, d] = await coordPost('/api/admin/coordinates/restore', { backup: b });
    toast(ok ? `Restored; previous file saved as ${d.previous_saved_as}` : (d.error || 'Restore failed'), ok ? 'success' : 'error');
    loadCoordHistory();
  });
  btn.textContent = label;
  return btn;
}

// Rates store (rates_store.py): which store the platform reads and who
// chose it, the nightly CSV / database check, and the manual override
const STORE_NAME = { csv: 'CSV', sqlite: 'database' };
function storeRender(d) {
  const db = d.db ? `database ${d.db.rows.toLocaleString('en')} rows, imported ${d.db.imported_at}` : (d.rates_db === 'on' ? 'database importing or not started' : 'no database');
  const why = d.chosen_by === 'automatic'
    ? (d.auto_read === 'sqlite' ? 'automatic: 7 clean nights' : `automatic: ${d.streak} of ${d.clean_nights_needed} clean nights so far`)
    : d.chosen_by === 'RATES_READ' ? `RATES_READ=${d.chosen} in Railway` : 'set in this panel';
  const fallback = d.chosen === 'sqlite' && d.read_from === 'csv' ? ' (database not ready: CSV meanwhile)' : '';
  document.getElementById('ri-store').textContent =
    `Rates store: the platform reads the ${STORE_NAME[d.read_from]} (${why})${fallback} · RATES_DB=${d.rates_db} · `
    + (d.csv_rows_unique != null ? `CSV ${d.csv_rows_unique.toLocaleString('en')} rows · ` : '') + db;
  const sel = document.getElementById('ri-store-choice');
  sel.value = d.manual || 'auto';
  sel.disabled = d.chosen_by === 'RATES_READ';
  sel.title = sel.disabled ? 'RATES_READ is set in Railway: it decides. Remove it to choose here.' : '';
  const list = document.getElementById('ri-store-history');
  list.replaceChildren();
  (d.history || []).slice(0, 8).forEach(h => {
    const line = document.createElement('div');
    line.className = 'adm-changelog-line';
    line.textContent = h.event === 'manual'
      ? `${h.at} · read from set to ${h.choice === 'auto' ? 'Automatic' : STORE_NAME[h.choice]} by ${h.by}`
      : `${h.at} · nightly check: ` + (h.result === 'same' ? `CSV and database agree (${h.days} scrape days; clean nights ${h.streak})`
        : h.result === 'differences' ? `differences on ${(h.days || []).map(x => x.day).join(', ')}; back to the CSV, count restarted`
        : `not run: ${h.note}`) + (h.switched ? ` · switched to the ${STORE_NAME[h.switched]}` : '');
    if (h.result === 'differences') line.style.color = 'var(--negative)';
    list.appendChild(line);
  });
}
async function loadRatesStore(full) {
  const diff = document.getElementById('ri-store-diff');
  const btn = document.getElementById('ri-store-compare');
  try {
    if (full) { btn.disabled = true; btn.textContent = 'Comparing…'; }
    const res = await fetch('/api/admin/rates-store' + (full ? '?full=1' : ''), { headers: authHeaders() });
    if (!res.ok) return;
    const d = await res.json();
    storeRender(d);
    if (full) {
      diff.hidden = false;
      diff.textContent = !d.db ? 'No database to compare with yet.'
        : d.mismatched_days.length ? 'Scrape days that differ: ' + d.mismatched_days.map(m => `${m.day} (CSV ${m.csv}, database ${m.db})`).join(' · ')
        : `CSV and database agree on all ${d.days_compared} scrape days.`;
    }
  } catch {} finally { btn.disabled = false; btn.textContent = 'Compare CSV and database'; }
}
document.getElementById('ri-store-compare').addEventListener('click', () => loadRatesStore(true));
document.getElementById('ri-store-choice').addEventListener('change', async e => {
  const choice = e.target.value;
  const label = choice === 'auto' ? 'Automatic' : STORE_NAME[choice];
  if (!confirm(`Make the platform read rates from: ${label}?`)) { loadRatesStore(false); return; }
  const [ok, d] = await coordPost('/api/admin/rates-store/read', { choice });
  toast(ok ? `Rates are read from: ${label}` : (d.error || 'Not changed'), ok ? 'success' : 'error');
  if (ok) storeRender(d); else loadRatesStore(false);
});
document.getElementById('ri-store-check').addEventListener('click', async e => {
  e.target.disabled = true; e.target.textContent = 'Checking…';
  const [ok, d] = await coordPost('/api/admin/rates-store/check', {});
  e.target.disabled = false; e.target.textContent = 'Run the check now';
  if (ok) storeRender(d); else toast(d.error || 'Check failed', 'error');
});

async function loadCoordHistory() {
  const el = document.getElementById('ri-coord-history');
  try {
    const res = await fetch('/api/admin/coordinates/history', { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    el.replaceChildren();
    if (!(data.backups || []).length && !(data.log || []).length) { el.textContent = 'No changes applied yet.'; return; }
    const groups = {};
    (data.backups || []).forEach(b => {
      const base = b.slice(0, b.lastIndexOf('.'));
      (groups[base] = groups[base] || []).push(b);
    });
    Object.keys(BACKUP_GROUPS).filter(base => groups[base]).forEach(base => {
      const section = document.createElement('div');
      section.className = 'adm-backup-group';
      const h = document.createElement('p');
      h.className = 'adm-backup-heading';
      h.textContent = BACKUP_GROUPS[base];
      const list = document.createElement('div');
      list.className = 'adm-backup-list';
      const rows = groups[base].map(b => backupRow(b));
      rows.forEach((r, i) => { if (i >= 5) r.hidden = true; list.appendChild(r); });
      section.append(h, list);
      if (rows.length > 5) {
        const more = document.createElement('button');
        more.type = 'button';
        more.className = 'adm-btn-text adm-backup-more';
        more.textContent = `Show all ${rows.length}`;
        more.addEventListener('click', () => {
          const open = more.dataset.open === '1';
          rows.forEach((r, i) => { if (i >= 5) r.hidden = open; });
          more.dataset.open = open ? '' : '1';
          more.textContent = open ? `Show all ${rows.length}` : 'Show latest 5';
        });
        section.appendChild(more);
      }
      el.appendChild(section);
    });
    const mig = (data.migrations || {}).migrations || [];
    if (mig.length || (data.migrations || {}).error) {
      const h = document.createElement('p');
      h.className = 'adm-backup-heading';
      h.textContent = 'Data migrations' + (data.migrations_on === false ? ' (off: DATA_MIGRATIONS=off)' : '');
      const list = document.createElement('div');
      list.className = 'adm-changelog';
      if (data.migrations.error) {
        const d = document.createElement('div'); d.className = 'adm-changelog-line'; d.textContent = data.migrations.error; list.appendChild(d);
      }
      mig.forEach(m => {
        const d = document.createElement('div');
        d.className = 'adm-changelog-line';
        d.textContent = `${m.id} · ${m.status === 'applied' ? 'Applied' : m.status === 'failed' ? 'Failed' : 'Pending'}`
          + (m.at ? ` ${m.at}` : '') + (m.summary ? ` · ${m.summary}` : '') + (m.error ? ` · ${m.error}` : '');
        if (m.status === 'failed') d.style.color = 'var(--negative)';
        list.appendChild(d);
      });
      el.append(h, list);
    }
    const logLines = (data.log || []).slice(0, 15);
    if (logLines.length) {
      const h = document.createElement('p');
      h.className = 'adm-backup-heading';
      h.textContent = 'Change log';
      el.appendChild(h);
    }
    const logList = document.createElement('div');
    logList.className = 'adm-changelog';
    el.appendChild(logList);
    logLines.forEach(l => {
      const d = document.createElement('div');
      d.className = 'adm-changelog-line';
      d.textContent = l.action === 'migration'
        ? `${l.at} · migration ${l.migration}: ${l.summary || 'nothing to do'}${l.changed ? '' : ' (no change)'}`
        : l.action === 'rates_read_switch'
          ? `${l.at} · rates read from ${l.to === 'auto' ? 'Automatic' : STORE_NAME[l.to] || l.to} (${l.result === 'manual' ? 'set' : 'nightly check'}) by ${l.by}`
        : l.action === 'migration_failed'
          ? `${l.at} · migration ${l.migration} failed, files put back: ${l.error}`
        : l.action === 'restore'
        ? `${l.at} · restored ${String(l.file || '').split('/').pop()} from ${String(l.restored_from || '').split('/').pop()} by ${l.by}`
        : l.action === 'import_ids'
          ? `${l.at} · imported ${l.imported} Google ID changes (${l.ids} IDs, ${l.overrides} manual, ${l.rejected || 0} rejected) by ${l.by}`
          : l.action === 'approve_candidates'
            ? `${l.at} · approved ${l.approved} Google ID candidates (${l.ids} IDs, ${l.coordinates} coordinates) by ${l.by}`
            : ['hide', 'unhide', 'remove'].includes(l.action)
              ? `${l.at} · ${l.action} ${l.hotel} (status ${l.old_status}${l.new_status ? ' → ' + l.new_status : ''})${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
              : l.action === 'rename'
                ? `${l.at} · renamed ${l.old_name} → ${l.new_name}${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'owner'
                  ? `${l.at} · ${l.hotel}: owner ${l.old_owner} → ${l.new_owner}${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'rooms'
                  ? `${l.at} · ${l.hotel}: rooms ${l.old_rooms} → ${l.new_rooms}${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'brand'
                  ? `${l.at} · ${l.hotel}: brand ${l.old_brand} → ${l.new_brand} (${l.new_brand_group})${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'notes'
                  ? `${l.at} · ${l.hotel}: notes changed${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'merge'
                  ? `${l.at} · merged hotel ${l.hotel_id} ${l.hotel} into ${l.into} ${l.into_name} (${l.comp_sets_changed || 0} comp sets updated)${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'pipeline_add'
                  ? `${l.at} · added pipeline project ${l.pipeline_id} ${l.hotel} (${l.new_city}${l.new_owner ? ', owner ' + l.new_owner : ''}, ${l.pipeline_status}, ${l.keys} keys) by ${l.by}`
                : l.action === 'pipeline_update'
                  ? `${l.at} · pipeline project ${l.pipeline_id} ${l.hotel}: ${Object.keys(l.new_fields || {}).join(', ')} changed${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'pipeline_remove'
                  ? `${l.at} · removed pipeline project ${l.pipeline_id} ${l.hotel}${l.into_hotel_id ? ' (now operating hotel ' + l.into_hotel_id + ')' : ''}${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                : l.action === 'add'
                  ? `${l.at} · added hotel ${l.hotel_id} ${l.hotel} (${l.new_city}${l.new_owner ? ', owner ' + l.new_owner : ''})${l.performance_file ? ' with its performance.csv row' : ''} by ${l.by}`
                : ['owner_add', 'owner_replace'].includes(l.action)
                  ? `${l.at} · ${l.action === 'owner_add' ? 'added' : 'replaced'} owner profile ${l.owner} (${l.hotels} hotels${l.old_hotels != null ? ', was ' + l.old_hotels : ''}) by ${l.by}`
                : l.action === 'city'
                  ? `${l.at} · ${l.hotel}: city ${l.old_city} → ${l.new_city}${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
                  : l.action === 'pipeline_position'
                    ? `${l.at} · pipeline project ${l.pipeline_id} ${l.hotel}: ${(l.old || []).join(', ')} → ${(l.new || []).join(', ')}${l.approximate ? ' (approximate)' : ''} by ${l.by}`
                  : l.action === 'to_pipeline'
                    ? `${l.at} · moved ${l.hotel} to the pipeline as "${l.pipeline_name}" (project ${l.pipeline_id})${l.reason ? ' · ' + l.reason : ''} by ${l.by}`
              : `${l.at} · ${l.hotel}: ${(l.old || []).join(', ')} → ${(l.new || []).join(', ')} (${l.approve}) by ${l.by}`;
      if (l.action === 'migration_failed') d.style.color = 'var(--negative)';
      if (l.action === 'migration' && (l.backups || []).length) {
        d.classList.add('adm-changelog-line--actions');
        l.backups.forEach(b => d.append(' ', restoreButton(b, `Restore ${b.slice(0, b.indexOf('.', b.indexOf('.') + 1)) || b}`)));
      }
      logList.appendChild(d);
    });
  } catch {}
}

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
    const om = document.getElementById('occ-model-shown');
    if (om) om.textContent = (data.model || 'v1').toUpperCase();
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

// v1 and v2 side by side, and v2 readiness (occupancy_compare.py)
let occSbs = null;
const sbsPct = v => (v == null ? '–' : `${Math.round(v)}%`);
const sbsRange = (lo, mid, hi) => (mid == null ? '–' : lo != null && hi != null ? `${Math.round(lo)}–${Math.round(mid)}–${Math.round(hi)}%` : sbsPct(mid));
const sbsDiff = (a, b) => (a == null || b == null ? '–' : `${b - a >= 0 ? '+' : '−'}${Math.abs(b - a).toFixed(1)}`);
function sbsTable(id, head, rows) {
  const t = document.getElementById(id);
  t.replaceChildren();
  const th = document.createElement('thead'), tr = document.createElement('tr');
  head.forEach(h => { const c = document.createElement('th'); c.textContent = h; tr.appendChild(c); });
  th.appendChild(tr); t.appendChild(th);
  const tb = document.createElement('tbody');
  rows.forEach(r => { const row = document.createElement('tr'); r.forEach(v => { const c = document.createElement('td'); c.textContent = v; row.appendChild(c); }); tb.appendChild(row); });
  t.appendChild(tb);
}
const MON3 = m => { const [y, mo] = m.split('-'); return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+mo - 1] + ' ' + y.slice(2); };
function renderSideBySide() {
  const d = occSbs; if (!d) return;
  const view = document.getElementById('occ-sbs-view').value, city = document.getElementById('occ-sbs-city').value;
  const cities = d.cities.filter(c => !city || c.city === city);
  if (view === 'city') {
    sbsTable('occ-sbs-table', ['City', 'Hotels', 'Official', 'v1 next 30 (range)', 'v2 next 30 (range)', 'v2 − v1', 'v1 12 months', 'v2 12 months', 'v2 − v1'],
      cities.map(c => [c.city, c.hotels, c.official == null ? 'none' : `${c.official}% ${c.official_year}${c.official_scope === 'national' ? ' (national)' : ''}`,
        sbsRange(c.v1_low, c.v1, c.v1_high), sbsRange(c.v2_low, c.v2, c.v2_high), sbsDiff(c.v1, c.v2), sbsPct(c.v1_year), sbsPct(c.v2_year), sbsDiff(c.v1_year, c.v2_year)]));
  } else if (view === 'month') {
    sbsTable('occ-sbs-table', ['City', 'Model', ...d.months.map(MON3)],
      cities.flatMap(c => [[c.city, 'v1', ...d.months.map(m => sbsPct(c.months[m].v1))], ['', 'v2', ...d.months.map(m => sbsPct(c.months[m].v2))]]));
  } else {
    sbsTable('occ-sbs-table', ['Hotel', 'City', 'Category', 'v1 next 30', 'v2 next 30', 'v2 − v1', 'v2 normal price'],
      d.hotels.filter(h => !city || h.city === city).map(h => [h.name, h.city, h.category, sbsRange(h.v1_low, h.v1, h.v1_high),
        sbsRange(h.v2_low, h.v2, h.v2_high), sbsDiff(h.v1, h.v2), h.v2_normal === 'history' ? 'own prices' : h.v2_normal === 'adr_fallback' ? 'stand-in' : 'none']));
  }
}
function renderReadiness() {
  const r = occSbs && occSbs.readiness; if (!r) return;
  const c = r.criteria, set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
  set('occ-rd-crit-nights', c.own_price_nights); set('occ-rd-crit-days', c.history_days); set('occ-rd-crit-recent', c.recent_days);
  set('occ-rd-crit-cmin', c.city_min_hotels); set('occ-rd-crit-cshare', Math.round(c.city_share * 100));
  set('occ-rd-crit-heat', Math.round(c.city_heat_nights * 100)); set('occ-rd-crit-switch', Math.round(c.switch_hotel_share * 100));
  set('occ-rd-hotels', `${r.hotels_ready} of ${r.hotels}`); set('occ-rd-rooms', `${r.rooms_share_ready}%`);
  set('occ-rd-cities', `${r.cities_ready} of ${r.cities_total}`);
  set('occ-rd-half', r.date_half || 'no date yet'); set('occ-rd-switch', r.date_switch || 'no date yet');
  set('occ-rd-note', `${r.days_of_data} days of data since ${r.data_start}. ${r.on_stand_in} hotel${r.on_stand_in === 1 ? '' : 's'} would still need the stand-in reference price; ${r.no_prices} have no prices yet (no date can be projected for them).`);
  const yes = b => (b ? 'yes' : 'no');
  sbsTable('occ-rd-cities-table', ['City', 'Hotels', 'Ready', '3+ ready', 'Share ready', 'Market signal nights', 'City ready', 'Projected'],
    r.city_rows.map(x => [x.city, x.hotels, x.ready_hotels, yes(x.checks.min_hotels), yes(x.checks.share), `${x.heat_nights_pct}%`, yes(x.ready), x.ready ? 'now' : (x.ready_on || 'no date')]));
  set('occ-rd-hotel-count', r.hotel_rows.length);
  sbsTable('occ-rd-hotels-table', ['Hotel', 'City', 'Priced nights', 'Days of prices', 'Last 7 days', 'Own price', 'Ready', 'Projected'],
    r.hotel_rows.map(x => [x.name, x.city, x.priced_nights, x.history_days, x.recent_days, yes(x.checks.own_price), yes(x.ready), x.ready ? 'now' : (x.ready_on || 'no date')]));
}
async function loadOfficialMonthly() {
  try {
    const res = await fetch('/api/admin/occupancy/official-monthly', { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) return;
    document.getElementById('occ-om-source').textContent = `${d.source}; latest month ${d.latest_month || '—'}`;
    const iss = document.getElementById('occ-om-issues');
    iss.replaceChildren(...(d.issues || []).map(t => { const li = document.createElement('div'); li.textContent = '• ' + t; return li; }));
    const months = ((d.rows || []).find(r => r.months && r.months.length) || { months: [] }).months.map(m => m.month);
    const mark = { official: '', unconfirmed: ' (unconfirmed)', derived: ' (rebuilt)', estimate: ' (Kodo estimate)', calibrated: ' (Kodo estimate, calibrated)', region: ' (Kodo estimate from region)', filled: ' (Kodo estimate, filled)', missing: '' };
    sbsTable('occ-om-table', ['City', 'Official figure', 'Level', 'Confidence', 'Used as', 'Yearly change', 'Note', ...months],
      (d.rows || []).map(r => [r.city || '—', r.official, r.level, r.confidence ? (r.confidence === 'high' ? 'high' : r.confidence.toUpperCase()) : '',
        r.use === 'series' ? (r.pattern ? 'monthly pattern' : 'series (too few months)') : r.use, r.growth_pts != null ? `${r.growth_pts > 0 ? '+' : ''}${r.growth_pts} pts` : '',
        r.note || '', ...months.map(m => { const x = (r.months || []).find(y => y.month === m); return x && x.value != null ? `${Math.round(x.value)}%${mark[x.status] || ''}${x.used ? '' : ' ·not used'}` : '–'; })]));
  } catch { /* the rest of the page still loads */ }
}
async function loadKpiChange() {
  const msg = document.getElementById('kc-msg');
  msg.textContent = 'Loading…';
  try {
    const city = document.getElementById('kc-city').value.trim();
    const res = await fetch('/api/admin/kpi-change?city=' + encodeURIComponent(city), { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) { msg.textContent = d.error || 'Failed'; return; }
    msg.textContent = `${d.city}: ${d.hotels} hotels · ${d.today} vs ${d.compared_with}` + (d.snapshot_before ? '' : ' · no snapshot from that day');
    const NAME = { occ: 'Occupancy (%)', revpar: 'Rooms RevPAR (MAD)', rate: 'Forward published rate (MAD)' };
    const f = (v, n) => v == null ? '–' : `${v} (${n})`;
    sbsTable('kc-table', ['Figure', 'Now, all hotels (n)', '7 days ago, all hotels (n)', 'Now, same hotels', '7 days ago, same hotels', 'Same hotels', 'Change shown', 'Entered', 'Left'],
      Object.entries(d.figures || {}).map(([k, x]) => [NAME[k] || k, f(x.now_all, x.hotels_now), f(x.before_all, x.hotels_before),
        x.now_same_hotels ?? '–', x.before_same_hotels ?? '–', x.same_hotels, x.change_shown == null ? '–' : (k === 'occ' ? `${x.change_shown} pts` : `${x.change_shown}%`),
        x.entered.join(', ') || '—', x.left.join(', ') || '—']));
    sbsTable('kc-movers', ['Hotel', 'Rooms', 'Rooms RevPAR before → now', 'Occupancy before → now', 'Forward rate before → now', 'Effect (MAD × rooms)'],
      (d.movers || []).map(m => [m.hotel, m.rooms, `${Math.round(m.revpar_before)} → ${Math.round(m.revpar_now)}`,
        `${m.occ_before ?? '–'} → ${m.occ_now ?? '–'}`, `${m.rate_before != null ? Math.round(m.rate_before) : '–'} → ${m.rate_now != null ? Math.round(m.rate_now) : '–'}`, m.weighted_change.toLocaleString('en')]));
  } catch { msg.textContent = 'Failed'; }
}
document.getElementById('kc-go').addEventListener('click', loadKpiChange);
async function loadResortLevels(body) {
  const msg = document.getElementById('rl-msg');
  try {
    const res = await fetch('/api/admin/resort-levels', body ? { method: 'POST', headers: authHeaders(true), body: JSON.stringify(body) } : { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) { msg.textContent = d.error || 'Failed'; return; }
    document.getElementById('rl-status').textContent = d.on ? 'on' : `off${d.env === 'off' ? ' (RESORT_LEVELS=off)' : d.killed ? ' (admin button)' : ''}`;
    document.getElementById('rl-off').style.display = d.on ? '' : 'none';
    document.getElementById('rl-on').style.display = d.killed && d.env !== 'off' ? '' : 'none';
    msg.textContent = body ? 'Saved; the model is running again (a few minutes).' : '';
    sbsTable('rl-table', ['Destination', 'Applies to', 'Real hotels', 'Hotels in the database', 'Hotels covered', 'Note shown'],
      (d.destinations || []).map(x => [x.city, x.scope, x.real_hotels ? x.real_hotels : 'none (borrowed from neighbouring destinations)', x.hotels_in_database, x.hotels_covered, x.note || '—']));
  } catch { msg.textContent = 'Failed'; }
}
document.getElementById('rl-off').addEventListener('click', () => {
  if (confirm('Turn the destination levels off? Saïdia, Nador and Al Hoceima go back to the national anchor and the resort profile.')) loadResortLevels({ off: true });
});
document.getElementById('rl-on').addEventListener('click', () => loadResortLevels({ off: false }));
async function loadClassGaps() {
  try {
    const res = await fetch('/api/admin/class-gaps', { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) return;
    const f = v => v == null ? '–' : `${v > 0 ? '+' : ''}${v}`;
    sbsTable('cg-table', ['City', 'Class', '12m gap', '24m gap', 'Min', 'Max', 'Drift (range)', 'Months of history', 'Used', 'Tested'],
      (d.rows || []).map(r => [r.city, r.class + (r.derived ? ' (derived)' : ''), f(r.gap_12m), f(r.gap_24m), f(r.min), f(r.max),
        r.drift ? `±${r.drift}` : '–', r.months + (r.note ? ` · ${r.note}` : ''), r.used ? 'yes' : 'no', r.tested]));
  } catch { /* the rest of the page still loads */ }
}
async function loadSideBySide(refresh) {
  loadOfficialMonthly();
  loadClassGaps();
  loadResortLevels();
  loadKpiChange();
  const msg = document.getElementById('occ-sbs-msg');
  msg.textContent = 'Loading… (up to a minute the first time each day)';
  try {
    const res = await fetch('/api/admin/occupancy/side-by-side' + (refresh ? '?refresh=1' : ''), { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) { msg.textContent = d.error || 'Failed'; return; }
    occSbs = d;
    document.getElementById('occ-sbs-shown').textContent = (d.shown_model || 'v1').toUpperCase();
    const sel = document.getElementById('occ-sbs-city'), keep = sel.value;
    sel.replaceChildren(new Option('All cities', ''), ...d.cities.map(c => new Option(c.city, c.city)));
    sel.value = keep;
    msg.textContent = `Computed for ${d.today}`;
    renderSideBySide(); renderReadiness();
    document.getElementById('occ-res-x').textContent = d.resort_season_x ?? '—';
    document.getElementById('occ-pp').textContent = { off: 'off', nonresort: 'on for non-resort hotels', all: 'on for every hotel' }[d.price_position] || '—';
    sbsTable('occ-res-table', ['Destination', 'Classified resorts', 'Resort swing', 'Confidence'],
      (d.resort_destinations || []).map(x => [x.city, x.resorts, x.swing_on ? 'on' : 'off', x.confidence]));
  } catch { msg.textContent = 'Failed'; }
}
// The automatic switch to v2 (model_switch.py): status, kill switch, snapshots
function renderSwitch(d) {
  const cities = Object.keys(d.cities || {});
  const off = d.killed || d.env_killed;
  document.getElementById('occ-sw-status').textContent = off
    ? `All hotels on v1 (kill switch${d.env_killed ? ': OCC_V2_OFF in the environment' : ''})`
    : d.forced_v2 ? 'All hotels on v2 (OCC_MODEL=v2)'
    : cities.length ? `v2 for ${d.hotels_on_v2} hotels in ${cities.length} cit${cities.length === 1 ? 'y' : 'ies'}: ${cities.join(', ')}` : 'All hotels on v1: no city switched yet';
  document.getElementById('occ-sw-kill').style.display = d.killed ? 'none' : '';
  document.getElementById('occ-sw-resume').style.display = d.killed ? '' : 'none';
  const lc = d.last_check;
  document.getElementById('occ-sw-note').textContent = [lc ? `Last check ${lc.at}: ${lc.rooms_share_ready}% of rooms in ready hotels (switching starts at 80%), ${lc.hotels_ready} hotels and ${lc.cities_ready} cities ready.` : 'Not checked yet: the check runs after the nightly model run.',
    d.stand_in_removed ? `Stand-in reference price removed ${d.stand_in_removed}.` : 'Stand-in reference price: kept until every city with 3 or more hotels is on v2 (it never reaches a figure clients see).'].join(' ');
  const f = x => (x && x.next30 != null ? `${Math.round(x.next30)}%${x.low != null ? ` (${Math.round(x.low)}–${Math.round(x.high)})` : ''} · 12 mo ${x.year != null ? Math.round(x.year) + '%' : '–'}` : '–');
  const rows = [];
  (d.history || []).slice().reverse().forEach(e => {
    if (e.kind === 'switch') {
      (e.cities || []).forEach(c => rows.push([e.at, `switched: ${c.city}`, `${c.hotels_switched} of ${c.hotels}`, c.official != null ? `${c.official}%` : '–', f(c.before), f(c.after)]));
      Object.entries(e.hotels_joined || {}).forEach(([c, n]) => rows.push([e.at, `joined: ${c}`, `+${n}`, '', '', '']));
    } else rows.push([e.at, e.kind === 'kill' ? 'kill switch on (all v1)' : e.kind === 'resume' ? 'resumed' : 'stand-in removed', e.by || '', '', '', '']);
  });
  sbsTable('occ-sw-table', ['When', 'Change', 'Hotels on v2', 'Official', 'Before (v1)', 'After (v2)'], rows.length ? rows : [['—', 'No switch yet', '', '', '', '']]);
}
async function loadSwitch(body) {
  const msg = document.getElementById('occ-sw-msg');
  try {
    const res = await fetch('/api/admin/occupancy/switch', body ? { method: 'POST', headers: authHeaders(true), body: JSON.stringify(body) } : { headers: authHeaders() });
    const d = await res.json();
    if (!res.ok) { msg.textContent = d.error || 'Failed'; return; }
    msg.textContent = body ? (body.killed ? 'Every hotel shows v1 now.' : 'Switching resumed.') : '';
    renderSwitch(d);
  } catch { msg.textContent = 'Failed'; }
}
document.getElementById('occ-sw-kill').addEventListener('click', () => {
  if (confirm('Return every hotel to v1 now? The switched cities stay recorded; Resume shows them on v2 again.')) loadSwitch({ killed: true });
});
document.getElementById('occ-sw-resume').addEventListener('click', () => loadSwitch({ killed: false }));
document.getElementById('occ-sbs-view').addEventListener('change', renderSideBySide);
document.getElementById('occ-sbs-city').addEventListener('change', renderSideBySide);
document.getElementById('occ-sbs-refresh').addEventListener('click', () => loadSideBySide(true));

// ════════════════════════ PRICE COVERAGE (read only) ═══════════════════
const PC_YES = b => (b ? 'yes' : 'no');
const pcMad = v => (v == null ? '—' : `MAD ${Math.round(v).toLocaleString('en')}`);
const pcDay = iso => { const d = new Date(iso + 'T12:00:00'); return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }); };
async function pcFetch(qs) {
  const res = await fetch('/api/admin/price-coverage' + (qs ? '?' + qs : ''), { headers: authHeaders() });
  const d = await res.json();
  if (!res.ok) throw new Error(d.error || 'Failed');
  return d;
}
async function loadPriceCoverage() {
  const meta = document.getElementById('pc-meta');
  meta.textContent = 'Loading…';
  try {
    const d = await pcFetch('');
    const s = d.summary;
    meta.textContent = `Latest nightly run: ${d.latest_run || 'none yet'} · next 30 nights ${pcDay(d.window.start)} – ${pcDay(d.window.end)}.`;
    document.getElementById('pc-cal-days').textContent = d.calendar_days;
    const stat = (v, l) => `<div class="adm-stat"><span class="adm-stat-val">${v}</span><span class="adm-stat-label">${l}</span></div>`;
    document.getElementById('pc-stats').innerHTML =
      stat(`${s.with_price_pct ?? '–'}%`, `Hotel-nights with a price (${s.with_price.toLocaleString('en')} of ${s.hotel_nights.toLocaleString('en')})`)
      + stat(`${s.from_last_run_pct ?? '–'}%`, 'Priced by the latest run')
      + stat(s.empty.toLocaleString('en'), 'Empty hotel-nights')
      + stat(s.hotels, 'Open hotels');
    sbsTable('pc-causes', ['Cause of the empty hotel-nights', 'Hotel-nights', 'Share of empty'],
      s.causes.map(c => [c.label, c.hotel_nights.toLocaleString('en'), `${c.pct_of_empty}%`])
        .concat([['Hotels by lookup in the latest run: ' + Object.entries(s.lookups).map(([k, v]) => `${k} ${v}`).join(' · '), '', '']]));
    const max = Math.max(1, ...s.gaps_by_day.map(g => g.empty));
    const days = document.getElementById('pc-days');
    days.replaceChildren(...s.gaps_by_day.map(g => {
      const col = document.createElement('div');
      col.className = 'pc-day';
      col.title = `${pcDay(g.night)} (day ${g.day}): ${g.empty} empty`;
      const bar = document.createElement('span');
      bar.className = 'pc-day-bar';
      bar.style.height = `${Math.round(100 * g.empty / max)}%`;
      const lab = document.createElement('span');
      lab.className = 'pc-day-lab';
      lab.textContent = g.day;
      col.append(bar, lab);
      return col;
    }));
    sbsTable('pc-sparse', ['Hotel', 'City', 'Nights priced (of 30)', 'Google lookup'],
      s.sparse.map(h => [h.name, h.city, h.priced, h.lookup]));
    document.querySelectorAll('#pc-sparse tbody tr').forEach((tr, i) => {
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => pcShowHotel(s.sparse[i].id));
    });
  } catch (e) { meta.textContent = e.message; }
}
async function pcShowHotel(id) {
  const head = document.getElementById('pc-hotel-head');
  head.textContent = 'Loading…';
  try {
    const { hotel: h } = await pcFetch('hotel_id=' + encodeURIComponent(id));
    document.getElementById('pc-search').value = h.name;
    head.textContent = `${h.name} · ${h.city} · Google lookup in the latest run: ${h.lookup}`
      + (h.google_title ? ` (Google calls it “${h.google_title}”)` : '') + ` · ${h.nights_returned} nights returned · ${h.priced} of 30 nights on the calendar`;
    sbsTable('pc-hotel-table', ['Night', 'Asked in latest run', 'Rate returned', 'Calendar shows', 'From run', 'Runs asked / returned a rate'],
      h.nights.map(n => [pcDay(n.night), PC_YES(n.asked), n.returned ? pcMad(n.rate) : 'no', pcMad(n.shown), n.shown_run || '—',
        `${n.runs_asked} / ${n.runs_returned}`]));
    head.scrollIntoView({ block: 'nearest' });
  } catch (e) { head.textContent = e.message; }
}
(function pcSearch() {
  const input = document.getElementById('pc-search'), list = document.getElementById('pc-results');
  let t = null, seq = 0;
  const close = () => { list.replaceChildren(); input.setAttribute('aria-expanded', 'false'); };
  input.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(async () => {
      const q = input.value.trim(), my = ++seq;
      if (q.length < 2) { close(); return; }
      try {
        const { matches } = await pcFetch('q=' + encodeURIComponent(q));
        if (my !== seq) return;
        list.replaceChildren(...(matches.length ? matches : [null]).map(m => {
          const b = document.createElement('button');
          b.type = 'button'; b.className = 'pc-result'; b.setAttribute('role', 'option');
          if (!m) { b.textContent = 'No open hotel with this name'; b.disabled = true; return b; }
          b.textContent = `${m.name} · ${m.city}`;
          b.addEventListener('click', () => { close(); pcShowHotel(m.id); });
          return b;
        }));
        input.setAttribute('aria-expanded', 'true');
      } catch { close(); }
    }, 200);
  });
  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') close();
    if (e.key === 'Enter') { const f = list.querySelector('.pc-result:not([disabled])'); if (f) f.click(); }
    if (e.key === 'ArrowDown') { const f = list.querySelector('.pc-result'); if (f) { e.preventDefault(); f.focus(); } }
  });
  list.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown') { e.preventDefault(); document.activeElement.nextElementSibling?.focus(); }
    if (e.key === 'ArrowUp') { e.preventDefault(); (document.activeElement.previousElementSibling || input).focus(); }
    if (e.key === 'Escape') { close(); input.focus(); }
  });
})();

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
        <span class="adm-row-meta" data-label="Exists"><span class="adm-pill pill--${info.exists ? 'green' : 'red'}">${info.exists ? 'Yes' : 'No'}</span></span>
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

// ─── Events (events.json + this server's changes, logged) ───────────────────
let evData = null;
async function loadEvents() {
  const res = await fetch('/api/admin/events', { headers: authHeaders() });
  if (!res.ok) { document.getElementById('ev-table').innerHTML = '<tr><td>Could not load events.</td></tr>'; return; }
  evData = await res.json();
  const order = evData.labels || {};     // {field: [[value, label], …]} in display order
  evData.labels = Object.fromEntries(Object.entries(order).map(([k, pairs]) => [k, Object.fromEntries(pairs)]));
  // Options show the display labels (events_db.LABELS); values stay the stored ones
  const form = document.getElementById('ev-form');
  ['type', 'impact', 'date_status', 'recurrence', 'effect', 'precision'].forEach(field => {
    const pairs = (order[field] || []).slice();
    if (field === 'type') pairs.sort((a, b) => a[1].localeCompare(b[1]));
    form.elements[field].innerHTML = pairs
      .map(([k, v]) => `<option value="${escHtml(k)}">${escHtml(v)}</option>`).join('');
  });
  document.getElementById('ev-cities').innerHTML = ['National', ...new Set(evData.events.map(e => e.city))].sort()
    .map(c => `<option value="${c.replace(/"/g, '&quot;')}">`).join('');
  renderEventsTable();
  const log = document.getElementById('ev-log');
  log.replaceChildren();
  if (!evData.log.length) { log.textContent = 'No changes made on this server yet.'; return; }
  const list = document.createElement('div');
  list.className = 'adm-changelog';
  evData.log.forEach(l => {
    const d = document.createElement('div');
    d.className = 'adm-changelog-line';
    const what = l.action === 'edit' ? `edited ${l.name}: ${Object.keys(l.changed || {}).join(', ')}` : `${l.action === 'add' ? 'added' : l.action === 'hide' ? 'hid' : 'showed again'} ${l.name}`;
    d.textContent = `${l.at} · ${what} by ${l.by}`;
    list.appendChild(d);
  });
  log.appendChild(list);
}
const evLabel = (field, v) => (evData.labels[field] || {})[v] || v;
function renderEventsTable() {
  const q = document.getElementById('ev-search').value.trim().toLowerCase();
  const show = document.getElementById('ev-filter').value;
  const today = new Date().toISOString().slice(0, 10);
  const rows = evData.events.filter(e =>
    (show === 'all' || (show === 'upcoming' && e.end >= today && !e.hidden) || (show === 'hidden' && e.hidden)
      || (show === 'edited' && (e.edited || e.added)) || (show === 'estimated' && ['estimated', 'moon'].includes(e.date_status)))
    && (!q || [e.name, e.city, evLabel('type', e.type), e.venue].join(' ').toLowerCase().includes(q)));
  const t = document.getElementById('ev-table');
  t.innerHTML = '<thead><tr><th>Dates</th><th>Event</th><th>City</th><th>Type</th><th>Impact</th><th>Date status</th><th>Source (internal)</th><th>Checked</th><th>Clients see</th><th></th></tr></thead>';
  const tb = document.createElement('tbody');
  rows.slice(0, 300).forEach(e => {
    const tr = document.createElement('tr');
    if (e.hidden) tr.style.opacity = '0.55';
    const cells = [e.start === e.end ? e.start : `${e.start} → ${e.end}`, e.name + (e.added ? ' (added here)' : e.edited ? ' (edited here)' : ''),
      e.city, evLabel('type', e.type), evLabel('impact', e.impact), evLabel('date_status', e.date_status)];
    cells.forEach(c => { const td = document.createElement('td'); td.textContent = c; tr.appendChild(td); });
    // Internal source record (admins only) and what clients see instead
    const srcTd = document.createElement('td');
    if (e.source) {
      const a = document.createElement('a');
      a.href = e.source; a.target = '_blank'; a.rel = 'noopener';
      a.textContent = e.source.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
      srcTd.appendChild(a);
      if (e.source_note) srcTd.appendChild(Object.assign(document.createElement('div'), { textContent: e.source_note, className: 'adm-hint' }));
    }
    const chkTd = document.createElement('td'); chkTd.textContent = e.checked || '';
    const seeTd = document.createElement('td'); seeTd.textContent = e.official_url ? 'Official page' : 'No source';
    tr.append(srcTd, chkTd, seeTd);
    const td = document.createElement('td');
    td.style.whiteSpace = 'nowrap';
    const edit = document.createElement('button');
    edit.type = 'button'; edit.className = 'adm-btn adm-btn-secondary adm-btn-sm'; edit.textContent = 'Edit';
    edit.addEventListener('click', () => openEventForm(e));
    const hide = document.createElement('button');
    hide.type = 'button'; hide.className = 'adm-btn adm-btn-secondary adm-btn-sm'; hide.style.marginLeft = '6px';
    hide.textContent = e.hidden ? 'Show' : 'Hide';
    hide.setAttribute('aria-label', `${e.hidden ? 'Show' : 'Hide'} ${e.name}`);
    hide.addEventListener('click', async () => {
      if (!e.hidden && !confirm(`Hide "${e.name}" everywhere (calendar, markers, occupancy model)? You can show it again.`)) return;
      const [ok, d] = await coordPost('/api/admin/events/hide', { id: e.id, hidden: !e.hidden });
      eventMsg(ok ? `${e.hidden ? 'Shown' : 'Hidden'}: ${e.name}` : (d.error || 'Failed'), ok);
      loadEvents();
    });
    td.append(edit, hide); tr.appendChild(td); tb.appendChild(tr);
  });
  t.appendChild(tb);
  if (!rows.length) t.insertAdjacentHTML('beforeend', '<tbody><tr><td colspan="10">No events match.</td></tr></tbody>');
}
function eventMsg(text, ok) {
  const m = document.getElementById('ev-msg');
  m.textContent = text; m.style.color = ok ? 'var(--positive)' : 'var(--negative)';
}
function openEventForm(e) {
  const f = document.getElementById('ev-form');
  f.reset();
  document.getElementById('ev-form-title').textContent = e ? `Edit: ${e.name}` : 'Add event';
  const vals = e || { type: 'music', impact: 'medium', date_status: 'confirmed', precision: 'day', recurrence: 'annual', effect: 'up', model: true,
                      checked: new Date().toISOString().slice(0, 10) };
  [...f.elements].forEach(el => {
    if (!el.name) return;
    const v = vals[el.name];
    el.value = el.name === 'model' ? String(v !== false) : (v == null ? '' : v);
  });
  f.hidden = false;
  f.querySelector('[name=name]').focus();
}
document.getElementById('ev-add').addEventListener('click', () => openEventForm(null));
document.getElementById('ev-cancel').addEventListener('click', () => { document.getElementById('ev-form').hidden = true; });
document.getElementById('ev-search').addEventListener('input', () => evData && renderEventsTable());
document.getElementById('ev-filter').addEventListener('change', () => evData && renderEventsTable());
document.getElementById('ev-form').addEventListener('submit', async ev => {
  ev.preventDefault();
  const body = Object.fromEntries(new FormData(ev.target).entries());
  body.model = body.model === 'true';
  const [ok, d] = await coordPost('/api/admin/events/save', body);
  eventMsg(ok ? `Saved: ${d.event.name}` : (d.error || 'Save failed'), ok);
  if (ok) { ev.target.hidden = true; loadEvents(); }
});

// ════════════════════════ DATA HEALTH (data_quality.py) ═════════════════════
// One page for the nightly agent and for us: last scraper run and coverage,
// hotels with problems, models and their confidence, calibration, the
// school-holiday test, the flags for changes clients would see and what each
// would change (computed on this server's data on request).
let dhData = null;
const dhPct = v => v == null ? '—' : `${Math.round(v * 100)}%`;
const dhNum = (v, d = 0) => v == null ? '—' : Number(v).toLocaleString('en', { maximumFractionDigits: d, minimumFractionDigits: d });
const dhTable = (id, head, rows) => {
  const t = document.getElementById(id);
  t.innerHTML = `<thead><tr>${head.map(h => `<th>${escHtml(h)}</th>`).join('')}</tr></thead><tbody>`
    + (rows.length ? rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')
      : `<tr><td colspan="${head.length}">Nothing to show.</td></tr>`) + '</tbody>';
};
const DH_STATUS = ['priced', 'sold_out', 'sold_out_candidate', 'no_price', 'closed_or_unknown', 'failed', 'not_checked'];

// The nightly checks (health_checks.py): the platform light, each check, 14 days
const HC_LABEL = { ok: 'OK', warning: 'Warning', problem: 'Problem', no_data: 'No data' };
const HC_PILL = { ok: 'pill--green', warning: 'pill--orange', problem: 'pill--red', no_data: 'pill--grey' };
function renderHealthChecks() {
  const R = dhData.checks, H = dhData.history || [];
  const light = document.getElementById('hc-light');
  if (!R) { light.innerHTML = '<p class="adm-hint">No check has run yet.</p>'; return; }
  const n = R.counts || {};
  const head = R.overall === 'problem' ? `${n.problem} problem${n.problem === 1 ? '' : 's'}` : R.overall === 'warning'
    ? `${n.warning} warning${n.warning === 1 ? '' : 's'}, no problem` : R.overall === 'ok' ? 'All checks OK' : 'No data yet';
  light.innerHTML = `<span class="hc-dot hc-dot--${R.overall}" aria-hidden="true"></span>
    <div><div class="hc-light-title">Platform: ${escHtml(head)}</div>
    <div class="adm-hint">Checked ${escHtml(R.checked_at.replace('T', ' ').slice(0, 16))} · ${n.ok || 0} OK · ${n.warning || 0} warning · ${n.problem || 0} problem · ${n.no_data || 0} no data · `
    + (R.overall === 'problem' ? (dhData.sanity_email ? `tonight's email goes to ${escHtml(dhData.sanity_email)}` : 'alert email off') : 'no email: nothing in "problem"') + '</div></div>';
  const groups = [...new Set(R.checks.map(c => c.group))];
  const rank = { problem: 0, warning: 1, no_data: 2, ok: 3 };
  document.getElementById('hc-checks').innerHTML = groups.map(g => {
    const cs = R.checks.filter(c => c.group === g).sort((a, b) => rank[a.status] - rank[b.status]);
    return `<h2 class="dh-h">${escHtml(g)}</h2><ul class="hc-list">` + cs.map(c => {
      const hotels = (c.hotels || []).map(h => `<li><a href="/dashboard#hotel=${encodeURIComponent(h.id)}" target="_blank" rel="noopener">${escHtml(h.name)}</a> <span class="adm-hint">${escHtml(h.city)}</span></li>`).join('');
      const items = (c.items || []).map(x => `<li>${escHtml(x)}</li>`).join('');
      const more = hotels || items ? `<details class="hc-more"><summary>${hotels ? `${c.hotels.length} hotel${c.hotels.length === 1 ? '' : 's'}` : 'Details'}</summary><ul>${hotels}${items}</ul></details>` : '';
      return `<li class="hc-item"><span class="hc-pill ${HC_PILL[c.status]}">${HC_LABEL[c.status]}</span>
        <div class="hc-body"><div class="hc-title">${escHtml(c.title)}${c.count != null && c.status !== 'ok' ? ` <span class="hc-count">${c.count}</span>` : ''}</div>
        <div class="hc-explain">${escHtml(c.explain)}</div>${more}</div></li>`;
    }).join('') + '</ul>';
  }).join('');
  const days = H.slice(-14);
  const t = document.getElementById('hc-history');
  if (!days.length) { t.innerHTML = '<tbody><tr><td>No history yet: one entry is kept per night.</td></tr></tbody>'; return; }
  const cell = s => `<td class="hc-hcell"><span class="hc-sq hc-dot--${s || 'no_data'}" title="${HC_LABEL[s || 'no_data']}"></span></td>`;
  const day = d => { const x = new Date(d + 'T12:00:00'); return `${x.getDate()}/${x.getMonth() + 1}`; };
  t.innerHTML = `<thead><tr><th>Check</th>${days.map(d => `<th class="hc-hcell">${day(d.date)}</th>`).join('')}</tr></thead><tbody>`
    + `<tr><td><strong>Platform</strong></td>${days.map(d => cell(d.overall)).join('')}</tr>`
    + R.checks.map(c => `<tr><td>${escHtml(c.title)}</td>${days.map(d => cell((d.checks[c.id] || {}).status)).join('')}</tr>`).join('') + '</tbody>';
}

async function loadDataHealth(run) {
  const msg = document.getElementById('dh-msg');
  msg.textContent = run ? 'Running the checks…' : 'Loading…';
  try {
    const res = run ? await fetch('/api/admin/data-health/run', { method: 'POST', headers: authHeaders(true) })
                    : await fetch('/api/admin/data-health', { headers: authHeaders() });
    dhData = await res.json();
    if (!res.ok) throw new Error(dhData.error || res.status);
  } catch (e) { msg.textContent = 'Could not load: ' + e.message; return; }
  msg.textContent = `Checked ${dhData.report.checked_at.replace('T', ' ')}`;
  renderDataHealth();
}

function renderDataHealth() {
  const R = dhData.report, S = R.stats, sc = dhData.scraper || {};
  const stat = (v, l) => `<div class="adm-stat"><span class="adm-stat-val">${v}</span><span class="adm-stat-label">${escHtml(l)}</span></div>`;
  document.getElementById('dh-stats').innerHTML = [
    stat(escHtml(sc.last_run_finished ? sc.last_run_finished.slice(0, 16).replace('T', ' ') : '—'), 'Last scraper run'),
    stat(sc.nights_found_pct == null ? '—' : sc.nights_found_pct + '%', 'Nights priced, last run'),
    stat(`${S.hotels_with_prices} / ${S.open_hotels}`, 'Hotels with prices'),
    stat(dhPct(S.coverage_30), 'Next 30 nights usable'),
    stat(S.history_days_max, 'Days of price history'),
    stat(`${S.confidence.medium + S.confidence.high} / ${S.open_hotels}`, 'Hotels at medium confidence or above'),
    stat(S.room_status.sourced, 'Room counts with a source'),
    stat(S.google_issues, 'Google ID problems'),
  ].join('');
  renderHealthChecks();
  document.getElementById('dh-problems').innerHTML = '';
  const st = S.statuses_30;
  document.getElementById('dh-problems').insertAdjacentHTML('beforeend',
    `<p class="adm-hint">Next 30 nights, all open hotels: ${DH_STATUS.map(k => `${k.replace(/_/g, ' ')} ${dhNum(st[k])}`).join(' · ')}. `
    + `Price flags: ${Object.entries(S.flags).map(([k, v]) => `${k.replace('_', ' ')} ${v}`).join(' · ')}. First price ${escHtml(S.first_price || '—')}.</p>`);

  dhTable('dh-flags', ['Flag', 'State', 'What it changes'], dhData.flags.map(f =>
    [`<code>${escHtml(f.name)}</code>`, f.on ? '<strong>on</strong>' : 'off', escHtml(f.what)]));

  renderDhHotels();
  dhTable('dh-cities', ['City', 'Hotels', 'Rooms', 'With prices', 'Next 30 usable', 'Median history (days)', 'Confidence'],
    Object.entries(R.cities).sort((a, b) => b[1].rooms - a[1].rooms).map(([c, v]) =>
      [escHtml(c), v.hotels, dhNum(v.rooms), v.hotels_with_prices, dhPct(v.coverage_30), v.median_history_days, escHtml(v.confidence)]));

  const P = R.plausibility;
  document.getElementById('dh-plaus-sub').textContent = `gap over ${P.gap_threshold_pts} pts flagged · ${P.year}`;
  document.getElementById('dh-plaus-note').textContent = P.note;
  dhTable('dh-plaus', ['City', 'Hotels', `Model ${P.year} (prior)`, 'Model, next 30 nights', 'Official 2025', 'Kodo 2026E', 'Kodo 2027F', 'Gap vs official', 'Riads', 'Upper upscale+'],
    P.rows.map(r => [escHtml(r.city), r.hotels, dhNum(r.model_year, 1) + '%', r.window_model == null ? '—' : dhNum(r.window_model, 1) + '%',
      r.official_2025 == null ? '—' : r.official_2025 + '%', r.kodo_2026e == null ? '—' : r.kodo_2026e + '%',
      r.kodo_2027f == null ? '—' : r.kodo_2027f + '%',
      r.gap_vs_official == null ? '—' : `<span class="${r.flag ? 'dh-bad' : ''}">${r.gap_vs_official > 0 ? '+' : ''}${r.gap_vs_official} pts</span>`,
      r.riad_share + '%', r.upper_share + '%']));
  document.getElementById('dh-plaus-causes').innerHTML = P.rows.filter(r => r.flag).map(r =>
    `<p class="adm-hint"><strong>${escHtml(r.city)}</strong> (${r.gap_vs_official > 0 ? '+' : ''}${r.gap_vs_official} pts): ${r.likely_causes.map(escHtml).join('; ')}. <em>${escHtml(r.proposal)}</em></p>`).join('');

  renderDhCalibration();
  const eff = R.new_hotels_effect || [];
  document.getElementById('dh-newhotels').innerHTML = eff.map(e => `<p class="adm-hint"><strong>${escHtml(e.figure)}</strong>: `
    + (e.rows.length ? e.rows.slice(0, 8).map(r => `${escHtml(r.group)} ${r.with_new} with, ${r.without_new} without (${r.change > 0 ? '+' : ''}${r.change}; ${r.new_hotels} of ${r.hotels} hotels new)`).join(' · ')
       : 'no figure to compare yet') + '</p>').join('');

  dhTable('dh-models', ['Model or figure', 'Data used', 'Assumes', 'Label clients see', 'Confidence today'],
    dhData.models.map(m => [`<strong>${escHtml(m.name)}</strong><div class="adm-hint">${escHtml(m.where)}</div>`, escHtml(m.data), escHtml(m.assumes), escHtml(m.label), escHtml(m.confidence)]));
  const T = R.thresholds;
  document.getElementById('dh-thresholds').innerHTML =
    `Confidence: medium from ${dhPct(T.confidence.medium.coverage)} of the next 30 nights priced, ${T.confidence.medium.history_days} days of history and price quality ${T.confidence.medium.quality}; `
    + `high also needs ${T.confidence.high.history_days} days, ${dhPct(T.confidence.high.coverage)} coverage and a calibration error within ${T.confidence.high.calibration_mae_pts} pts; `
    + `low from ${dhPct(T.confidence.low.coverage)} coverage or ${T.confidence.low.history_days} days. Proposed: shown from ${T.show_from}, greyed when low, hidden when insufficient (with CONFIDENCE_UI). `
    + `Labels clients would see: ${Object.entries(dhData.labels).map(([k, v]) => `${k} "${escHtml(v)}"`).join(', ')}. `
    + `Price checks: own outlier ×${T.price_checks.outlier_self}, peer outlier ×${T.price_checks.outlier_peer}, jump ×${T.price_checks.jump}, flat from ${T.price_checks.flat_min_nights} nights, stale after ${T.price_checks.stale_days} days, `
    + `${T.price_checks.min_rate}–${dhNum(T.price_checks.max_rate)} MAD; a night counts as covered from a quality score of ${T.usable_score}. Google listing drift over ${T.google_drift_km} km.`;
}

function renderDhHotels() {
  const R = dhData.report, f = document.getElementById('dh-filter').value, q = document.getElementById('dh-search').value.trim().toLowerCase();
  const test = {
    any: v => v.issues.length || !v.history_days || v.price_quality != null && v.price_quality < 0.85,
    noprice: v => !v.history_days, google: v => v.google.issues.length,
    outlier: v => v.flags.outlier_self || v.flags.outlier_peer || v.flags.currency,
    rooms: v => v.room_status !== 'sourced', lowcov: v => v.coverage_30 < 0.5,
    dup: v => v.issues.some(i => i.includes('duplicate') || i.includes('same Google')), all: () => true,
  }[f];
  const rows = Object.entries(R.hotels).filter(([, v]) => test(v) && (!q || `${v.name} ${v.city}`.toLowerCase().includes(q)))
    .sort((a, b) => b[1].keys - a[1].keys);
  document.getElementById('dh-count').textContent = `${rows.length} hotel${rows.length === 1 ? '' : 's'}`;
  dhTable('dh-hotels', ['Hotel', 'City', 'Rooms', 'Room count', 'History (days)', 'Next 30 usable', 'Statuses, next 30', 'Price quality', 'Flags', 'Confidence', 'Issues', 'Model rules'],
    rows.slice(0, 400).map(([id, v]) => [
      `${escHtml(v.name)} <span class="adm-hint">${escHtml(id)}</span>`, escHtml(v.city), dhNum(v.keys),
      escHtml(v.room_status.replace(/_/g, ' ')), v.history_days, dhPct(v.coverage_30),
      escHtml(Object.entries(v.statuses_30).map(([k, n]) => `${k.replace(/_/g, ' ')} ${n}`).join(', ')),
      v.price_quality == null ? '—' : v.price_quality, escHtml(Object.entries(v.flags).map(([k, n]) => `${k} ${n}`).join(', ') || '—'),
      `${escHtml(v.confidence)}${v.confidence_reasons.length ? `<div class="adm-hint">${escHtml(v.confidence_reasons.join('; '))}</div>` : ''}`,
      escHtml(v.issues.join('; ') || '—'), escHtml(v.model_rules.join('; ') || '—')]));
}

function renderDhCalibration() {
  const C = dhData.calibration || {}, got = dhData.figures_received || [];
  const recv = got.length ? `<p class="adm-hint">Figures received from ${got.length} hotel${got.length === 1 ? '' : 's'}: `
    + got.map(g => `${escHtml(g.name)} (${g.months.length} months${g.nights ? `, ${g.nights} nights` : ''})`).join(' · ') + '. Confidential: admin only.</p>'
    : '<p class="adm-hint">No figures received from hotels yet. Send them the template (Uploads), then upload what comes back.</p>';
  let body = `<p class="adm-hint">${escHtml(C.message || 'Calibration has not run yet.')} ${C.run_at ? 'Last run ' + escHtml(C.run_at.slice(0, 16).replace('T', ' ')) + '.' : ''}</p>`;
  const block = (b, what) => {
    if (!b) return '';
    const line = s => `v1 ${s.v1_mae_pts ?? '—'} pts (bias ${s.v1_bias_pts ?? '—'}) · v2 ${s.v2_mae_pts ?? '—'} pts (bias ${s.v2_bias_pts ?? '—'}), inside the v2 range ${s.v2_inside_range_pct ?? '—'}%`;
    const grp = (title, g, name = k => k) => `<tr><td colspan="3"><strong>${title}</strong></td></tr>` + Object.entries(g || {}).map(([k, s]) =>
      `<tr><td>${escHtml(name(k))}</td><td>${s.n}</td><td>${escHtml(line(s))}</td></tr>`).join('');
    const names = Object.fromEntries((b.details || []).map(d => [d.hotel_id, d.hotel]));
    return `<p class="adm-hint"><strong>${what}</strong>: ${escHtml(b.note)}. Overall: ${escHtml(line(b.overall))}</p>`
      + `<div class="dh-scroll"><table class="adm-table"><thead><tr><th>Group</th><th>n</th><th>Average error (absolute) and bias, pts</th></tr></thead><tbody>`
      + grp('By hotel', b.by_hotel, k => names[k] || k) + grp('By city', b.by_city) + grp('By month', b.by_month) + '</tbody></table></div>';
  };
  body += block(C.daily, 'Nights') + block(C.monthly, 'Months');
  document.getElementById('dh-calib').innerHTML = recv + body;
  const A = C.abroad_holidays;
  document.getElementById('dh-abroad').innerHTML = A
    ? `<p class="adm-hint">${escHtml(A.verdict)} Nights compared ${A.nights_compared}, inside the periods ${A.nights_in_periods}. `
      + (A.overall && A.overall.with && A.overall.with.v2 != null ? `v2 error with ${A.overall.with.v2}, without all ${A.overall.without_all.v2} pts.` : '') + '</p>'
    : '<p class="adm-hint">Runs with the calibration, once real figures cover the 39 periods (from 20 Nov 2026).</p>';
}

async function loadDhPreview() {
  const box = document.getElementById('dh-preview');
  box.innerHTML = '<p class="adm-loading">Computing…</p>';
  let P;
  try { const r = await fetch('/api/admin/data-health/preview', { headers: authHeaders() }); P = await r.json(); if (!r.ok) throw new Error(P.error || r.status); }
  catch (e) { box.innerHTML = `<p class="adm-hint">Could not compute: ${escHtml(e.message)}</p>`; return; }
  const n = (v, d = 1) => v == null ? '—' : dhNum(v, d);
  const C = P.CONFIDENCE_UI, Q = P.QUALITY_RANGES;
  let h = `<h3 class="dh-h3">CONFIDENCE_UI · modelled occupancy, next 30 nights</h3><div class="dh-scroll"><table class="adm-table"><thead><tr><th>City or hotel</th><th>Before</th><th>After</th><th>Shown as</th></tr></thead><tbody>`
    + C.cities.map(r => `<tr><td>${escHtml(r.city)}</td><td>${n(r.before)}%</td><td>${r.after_shown === 'hidden' ? 'hidden' : n(r.after) + '%'}</td><td>${escHtml(r.after_label)} (${r.after_shown})</td></tr>`).join('')
    + C.hotels.map(r => `<tr><td>${escHtml(r.hotel)} <span class="adm-hint">${escHtml(r.city)}</span></td><td>${n(r.before)}%</td><td>${r.after == null ? 'hidden' : n(r.after) + '%'}</td><td>${escHtml(r.after_label)}<div class="adm-hint">${escHtml(r.reasons.join('; '))}</div></td></tr>`).join('')
    + '</tbody></table></div>';
  h += `<h3 class="dh-h3">QUALITY_RANGES · v2 occupancy over the next 30 nights, low / mid / high</h3>`
    + (Q.error ? `<p class="adm-hint">${escHtml(Q.error)}</p>` : `<div class="dh-scroll"><table class="adm-table"><thead><tr><th>Hotel</th><th>Before</th><th>After</th></tr></thead><tbody>`
      + Q.hotels.map(r => `<tr><td>${escHtml(r.hotel)} <span class="adm-hint">${escHtml(r.city)}</span></td><td>${n(r.before.low)} / ${n(r.before.mid)} / ${n(r.before.high)}</td><td>${n(r.after.low)} / ${n(r.after.mid)} / ${n(r.after.high)}</td></tr>`).join('') + '</tbody></table></div>');
  h += `<h3 class="dh-h3">VALUATION_V2 · segment defaults, 150 keys, no purchase price</h3>` + dhValuationTable();
  box.innerHTML = h;
}

// The valuation engine runs in the page (static/js/valuation_engine.js):
// each segment's defaults, today's engine (v1) against the corrected one (v2)
function dhValuationTable() {
  if (!window.KodoValuation) return '<p class="adm-hint">Valuation engine not loaded.</p>';
  const SEG = { 'Luxury': [65, 4500, 60, 28, 30, 24, 3.5, 4.5, 7.0, 6.0], 'Upper Upscale': [63, 2800, 65, 22, 32, 26, 3, 4, 7.0, 6.5],
                'Upscale': [60, 1800, 70, 18, 34, 28, 3, 4, 7.5, 7.0], 'Midscale': [58, 1000, 78, 12, 36, 30, 2.5, 3.5, 8.0, 7.5] };
  const m = v => `${(v / 1e6).toFixed(0)}M`;
  const rows = Object.entries(SEG).map(([seg, d]) => {
    const inp = { keys: 150, stabilized_occ: d[0], adr: d[1], growth_rate: 3.5, rampup: 0, rooms_rev_pct: d[2], fb_rev_pct: d[3], dept_exp_pct: d[4],
                  undist_exp_pct: d[5], mgmt_fee_pct: d[6], ffe_pct: d[7], discount_rate: d[8], terminal_cap_rate: d[9], hold_period: 10,
                  capex_yr1: 0, purchase_price: 0, equity_pct: 35, txn_pct: 3, loan_rate: 6.5 };
    const a = KodoValuation.run(inp, 'v1'), b = KodoValuation.run(inp, 'v2');
    return `<tr><td>${seg}</td><td>MAD ${m(a.range_low)}–${m(a.range_high)} · ${(a.value_per_key / 1e6).toFixed(2)}M/key · GOP ${a.cashFlows[2].gop_margin.toFixed(0)}% · IRR ${a.irr.toFixed(1)}% · EM ${a.equity_multiple.toFixed(2)}x</td>`
      + `<td>MAD ${m(b.range_low)}–${m(b.range_high)} · ${(b.value_per_key / 1e6).toFixed(2)}M/key · GOP ${b.cashFlows[2].gop_margin.toFixed(0)}% · IRR ${b.irr.toFixed(1)}% · EM ${b.equity_multiple.toFixed(2)}x</td></tr>`;
  });
  return `<div class="dh-scroll"><table class="adm-table"><thead><tr><th>Segment</th><th>Before (v1)</th><th>After (v2)</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}

document.getElementById('dh-run').addEventListener('click', () => loadDataHealth(true));
document.getElementById('dh-filter').addEventListener('change', () => dhData && renderDhHotels());
document.getElementById('dh-search').addEventListener('input', () => dhData && renderDhHotels());
document.getElementById('dh-preview').addEventListener('click', e => { if (e.target.id === 'dh-preview-btn') loadDhPreview(); });
document.getElementById('dh-calibrate').addEventListener('click', async () => {
  const msg = document.getElementById('dh-msg');
  msg.textContent = 'Running the calibration…';
  const r = await fetch('/api/admin/occupancy/calibrate', { method: 'POST', headers: authHeaders(true) });
  const d = await r.json().catch(() => ({}));
  msg.textContent = r.ok ? (d.message || 'Done.') : (d.error || 'Calibration failed.');
  if (r.ok) loadDataHealth(false);
});
