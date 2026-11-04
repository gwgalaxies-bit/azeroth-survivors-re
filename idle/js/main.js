// Valdoran — boot, main loop, saving and synthesized sound.
'use strict';

// ------------------------------------------------------------------------------------------ sound
const Snd = (() => {
  let ac = null, master = null;
  const last = {};
  function unlock() {
    if (ac) { if (ac.state === 'suspended') ac.resume(); return; }
    try {
      ac = new (window.AudioContext || window.webkitAudioContext)();
      master = ac.createGain();
      master.gain.value = 0.22;
      master.connect(ac.destination);
    } catch (e) { ac = null; }
  }
  function tone(f, t0, dur, type = 'square', vol = 0.3, f2) {
    const o = ac.createOscillator(), gn = ac.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f, t0);
    if (f2) o.frequency.exponentialRampToValueAtTime(f2, t0 + dur);
    gn.gain.setValueAtTime(0.0001, t0);
    gn.gain.exponentialRampToValueAtTime(vol, t0 + 0.01);
    gn.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(gn); gn.connect(master);
    o.start(t0); o.stop(t0 + dur + 0.02);
  }
  function noise(t0, dur, vol = 0.2, freq = 1200) {
    const len = Math.floor(ac.sampleRate * dur);
    const buf = ac.createBuffer(1, len, ac.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / len);
    const src = ac.createBufferSource(), f = ac.createBiquadFilter(), gn = ac.createGain();
    src.buffer = buf; f.type = 'bandpass'; f.frequency.value = freq; gn.gain.value = vol;
    src.connect(f); f.connect(gn); gn.connect(master);
    src.start(t0);
  }
  const arp = (notes, step, type, vol, dur) => { const t = ac.currentTime; notes.forEach((n, i) => tone(n, t + i * step, dur || step * 1.6, type, vol)); };
  const SFX = {
    click: () => tone(660, ac.currentTime, 0.05, 'square', 0.08),
    tap: () => noise(ac.currentTime, 0.06, 0.25, 1800),
    coin: () => arp([988, 1319], 0.06, 'square', 0.12),
    quest: () => arp([523, 659, 784, 1047], 0.09, 'triangle', 0.25),
    turnin: () => arp([392, 523, 659, 784, 1047], 0.08, 'triangle', 0.22),
    levelup: () => { arp([523, 659, 784, 1047, 1319], 0.1, 'triangle', 0.28, 0.5); arp([262, 330, 392, 523], 0.1, 'sine', 0.2, 0.6); },
    epic: () => arp([659, 831, 988, 1319], 0.08, 'sine', 0.25, 0.4),
    legendary: () => { arp([523, 784, 1047, 1568, 2093], 0.09, 'sine', 0.3, 0.6); noise(ac.currentTime, 0.6, 0.1, 4000); },
    death: () => tone(330, ac.currentTime, 0.8, 'sawtooth', 0.15, 80),
    warn: () => arp([880, 660, 880], 0.12, 'square', 0.12),
    start: () => arp([196, 262, 392], 0.12, 'sawtooth', 0.12),
    win: () => arp([392, 523, 659, 784, 659, 1047], 0.1, 'triangle', 0.25),
    lose: () => arp([392, 330, 262, 196], 0.16, 'triangle', 0.2),
    anvil: () => { noise(ac.currentTime, 0.15, 0.4, 3000); tone(1800, ac.currentTime, 0.3, 'triangle', 0.12); },
    brew: () => { for (let i = 0; i < 4; i++) tone(300 + Math.random() * 400, ac.currentTime + i * 0.07, 0.08, 'sine', 0.15); },
    gather: () => { noise(ac.currentTime, 0.1, 0.3, 900); noise(ac.currentTime + 0.12, 0.1, 0.3, 1100); },
    achievement: () => arp([784, 988, 1175, 1568], 0.1, 'triangle', 0.25, 0.5),
    upgrade: () => arp([440, 554, 659], 0.06, 'square', 0.12),
    equip: () => noise(ac.currentTime, 0.12, 0.3, 600),
    splash: () => noise(ac.currentTime, 0.25, 0.35, 700),
    catch: () => arp([523, 659, 784], 0.07, 'triangle', 0.2),
  };
  function play(name) {
    if (!ac || !S || !S.settings.sound || document.hidden) return;
    const t = performance.now();
    if (last[name] && t - last[name] < 60) return;
    last[name] = t;
    try { (SFX[name] || (() => {}))(); } catch (e) { /* audio is optional */ }
  }
  return { unlock, play };
})();

// ------------------------------------------------------------------------------------------ saving
const Save = (() => {
  const KEY = 'valdoran_idle_v1';
  const api = { cloud: false };
  let db = null, uid = null, lastCloud = 0;

  function readLocal() {
    try { const s = localStorage.getItem(KEY); return s ? JSON.parse(s) : null; } catch (e) { return null; }
  }
  function writeLocal() {
    if (!S) return;
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* storage may be unavailable */ }
  }
  api.write = (force) => {
    if (!S) return;
    S.lastSeen = now();
    writeLocal();
    if (db && uid && (force || now() - lastCloud > 60000)) {
      lastCloud = now();
      db.doc(`data/users/${uid}/save`).set({ json: JSON.stringify(S), ts: S.lastSeen }).catch(() => {});
    }
  };
  api.readLocal = readLocal;
  api.wipe = () => {
    try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
    if (db && uid) db.doc(`data/users/${uid}/save`).delete().catch(() => {});
    S = null;
    battle = null;
  };
  api.exportString = () => {
    try { return btoa(unescape(encodeURIComponent(JSON.stringify(S)))); } catch (e) { return ''; }
  };
  api.importString = (str) => {
    try {
      const s = JSON.parse(decodeURIComponent(escape(atob(str))));
      if (!s || !s.cls || !CLASSES[s.cls] || typeof s.level !== 'number') return false;
      Game.adopt(s, false);
      api.write(true);
      return true;
    } catch (e) { return false; }
  };
  // Cloud save through the Claude artifact runtime, when the page is served there. Optional.
  api.connect = async () => {
    try {
      if (!window.claude || typeof window.claude.use !== 'function') return null;
      const [d, u] = await Promise.all([window.claude.use('db'), window.claude.use('user')]);
      if (!d || !u) return null;
      const id = await u.id();
      if (!id) return null;
      db = d; uid = id; api.cloud = true;
      const snap = await db.doc(`data/users/${uid}/save`).get();
      if (snap.exists) { const v = snap.data(); return v && v.json ? JSON.parse(v.json) : null; }
    } catch (e) { /* cloud is a bonus */ }
    return null;
  };
  return api;
})();

// ------------------------------------------------------------------------------------------ game boot & loop
const Game = (() => {
  let last = 0, perT = 0, saveT = 0, hiddenAt = 0, started = false;

  function adopt(s, showOffline = true) {
    S = migrate(s);
    statsDirty = true;
    const away = (now() - (S.lastSeen || now())) / 1000;
    checkDaily();
    checkLogin();
    checkOffers();
    startAdventure();
    let gathered = null;
    if (away > 60) {
      const eff = 0.6 + heroStats().offline / 100;
      const o = offlineProgress(away, eff);
      gathered = catchUpProfessions();
      o.gathered = gathered;
      if (showOffline && away > 120 && !S.needsRace) UI.showOffline(o, away);
    } else catchUpProfessions();
    S.lastSeen = now();
    UI.rebuild();
    if (S.needsRace) UI.showCreate(true);
    if (S.potionNote) {
      UI.toast(`Du trägst höchstens ${POTION_CAP} Heiltränke. ${S.potionNote} überzählige wurden verkauft.`, 'potion_heal', '#e02838');
      delete S.potionNote;
    }
  }

  function create(cls, name, race) {
    S = newState(cls, name, race);
    statsDirty = true;
    checkDaily();
    checkLogin();
    checkOffers();
    startAdventure();
    UI.rebuild();
    Save.write(true);
    UI.toast(`Willkommen, ${name}!`, 'castle', '#ffd200');
    setTimeout(() => { if (S && !S.login.claimed) UI.toast('Deine erste Tagesbelohnung wartet in der Stadt!', 'gift', '#ffd200'); }, 4000);
  }

  function loop(ts) {
    const dt = Math.min(0.25, (ts - last) / 1000 || 0);
    last = ts;
    if (S && battle) {
      let rest = dt;
      while (rest > 0) { const s = Math.min(0.05, rest); tickBattle(battle, s); rest -= s; }
      perT -= dt;
      if (perT <= 0) { perT = 0.25; periodic(0.25); }
      saveT -= dt;
      if (saveT <= 0) { saveT = 15; Save.write(); }
    }
    Scene.frame(dt);
    UI.update(dt);
    requestAnimationFrame(loop);
  }

  function onHide() {
    if (!S) return;
    hiddenAt = now();
    Save.write(true);
  }
  function onShow() {
    if (!S || !hiddenAt) return;
    const away = (now() - hiddenAt) / 1000;
    hiddenAt = 0;
    if (away > 10) {
      const o = offlineProgress(away, 0.8 + heroStats().offline / 100);
      catchUpProfessions();
      if (away > 120) UI.showOffline(o, away);
      else if (o.kills) UI.toast(`Im Hintergrund: ${fmt(o.kills)} Siege, +${fmt(o.xp)} EP`, 'clock');
    }
  }

  async function start(hot) {
    await Scene.init(document.getElementById('scene'));
    UI.init();
    let local = Save.readLocal();
    if (hot && hot.save) { try { local = JSON.parse(hot.save); } catch (e) { /* ignore */ } }
    const cloudP = Save.connect();
    if (local) {
      adopt(local, !(hot && hot.save));
      cloudP.then((cloud) => {
        if (cloud && cloud.lastSeen > (S ? S.lastSeen : 0) + 60000) { adopt(cloud, true); UI.toast('Spielstand aus deinem Konto geladen', 'scroll'); }
      });
    } else {
      const cloud = await Promise.race([cloudP, new Promise((r) => setTimeout(() => r(null), 2500))]);
      if (cloud) adopt(cloud, true);
      else UI.showCreate();
    }
    document.addEventListener('visibilitychange', () => (document.hidden ? onHide() : onShow()));
    window.addEventListener('pagehide', () => Save.write(true));
    if (window.claude && window.claude.hot && typeof window.claude.hot.snapshot === 'function') {
      window.claude.hot.snapshot(() => ({ save: S ? JSON.stringify(Object.assign({}, S, { lastSeen: now() })) : null }));
    }
    if (!started) { started = true; requestAnimationFrame((t) => { last = t; loop(t); }); }
  }

  return { start, create, adopt };
})();

(function boot() {
  const hot = window.claude && window.claude.hot;
  const go = (data) => Game.start(data || {});
  if (hot && typeof hot.ready === 'function') hot.ready(go);
  else go(hot && hot.data);
})();
