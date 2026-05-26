// game-base.js — Steam Manager v4

const $ = id => document.getElementById(id);

// ── Restaurar sesión desde localStorage ──────────────────────────────────────
const SESSION_KEY = 'steam_session';
function loadSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (Date.now() > data.expires) { localStorage.removeItem(SESSION_KEY); return null; }
    return data;
  } catch { return null; }
}
const session = loadSession();
const userName = session ? session.email : 'Invitado';

// ── Nombre del juego ──────────────────────────────────────────────────────────
const _gameName = typeof GAME_NAME !== 'undefined' ? GAME_NAME : 'Juego';
if ($('gameName')) $('gameName').textContent = _gameName;
document.title = _gameName + ' — Steam Manager';

// ── Estado de la partida ──────────────────────────────────────────────────────
let startTs = null;
let totalMinutes = 0;

// ── UI de sesión ──────────────────────────────────────────────────────────────
function setStatus(text, type = 'info') {
  const el = $('sessionMsg');
  if (!el) return;
  el.textContent = text;
  el.dataset.type = type;
}

function resetSessionUI() {
  const running = Boolean(startTs);
  if ($('startBtn')) $('startBtn').disabled = running;
  if ($('endBtn'))   $('endBtn').disabled   = !running;
}

// ── Stub de compatibilidad con game-utils ────────────────────────────────────
function save() {}
function createGameState(n, d = {}) { return { totalMinutes, loginCount: 0, lastPlayedAt: null, ...d }; }
function loadGameState(n) { return createGameState(n); }
function saveGameState(n, p = {}) { return { ...createGameState(n), ...p }; }

const rec = createGameState(_gameName);

// ── Botón Iniciar ─────────────────────────────────────────────────────────────
if ($('startBtn')) {
  $('startBtn').onclick = () => {
    if (startTs) return;
    startTs = Date.now();
    rec.loginCount++;
    rec.lastPlayedAt = new Date().toISOString();
    setStatus(`Jugando como ${userName}`, 'success');
    resetSessionUI();
    document.dispatchEvent(new CustomEvent('game:start', { detail: { gameName: _gameName } }));
  };
}

// ── Botón Finalizar ───────────────────────────────────────────────────────────
if ($('endBtn')) {
  $('endBtn').onclick = () => {
    if (!startTs) return;
    const m = Math.max(1, Math.round((Date.now() - startTs) / 60000));
    totalMinutes += m;
    rec.totalMinutes = totalMinutes;
    startTs = null;
    setStatus(`Partida finalizada · +${m} min · Total: ${totalMinutes} min`, 'info');
    resetSessionUI();
    document.dispatchEvent(new CustomEvent('game:end', { detail: { gameName: _gameName, minutes: m } }));
  };
}

resetSessionUI();
