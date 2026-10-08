// ─── Kōdō Admin ──────────────────────────────────────────────────────────
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
  active:   { label: 'Active',   color: 'var(--positive)' },
  pending:  { label: 'Pending',  color: 'var(--cat-orange)' },
  disabled: { label: 'Disabled', color: 'var(--text-muted)' },
};
// Tier badges are neutral outlines, never orange (orange is reserved for
// the Pending status above) — Advisory reads as an ink/white outline, not
// a color, since being an admin is called out separately by .adm-admin-tag.
const TIER_META = {
  observer:    { label: 'Observer',    color: 'var(--text-muted)' },
  benchmarker: { label: 'Benchmarker', color: 'var(--accent)' },
  advisory:    { label: 'Advisory',    color: 'var(--text)' },
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
      const tierMeta = TIER_META[u.tier] || TIER_META.observer;
      const statusMeta = STATUS_META[statusBucket(u)];
      return `<div class="adm-row adm-row-users">
        <div class="adm-row-main" data-label="Name" style="flex-direction:row;align-items:center;gap:6px">
          <span class="adm-row-name" title="${escHtml(u.name || u.email)}">${escHtml(u.name || '—')}</span>
          ${u.is_admin ? '<span class="adm-admin-tag">Admin</span>' : ''}
        </div>
        <span class="adm-row-email" data-label="Email" title="${escHtml(u.email)}">${escHtml(u.email)}</span>
        <span data-label="Tier"><span class="adm-pill" style="color:${tierMeta.color}">${tierMeta.label}</span></span>
        <span data-label="Status"><span class="adm-pill" style="color:${statusMeta.color}">${statusMeta.label}</span></span>
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
      confirmMessage: `Delete ${u.name || u.email}? This cannot be undone.`,
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
          <span class="adm-pill" style="color:${STATUS_META[statusBucket(m)].color}">${escHtml((m.status || '').replace(/_/g, ' '))}</span>
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
        ${a.featured ? '<span class="adm-row-sub" style="color:#4A7FA5">Featured</span>' : ''}
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
