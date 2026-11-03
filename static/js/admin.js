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
const SECTIONS = ['overview', 'users', 'orgs', 'news', 'uploads', 'rates', 'occupancy', 'events', 'system'];
const SECTION_LOADERS = {
  overview: loadOverview,
  users: loadUsers,
  orgs: loadOrgs,
  news: loadArticles,
  uploads: () => { loadHotelsForDI(); loadRecentUploads(); },
  rates: () => { loadScraperStatus(); loadScrapeCoverage(); populateHotelSelect(); loadIdOverrides(); loadCoordHistory(); },
  occupancy: loadOccupancyStatus,
  events: loadEvents,
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
    t.innerHTML = '<thead><tr><th>Night</th><th>v1</th><th>v2 low–mid–high</th><th>Published rate</th><th>Price coverage</th><th>v2 signals</th></tr></thead>';
    const tb = document.createElement('tbody');
    (d.nights || []).forEach(n => {
      const tr = document.createElement('tr');
      [n.night, n.v1 != null ? `${Math.round(n.v1)}%` : '–',
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
    + (r.pipeline_name ? ` · pipeline project ${r.pipeline_id} "${r.pipeline_name}"${r.pipeline_new ? ' (new)' : ''}` : '')
    + (r.new && r.action === 'pipeline_position' ? ` · ${(r.old || []).join(', ')} → ${r.new.join(', ')}${r.approximate ? ' (approximate)' : ''}` : '')
    + (r.note ? ` · ${r.note}` : '') + (r.reason ? ` · ${r.reason}` : ''),
  'Change this server\'s hotel list as previewed? hotels.csv (and pipeline.csv for a pipeline move, performance.csv for an added hotel) is backed up first.',
  ['hide', 'unhide', 'remove', 'rename', 'city', 'owner', 'add', 'to_pipeline', 'pipeline_position']);
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
  row.append(name, when, btn);
  return row;
}

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
      d.textContent = l.action === 'restore'
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
  const typeSel = document.getElementById('ev-type');
  typeSel.innerHTML = Object.entries(evData.types).map(([k, v]) => `<option value="${k}">${v}</option>`).join('');
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
function renderEventsTable() {
  const q = document.getElementById('ev-search').value.trim().toLowerCase();
  const show = document.getElementById('ev-filter').value;
  const today = new Date().toISOString().slice(0, 10);
  const rows = evData.events.filter(e =>
    (show === 'all' || (show === 'upcoming' && e.end >= today && !e.hidden) || (show === 'hidden' && e.hidden)
      || (show === 'edited' && (e.edited || e.added)) || (show === 'estimated' && ['estimated', 'moon'].includes(e.date_status)))
    && (!q || [e.name, e.city, e.type, e.venue].join(' ').toLowerCase().includes(q)));
  const t = document.getElementById('ev-table');
  t.innerHTML = '<thead><tr><th>Dates</th><th>Event</th><th>City</th><th>Type</th><th>Impact</th><th>Date</th><th></th></tr></thead>';
  const tb = document.createElement('tbody');
  rows.slice(0, 300).forEach(e => {
    const tr = document.createElement('tr');
    if (e.hidden) tr.style.opacity = '0.55';
    const cells = [e.start === e.end ? e.start : `${e.start} → ${e.end}`, e.name + (e.added ? ' (added here)' : e.edited ? ' (edited here)' : ''),
      e.city, evData.types[e.type] || e.type, e.impact, e.date_status];
    cells.forEach(c => { const td = document.createElement('td'); td.textContent = c; tr.appendChild(td); });
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
  if (!rows.length) t.insertAdjacentHTML('beforeend', '<tbody><tr><td colspan="7">No events match.</td></tr></tbody>');
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
    el.value = el.name === 'markets' ? (v || []).join(', ') : el.name === 'model' ? String(v !== false) : (v == null ? '' : v);
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
