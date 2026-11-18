/* HOTS Hosts — console web d'administration à distance.
 * Application monopage sans dépendance. Toutes les données venant des PC sont insérées via
 * textContent (fonction h()), jamais en HTML brut : un PC compromis ne peut pas injecter de script.
 */
'use strict';

const TERMINAL = ['done', 'error', 'expired', 'cancelled'];
const S = { boot: null, timers: [], navToken: 0 };

/* ============================== Utilitaires DOM ============================== */

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k === 'style' && typeof v === 'object') for (const [p, val] of Object.entries(v)) el.style.setProperty(p, val);
      else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
      else if (k === 'value') el.value = v;
      else if (k === 'checked') el.checked = !!v;
      else if (k === 'disabled') el.disabled = !!v;
      else el.setAttribute(k, v === true ? '' : String(v));
    }
  }
  append(el, children);
  return el;
}

function append(el, children) {
  for (const c of [children].flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); return el; }
/** Comme Element.append, mais ignore null/undefined/false (append natif écrirait « null »). */
function put(el, ...children) { return append(el, children); }

const ICONS = {
  monitor: '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  shieldoff: '<path d="M19.69 14a6.9 6.9 0 0 0 .31-2V5l-8-3-3.16 1.18M4.73 4.73L4 5v7c0 6 8 10 8 10a20.29 20.29 0 0 0 5.62-4.38M1 1l22 22"/>',
  lock: '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
  apps: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  eyeoff: '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><path d="M1 1l22 22"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>',
  tool: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  refresh: '<path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
  trash: '<path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>',
  edit: '<path d="M12 20h9M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
  check: '<path d="M20 6L9 17l-5-5"/>',
  x: '<path d="M18 6L6 18M6 6l12 12"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  alert: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/>',
  back: '<path d="M19 12H5M12 19l-7-7 7-7"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  wifioff: '<path d="M1 1l22 22M16.72 11.06A10.94 10.94 0 0 1 19 12.55M5 12.55a10.94 10.94 0 0 1 5.17-2.39M10.71 5.05A16 16 0 0 1 22.58 9M1.42 9a15.91 15.91 0 0 1 4.7-2.88M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01"/>',
  server: '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
  key: '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.78 7.78 5.5 5.5 0 0 1 7.78-7.78zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>',
  history: '<path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>',
  browser: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 9h20M6 6.5h.01M9 6.5h.01"/>',
  smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
  zap: '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>',
  mail: '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="M22 6l-10 7L2 6"/>',
};

function icon(name) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = ICONS[name] || ICONS.info; // constantes internes uniquement
  return svg;
}

function btn(label, opts = {}) {
  const cls = ['btn', opts.kind || '', opts.small ? 'small' : '', opts.big ? 'big' : '', !label ? 'icon' : ''].join(' ').trim();
  const b = h(opts.href ? 'a' : 'button', {
    class: cls, type: opts.href ? null : (opts.type || 'button'), href: opts.href || null,
    target: opts.target || null, rel: opts.target ? 'noopener noreferrer' : null,
    title: opts.title || (label ? null : opts.label) || null, 'aria-label': !label ? (opts.label || opts.title) : null,
    disabled: opts.disabled,
  }, opts.icon ? icon(opts.icon) : null, label || null);
  if (opts.onclick) {
    b.addEventListener('click', async (ev) => {
      if (b.classList.contains('busy')) return;
      b.classList.add('busy');
      try { await opts.onclick(ev); } catch (e) { showError(e); } finally { b.classList.remove('busy'); }
    });
  }
  return b;
}

function badge(text, kind = '', iconName = null) {
  return h('span', { class: `badge ${kind}` }, iconName ? icon(iconName) : null, text);
}

function banner(kind, iconName, ...content) {
  return h('div', { class: `banner ${kind}` }, icon(iconName), h('div', null, ...content));
}

function card(title, iconName, desc, ...content) {
  return h('section', { class: 'card' },
    h('div', { class: 'card-head' },
      iconName ? h('div', { class: 'icon-badge' }, icon(iconName)) : null,
      h('div', { class: 'spacer' }, h('h3', null, title), desc ? h('div', { class: 'muted small' }, desc) : null)),
    ...content);
}

function field(label, input, help) {
  return h('label', { class: 'field' }, h('span', null, label), input, help ? h('small', null, help) : null);
}

function switchEl(checked, onchange, { disabled = false, label = '' } = {}) {
  const input = h('input', { type: 'checkbox', role: 'switch', checked, disabled, 'aria-label': label });
  const wrap = h('label', { class: 'switch' }, input, h('span', { class: 'slider' }));
  input.addEventListener('change', async () => {
    const target = input.checked;
    input.checked = !target;           // l'état réel sera affiché après confirmation du PC
    wrap.classList.add('busy');
    input.disabled = true;
    try {
      const ok = await onchange(target);
      if (ok) input.checked = target;
    } catch (e) {
      showError(e);
    } finally {
      wrap.classList.remove('busy');
      input.disabled = disabled;
    }
  });
  return wrap;
}

function settingRow(title, desc, control, extra) {
  return h('div', { class: 'setting' },
    h('div', { class: 'text' }, h('div', { class: 'title' }, title), desc ? h('div', { class: 'desc' }, desc) : null, extra || null),
    control);
}

/* ============================== Formats ============================== */

const DATE_FMT = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium', timeStyle: 'short' });
function fmtDate(ts) { return ts ? DATE_FMT.format(new Date(ts * 1000)) : '—'; }
function fmtAgo(ts) {
  if (!ts) return 'jamais';
  const d = Math.max(0, Date.now() / 1000 - ts);
  if (d < 45) return "à l'instant";
  if (d < 3600) return `il y a ${Math.round(d / 60)} min`;
  if (d < 86400) return `il y a ${Math.round(d / 3600)} h`;
  if (d < 86400 * 30) return `il y a ${Math.round(d / 86400)} j`;
  return fmtDate(ts);
}
function fmtSize(n) {
  if (n == null) return '—';
  if (n < 1024) return `${n} o`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} Ko`;
  return `${(n / 1024 / 1024).toFixed(1)} Mo`;
}
function fmtUptime(s) {
  if (!s && s !== 0) return '—';
  const d = Math.floor(s / 86400), hh = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60);
  return d ? `${d} j ${hh} h` : hh ? `${hh} h ${m} min` : `${m} min`;
}
function initials(text) {
  return (text || '?').split(/[\s@.]+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';
}

/* ============================== API ============================== */

class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

async function api(method, path, body) {
  const opts = { method, headers: { Accept: 'application/json' }, credentials: 'same-origin' };
  if (method !== 'GET') opts.headers['X-HOTS-CSRF'] = '1';
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  let r;
  try {
    r = await fetch(path, opts);
  } catch (e) {
    throw new ApiError(0, 'Serveur injoignable. Vérifiez votre connexion.');
  }
  let data = null;
  try { data = await r.json(); } catch (e) { data = null; }
  if (r.status === 401 && !path.startsWith('/api/auth/') && path !== '/api/bootstrap') {
    if (S.boot) S.boot.user = null;
    go('#/login');
    throw new ApiError(401, (data && data.detail) || 'Session expirée.');
  }
  if (!r.ok) throw new ApiError(r.status, (data && data.detail) || `Erreur ${r.status}`);
  return data;
}

function showError(e) {
  console.error(e);
  if (e && e.status === 401) return;
  toast((e && e.message) || String(e), 'error');
}

/* ============================== Toasts & modales ============================== */

function toast(message, kind = 'info', ms = 4500) {
  const box = document.getElementById('toasts');
  const t = h('div', { class: `toast ${kind}`, role: kind === 'error' ? 'alert' : 'status' },
    icon(kind === 'ok' ? 'check' : kind === 'error' ? 'alert' : 'info'), h('div', null, message));
  put(box, t);
  setTimeout(() => t.remove(), kind === 'error' ? ms * 1.6 : ms);
}

function modal({ title, body, actions = [], wide = false, iconName = null, onclose = null }) {
  return new Promise((resolve) => {
    const prevFocus = document.activeElement;
    const close = (value) => {
      document.removeEventListener('keydown', onKey);
      backdrop.remove();
      if (onclose) onclose();
      if (prevFocus && prevFocus.focus) prevFocus.focus();
      resolve(value);
    };
    const onKey = (ev) => { if (ev.key === 'Escape') close(null); };
    const foot = h('div', { class: 'modal-foot' });
    for (const a of actions) {
      put(foot, btn(a.label, {
        kind: a.kind, icon: a.icon, type: a.submit ? 'submit' : 'button',
        onclick: a.submit ? null : async () => {
          if (a.onclick) {
            const res = await a.onclick();
            if (res === false) return;
            close(res === undefined ? a.value : res);
          } else close(a.value);
        },
      }));
    }
    const dlg = h('div', { class: `modal${wide ? ' wide' : ''}`, role: 'dialog', 'aria-modal': 'true', 'aria-label': title },
      h('div', { class: 'modal-head' },
        iconName ? h('div', { class: 'icon-badge' }, icon(iconName)) : null,
        h('h2', null, title),
        btn('', { kind: 'ghost', icon: 'x', label: 'Fermer', onclick: () => close(null) })),
      h('div', { class: 'modal-body' }, body), foot);
    const backdrop = h('div', { class: 'modal-backdrop', onmousedown: (ev) => { if (ev.target === backdrop) close(null); } }, dlg);
    document.body.append(backdrop);
    document.addEventListener('keydown', onKey);
    const first = dlg.querySelector('input, textarea, select') || foot.querySelector('.btn.primary, .btn.danger');
    if (first) setTimeout(() => first.focus(), 30);
    dlg._close = close;
  });
}

function confirmDialog(message, { title = 'Confirmation', ok = 'Confirmer', danger = false, iconName = 'alert' } = {}) {
  return modal({
    title, iconName,
    body: h('p', null, message),
    actions: [{ label: 'Annuler', value: false }, { label: ok, kind: danger ? 'danger' : 'primary', value: true }],
  }).then((v) => v === true);
}

/** Modale contenant un formulaire. submit(values) peut lever une erreur pour rester ouverte. */
function formDialog({ title, iconName, fields, submitLabel = 'Enregistrer', intro = null, submit }) {
  const inputs = {};
  const form = h('form', { novalidate: true });
  if (intro) put(form, intro);
  for (const f of fields) {
    let input;
    if (f.type === 'textarea') input = h('textarea', { rows: f.rows || 6, placeholder: f.placeholder || '', value: f.value || '' });
    else if (f.type === 'select') input = h('select', null, f.options.map(([v, l]) => h('option', { value: v, selected: v === f.value }, l)));
    else if (f.type === 'checkbox') input = h('input', { type: 'checkbox', checked: !!f.value });
    else input = h('input', { type: f.type || 'text', placeholder: f.placeholder || '', value: f.value ?? '', autocomplete: f.autocomplete || 'off', required: f.required });
    inputs[f.name] = input;
    if (f.type === 'checkbox') put(form, h('label', { class: 'field row' }, input, h('span', null, f.label)));
    else put(form, field(f.label, input, f.help));
  }
  const errBox = h('div', { class: 'banner danger hidden' });
  put(form, errBox);
  let closeFn = null;
  const doSubmit = async () => {
    const values = {};
    for (const [k, el] of Object.entries(inputs)) values[k] = el.type === 'checkbox' ? el.checked : el.value;
    try {
      const res = await submit(values);
      return res === undefined ? true : res;
    } catch (e) {
      clear(errBox).classList.remove('hidden');
      put(errBox, icon('alert'), h('div', null, e.message || String(e)));
      return false;
    }
  };
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const res = await doSubmit();
    if (res !== false && closeFn) closeFn(res);
  });
  const p = modal({
    title, iconName, body: form,
    actions: [{ label: 'Annuler', value: null }, { label: submitLabel, kind: 'primary', onclick: doSubmit }],
  });
  closeFn = (v) => { const dlg = form.closest('.modal'); if (dlg && dlg._close) dlg._close(v); };
  return p;
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast('Copié dans le presse-papiers', 'ok', 2000);
  } catch (e) {
    toast('Copie impossible : sélectionnez le texte manuellement.', 'error');
  }
}

function copyBox(value, extraClass = '') {
  return h('div', { class: 'copybox' }, h('div', { class: `value ${extraClass}` }, value),
    btn('Copier', { small: true, icon: 'copy', onclick: () => copyText(value) }));
}

/* ============================== Routage & mise en page ============================== */

function go(hash) { if (location.hash !== hash) location.hash = hash; else render(); }
function every(ms, fn) { S.timers.push(setInterval(fn, ms)); }
function stopTimers() { S.timers.forEach(clearInterval); S.timers = []; }

const ROUTES = [
  [/^#\/setup\/([\w-]+)$/, viewSetup, true],
  [/^#\/login$/, viewLogin, true],
  [/^#\/register$/, viewRegister, true],
  [/^#\/pc\/([\w]+)(?:\/(\w+))?$/, viewDevice, false],
  [/^#\/account$/, viewAccount, false],
  [/^#\/admin$/, viewAdmin, false],
  [/^(#\/?)?$/, viewDashboard, false],
];

async function render() {
  stopTimers();
  const token = ++S.navToken;
  const hash = location.hash || '#/';
  try {
    if (!S.boot || !S.boot.user) S.boot = await api('GET', '/api/bootstrap');
  } catch (e) {
    return mountBare(h('div', { class: 'auth-card card' }, banner('danger', 'alert', e.message)));
  }
  if (token !== S.navToken) return;
  document.title = S.boot.server_name || 'Console HOTS Hosts';
  for (const [re, view, isPublic] of ROUTES) {
    const m = hash.match(re);
    if (!m) continue;
    if (S.boot.setup_required && view !== viewSetup) return viewNotConfigured();
    if (!isPublic && !S.boot.user) return go('#/login');
    if ((view === viewLogin || view === viewRegister) && S.boot.user) return go('#/');
    try {
      await view(m.slice(1), token);
    } catch (e) {
      showError(e);
    }
    return;
  }
  go('#/');
}

function mountBare(...content) {
  const app = clear(document.getElementById('app'));
  put(app, h('div', { class: 'auth-wrap' }, ...content));
}

function shell(active, ...content) {
  const u = S.boot.user;
  const navItem = (href, iconName, label, key) =>
    h('a', { href, class: active === key ? 'active' : null }, icon(iconName), h('span', null, label));
  const app = clear(document.getElementById('app'));
  const main = h('main', null, ...content);
  put(app, 
    h('header', { class: 'topbar' },
      h('a', { class: 'brand', href: '#/' }, h('img', { src: '/static/logo.png', alt: '' }),
        h('div', null, S.boot.server_name || 'Console HOTS Hosts', h('span', { class: 'sub' }, 'Administration à distance'))),
      h('nav', { class: 'nav' },
        navItem('#/', 'monitor', 'Mes PC', 'devices'),
        navItem('#/account', 'user', 'Mon compte', 'account'),
        u.is_superadmin ? navItem('#/admin', 'server', 'Administration', 'admin') : null),
      h('div', { class: 'userbox' },
        h('div', { class: 'who', title: u.email }, u.name || u.email,
          u.account_name && u.account_name !== u.name ? h('div', { class: 'small' }, u.account_name) : null),
        h('div', { class: 'avatar', 'aria-hidden': 'true' }, initials(u.name || u.email)),
        btn('', { kind: 'ghost', icon: 'logout', label: 'Se déconnecter', onclick: logout }))),
    main);
  return main;
}

async function logout() {
  try { await api('POST', '/api/auth/logout'); } catch (e) { /* ignoré */ }
  S.boot = null;
  go('#/login');
}

/* ============================== Premier lancement ============================== */

function viewNotConfigured() {
  mountBare(h('div', { class: 'auth-card card' },
    h('div', { class: 'auth-logo' }, h('img', { src: '/static/logo.png', alt: '' }), h('h1', null, 'Console HOTS Hosts')),
    banner('info', 'info', h('p', null, "Ce serveur n'est pas encore configuré."),
      h('p', null, 'Ouvrez le lien de configuration affiché à la fin de ', h('code', null, 'deploy.sh'),
        '. Pour l\'afficher à nouveau sur le serveur :'),
      h('pre', null, 'sudo hots-server setup-link'))));
}

function passwordMeter(input) {
  const bar = h('div');
  input.addEventListener('input', () => {
    const v = input.value;
    let score = 0;
    if (v.length >= 10) score++;
    if (v.length >= 14) score++;
    if (/[a-z]/.test(v) && /[A-Z]/.test(v)) score++;
    if (/\d/.test(v)) score++;
    if (/[^\w]/.test(v)) score++;
    const pct = Math.min(100, score * 20);
    bar.style.setProperty('width', `${pct}%`);
    bar.style.setProperty('background', pct < 40 ? 'var(--danger)' : pct < 80 ? 'var(--warn)' : 'var(--ok)');
  });
  return h('div', { class: 'pw-meter' }, bar);
}

function viewSetup([token]) {
  const data = { server_name: 'Console HOTS Hosts', account_name: '', name: '', email: '', password: '', registration_open: false };
  let step = 0;
  const wrap = h('div', { class: 'auth-card wide card' });
  mountBare(wrap);

  const stepsBar = () => h('div', { class: 'steps' }, [0, 1, 2, 3].map((i) => h('div', { class: `step${i <= step ? ' done' : ''}` })));
  const header = (title, sub) => [
    h('div', { class: 'auth-logo' }, h('img', { src: '/static/logo.png', alt: '' }), h('h1', null, title), h('p', { class: 'muted' }, sub)),
    stepsBar(),
  ];

  function paint() {
    clear(wrap);
    if (step === 0) {
      const name = h('input', { type: 'text', value: data.server_name, maxlength: 80 });
      put(wrap, ...header('Bienvenue 👋', 'Configurons votre console en 3 étapes (1 minute).'),
        h('h2', null, 'Nom de votre console'),
        field('Nom affiché', name, 'Par exemple : « Console famille Dupont » ou le nom de votre entreprise.'),
        h('div', { class: 'row end' }, btn('Continuer', { kind: 'primary', big: true, onclick: () => { data.server_name = name.value.trim() || data.server_name; step = 1; paint(); } })));
    } else if (step === 1) {
      const name = h('input', { type: 'text', value: data.name, autocomplete: 'name' });
      const email = h('input', { type: 'email', value: data.email, autocomplete: 'email' });
      const pw = h('input', { type: 'password', autocomplete: 'new-password' });
      const pw2 = h('input', { type: 'password', autocomplete: 'new-password' });
      const err = h('div', { class: 'banner danger hidden' });
      put(wrap, ...header('Votre compte administrateur', 'Ce compte gère le serveur et vos propres PC.'),
        field('Votre nom', name), field('Adresse e-mail (identifiant)', email),
        field('Mot de passe', pw, 'Au moins 10 caractères.'), passwordMeter(pw),
        h('div', { style: { height: '12px' } }), field('Confirmez le mot de passe', pw2), err,
        h('div', { class: 'row' }, btn('Retour', { onclick: () => { step = 0; paint(); } }), h('div', { class: 'spacer' }),
          btn('Continuer', {
            kind: 'primary', big: true, onclick: () => {
              const problem = !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim()) ? 'Adresse e-mail invalide.'
                : pw.value.length < 10 ? 'Le mot de passe doit contenir au moins 10 caractères.'
                  : pw.value !== pw2.value ? 'Les deux mots de passe ne correspondent pas.' : '';
              if (problem) { clear(err).classList.remove('hidden'); put(err, icon('alert'), h('div', null, problem)); return; }
              Object.assign(data, { name: name.value.trim(), email: email.value.trim(), password: pw.value });
              step = 2; paint();
            },
          })));
    } else if (step === 2) {
      const reg = h('input', { type: 'checkbox', checked: data.registration_open });
      put(wrap, ...header('Comment vos clients obtiennent-ils un compte ?', 'Chaque client ne voit et ne gère que ses propres PC.'),
        h('div', { class: 'card flat stack' },
          h('label', { class: 'row' }, h('input', { type: 'radio', name: 'reg', checked: !data.registration_open, onchange: () => { reg.checked = false; } }),
            h('div', null, h('strong', null, 'Je crée moi-même les comptes clients'), h('div', { class: 'muted small' }, 'Recommandé. Depuis le menu « Administration ».'))),
          h('label', { class: 'row' }, h('input', { type: 'radio', name: 'reg', checked: data.registration_open, onchange: () => { reg.checked = true; } }),
            h('div', null, h('strong', null, 'Inscription libre'), h('div', { class: 'muted small' }, 'Toute personne connaissant l\'adresse de la console peut créer un compte.')))),
        h('div', { style: { height: '16px' } }),
        h('div', { class: 'row' }, btn('Retour', { onclick: () => { step = 1; paint(); } }), h('div', { class: 'spacer' }),
          btn('Terminer la configuration', {
            kind: 'primary', big: true, icon: 'check', onclick: async () => {
              data.registration_open = reg.checked;
              try {
                await api('POST', '/api/setup', { token, ...data, account_name: data.name || 'Administration' });
                S.boot = null;
                step = 3; paint();
              } catch (e) { showError(e); }
            },
          })));
    } else {
      put(wrap, ...header('C\'est prêt ! 🎉', 'Votre console est opérationnelle.'),
        h('ol', { class: 'howto' },
          h('li', null, h('div', null, h('strong', null, 'Ajoutez un premier PC'), h('div', { class: 'muted' }, 'Bouton « Ajouter un PC » : un code à saisir pendant l\'installation de HOTS Hosts.'))),
          h('li', null, h('div', null, h('strong', null, 'Créez des comptes clients'), h('div', { class: 'muted' }, 'Menu « Administration » : chaque client gère ses PC indépendamment.'))),
          h('li', null, h('div', null, h('strong', null, 'Pilotez tout à distance'), h('div', { class: 'muted' }, 'Contrôle parental, blocages, confidentialité, fichier hosts…')))),
        h('div', { style: { height: '18px' } }),
        h('div', { class: 'row end' }, btn('Ouvrir la console', { kind: 'primary', big: true, onclick: () => go('#/') })));
    }
  }
  paint();
}

/* ============================== Connexion / inscription ============================== */

function viewLogin() {
  const email = h('input', { type: 'email', autocomplete: 'username', required: true });
  const pw = h('input', { type: 'password', autocomplete: 'current-password', required: true });
  const err = h('div', { class: 'banner danger hidden' });
  const submit = btn('Se connecter', { kind: 'primary', big: true, type: 'submit' });
  const form = h('form', null, field('Adresse e-mail', email), field('Mot de passe', pw), err, submit);
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    submit.classList.add('busy');
    try {
      await api('POST', '/api/auth/login', { email: email.value.trim(), password: pw.value });
      S.boot = null;
      go('#/');
    } catch (e) {
      clear(err).classList.remove('hidden');
      put(err, icon('alert'), h('div', null, e.message));
    } finally { submit.classList.remove('busy'); }
  });
  mountBare(h('div', { class: 'auth-card card' },
    h('div', { class: 'auth-logo' }, h('img', { src: '/static/logo.png', alt: '' }), h('h1', null, S.boot.server_name),
      h('p', { class: 'muted' }, 'Administration à distance de HOTS Hosts')),
    form,
    S.boot.registration_open ? h('p', { class: 'muted small', style: { 'margin-top': '16px', 'text-align': 'center' } },
      'Pas encore de compte ? ', h('a', { href: '#/register' }, 'Créer un compte')) : null));
  setTimeout(() => email.focus(), 30);
}

function viewRegister() {
  const fields = {
    account_name: h('input', { type: 'text', placeholder: 'Ex. : Famille Martin' }),
    name: h('input', { type: 'text', autocomplete: 'name' }),
    email: h('input', { type: 'email', autocomplete: 'email' }),
    password: h('input', { type: 'password', autocomplete: 'new-password' }),
  };
  const err = h('div', { class: 'banner danger hidden' });
  const submit = btn('Créer mon compte', { kind: 'primary', big: true, type: 'submit' });
  const form = h('form', null,
    field('Nom du compte (famille, entreprise…)', fields.account_name), field('Votre nom', fields.name),
    field('Adresse e-mail', fields.email), field('Mot de passe', fields.password, 'Au moins 10 caractères.'),
    passwordMeter(fields.password), h('div', { style: { height: '12px' } }), err, submit);
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    try {
      const body = {};
      for (const [k, el] of Object.entries(fields)) body[k] = el.value.trim();
      body.password = fields.password.value;
      await api('POST', '/api/auth/register', body);
      S.boot = null;
      go('#/');
    } catch (e) {
      clear(err).classList.remove('hidden');
      put(err, icon('alert'), h('div', null, e.message));
    }
  });
  mountBare(h('div', { class: 'auth-card card' },
    h('div', { class: 'auth-logo' }, h('img', { src: '/static/logo.png', alt: '' }), h('h1', null, 'Créer un compte')),
    form, h('p', { class: 'muted small', style: { 'margin-top': '16px', 'text-align': 'center' } },
      'Déjà inscrit ? ', h('a', { href: '#/login' }, 'Se connecter'))));
}

/* ============================== Tableau de bord ============================== */

function statusDot(d) {
  if (d.uninstalled_at) return h('span', { class: 'dot gone', title: 'Désinstallé' });
  return h('span', { class: `dot ${d.online ? 'on' : 'off'}`, title: d.online ? 'En ligne' : 'Hors ligne' });
}

function statusText(d) {
  if (d.uninstalled_at) return `HOTS Hosts désinstallé ${fmtAgo(d.uninstalled_at)}`;
  if (d.online) return 'En ligne';
  return d.last_seen ? `Hors ligne · vu ${fmtAgo(d.last_seen)}` : 'En attente de la première connexion';
}

function summaryBadges(sum) {
  if (!sum) return [badge('État inconnu', '', 'clock')];
  const out = [];
  out.push(badge(`${sum.categories_active}/${sum.categories_total} catégories`, sum.categories_active ? 'accent' : '', 'smile'));
  if (sum.cf_family) out.push(badge('DNS familial', 'ok', 'shield'));
  if (sum.netblock) out.push(badge('Internet coupé', 'danger', 'wifioff'));
  if (sum.hosts_lock) out.push(badge('Hosts verrouillé', 'ok', 'lock'));
  if (sum.apps_blocked) out.push(badge(`${sum.apps_blocked} appli(s) bloquée(s)`, 'info', 'apps'));
  if (sum.privacy_total) out.push(badge(`Confidentialité ${sum.privacy_active}/${sum.privacy_total}`, sum.privacy_active ? 'ok' : '', 'eyeoff'));
  return out;
}

async function viewDashboard(_m, token) {
  const main = shell('devices', h('div', { class: 'loading' }, h('span', { class: 'spinner' }), 'Chargement des PC…'));
  const listBox = h('div');
  const paint = (devices) => {
    put(clear(main), 
      h('div', { class: 'page-head' },
        h('div', null, h('h1', null, 'Mes PC'), h('p', { class: 'muted' },
          devices.length ? `${devices.filter((d) => d.online).length} en ligne sur ${devices.length}` : 'Ajoutez un PC pour commencer.')),
        btn('Ajouter un PC', { kind: 'primary', icon: 'plus', onclick: () => addDeviceDialog(devices.length) })),
      listBox);
    clear(listBox);
    if (!devices.length) {
      put(listBox, h('div', { class: 'empty' },
        h('div', { class: 'icon-badge' }, icon('monitor')),
        h('h2', null, 'Aucun PC pour l\'instant'),
        h('p', null, 'Installez HOTS Hosts sur le PC à protéger et saisissez le code d\'ajout : il apparaîtra ici automatiquement.'),
        btn('Ajouter mon premier PC', { kind: 'primary', big: true, icon: 'plus', onclick: () => addDeviceDialog(0) })));
      return;
    }
    put(listBox, h('div', { class: 'grid cols-2' }, devices.map((d) =>
      h('a', { class: 'card pc-card', href: `#/pc/${d.id}` },
        h('div', { class: 'top' },
          h('div', { class: 'pc-icon' }, icon('monitor'), statusDot(d)),
          h('div', { class: 'spacer' }, h('div', { class: 'name' }, d.name),
            h('div', { class: 'meta' }, statusText(d)),
            h('div', { class: 'meta' }, d.os || '')),
          d.pending_commands ? badge(`${d.pending_commands} en attente`, 'warn', 'clock') : null),
        h('div', { class: 'badges' }, summaryBadges(d.summary))))));
  };
  const load = async () => {
    const { devices } = await api('GET', '/api/devices');
    if (token === S.navToken) paint(devices);
  };
  await load();
  every(15000, () => load().catch(() => {}));
}

async function addDeviceDialog(knownCount) {
  let code;
  try {
    // Réutilise un code « multi-PC » encore valide plusieurs jours plutôt que d'en créer un à chaque fois.
    const { codes } = await api('GET', '/api/enroll-codes');
    code = codes.find((c) => c.valid && !c.label && c.max_uses === null && c.expires_at > Date.now() / 1000 + 3 * 86400);
    if (!code) code = await api('POST', '/api/enroll-codes', { label: '', days: 7 });
  } catch (e) { return showError(e); }
  const origin = location.origin;
  const detected = h('div');
  const body = h('div', null,
    h('ol', { class: 'howto' },
      h('li', null, h('div', null, h('strong', null, 'Téléchargez HOTS Hosts sur le PC à protéger'),
        h('div', { class: 'muted small' }, 'Installateur Windows officiel de cette console.'),
        h('div', { style: { 'margin-top': '8px' } }, btn('Télécharger l\'installateur', { kind: 'primary', icon: 'download', href: S.boot.download_url, target: '_blank' })))),
      h('li', null, h('div', null, h('strong', null, 'Lancez l\'installation et, à l\'étape « Administration à distance », saisissez :'),
        h('div', { class: 'small muted', style: { 'margin-top': '8px' } }, 'Adresse de la console'), copyBox(origin),
        h('div', { class: 'small muted', style: { 'margin-top': '10px' } }, `Code d'ajout — valable jusqu'au ${fmtDate(code.expires_at)}, utilisable pour plusieurs PC`),
        copyBox(code.code, 'code'))),
      h('li', null, h('div', null, h('strong', null, 'C\'est tout !'),
        h('div', { class: 'muted small' }, 'Le PC apparaît ici dans les secondes qui suivent la fin de l\'installation.'), detected))),
    h('details', null, h('summary', null, 'HOTS Hosts est déjà installé sur ce PC ?'),
      h('p', { class: 'small' }, 'Ouvrez HOTS Hosts sur le PC, puis ', h('strong', null, 'Options → Administration à distance'),
        ', et saisissez la même adresse et le même code. Vous pouvez aussi relancer l\'installateur : il met à jour le programme sans rien perdre.')),
    h('details', null, h('summary', null, 'Déploiement silencieux (plusieurs PC, informaticiens)'),
      h('pre', null, `HOTS_Hosts_setup.exe /VERYSILENT /SERVER=${origin} /CODE=${code.code}`)));
  const timer = setInterval(async () => {
    try {
      const { devices } = await api('GET', '/api/devices');
      if (devices.length > knownCount) {
        const newest = devices.slice().sort((a, b) => b.enrolled_at - a.enrolled_at)[0];
        put(clear(detected), banner('ok', 'check', h('p', null, h('strong', null, `Nouveau PC détecté : ${newest.name}`))));
        knownCount = devices.length;
      }
    } catch (e) { /* ignoré */ }
  }, 3000);
  await modal({ title: 'Ajouter un PC', iconName: 'plus', wide: true, body, actions: [{ label: 'Terminé', kind: 'primary', value: true }], onclose: () => clearInterval(timer) });
  render();
}

/* ============================== Détail d'un PC ============================== */

const TABS = [
  ['parental', 'smile', 'Contrôle parental'],
  ['protections', 'shield', 'Protections'],
  ['apps', 'apps', 'Applications'],
  ['privacy', 'eyeoff', 'Confidentialité'],
  ['hosts', 'file', 'Fichier hosts'],
  ['tools', 'tool', 'Outils'],
  ['journal', 'list', 'Journal'],
];

const STATUS_LABELS = {
  pending: ['En attente', 'warn'], sent: ['En cours', 'info'], done: ['Effectuée', 'ok'],
  error: ['Échec', 'danger'], expired: ['Expirée', 'danger'], cancelled: ['Annulée', ''],
};

async function viewDevice([id, tab], token) {
  tab = TABS.some((t) => t[0] === tab) ? tab : 'parental';
  const ctx = { id, tab, device: null, dirty: false, token };
  const main = shell('devices', h('div', { class: 'loading' }, h('span', { class: 'spinner' }), 'Chargement…'));
  const headBox = h('div');
  const tabBox = h('div');

  ctx.reload = async () => {
    ctx.device = await api('GET', `/api/devices/${id}`);
    if (token !== S.navToken) return;
    paintHead();
    ctx.dirty = false;
    await paintTab();
  };

  /** Envoie une commande au PC et attend le résultat (ou la programme s'il est hors ligne). */
  ctx.exec = async (action, params, summary, { quiet = false, reload = true } = {}) => {
    const d = ctx.device;
    if (!d.online) {
      if (READ_ONLY.has(action)) { toast('Le PC est hors ligne : réessayez quand il sera allumé.', 'error'); return null; }
      const ok = await confirmDialog(`« ${d.name} » est hors ligne. La modification sera appliquée automatiquement dès qu'il se reconnectera.`,
        { title: 'PC hors ligne', ok: 'Programmer', iconName: 'clock' });
      if (!ok) return null;
    }
    let cmd = await api('POST', `/api/devices/${id}/commands`, { action, params: params || {}, summary: summary || '' });
    if (!d.online) {
      toast(`Programmé : ${summary || action}`, 'info');
      paintHead();
      return cmd;
    }
    const deadline = Date.now() + 150000;
    while (!TERMINAL.includes(cmd.status) && Date.now() < deadline && token === S.navToken) {
      cmd = await api('GET', `/api/commands/${cmd.id}?wait=25`);
    }
    if (cmd.status === 'done') {
      if (!quiet) toast(summary ? `${summary} : effectué` : 'Effectué', 'ok');
      if (reload && !READ_ONLY.has(action)) await ctx.reload();
    } else if (cmd.status === 'error' || cmd.status === 'expired') {
      toast(cmd.error || 'Le PC a signalé une erreur.', 'error');
      if (reload && !READ_ONLY.has(action)) await ctx.reload();
    } else {
      toast('Le PC n\'a pas encore répondu : la commande reste en file d\'attente.', 'info');
    }
    return cmd;
  };

  function paintHead() {
    const d = ctx.device;
    put(clear(headBox), 
      h('a', { class: 'back', href: '#/' }, icon('back'), 'Tous mes PC'),
      h('div', { class: 'device-head' },
        h('div', { class: 'pc-icon' }, icon('monitor'), statusDot(d)),
        h('div', { class: 'spacer' }, h('h1', null, d.name),
          h('div', { class: 'muted' }, statusText(d), d.os ? ` · ${d.os}` : '', d.hostname && d.hostname !== d.name ? ` · ${d.hostname}` : '')),
        d.pending_commands ? badge(`${d.pending_commands} commande(s) en attente`, 'warn', 'clock') : null,
        btn('Actualiser', {
          icon: 'refresh', disabled: !d.online, title: d.online ? 'Relire l\'état du PC' : 'PC hors ligne',
          onclick: async () => { await ctx.exec('get_state', {}, 'Actualisation de l\'état', { quiet: true }); await ctx.reload(); },
        })),
      d.uninstalled_at ? banner('danger', 'alert', h('p', null, 'HOTS Hosts a été désinstallé de ce PC. Vous pouvez le retirer de la console (onglet Outils).')) : null,
      !d.online && !d.uninstalled_at ? banner('warn', 'clock', h('p', null,
        'Ce PC est hors ligne (éteint ou sans Internet). Vous voyez son dernier état connu ',
        d.state_at ? `(${fmtAgo(d.state_at)})` : '', '. Les modifications seront appliquées à sa prochaine connexion.')) : null,
      h('nav', { class: 'tabs' }, TABS.map(([key, ic, label]) =>
        h('a', { href: `#/pc/${id}/${key}`, class: key === tab ? 'active' : null }, icon(ic), label))));
  }

  async function paintTab() {
    const state = ctx.device.state;
    clear(tabBox);
    const needsState = !['tools', 'journal', 'hosts'].includes(tab);
    if (needsState && !state) {
      put(tabBox, banner('info', 'clock', h('p', null, 'Aucune donnée reçue de ce PC pour l\'instant. Elles arrivent dès sa première connexion.')));
      return;
    }
    if (state && state.errors && Object.keys(state.errors).length && needsState) {
      put(tabBox, banner('warn', 'alert', h('p', null, 'Certaines informations n\'ont pas pu être lues sur le PC : ',
        Object.keys(state.errors).join(', '))));
    }
    await TAB_RENDERERS[tab](ctx, tabBox);
  }

  ctx.device = await api('GET', `/api/devices/${id}`);
  if (token !== S.navToken) return;
  put(clear(main), headBox, tabBox);
  paintHead();
  await paintTab();

  every(10000, async () => {
    try {
      const fresh = await api('GET', `/api/devices/${id}`);
      if (token !== S.navToken) return;
      const stateChanged = fresh.state_at !== ctx.device.state_at;
      const statusChanged = fresh.online !== ctx.device.online || fresh.pending_commands !== ctx.device.pending_commands;
      ctx.device = fresh;
      if (statusChanged || stateChanged) paintHead();
      if (stateChanged && !ctx.dirty && !['hosts', 'journal'].includes(tab)) await paintTab();
    } catch (e) { /* ignoré : nouvel essai au prochain tour */ }
  });
}

const READ_ONLY = new Set(['agent.ping', 'get_state', 'hosts.read', 'hosts.backups', 'apps.list_installed', 'privacy.check_drift']);

/* ---------- Onglet : contrôle parental ---------- */

function tabParental(ctx, box) {
  const st = ctx.device.state;
  const p = st.parental || { categories: [] };
  const cats = p.categories || [];
  const active = cats.filter((c) => c.active).length;

  const grid = h('div', { class: 'grid cats' }, cats.map((c) =>
    h('div', { class: `cat${c.active ? ' on' : ''}`, style: { '--cat-color': /^#[0-9a-f]{3,8}$/i.test(c.color || '') ? c.color : 'var(--accent)' } },
      h('div', { class: 'emoji', 'aria-hidden': 'true' }, c.icon || '•'),
      h('div', { class: 'label' }, c.label, h('small', null, c.active ? 'Bloqué' : 'Autorisé')),
      switchEl(c.active, async (on) => {
        const r = await ctx.exec('parental.set', { category: c.file, enabled: on }, `${on ? 'Bloquer' : 'Débloquer'} ${c.label}`);
        return r && r.status === 'done';
      }, { disabled: !c.available, label: c.label }))));

  const cf = st.cf_family || {};
  const custom = p.custom || { domains: [] };
  const ta = h('textarea', { rows: 8, placeholder: 'exemple.com\njeux-en-ligne.fr\n…', value: (custom.domains || []).join('\n') });
  ta.addEventListener('input', () => { ctx.dirty = true; });

  put(box, h('div', { class: 'stack' },
    card(`Sites bloqués par catégorie — ${active}/${cats.length} actives`, 'smile',
      'Le blocage s\'applique à tout le PC (tous les navigateurs et applications), via le fichier hosts.', grid),
    card('Filtre DNS familial', 'shield', 'Cloudflare Family (1.1.1.3) : bloque les contenus pour adultes et les sites malveillants au niveau du réseau.',
      settingRow(cf.active ? 'Activé' : 'Désactivé', cf.details ? `Serveurs DNS actuels : ${cf.details}` : null,
        switchEl(!!cf.active, async (on) => {
          if (on && !(await confirmDialog('Le filtre DNS remplace le blocage « adultes » du fichier hosts, qui sera désactivé. Continuer ?', { ok: 'Activer' }))) return false;
          const r = await ctx.exec('cf_family.set', { enabled: on }, `${on ? 'Activer' : 'Désactiver'} le filtre DNS familial`);
          return r && r.status === 'done';
        }, { label: 'Filtre DNS familial' }))),
    card('Mes sites bloqués', 'edit', 'Un domaine par ligne (les adresses complètes sont acceptées : https://exemple.com/page devient exemple.com).',
      settingRow(custom.active ? 'Blocage actif' : 'Blocage inactif', `${(custom.domains || []).length} domaine(s) dans la liste`,
        switchEl(!!custom.active, async (on) => {
          const r = await ctx.exec('parental.set', { category: 'custom_domains.txt', enabled: on }, `${on ? 'Activer' : 'Désactiver'} mes sites bloqués`);
          return r && r.status === 'done';
        }, { disabled: !(custom.domains || []).length && !custom.active, label: 'Mes sites bloqués' })),
      ta, h('div', { class: 'row end', style: { 'margin-top': '10px' } },
        btn('Enregistrer la liste', {
          kind: 'primary', icon: 'check', onclick: async () => {
            const domains = ta.value.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
            await ctx.exec('custom_domains.set', { domains, apply: true }, `Mettre à jour mes sites bloqués (${domains.length})`);
          },
        })))));
}

/* ---------- Onglet : protections ---------- */

function tabProtections(ctx, box) {
  const st = ctx.device.state;
  const pr = st.protections || {};
  const sw = (key, action, label, confirmOn) => switchEl(!!pr[key], async (on) => {
    if (on && confirmOn && !(await confirmDialog(confirmOn, { ok: 'Activer' }))) return false;
    const r = await ctx.exec(action, { enabled: on }, `${on ? 'Activer' : 'Désactiver'} : ${label}`);
    return r && r.status === 'done';
  }, { label });

  const doh = (pr.doh || []).map((b) => settingRow(b.name,
    b.installed ? 'Installé sur ce PC' : 'Non détecté (la règle s\'appliquera s\'il est installé plus tard)',
    switchEl(!!b.blocked, async (on) => {
      const r = await ctx.exec('doh.set', { browser: b.id, enabled: on }, `${on ? 'Bloquer' : 'Autoriser'} le DNS sécurisé de ${b.name}`);
      return r && r.status === 'done';
    }, { label: b.name })));

  put(box, h('div', { class: 'grid cols-2' },
    card('Protections du PC', 'shield', null,
      settingRow('Verrouiller le fichier hosts', 'Empêche toute modification des blocages en dehors de HOTS Hosts (par un enfant ou un logiciel malveillant). Les changements faits depuis cette console restent possibles.',
        sw('hosts_lock', 'hosts_lock.set', 'verrou du fichier hosts')),
      settingRow('Bloquer les applications VPN', '10 VPN courants (NordVPN, ProtonVPN, Surfshark…) qui permettraient de contourner les filtres.',
        sw('vpn', 'vpn.set', 'blocage des VPN')),
      settingRow('Bloquer la restauration du système', 'Empêche d\'annuler les protections en restaurant Windows à une date antérieure.',
        sw('rstrui', 'rstrui_lock.set', 'blocage de la restauration du système'))),
    card('Couper Internet', 'wifioff', 'Coupe l\'accès à Internet de tout le PC (Wi-Fi et câble). Le réseau local reste accessible et la liaison avec cette console est préservée : vous pourrez rétablir Internet à distance.',
      settingRow(pr.netblock ? 'Internet est coupé' : 'Internet est accessible', null,
        sw('netblock', 'netblock.set', 'coupure d\'Internet', 'Couper l\'accès à Internet sur ce PC ? Vous pourrez le rétablir depuis cette console.')),
      pr.netblock ? banner('danger', 'wifioff', h('p', null, 'Internet est actuellement coupé sur ce PC.')) : null),
    card('DNS sécurisé des navigateurs (DoH)', 'browser', 'Les navigateurs peuvent contourner le fichier hosts grâce au « DNS sécurisé ». Bloquez-le pour que les filtres s\'appliquent.', ...doh)));
}

/* ---------- Onglet : applications ---------- */

function tabApps(ctx, box) {
  const apps = ctx.device.state.apps || [];
  const exe = h('input', { type: 'text', placeholder: 'jeu.exe' });
  const label = h('input', { type: 'text', placeholder: 'Nom affiché (facultatif)' });
  const add = async (exeName, displayName, path) => {
    exeName = (exeName || '').trim();
    if (!exeName) return toast('Indiquez le nom du programme (ex. : jeu.exe).', 'error');
    await ctx.exec('apps.add', { exe_name: exeName, display_name: (displayName || '').trim(), path: path || '' }, `Bloquer ${displayName || exeName}`);
  };
  const catLabel = { vpn: ['VPN', 'info'], custom: ['Personnalisé', ''] };
  const rows = apps.map((a) => h('tr', { class: a.enabled ? null : 'off' },
    h('td', null, h('strong', null, a.display_name || a.exe_name), h('div', { class: 'mono small muted' }, a.exe_name)),
    h('td', null, badge(...(catLabel[a.category] || [a.category || '—', '']))),
    h('td', null, a.locked_path ? h('span', { class: 'small muted', title: a.locked_path }, 'Fichier verrouillé') : h('span', { class: 'small muted' }, '—')),
    h('td', null, switchEl(a.enabled, async (on) => {
      const r = await ctx.exec('apps.set_enabled', { exe_name: a.exe_name, enabled: on }, `${on ? 'Réactiver le blocage de' : 'Suspendre le blocage de'} ${a.display_name || a.exe_name}`);
      return r && r.status === 'done';
    }, { label: a.display_name || a.exe_name })),
    h('td', { class: 'actions' }, btn('', {
      kind: 'ghost', icon: 'trash', label: 'Retirer', onclick: async () => {
        if (await confirmDialog(`Autoriser à nouveau ${a.display_name || a.exe_name} ?`, { ok: 'Débloquer' })) {
          await ctx.exec('apps.remove', { exe_name: a.exe_name }, `Débloquer ${a.display_name || a.exe_name}`);
        }
      },
    }))));

  put(box, h('div', { class: 'stack' },
    card('Bloquer un programme', 'plus', 'Le programme ne pourra plus être lancé sur ce PC, par aucun utilisateur.',
      h('div', { class: 'inline-form' }, field('Nom du programme', exe), field('Nom affiché', label),
        btn('Bloquer', { kind: 'primary', icon: 'plus', onclick: async () => { await add(exe.value, label.value); } }),
        btn('Choisir parmi les programmes installés', { icon: 'search', onclick: () => installedDialog(ctx, add) }))),
    card(`Programmes bloqués (${apps.length})`, 'apps', null,
      apps.length ? h('div', { class: 'table-wrap' }, h('table', null,
        h('thead', null, h('tr', null, h('th', null, 'Programme'), h('th', null, 'Type'), h('th', null, 'Fichier'), h('th', null, 'Bloqué'), h('th', null, ''))),
        h('tbody', null, rows)))
        : h('p', { class: 'muted' }, 'Aucun programme bloqué.'))));
}

async function installedDialog(ctx, add) {
  const r = await ctx.exec('apps.list_installed', {}, 'Liste des programmes installés', { quiet: true });
  if (!r || r.status !== 'done') return;
  const programs = (r.result && r.result.programs) || [];
  const search = h('input', { type: 'search', placeholder: 'Rechercher…' });
  const list = h('div', { class: 'table-wrap' });
  const paint = () => {
    const q = search.value.toLowerCase();
    const rows = programs.filter((p) => !q || p.name.toLowerCase().includes(q) || p.exe.toLowerCase().includes(q)).slice(0, 300);
    put(clear(list), h('table', null, h('tbody', null, rows.map((p) => h('tr', null,
      h('td', null, h('strong', null, p.name), h('div', { class: 'mono small muted' }, p.path)),
      h('td', { class: 'actions' }, btn('Bloquer', {
        small: true, kind: 'primary', onclick: async () => {
          list.closest('.modal')._close(true);
          await add(p.exe, p.name, p.path);
        },
      })))))));
  };
  search.addEventListener('input', paint);
  paint();
  await modal({ title: `Programmes installés (${programs.length})`, iconName: 'apps', wide: true, body: h('div', null, search, h('div', { style: { height: '10px' } }), list), actions: [{ label: 'Fermer', value: null }] });
}

/* ---------- Onglet : confidentialité ---------- */

function tabPrivacy(ctx, box) {
  const st = ctx.device.state;
  const levels = (st.privacy && st.privacy.levels) || [];
  const tel = (st.parental && st.parental.telemetry) || null;
  put(box, banner('info', 'info', h('p', null,
    'Réduit la télémétrie et le pistage de Windows. Les réglages marqués « session utilisateur » se modifient depuis l\'application sur le PC.')));
  const tools = h('div', { class: 'row', style: { 'margin-bottom': '16px' } },
    btn('Vérifier les réglages annulés par Windows', {
      icon: 'search', onclick: async () => {
        const r = await ctx.exec('privacy.check_drift', {}, 'Vérification des réglages de confidentialité', { quiet: true });
        if (r && r.status === 'done') {
          const reg = r.result.regressed || [];
          toast(reg.length ? `${reg.length} réglage(s) ont été annulés par Windows : réactivez-les.` : 'Aucun réglage annulé : tout est en place.', reg.length ? 'error' : 'ok', 7000);
          await ctx.reload();
        }
      },
    }),
    btn('Créer un point de restauration', {
      icon: 'history', onclick: async () => {
        const r = await ctx.exec('system.restore_point', {}, 'Création d\'un point de restauration', { quiet: true });
        if (r && r.status === 'done') toast(r.result.status === 'created' ? 'Point de restauration créé.' : r.result.message, r.result.status === 'created' ? 'ok' : 'info', 7000);
      },
    }));
  put(box, tools);
  if (tel) {
    put(box, h('div', { style: { 'margin-bottom': '16px' } }, card('Domaines de télémétrie', 'globe', 'Bloque les serveurs de télémétrie de Microsoft via le fichier hosts.',
      settingRow(tel.active ? 'Bloqués' : 'Autorisés', null, switchEl(!!tel.active, async (on) => {
        const r = await ctx.exec('parental.set', { category: tel.file, enabled: on }, `${on ? 'Bloquer' : 'Autoriser'} les domaines de télémétrie`);
        return r && r.status === 'done';
      }, { label: 'Domaines de télémétrie' })))));
  }
  put(box, h('div', { class: 'stack' }, levels.map((lvl) => {
    const machine = lvl.items.filter((i) => !i.user_scope && !i.missing);
    const on = machine.filter((i) => i.active).length;
    return card(`${lvl.label} — ${on}/${machine.length} actifs`, 'eyeoff', null,
      h('div', { class: 'row end', style: { 'margin-top': '-6px' } },
        btn('Tout activer', { small: true, onclick: () => ctx.exec('privacy.set_level', { level: lvl.id, enabled: true }, `Confidentialité : activer le niveau ${lvl.label}`) }),
        btn('Tout désactiver', { small: true, onclick: () => ctx.exec('privacy.set_level', { level: lvl.id, enabled: false }, `Confidentialité : désactiver le niveau ${lvl.label}`) })),
      lvl.items.map((it) => settingRow(it.label, it.desc,
        it.user_scope ? badge('Session utilisateur', '', 'user')
          : it.missing ? badge('Absent sur ce PC', '')
            : switchEl(!!it.active, async (v) => {
              const r = await ctx.exec('privacy.set_item', { id: it.id, enabled: v }, `${v ? 'Activer' : 'Désactiver'} : ${it.label}`);
              return r && r.status === 'done';
            }, { label: it.label }))));
  })));
}

/* ---------- Onglet : fichier hosts ---------- */

async function tabHosts(ctx, box) {
  if (!ctx.device.online) {
    put(box, banner('warn', 'clock', h('p', null, 'Le fichier hosts se consulte en direct : ce PC doit être en ligne.')));
    return;
  }
  put(box, h('div', { class: 'loading' }, h('span', { class: 'spinner' }), 'Lecture du fichier hosts sur le PC…'));
  const r = await ctx.exec('hosts.read', {}, 'Lecture du fichier hosts', { quiet: true });
  if (!r || r.status !== 'done') { put(clear(box), banner('danger', 'alert', h('p', null, (r && r.error) || 'Lecture impossible.'))); return; }
  const data = r.result;
  let sub = 'entries';
  const content = h('div');
  const reread = async () => { await paintTabAgain(); };
  const paintTabAgain = async () => { clear(box); await tabHosts(ctx, box); };

  const exec = async (action, params, summary) => {
    const res = await ctx.exec(action, params, summary, { reload: false });
    if (res && (res.status === 'done' || res.status === 'error')) await reread();
  };

  function entriesView() {
    const search = h('input', { type: 'search', placeholder: 'Filtrer (domaine, IP, commentaire)…' });
    let limit = 200;
    const tableBox = h('div');
    const paint = () => {
      const q = search.value.toLowerCase().trim();
      const list = data.entries.filter((e) => !q || e.hostname.toLowerCase().includes(q) || e.ip.includes(q) || (e.comment || '').toLowerCase().includes(q));
      const shown = list.slice(0, limit);
      put(clear(tableBox), 
        h('p', { class: 'muted small' }, `${list.length} entrée(s)${q ? ' correspondante(s)' : ''}`),
        h('div', { class: 'table-wrap' }, h('table', null,
          h('thead', null, h('tr', null, h('th', null, 'Active'), h('th', null, 'Adresse IP'), h('th', null, 'Nom d\'hôte'), h('th', null, 'Commentaire'), h('th', null, ''))),
          h('tbody', null, shown.map((e) => h('tr', { class: e.enabled ? null : 'off' },
            h('td', null, switchEl(e.enabled, async (on) => {
              await exec('hosts.update_entry', { line: e.line, expect: e.raw, enabled: on }, `${on ? 'Activer' : 'Désactiver'} l'entrée ${e.hostname}`);
              return false;
            }, { label: e.hostname })),
            h('td', { class: 'mono' }, e.ip), h('td', { class: 'mono' }, e.hostname), h('td', { class: 'small muted' }, e.comment || ''),
            h('td', { class: 'actions' },
              btn('', { kind: 'ghost', icon: 'edit', label: 'Modifier', onclick: () => editEntry(e) }),
              btn('', {
                kind: 'ghost', icon: 'trash', label: 'Supprimer', onclick: async () => {
                  if (await confirmDialog(`Supprimer l'entrée « ${e.ip} ${e.hostname} » ?`, { ok: 'Supprimer', danger: true })) {
                    await exec('hosts.delete_entry', { line: e.line, expect: e.raw }, `Supprimer l'entrée ${e.hostname}`);
                  }
                },
              }))))))),
        list.length > limit ? h('div', { class: 'row end', style: { 'margin-top': '10px' } }, btn(`Afficher plus (${list.length - limit} restantes)`, { onclick: () => { limit += 500; paint(); } })) : null);
    };
    search.addEventListener('input', () => { limit = 200; paint(); });
    paint();
    return h('div', null,
      h('div', { class: 'row', style: { 'margin-bottom': '12px' } }, h('div', { class: 'spacer' }, search),
        btn('Ajouter une entrée', { kind: 'primary', icon: 'plus', onclick: () => editEntry(null) })),
      tableBox);
  }

  function editEntry(e) {
    return formDialog({
      title: e ? 'Modifier l\'entrée' : 'Ajouter une entrée', iconName: 'edit',
      intro: h('p', { class: 'muted small' }, 'Pour bloquer un site, utilisez l\'adresse 0.0.0.0.'),
      fields: [
        { name: 'ip', label: 'Adresse IP', value: e ? e.ip : '0.0.0.0' },
        { name: 'hostname', label: 'Nom d\'hôte', value: e ? e.hostname : '', placeholder: 'exemple.com' },
        { name: 'comment', label: 'Commentaire (facultatif)', value: e ? e.comment : '' },
      ],
      submit: async (v) => {
        if (!v.hostname.trim()) throw new Error('Le nom d\'hôte est obligatoire.');
        const params = { ip: v.ip.trim(), hostname: v.hostname.trim(), comment: v.comment.trim() };
        setTimeout(() => exec(e ? 'hosts.update_entry' : 'hosts.add_entry', e ? { ...params, line: e.line, expect: e.raw } : params,
          `${e ? 'Modifier' : 'Ajouter'} l'entrée ${params.hostname}`), 0);
      },
    });
  }

  function rawView() {
    if (data.text === null) return banner('warn', 'alert', h('p', null, 'Fichier trop volumineux pour l\'édition en texte brut.'));
    const ta = h('textarea', { rows: 24, value: data.text, spellcheck: 'false' });
    ta.addEventListener('input', () => { ctx.dirty = true; });
    return h('div', null, ta, h('div', { class: 'row end', style: { 'margin-top': '10px' } },
      btn('Annuler les modifications', { onclick: () => { ta.value = data.text; ctx.dirty = false; } }),
      btn('Enregistrer le fichier', {
        kind: 'primary', icon: 'check', onclick: async () => {
          if (!(await confirmDialog('Remplacer le fichier hosts du PC par ce contenu ? Une sauvegarde est créée automatiquement.', { ok: 'Enregistrer' }))) return;
          await exec('hosts.save_text', { text: ta.value, expect_sha256: data.sha256 }, 'Enregistrement du fichier hosts (texte brut)');
        },
      })));
  }

  async function backupsView() {
    const holder = h('div', null, h('div', { class: 'loading' }, h('span', { class: 'spinner' })));
    (async () => {
      const res = await ctx.exec('hosts.backups', {}, 'Liste des sauvegardes du fichier hosts', { quiet: true });
      clear(holder);
      if (!res || res.status !== 'done') { put(holder, banner('danger', 'alert', h('p', null, 'Lecture impossible.'))); return; }
      const list = res.result.backups || [];
      if (!list.length) { put(holder, h('p', { class: 'muted' }, 'Aucune sauvegarde pour l\'instant. Une sauvegarde est créée avant chaque modification.')); return; }
      put(holder, h('div', { class: 'table-wrap' }, h('table', null,
        h('thead', null, h('tr', null, h('th', null, 'Date'), h('th', null, 'Taille'), h('th', null, ''))),
        h('tbody', null, list.map((b) => h('tr', null,
          h('td', null, new Date(b.date).toLocaleString('fr-FR')), h('td', null, fmtSize(b.size)),
          h('td', { class: 'actions' }, btn('Restaurer', {
            small: true, icon: 'history', onclick: async () => {
              if (await confirmDialog(`Restaurer le fichier hosts tel qu'il était le ${new Date(b.date).toLocaleString('fr-FR')} ?`, { ok: 'Restaurer' })) {
                await exec('hosts.restore_backup', { name: b.name }, `Restaurer la sauvegarde du ${new Date(b.date).toLocaleString('fr-FR')}`);
              }
            },
          }))))))));
    })().catch(showError);
    return holder;
  }

  const subtabs = h('div', { class: 'subtabs' });
  const paintSub = async () => {
    put(clear(subtabs), ...[['entries', 'Entrées'], ['raw', 'Texte brut'], ['backups', 'Sauvegardes']].map(([k, l]) =>
      h('button', { type: 'button', class: k === sub ? 'active' : null, onclick: () => { sub = k; paintSub(); } }, l)));
    put(clear(content), sub === 'entries' ? entriesView() : sub === 'raw' ? rawView() : await backupsView());
  };
  put(clear(box), 
    h('div', { class: 'row', style: { 'margin-bottom': '12px' } },
      badge(`${data.entries.filter((e) => e.enabled).length} entrées actives`, 'accent'), badge(fmtSize(data.size)),
      data.locked ? badge('Verrouillé', 'ok', 'lock') : null,
      h('span', { class: 'muted small mono' }, data.path), h('div', { class: 'spacer' }),
      btn('Relire', { small: true, icon: 'refresh', onclick: reread })),
    data.locked ? banner('info', 'lock', h('p', null, 'Le fichier est verrouillé : HOTS Hosts le déverrouille brièvement pour chaque modification faite d\'ici, puis le reverrouille.')) : null,
    subtabs, content);
  await paintSub();
}

/* ---------- Onglet : outils ---------- */

function tabTools(ctx, box) {
  const d = ctx.device;
  const sys = (d.state && d.state.system) || {};
  const info = [
    ['Nom de l\'ordinateur', d.hostname || '—'], ['Windows', d.os || '—'],
    ['HOTS Hosts', d.app_version || '—'], ['Agent', d.agent_version || '—'],
    ['Allumé depuis', fmtUptime(sys.uptime_s)], ['Dernière connexion', d.last_seen ? `${fmtDate(d.last_seen)} (${fmtAgo(d.last_seen)})` : '—'],
    ['Adresse IP publique', d.last_ip || '—'], ['Ajouté à la console', fmtDate(d.enrolled_at)],
    ['État remonté', d.state_at ? fmtAgo(d.state_at) : '—'],
  ];
  const name = h('input', { type: 'text', value: d.name, maxlength: 80 });
  const notes = h('textarea', { rows: 3, value: d.notes || '', placeholder: 'Ex. : PC de Léa, chambre du haut' });
  [name, notes].forEach((el) => el.addEventListener('input', () => { ctx.dirty = true; }));
  put(box, h('div', { class: 'grid cols-2' },
    card('Informations', 'info', null, h('div', { class: 'table-wrap' }, h('table', null, h('tbody', null,
      info.map(([k, v]) => h('tr', null, h('th', { scope: 'row' }, k), h('td', null, v))))))),
    h('div', { class: 'stack' },
      card('Nom et notes', 'edit', null, field('Nom affiché dans la console', name), field('Notes', notes),
        h('div', { class: 'row end' }, btn('Enregistrer', {
          kind: 'primary', icon: 'check', onclick: async () => {
            await api('PATCH', `/api/devices/${d.id}`, { name: name.value.trim() || d.name, notes: notes.value });
            toast('Enregistré', 'ok');
            await ctx.reload();
          },
        }))),
      card('Actions rapides', 'zap', null,
        settingRow('Vider le cache DNS', 'Applique immédiatement les changements de blocage dans les navigateurs ouverts.',
          btn('Vider', { icon: 'zap', onclick: () => ctx.exec('dns.flush', {}, 'Vidage du cache DNS') })),
        settingRow('Point de restauration Windows', 'Permet de revenir en arrière en cas de problème.',
          btn('Créer', { icon: 'history', onclick: () => ctx.exec('system.restore_point', {}, 'Création d\'un point de restauration') }))),
      card('Retirer ce PC de la console', 'trash', 'Le PC ne sera plus administrable à distance. Ses protections restent actives sur le PC. Pour le réajouter, utilisez un nouveau code d\'ajout.',
        h('div', { class: 'row end' }, btn('Retirer de la console', {
          kind: 'danger', icon: 'trash', onclick: async () => {
            if (!(await confirmDialog(`Retirer « ${d.name} » de la console ?`, { ok: 'Retirer', danger: true }))) return;
            await api('DELETE', `/api/devices/${d.id}`);
            toast('PC retiré de la console', 'ok');
            go('#/');
          },
        }))))));
}

/* ---------- Onglet : journal ---------- */

async function tabJournal(ctx, box) {
  const { commands } = await api('GET', `/api/devices/${ctx.id}/commands?limit=150`);
  if (!commands.length) { put(box, h('p', { class: 'muted' }, 'Aucune action pour l\'instant.')); return; }
  put(box, h('div', { class: 'table-wrap' }, h('table', null,
    h('thead', null, h('tr', null, h('th', null, 'Date'), h('th', null, 'Action'), h('th', null, 'Par'), h('th', null, 'Statut'), h('th', null, ''))),
    h('tbody', null, commands.map((c) => {
      const [label, kind] = STATUS_LABELS[c.status] || [c.status, ''];
      return h('tr', null,
        h('td', { class: 'nowrap small', title: fmtDate(c.created_at) }, fmtAgo(c.created_at)),
        h('td', null, c.summary || c.action, c.error ? h('div', { class: 'small', style: { color: 'var(--danger)' } }, c.error) : null),
        h('td', { class: 'small muted' }, c.user || '—'),
        h('td', null, badge(label, kind), c.duration_ms != null && c.status === 'done' ? h('span', { class: 'small muted' }, ` ${(c.duration_ms / 1000).toFixed(1)} s`) : null),
        h('td', { class: 'actions' }, c.status === 'pending' ? btn('Annuler', {
          small: true, onclick: async () => { await api('POST', `/api/commands/${c.id}/cancel`); clear(box); await tabJournal(ctx, box); },
        }) : null));
    })))));
}

const TAB_RENDERERS = {
  parental: tabParental, protections: tabProtections, apps: tabApps, privacy: tabPrivacy,
  hosts: tabHosts, tools: tabTools, journal: tabJournal,
};

/* ============================== Mon compte ============================== */

async function viewAccount(_m, token) {
  const main = shell('account', h('div', { class: 'loading' }, h('span', { class: 'spinner' })));
  const [acc, codes, events] = await Promise.all([api('GET', '/api/account/users'), api('GET', '/api/enroll-codes'), api('GET', '/api/events')]);
  if (token !== S.navToken) return;
  const u = S.boot.user;
  const isOwner = u.role === 'owner' || u.is_superadmin;

  const name = h('input', { type: 'text', value: u.name || '' });
  const accountName = h('input', { type: 'text', value: acc.account.name, disabled: !isOwner });
  const cur = h('input', { type: 'password', autocomplete: 'current-password' });
  const pw1 = h('input', { type: 'password', autocomplete: 'new-password' });
  const pw2 = h('input', { type: 'password', autocomplete: 'new-password' });

  const usersTable = h('div', { class: 'table-wrap' }, h('table', null,
    h('thead', null, h('tr', null, h('th', null, 'Utilisateur'), h('th', null, 'Rôle'), h('th', null, 'Dernière connexion'), h('th', null, ''))),
    h('tbody', null, acc.users.map((x) => h('tr', null,
      h('td', null, h('strong', null, x.name || x.email), h('div', { class: 'small muted' }, x.email)),
      h('td', null, badge(x.role === 'owner' ? 'Responsable' : 'Membre', x.role === 'owner' ? 'accent' : '')),
      h('td', { class: 'small' }, fmtAgo(x.last_login)),
      h('td', { class: 'actions' }, isOwner && x.id !== u.id && !x.is_superadmin ? btn('', {
        kind: 'ghost', icon: 'trash', label: 'Retirer', onclick: async () => {
          if (await confirmDialog(`Retirer l'accès de ${x.email} ?`, { ok: 'Retirer', danger: true })) {
            await api('DELETE', `/api/account/users/${x.id}`); render();
          }
        },
      }) : null))))));

  const codeRows = codes.codes.map((c) => h('tr', null,
    h('td', { class: 'mono' }, h('strong', null, c.code)), h('td', null, c.label || '—'),
    h('td', { class: 'small' }, `${c.uses}${c.max_uses ? ` / ${c.max_uses}` : ''}`),
    h('td', { class: 'small' }, fmtDate(c.expires_at)),
    h('td', null, c.valid ? badge('Valide', 'ok') : badge(c.revoked ? 'Révoqué' : 'Expiré', '')),
    h('td', { class: 'actions' }, c.valid ? btn('Révoquer', { small: true, onclick: async () => { await api('DELETE', `/api/enroll-codes/${c.id}`); render(); } }) : null)));

  put(clear(main), 
    h('div', { class: 'page-head' }, h('div', null, h('h1', null, 'Mon compte'), h('p', { class: 'muted' }, acc.account.name))),
    h('div', { class: 'grid cols-2' },
      card('Profil', 'user', null, field('Votre nom', name), field('Nom du compte', accountName, isOwner ? null : 'Modifiable par le responsable du compte.'),
        h('div', { class: 'row end' }, btn('Enregistrer', {
          kind: 'primary', onclick: async () => {
            const body = { name: name.value.trim() };
            if (isOwner) body.account_name = accountName.value.trim() || acc.account.name;
            await api('POST', '/api/me/profile', body);
            S.boot = null; toast('Profil enregistré', 'ok'); render();
          },
        }))),
      card('Mot de passe', 'key', null, field('Mot de passe actuel', cur), field('Nouveau mot de passe', pw1, 'Au moins 10 caractères.'), passwordMeter(pw1),
        h('div', { style: { height: '12px' } }), field('Confirmation', pw2),
        h('div', { class: 'row end' }, btn('Changer le mot de passe', {
          kind: 'primary', onclick: async () => {
            if (pw1.value !== pw2.value) return toast('Les deux mots de passe ne correspondent pas.', 'error');
            await api('POST', '/api/me/password', { current: cur.value, new: pw1.value });
            cur.value = pw1.value = pw2.value = '';
            toast('Mot de passe modifié. Vos autres sessions ont été déconnectées.', 'ok');
          },
        })))),
    h('div', { style: { height: '16px' } }),
    card('Personnes ayant accès à ce compte', 'users', 'Par exemple l\'autre parent : chacun a son identifiant et voit les mêmes PC.',
      usersTable,
      isOwner ? h('div', { class: 'row end', style: { 'margin-top': '12px' } }, btn('Ajouter une personne', {
        icon: 'plus', onclick: () => formDialog({
          title: 'Ajouter une personne', iconName: 'users',
          fields: [
            { name: 'name', label: 'Nom' }, { name: 'email', label: 'Adresse e-mail', type: 'email' },
            { name: 'password', label: 'Mot de passe initial', type: 'password', help: 'Au moins 10 caractères. La personne pourra le changer.' },
            { name: 'role', label: 'Rôle', type: 'select', value: 'member', options: [['member', 'Membre (gère les PC)'], ['owner', 'Responsable (gère aussi les accès)']] },
          ],
          submit: async (v) => { await api('POST', '/api/account/users', v); toast('Accès ajouté', 'ok'); setTimeout(render, 0); },
        }),
      })) : null),
    h('div', { style: { height: '16px' } }),
    card('Codes d\'ajout de PC', 'key', 'Un code permet d\'ajouter un ou plusieurs PC à votre compte pendant sa durée de validité.',
      codeRows.length ? h('div', { class: 'table-wrap' }, h('table', null,
        h('thead', null, h('tr', null, h('th', null, 'Code'), h('th', null, 'Libellé'), h('th', null, 'Utilisations'), h('th', null, 'Expire le'), h('th', null, 'État'), h('th', null, ''))),
        h('tbody', null, codeRows))) : h('p', { class: 'muted' }, 'Aucun code récent.'),
      h('div', { class: 'row end', style: { 'margin-top': '12px' } }, btn('Nouveau code', {
        icon: 'plus', onclick: () => formDialog({
          title: 'Nouveau code d\'ajout', iconName: 'key',
          fields: [
            { name: 'label', label: 'Libellé (facultatif)', placeholder: 'PC de Léa' },
            { name: 'days', label: 'Validité', type: 'select', value: '7', options: [['1', '24 heures'], ['7', '7 jours'], ['30', '30 jours'], ['90', '90 jours']] },
            { name: 'single', label: 'Utilisable pour un seul PC', type: 'checkbox', value: false },
          ],
          submitLabel: 'Créer',
          submit: async (v) => {
            const c = await api('POST', '/api/enroll-codes', { label: v.label.trim(), days: Number(v.days), max_uses: v.single ? 1 : null });
            setTimeout(async () => {
              await modal({ title: 'Code créé', iconName: 'key', body: h('div', null, h('p', null, 'Adresse de la console :'), copyBox(location.origin), h('p', { style: { 'margin-top': '12px' } }, 'Code d\'ajout :'), copyBox(c.code, 'code')), actions: [{ label: 'OK', kind: 'primary', value: true }] });
              render();
            }, 0);
          },
        }),
      }))),
    h('div', { style: { height: '16px' } }),
    card('Journal d\'activité du compte', 'list', null,
      events.events.length ? h('div', { class: 'table-wrap' }, h('table', null,
        h('thead', null, h('tr', null, h('th', null, 'Date'), h('th', null, 'Événement'), h('th', null, 'Utilisateur'), h('th', null, 'Adresse IP'))),
        h('tbody', null, events.events.slice(0, 100).map((ev) => h('tr', null,
          h('td', { class: 'nowrap small', title: fmtDate(ev.created_at) }, fmtAgo(ev.created_at)),
          h('td', null, ev.message), h('td', { class: 'small muted' }, ev.user || ev.device || '—'), h('td', { class: 'small muted mono' }, ev.ip || '—'))))))
        : h('p', { class: 'muted' }, 'Aucun événement.')));
}

/* ============================== Administration du serveur ============================== */

function randomPassword() {
  const alphabet = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const values = crypto.getRandomValues(new Uint32Array(14));
  return Array.from(values, (v) => alphabet[v % alphabet.length]).join('');
}

async function viewAdmin(_m, token) {
  if (!S.boot.user.is_superadmin) return go('#/');
  const main = shell('admin', h('div', { class: 'loading' }, h('span', { class: 'spinner' })));
  const [{ accounts }, conf] = await Promise.all([api('GET', '/api/admin/accounts'), api('GET', '/api/admin/settings')]);
  if (token !== S.navToken) return;
  const totalPc = accounts.reduce((n, a) => n + a.devices, 0);
  const online = accounts.reduce((n, a) => n + a.online, 0);
  const stat = (value, label, ic) => h('div', { class: 'card stat' }, h('div', { class: 'icon-badge' }, icon(ic)), h('div', null, h('div', { class: 'value' }, value), h('div', { class: 'label' }, label)));

  const serverName = h('input', { type: 'text', value: conf.server_name });
  const downloadUrl = h('input', { type: 'url', value: conf.download_url });

  const rows = accounts.map((a) => h('tr', { class: a.suspended ? 'off' : null },
    h('td', null, h('strong', null, a.name), a.users.map((u) => h('div', { class: 'small muted' }, u.email, u.is_superadmin ? ' (vous)' : ''))),
    h('td', null, `${a.online} / ${a.devices}`, a.max_devices ? h('div', { class: 'small muted' }, `max ${a.max_devices}`) : null),
    h('td', { class: 'small' }, fmtDate(a.created_at)),
    h('td', null, a.suspended ? badge('Suspendu', 'danger') : badge('Actif', 'ok')),
    h('td', { class: 'actions' },
      btn('', {
        kind: 'ghost', icon: 'key', label: 'Réinitialiser un mot de passe', onclick: () => {
          const pw = randomPassword();
          return formDialog({
            title: `Nouveau mot de passe — ${a.name}`, iconName: 'key',
            fields: [
              { name: 'user', label: 'Utilisateur', type: 'select', value: String(a.users[0].id), options: a.users.map((u) => [String(u.id), u.email]) },
              { name: 'password', label: 'Nouveau mot de passe', value: pw, help: 'Communiquez-le à la personne ; elle pourra le changer dans « Mon compte ».' },
            ],
            submit: async (v) => { await api('POST', `/api/admin/users/${v.user}/password`, { password: v.password }); toast('Mot de passe modifié', 'ok'); },
          });
        },
      }),
      btn('', {
        kind: 'ghost', icon: 'sliders', label: 'Limite de PC', onclick: () => formDialog({
          title: `Limite de PC — ${a.name}`, iconName: 'sliders',
          fields: [{ name: 'max', label: 'Nombre maximal de PC (vide = illimité)', type: 'number', value: a.max_devices ?? '' }],
          submit: async (v) => { await api('PATCH', `/api/admin/accounts/${a.id}`, { max_devices: v.max ? Number(v.max) : null }); setTimeout(render, 0); },
        }),
      }),
      a.users.some((u) => u.is_superadmin) ? null : btn(a.suspended ? 'Réactiver' : 'Suspendre', {
        small: true, onclick: async () => {
          if (!a.suspended && !(await confirmDialog(`Suspendre « ${a.name} » ? Ses utilisateurs ne pourront plus se connecter ; ses PC gardent leurs protections.`, { ok: 'Suspendre', danger: true }))) return;
          await api('PATCH', `/api/admin/accounts/${a.id}`, { suspended: !a.suspended }); render();
        },
      }),
      a.users.some((u) => u.is_superadmin) ? null : btn('', {
        kind: 'ghost', icon: 'trash', label: 'Supprimer', onclick: async () => {
          if (await confirmDialog(`Supprimer définitivement le compte « ${a.name} », ses utilisateurs et ses ${a.devices} PC ? Les PC ne seront plus administrables (leurs protections restent en place).`, { ok: 'Supprimer', danger: true })) {
            await api('DELETE', `/api/admin/accounts/${a.id}`); render();
          }
        },
      }))));

  put(clear(main), 
    h('div', { class: 'page-head' },
      h('div', null, h('h1', null, 'Administration du serveur'), h('p', { class: 'muted' }, 'Comptes clients et réglages. Chaque client ne voit que ses propres PC.')),
      btn('Nouveau client', {
        kind: 'primary', icon: 'plus', onclick: () => formDialog({
          title: 'Nouveau compte client', iconName: 'users',
          fields: [
            { name: 'account_name', label: 'Nom du compte', placeholder: 'Famille Martin / Entreprise X' },
            { name: 'name', label: 'Nom du contact' },
            { name: 'email', label: 'E-mail (identifiant de connexion)', type: 'email' },
            { name: 'password', label: 'Mot de passe initial', value: randomPassword(), help: 'Communiquez-le au client ; il pourra le changer.' },
            { name: 'max_devices', label: 'Nombre maximal de PC (vide = illimité)', type: 'number' },
          ],
          submitLabel: 'Créer le compte',
          submit: async (v) => {
            await api('POST', '/api/admin/accounts', { ...v, max_devices: v.max_devices ? Number(v.max_devices) : null });
            setTimeout(async () => {
              await modal({
                title: 'Compte créé', iconName: 'check',
                body: h('div', null, h('p', null, 'Transmettez ces informations au client :'),
                  copyBox(`Console : ${location.origin}\nIdentifiant : ${v.email}\nMot de passe : ${v.password}`)),
                actions: [{ label: 'OK', kind: 'primary', value: true }],
              });
              render();
            }, 0);
          },
        }),
      })),
    h('div', { class: 'grid cols-3' }, stat(accounts.length, 'comptes clients', 'users'), stat(totalPc, 'PC administrés', 'monitor'), stat(online, 'PC en ligne', 'globe')),
    h('div', { style: { height: '16px' } }),
    card('Comptes clients', 'users', null, h('div', { class: 'table-wrap' }, h('table', null,
      h('thead', null, h('tr', null, h('th', null, 'Compte'), h('th', null, 'PC en ligne'), h('th', null, 'Créé le'), h('th', null, 'État'), h('th', null, ''))),
      h('tbody', null, rows)))),
    h('div', { style: { height: '16px' } }),
    card('Réglages', 'sliders', null,
      field('Nom de la console', serverName),
      field('Lien de téléchargement de l\'installateur', downloadUrl, 'Par défaut : la dernière version publiée sur GitHub.'),
      settingRow('Inscription libre', 'Toute personne connaissant l\'adresse peut créer son propre compte client.',
        switchEl(conf.registration_open, async (on) => { await api('PATCH', '/api/admin/settings', { registration_open: on }); toast('Réglage enregistré', 'ok'); return true; }, { label: 'Inscription libre' })),
      h('div', { class: 'row end' }, btn('Enregistrer', {
        kind: 'primary', onclick: async () => {
          await api('PATCH', '/api/admin/settings', { server_name: serverName.value.trim() || conf.server_name, download_url: downloadUrl.value.trim() });
          S.boot = null; toast('Réglages enregistrés', 'ok'); render();
        },
      })),
      h('p', { class: 'muted small' }, `Version du serveur : ${conf.version}`)));
}

/* ============================== Démarrage ============================== */

window.addEventListener('hashchange', render);
render();
