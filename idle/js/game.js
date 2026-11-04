// Valdoran — game state, formulas and systems. No DOM access here; the UI listens through Hooks.
'use strict';

const Hooks = {
  toast() {}, log() {}, dirty() {}, fx: null, levelUp() {}, battleEnd() {}, sound() {},
};

// ------------------------------------------------------------------------------------------ utils
const now = () => Date.now();
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.random() * (b - a);
const irnd = (a, b) => Math.floor(rnd(a, b + 1));
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const chance = (p) => Math.random() < p;
const g = (L) => Math.pow(1.1, L - 1);
const MIN = 60000, HOUR = 3600000, DAY = 86400000;

function fmt(n) {
  if (n === undefined || n === null || isNaN(n)) return '0';
  const neg = n < 0;
  n = Math.abs(n);
  let s;
  if (n < 1000) s = (n < 1 && n > 0 ? n.toFixed(1) : Math.round(n).toString());
  else {
    const units = ['K', 'M', 'B', 'T', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah'];
    let i = -1;
    while (n >= 1000 && i < units.length - 1) { n /= 1000; i++; }
    s = (n >= 100 ? n.toFixed(0) : n >= 10 ? n.toFixed(1) : n.toFixed(2)) + units[i];
  }
  return (neg ? '-' : '') + s.replace('.', ',');
}
function fmtInt(n) { return Math.floor(n).toLocaleString('de-DE'); }
function fmtTime(sec) {
  sec = Math.max(0, Math.ceil(sec));
  const d = Math.floor(sec / 86400), h = Math.floor(sec % 86400 / 3600), m = Math.floor(sec % 3600 / 60), s = sec % 60;
  if (d) return `${d}T ${h}Std`;
  if (h) return `${h}:${String(m).padStart(2, '0')} Std`;
  if (m) return `${m}:${String(s).padStart(2, '0')} Min`;
  return `${s} Sek`;
}
function dayKey(t) { const d = new Date(t); return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`; }
function nextMidnight(t) { const d = new Date(t); d.setHours(24, 0, 0, 0); return d.getTime(); }
function weekStart(t) {
  // weekly reset: Wednesday 05:00 local time
  const d = new Date(t);
  d.setHours(5, 0, 0, 0);
  const back = (d.getDay() - 3 + 7) % 7;
  d.setDate(d.getDate() - back);
  if (d.getTime() > t) d.setDate(d.getDate() - 7);
  return d.getTime();
}
function weekKey(t) { return dayKey(weekStart(t)); }
function seeded(seed) {
  let s = 0;
  for (const ch of String(seed)) s = (s * 31 + ch.charCodeAt(0)) >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

// ------------------------------------------------------------------------------------------ economy
const killXP = (L) => 6 * Math.pow(1.095, L - 1);
const xpNeed = (L) => Math.floor(killXP(L) * 6 * Math.pow(1.095, L - 1) * (1 + L / 15));
const gpk = (L) => 3 * g(L); // gold per normal kill
const xpPenalty = (heroL, mobL) => { if (S.worldTier > 0) return 1; const d = heroL - mobL; return d >= 8 ? 0.02 : d >= 5 ? 0.1 : d >= 3 ? 0.5 : 1; };
const paragonNeed = (p) => Math.floor(xpNeed(60) * 0.6 * Math.pow(1.04, p));
const MAX_LEVEL = 60;
const BAG_SIZE = 40;
const KEY_MAX = 5, KEY_REGEN = 20 * MIN;
const ARENA_TICKETS = 5;

const KIND = {
  normal: { hp: 1, atk: 1, iv: 2.0, xp: 1, gold: 1, limit: 0 },
  elite: { hp: 5, atk: 1.5, iv: 2.0, xp: 6, gold: 6, limit: 0 },
  boss: { hp: 13, atk: 1.3, iv: 2.4, xp: 25, gold: 30, limit: 60, special: 13, spMul: 0.15 },
  dboss: { hp: 10, atk: 1.25, iv: 2.2, xp: 14, gold: 18, limit: 75, special: 15, spMul: 0.15 },
  rboss: { hp: 60, atk: 2.0, iv: 2.4, xp: 30, gold: 45, limit: 120, special: 14, spMul: 0.3 },
  wboss: { hp: 26, atk: 1.4, iv: 2.4, xp: 30, gold: 45, limit: 120, special: 16, spMul: 0.22 },
  arena: { hp: 1, atk: 1, iv: 1.7, xp: 0, gold: 0, limit: 60 },
};
const DROP_TABLE = {
  normal: [30, 38, 24, 6.5, 1.48, 0.02], elite: [0, 8, 60, 26, 5.9, 0.1], boss: [0, 0, 28, 52, 19.5, 0.5],
  dboss: [0, 0, 8, 58, 33.2, 0.8], rboss: [0, 0, 0, 12, 85, 3], wboss: [0, 0, 0, 30, 68, 2], chest: [0, 0, 20, 55, 24, 1],
};

// Monsters are tuned against an "expected" hero of their level: full rare gear and trainer ranks at 70% of the level.
function expHero(L) { const m = 1 + 0.021 * L; return { atk: g(L) * 15.4 * m, hp: g(L) * 124 * m, def: g(L) * 11.75 * m }; }
function mobBase(L) {
  const e = expHero(L);
  const dr = e.def / (e.def + 22 * g(L));
  const s = Math.min(1, 0.22 + L * 0.04);
  return { hp: e.atk * 2.1 * s, atk: e.hp * 0.05 / (1 - dr) * s };
}

// ------------------------------------------------------------------------------------------ state
let S = null;

function newState(cls, name) {
  const t = now();
  const s = {
    v: 1, created: t, lastSeen: t, name, cls, title: '',
    level: 1, xp: 0, rested: 0, paragon: 0, pxp: 0,
    gold: 0, badges: 0, raidmarks: 0, honor: 0, keys: 3, keyT: t,
    gear: {}, bag: [], nextId: 1,
    zone: 0, zoneMax: 0, worldTier: 0, wtMax: 0,
    quests: {}, zonesDone: 0,
    talents: {}, training: {}, comp: {}, mounts: [], mount: null,
    cons: { potion_heal: 3 }, mats: {}, buffs: {},
    prof: { mining: { skill: 1 }, herb: { skill: 1 }, smith: { skill: 1 }, alch: { skill: 1 }, cook: { skill: 1 }, fish: { skill: 1 } },
    gatherT: t + 120000, gatherCd: 0,
    fishLog: {},
    dungeons: {}, raids: { week: weekKey(t), kills: {} }, raidEver: {},
    wbKilled: -1,
    arena: { day: dayKey(t), tickets: ARENA_TICKETS, rating: 1000, best: 1000, wins: 0, opp: null },
    exp: { offers: [], active: [], slots: 2 },
    daily: null, weekly: null,
    login: { last: '', cycle: 0, streak: 0, best: 0, claimed: false },
    chestT: t,
    ach: {}, achClaimed: {},
    stats: { kills: 0, bosses: 0, dungeons: 0, fish: 0, crafts: 0, gathers: 0, arena: 0, expeds: 0, taps: 0, loot: 0,
      goldEarned: 0, epics: 0, legendaries: 0, raidBoss: 0, worldBoss: 0, deaths: 0, mythic: 0, raidKills: 0, playTime: 0 },
    settings: { sound: true, autoSell: 0, autoEquip: false, music: false },
    tut: {},
  };
  const starter = makeItem(1, 1, 'weapon', s.cls);
  starter.name = CLASSES[cls].name === 'Magier' ? 'Lehrlingsstab' : CLASSES[cls].name === 'Jäger' ? 'Jagdbogen des Rekruten' : CLASSES[cls].name === 'Priester' ? 'Knüppel des Novizen' : 'Kurzschwert des Rekruten';
  starter.id = s.nextId++;
  s.gear.weapon = starter;
  return s;
}

function migrate(s) {
  const base = newState(s.cls || 'krieger', s.name || 'Held');
  for (const k in base) if (s[k] === undefined) s[k] = base[k];
  for (const k in base.stats) if (s.stats[k] === undefined) s.stats[k] = 0;
  for (const k in base.prof) if (!s.prof[k]) s.prof[k] = { skill: 1 };
  for (const k in base.settings) if (s.settings[k] === undefined) s.settings[k] = base.settings[k];
  return s;
}

// ------------------------------------------------------------------------------------------ items
function itemTier(ilvl) { return clamp(Math.floor((ilvl - 1) / 12), 0, 4); }

function makeItem(ilvl, r, slot, cls) {
  slot = slot || pick(SLOTS);
  cls = cls || (S && S.cls) || 'krieger';
  ilvl = Math.max(1, Math.round(ilvl));
  const it = { id: S ? S.nextId++ : 0, ilvl, r, slot, cls: slot === 'weapon' ? cls : undefined, up: 0, sec: [] };
  const nSec = [0, 0, 1, 1, 2, 3][r];
  const pool = ['crit', 'haste', 'critDmg', 'goldP', 'xpP', 'atkP', 'hpP'];
  for (let i = 0; i < nSec; i++) {
    let k;
    do { k = pick(pool); } while (it.sec.some((x) => x[0] === k));
    it.sec.push([k, secValue(k, r, ilvl)]);
  }
  it.name = itemName(it);
  return it;
}

function secValue(k, r, ilvl) {
  const lv = ilvl / 40;
  const v = { crit: 0.8 + r * 0.5 + lv, haste: 1 + r * 0.6 + lv, critDmg: 4 + r * 2.5 + lv * 2, goldP: 3 + r * 2 + lv * 2,
    xpP: 2 + r * 1.5 + lv * 1.5, atkP: 1 + r * 0.8 + lv, hpP: 1.5 + r + lv }[k];
  return Math.round(v * rnd(0.85, 1.15) * 10) / 10;
}

function itemName(it) {
  if (it.r === 5) return LEGENDARY[it.slot === 'weapon' ? it.cls : it.slot];
  const t = itemTier(it.ilvl);
  const [base, gen] = BASES[it.slot === 'weapon' ? it.cls : it.slot][t];
  const adj = pick(RARITY[it.r].adj);
  const end = { m: 'er', f: 'e', n: 'es', p: 'e' }[gen];
  let name = `${adj}${end} ${base}`;
  if (it.r >= 2 && it.sec.length) name += ' ' + SECONDARY[it.sec[0][0]].suffix;
  return name;
}

function itemIcon(it) {
  const t = it.r === 5 ? 5 : itemTier(it.ilvl);
  return it.slot === 'weapon' ? `w_${it.cls}_${t}` : `a_${it.slot}_${t}`;
}

function itemStats(it) {
  const B = g(it.ilvl) * RARITY[it.r].q * (1 + 0.1 * (it.up || 0));
  const s = { atk: 0, hp: 0, def: 0 };
  switch (it.slot) {
    case 'weapon': s.atk = 6 * B; break;
    case 'head': case 'chest': case 'legs': s.hp = 11 * B; s.def = 1.5 * B; break;
    case 'shoulder': case 'hands': case 'feet': s.hp = 7 * B; s.def = 1.0 * B; break;
    case 'trinket': s.atk = 2 * B; s.hp = 3 * B; break;
  }
  return s;
}

const sellValue = (it) => Math.ceil(gpk(it.ilvl) * [1, 2, 4, 9, 20, 60][it.r] * (1 + (it.up || 0) * 0.3));
const dustValue = (it) => [0, 1, 2, 5, 12, 40][it.r] + Math.floor(it.ilvl / 15);
const upgradeCost = (it) => ({ gold: Math.ceil(gpk(it.ilvl) * 12 * Math.pow(1.6, it.up || 0)), dust: Math.ceil((1 + (it.up || 0)) * (it.r + 1) * 1.5) });
const MAX_UP = 10;

function rollRarity(table, luck = 0) {
  const w = table.slice();
  for (let i = 3; i < 6; i++) w[i] *= 1 + luck / 100;
  const tot = w.reduce((a, b) => a + b, 0);
  let x = Math.random() * tot;
  for (let i = 0; i < 6; i++) { x -= w[i]; if (x <= 0) return i; }
  return 2;
}

function dropItem(ilvl, table, slot) {
  const st = heroStats();
  const r = rollRarity(DROP_TABLE[table] || table, st.lootP);
  return makeItem(ilvl + (r >= 4 ? irnd(1, 3) : 0) + (r === 5 ? 3 : 0) + irnd(-1, 1), r, slot);
}

// Adds to bag (or auto-sells). Returns 'bag' | 'sold' | 'equipped'.
function giveItem(it, silent) {
  S.stats.loot++;
  if (it.r === 4) S.stats.epics++;
  if (it.r === 5) S.stats.legendaries++;
  if (!silent) {
    Hooks.log(`Du erhältst Beute: <span class="q${it.r}">[${it.name}]</span>`);
    if (it.r >= 4) Hooks.toast(`${RARITY[it.r].name}: ${it.name}`, itemIcon(it), RARITY[it.r].color);
    if (it.r >= 3 && Hooks.fx) Hooks.fx.loot(itemIcon(it), it.r);
    if (it.r >= 4) Hooks.sound(it.r === 5 ? 'legendary' : 'epic');
  }
  if (S.settings.autoEquip && itemUpgrade(it) > 0) { equipItem(it, true); return 'equipped'; }
  if (it.r <= S.settings.autoSell - 1 || it.r === 0) { S.gold += sellValue(it); return 'sold'; }
  if (S.bag.length >= BAG_SIZE) {
    S.gold += sellValue(it);
    if (!silent) Hooks.log('<span class="sys">Deine Taschen sind voll — Gegenstand verkauft.</span>');
    return 'sold';
  }
  S.bag.push(it);
  Hooks.dirty('bag');
  return 'bag';
}

function equipItem(it, auto) {
  const i = S.bag.indexOf(it);
  if (i >= 0) S.bag.splice(i, 1);
  const old = S.gear[it.slot];
  S.gear[it.slot] = it;
  if (old) S.bag.push(old);
  statsDirty = true;
  if (auto) Hooks.log(`Automatisch angelegt: <span class="q${it.r}">[${it.name}]</span>`);
  Hooks.dirty('gear');
}

function itemUpgrade(it) {
  const cur = S.gear[it.slot];
  return power(statsWith(it.slot, it)) - power(statsWith(it.slot, cur || null));
}

function equipBest() {
  let changed = 0;
  for (let guard = 0; guard < 20; guard++) {
    let best = null, bestGain = 0;
    for (const it of S.bag) {
      const gain = itemUpgrade(it);
      if (gain > bestGain + 0.0001) { best = it; bestGain = gain; }
    }
    if (!best) break;
    equipItem(best);
    changed++;
  }
  return changed;
}

function sellItem(it) {
  const i = S.bag.indexOf(it);
  if (i < 0) return;
  S.bag.splice(i, 1);
  const v = sellValue(it);
  S.gold += v;
  Hooks.sound('coin');
  Hooks.dirty('bag');
  return v;
}

function salvageItem(it) {
  const i = S.bag.indexOf(it);
  if (i < 0) return;
  S.bag.splice(i, 1);
  const d = dustValue(it);
  addMat('dust', d);
  Hooks.dirty('bag');
  return d;
}

function upgradeItem(it) {
  if ((it.up || 0) >= MAX_UP) return false;
  const c = upgradeCost(it);
  if (S.gold < c.gold || (S.mats.dust || 0) < c.dust) return false;
  S.gold -= c.gold;
  S.mats.dust -= c.dust;
  it.up = (it.up || 0) + 1;
  statsDirty = true;
  Hooks.sound('upgrade');
  Hooks.dirty('gear');
  return true;
}

function addMat(id, n) { S.mats[id] = (S.mats[id] || 0) + n; }

// ------------------------------------------------------------------------------------------ stats
let statsDirty = true, statsCache = null;
const BASE_P = () => ({ atkP: 0, hpP: 0, defP: 0, crit: 0, critDmg: 50, haste: 0, skillP: 0, bossP: 0, goldP: 0, xpP: 0, tapP: 0,
  regen: 0, offline: 0, compP: 0, cdr: 0, potion: 0, lootP: 0 });

function computeStats(gear, opt = {}) {
  const c = CLASSES[S.cls];
  const L = opt.level || S.level;
  let atk = 5 * g(L) * c.mods.atk, hp = 50 * g(L) * c.mods.hp, def = 2 * g(L) * c.mods.def;
  const p = BASE_P();
  p.crit += c.mods.crit;
  p.haste += c.mods.haste;
  for (const slot of SLOTS) {
    const it = gear[slot];
    if (!it) continue;
    const s = itemStats(it);
    atk += s.atk * (slot === 'weapon' ? c.mods.atk : 1);
    hp += s.hp;
    def += s.def;
    for (const [k, v] of it.sec) p[k] += v;
  }
  if (!opt.bare) {
    const tal = TALENTS[S.cls];
    for (const i in S.talents) { const t = tal[i]; if (t) p[t[1]] += t[2] * S.talents[i]; }
    for (const tr of TRAINING) p[tr.key] += tr.per * (S.training[tr.id] || 0);
    p.atkP += S.paragon;
    p.hpP += S.paragon;
    const t = now();
    const b = S.buffs;
    if (b.atk > t) p.atkP += 25;
    if (b.xp > t) p.xpP += 50;
    if (b.luck > t) { p.goldP += 40; p.lootP += 30; }
    if (b.titan > t) { p.atkP += 20; p.hpP += 20; p.defP += 20; }
    if (b.food > t && b.foodId) for (const k in CONSUMABLES[b.foodId].food) p[k] += CONSUMABLES[b.foodId].food[k];
    if (S.mount) { const m = MOUNTS.find((x) => x.id === S.mount); if (m) { p.goldP += m.bonus; p.xpP += m.bonus; } }
    p.goldP += Math.min(30, S.login.streak || 0);
  }
  p.crit = Math.min(75, p.crit);
  p.haste = Math.min(150, p.haste);
  p.cdr = Math.min(50, p.cdr);
  atk *= 1 + p.atkP / 100;
  hp *= 1 + p.hpP / 100;
  def *= 1 + p.defP / 100;
  const st = Object.assign(p, { atk, hp, def, interval: 1.6 / (1 + p.haste / 100) });
  st.power = power(st);
  return st;
}

function power(st) {
  if (!st) return 0;
  const dps = st.atk / st.interval * (1 + st.crit / 100 * st.critDmg / 100) * (1.6 + st.skillP / 150);
  const ehp = st.hp * (1 + st.def / (st.hp * 0.08 + 1)) * (1 + st.regen / 3);
  return Math.round(Math.sqrt(dps * ehp) * 3);
}

function heroStats() {
  if (statsDirty || !statsCache) { statsCache = computeStats(S.gear); statsDirty = false; }
  return statsCache;
}

function statsWith(slot, item) {
  const gear = Object.assign({}, S.gear);
  if (item) gear[slot] = item; else delete gear[slot];
  return computeStats(gear);
}

// Reference hero for recommendations: level L, all slots filled at ilvl with quality r, `train` ranks.
function refPower(L, ilvl, r, train) {
  const gear = {};
  for (const slot of SLOTS) gear[slot] = { slot, ilvl, r, up: 0, sec: [], cls: S.cls };
  const st = computeStats(gear, { level: Math.min(L, MAX_LEVEL), bare: true });
  const tp = 1 + (train || 0) * 0.06;
  st.atk *= tp; st.hp *= tp;
  return power(st);
}

function talentPoints() { return Math.max(0, S.level - 4); }
function talentSpent() { let n = 0; for (const k in S.talents) n += S.talents[k]; return n; }
function compPower(id) {
  const lv = S.comp[id] || 0;
  if (!lv) return 0;
  return 2.4 * g(lv) * (1 + heroStats().compP / 100);
}
const compRecruitCost = (c) => Math.ceil(gpk(c.unlock) * 400);
const compUpCost = (lv) => Math.ceil(30 * Math.pow(1.165, lv));
const mountCost = (m) => Math.ceil(m.price * 10 * gpk(m.lvl));
const trainCost = (tr, rank) => Math.ceil(tr.base * Math.pow(tr.growth, rank));
const trainCap = (tr) => tr.max || (S.level + S.wtMax * 10);
function questN(zi, q) { return q.kind === 'elite' || q.kind === 'boss' ? q.n : Math.round(q.n * (1 + zi * 0.5)); }
const talentResetCost = () => Math.ceil(gpk(S.level) * 50);

// ------------------------------------------------------------------------------------------ zones & quests
function zoneOf(i) { return ZONES[clamp(i, 0, ZONES.length - 1)]; }
function wtLevel(tier, zi) { return 58 + tier * 8 + zi; }
function mobLevel(zi) {
  const z = zoneOf(zi);
  if (S.worldTier > 0) return wtLevel(S.worldTier, zi);
  return clamp(S.level, z.lvl[0], z.lvl[1]);
}
function questState(zi) {
  if (!S.quests[zi]) S.quests[zi] = { i: 0, p: 0, done: false };
  return S.quests[zi];
}
function currentQuest(zi) {
  const qs = questState(zi);
  if (qs.i >= 6) return null;
  return zoneOf(zi).quests[qs.i];
}
function questLevel(zi, qi) { const z = zoneOf(zi); return z.lvl[0] + Math.floor((z.lvl[1] - z.lvl[0]) * qi / 5); }
function questRewards(zi, qi) {
  const L = questLevel(zi, qi);
  const xpm = [0.25, 0.25, 0.3, 0.4, 0.3, 0.7][qi];
  const gm = [12, 12, 14, 28, 18, 70][qi];
  const r = { xp: Math.floor(xpNeed(Math.min(L, S.level)) * xpm), gold: Math.ceil(gpk(L) * gm) };
  if (qi === 3) r.item = { ilvl: L + 1, r: 3 };
  if (qi === 5) r.item = { ilvl: L + 2, r: zi >= 3 ? 4 : 3 };
  return r;
}

function questProgress(kind, target, zi, n = 1) {
  const qs = questState(zi);
  const q = currentQuest(zi);
  if (!q || qs.done) return;
  let hit = false;
  if (q.kind === 'kill' && kind === 'kill' && q.target === target) hit = true;
  if (q.kind === 'any' && kind === 'kill') hit = true;
  if (q.kind === 'elite' && kind === 'elite' && q.target === target) hit = true;
  if (q.kind === 'boss' && kind === 'boss' && q.target === target) hit = true;
  if (q.kind === 'collect' && kind === 'collect' && q.target === target) hit = true;
  if (!hit) return;
  const need = questN(zi, q);
  qs.p = Math.min(need, qs.p + n);
  if (q.kind === 'collect' && n === 1) Hooks.log(`<span class="quest">${q.item}: ${qs.p}/${need}</span>`);
  if (qs.p >= need) {
    qs.done = true;
    Hooks.toast(`Quest abgeschlossen: ${q.t}`, 'scroll', '#ffd200');
    Hooks.sound('quest');
    Hooks.log(`<span class="quest">${q.t} abgeschlossen. Kehre zu ${zoneOf(zi).giver} zurück.</span>`);
  }
  Hooks.dirty('quest');
}

function turnInQuest(zi) {
  const qs = questState(zi);
  if (!qs.done) return;
  const q = currentQuest(zi);
  const rw = questRewards(zi, qs.i);
  gainXP(rw.xp, true);
  gainGold(rw.gold);
  let itemTxt = '';
  if (rw.item) {
    const it = makeItem(rw.item.ilvl, rw.item.r);
    giveItem(it);
    itemTxt = it.name;
  }
  Hooks.log(`<span class="quest">Quest abgegeben: ${q.t}.</span> +${fmt(rw.xp)} EP, +${fmt(rw.gold)} Gold`);
  Hooks.sound('turnin');
  qs.i++;
  qs.p = 0;
  qs.done = false;
  if (qs.i >= 6) {
    S.zonesDone = Math.max(S.zonesDone, zi + 1);
    if (zi + 1 < ZONES.length) {
      if (S.zoneMax < zi + 1) {
        S.zoneMax = zi + 1;
        Hooks.toast(`Neue Zone: ${ZONES[zi + 1].name}`, 'map', '#ffd200');
        if (S.zone === zi) travel(zi + 1);
      }
    } else if (S.wtMax < 1) {
      S.wtMax = 1;
      Hooks.toast('Weltstufe 1 freigeschaltet!', 'star', '#ff8000');
    }
  }
  Hooks.dirty('quest');
  return { rw, itemTxt };
}

function travel(zi) {
  if (zi > S.zoneMax) return;
  S.zone = zi;
  if (battle && battle.mode === 'adventure') startAdventure();
  Hooks.dirty('zone');
}

function setWorldTier(t) {
  if (t > S.wtMax || t < 0) return;
  S.worldTier = t;
  if (battle && battle.mode === 'adventure') startAdventure();
  Hooks.dirty('zone');
}

function bossAvailable(zi) {
  const q = currentQuest(zi);
  const qs = questState(zi);
  return qs.i >= 6 || (q && q.kind === 'boss') || S.worldTier > 0;
}

// ------------------------------------------------------------------------------------------ xp & gold
function gainGold(n) {
  n = Math.ceil(n);
  S.gold += n;
  S.stats.goldEarned += n;
  return n;
}

function gainXP(n, noRested) {
  let bonus = 0;
  if (!noRested && S.rested > 0 && S.level < MAX_LEVEL) {
    bonus = Math.min(S.rested, n);
    S.rested -= bonus;
  }
  n += bonus;
  if (S.level >= MAX_LEVEL) {
    S.pxp += n;
    while (S.pxp >= paragonNeed(S.paragon)) {
      S.pxp -= paragonNeed(S.paragon);
      S.paragon++;
      statsDirty = true;
      Hooks.toast(`Ruhmstufe ${S.paragon}! +1% Angriff und Leben`, 'star', '#ff8000');
    }
    return n;
  }
  S.xp += n;
  while (S.level < MAX_LEVEL && S.xp >= xpNeed(S.level)) {
    S.xp -= xpNeed(S.level);
    S.level++;
    statsDirty = true;
    Hooks.levelUp(S.level);
    if (battle) battle.h.hp = heroStats().hp;
  }
  if (S.level >= MAX_LEVEL) { S.pxp += S.xp; S.xp = 0; }
  return n;
}

// ------------------------------------------------------------------------------------------ battle engine
let battle = null;

function makeEnemy(spec) {
  const k = KIND[spec.kind];
  const L = spec.level;
  const e = {
    key: spec.key, name: spec.name, sprite: spec.sprite || spec.key, level: L, kind: spec.kind,
    maxHp: mobBase(L).hp * k.hp * (spec.hpMul || 1), atk: mobBase(L).atk * k.atk * (spec.atkMul || 1), iv: k.iv,
    timer: k.iv * 0.8, dots: [], slow: 0, spT: k.special ? k.special : 0, special: spec.special, warn: 0, crit: spec.crit || 0,
  };
  e.hp = e.maxHp;
  if (spec.stats) Object.assign(e, spec.stats, { hp: spec.stats.maxHp });
  return e;
}

function newBattle(mode, opts = {}) {
  const st = heroStats();
  const b = {
    mode, bg: opts.bg || zoneOf(S.zone).bg, title: opts.title || '', queue: opts.queue || [], enemy: null,
    h: { hp: battle && mode === 'adventure' && battle.mode === 'adventure' ? Math.min(battle.h.hp, st.hp) : st.hp,
      res: CLASSES[S.cls].res === 'Wut' ? 0 : 100, timer: 0.4, buffT: 0, buffMul: 0, dead: 0, potionCd: 0 },
    cd: {}, comp: {}, t: 0, respawn: 0.5, result: null, dmgMul: opts.dmgMul || 1, healPct: opts.healPct || 0,
    fx: opts.headless ? false : true, onKill: opts.onKill, onEnd: opts.onEnd, eliteCd: 0, killsInRow: 0, meta: opts.meta || {},
    total: opts.queue ? opts.queue.length : 0, log: [],
  };
  return b;
}

function startAdventure() {
  battle = newBattle('adventure', { bg: zoneOf(S.zone).bg });
  Hooks.dirty('battle');
}

function adventureSpec() {
  const z = zoneOf(S.zone);
  const L = mobLevel(S.zone);
  const q = currentQuest(S.zone);
  const qs = questState(S.zone);
  if (q && !qs.done && q.kind === 'elite' && battle.eliteCd <= 0) {
    return { key: z.elite, name: MOBS[z.elite], level: L + 1, kind: 'elite' };
  }
  if (S.worldTier > 0 && chance(0.04)) return { key: z.elite, name: MOBS[z.elite], level: L + 1, kind: 'elite' };
  let key = pick(z.mobs);
  if (q && !qs.done && (q.kind === 'kill' || q.kind === 'collect') && chance(0.5)) key = q.target;
  return { key, name: MOBS[key], level: Math.max(z.lvl[0], L - (chance(0.4) ? 1 : 0)), kind: 'normal' };
}

function startBossFight(zi) {
  const z = zoneOf(zi);
  const L = (S.worldTier > 0 ? wtLevel(S.worldTier, zi) : z.lvl[1]) + 1;
  startInstance('boss', {
    bg: z.bg, title: z.name,
    queue: [{ key: z.boss, name: MOBS[z.boss], level: L, kind: 'boss', special: 'Vernichtender Schlag' }],
    meta: { zone: zi },
  });
}

function startInstance(mode, opts) {
  battle = newBattle(mode, opts);
  battle.respawn = 1.2;
  Hooks.dirty('battle');
  Hooks.sound('start');
}

function endBattle(win) {
  const b = battle;
  if (!b || b.result) return;
  b.result = win ? 'win' : 'lose';
  const res = b.onEnd ? b.onEnd(win, b) : null;
  if (b.mode === 'boss') {
    if (win) {
      S.stats.bosses++;
      if (S.worldTier >= S.wtMax && b.meta.zone === ZONES.length - 1 && S.worldTier > 0) {
        S.wtMax = S.worldTier + 1;
        Hooks.toast(`Weltstufe ${S.wtMax} freigeschaltet!`, 'star', '#ff8000');
      }
    }
  }
  if (b.fx) Hooks.battleEnd(b, win, res);
  if (b.fx) setTimeout(() => { if (battle === b) startAdventure(); }, 2600);
  else startAdventure();
}

function leaveInstance() {
  if (!battle || battle.mode === 'adventure') return;
  battle.result = 'lose';
  startAdventure();
}

function heroHit(b, st, mult, src, fxKind) {
  const e = b.enemy;
  if (!e || e.hp <= 0) return 0;
  let d = st.atk * mult * rnd(0.92, 1.08);
  if (src !== 'auto' && src !== 'tap') d *= 1 + st.skillP / 100;
  if (e.kind !== 'normal') d *= 1 + st.bossP / 100;
  if (src === 'tap') d *= 1 + st.tapP / 100;
  if (b.h.buffT > 0) d *= 1 + b.h.buffMul;
  d *= b.dmgMul;
  const crit = Math.random() * 100 < st.crit;
  if (crit) d *= 1 + st.critDmg / 100;
  e.hp -= d;
  if (b.fx && Hooks.fx) Hooks.fx.hit('enemy', d, crit, fxKind || src);
  return d;
}

function enemyDies(b) {
  const e = b.enemy;
  e.hp = 0;
  e.dead = true;
  const kd = KIND[e.kind];
  if (b.fx && Hooks.fx) Hooks.fx.death('enemy');
  if (b.mode === 'adventure' || b.mode === 'boss') {
    const st = heroStats();
    let xp = killXP(e.level) * kd.xp * (1 + st.xpP / 100);
    xp *= xpPenalty(S.level, e.level);
    const gold = gpk(e.level) * kd.gold * rnd(0.8, 1.2) * (1 + st.goldP / 100);
    const gx = gainXP(xp);
    gainGold(gold);
    if (b.fx && Hooks.fx) Hooks.fx.reward(gx, gold);
    S.stats.kills++;
    if (e.kind === 'normal' || e.kind === 'elite') questProgress('kill', e.key, S.zone);
    if (e.kind === 'elite') { questProgress('elite', e.key, S.zone); }
    if (e.kind === 'boss') questProgress('boss', e.key, b.meta.zone !== undefined ? b.meta.zone : S.zone);
    const q = currentQuest(S.zone);
    if (q && q.kind === 'collect' && q.target === e.key && chance(0.6)) questProgress('collect', e.key, S.zone);
    // loot
    const dropIlvl = e.level;
    if (e.kind === 'normal') { if (chance(0.07 * (1 + st.lootP / 100))) giveItem(dropItem(dropIlvl, 'normal')); }
    else if (e.kind === 'elite') giveItem(dropItem(dropIlvl, 'elite'));
    else if (e.kind === 'boss') { giveItem(dropItem(dropIlvl, 'boss')); giveItem(dropItem(dropIlvl, 'boss')); }
    if (chance(0.045)) {
      const tier = clamp(Math.floor((S.worldTier > 0 ? 7 : S.zone) / 1.6), 0, 4);
      const m = chance(0.5) ? ORES[tier] : HERBS[tier];
      addMat(m, 1);
      Hooks.log(`Du findest: <span class="q1">[${MAT_NAME[m]}]</span>`);
    }
    if (e.kind === 'normal') b.eliteCd = Math.max(0, b.eliteCd - 1);
  }
  if (b.onKill) b.onKill(e, b);
  Hooks.dirty('kill');
}

function heroDies(b) {
  b.h.hp = 0;
  S.stats.deaths++;
  if (b.fx && Hooks.fx) Hooks.fx.death('hero');
  Hooks.sound('death');
  if (b.mode === 'adventure') {
    b.h.dead = 4;
    if (b.enemy && b.enemy.kind === 'elite') b.eliteCd = 6;
    Hooks.log('<span class="bad">Du bist gestorben. Ein Geistheiler wird dich gleich wiederbeleben.</span>');
  } else {
    Hooks.log('<span class="bad">Du wurdest besiegt.</span>');
    endBattle(false);
  }
}

function spawnNext(b) {
  let spec;
  if (b.mode === 'adventure') spec = adventureSpec();
  else {
    spec = b.queue.shift();
    if (!spec) { endBattle(true); return; }
  }
  b.enemy = makeEnemy(spec);
  b.t = 0;
  if (b.fx && Hooks.fx) Hooks.fx.spawn(b.enemy);
  if (b.mode !== 'adventure') Hooks.dirty('battle');
}

function tickBattle(b, dt) {
  if (!b || b.result) return;
  const st = heroStats();
  const h = b.h;
  const isRage = CLASSES[S.cls].res === 'Wut';
  h.potionCd -= dt;
  for (const id of CLASSES[S.cls].skills) if (b.cd[id] > 0) b.cd[id] -= dt;
  // dead (adventure only)
  if (h.dead > 0) {
    h.dead -= dt;
    if (h.dead <= 0) {
      h.hp = st.hp;
      if (b.enemy && !b.enemy.dead) { b.enemy.hp = b.enemy.maxHp; b.enemy.dots = []; }
      if (b.fx && Hooks.fx) Hooks.fx.revive();
    }
    return;
  }
  const e = b.enemy;
  if (!e || e.dead) {
    b.respawn -= dt;
    h.hp = Math.min(st.hp, h.hp + st.hp * (b.mode === 'adventure' ? 0.12 : 0.25) * dt);
    if (!isRage) h.res = Math.min(100, h.res + 25 * dt);
    if (b.respawn <= 0) {
      if (e && e.dead && b.mode !== 'adventure' && b.queue.length === 0) { endBattle(true); return; }
      b.respawn = b.mode === 'adventure' ? 0.75 : 1.6;
      spawnNext(b);
    }
    return;
  }
  b.t += dt;
  // resources
  if (!isRage) h.res = Math.min(100, h.res + (CLASSES[S.cls].res === 'Fokus' ? 12 : 8) * dt);
  // buffs
  if (h.buffT > 0) h.buffT -= dt;
  // regen
  h.hp = Math.min(st.hp, h.hp + st.hp * (st.regen / 100 + b.healPct / 100 + 0.004) * dt);
  // auto attack
  h.timer -= dt;
  if (h.timer <= 0) {
    h.timer += st.interval;
    heroHit(b, st, 1, 'auto', S.cls === 'jaeger' ? 'arrow' : S.cls === 'magier' ? 'bolt' : S.cls === 'priester' ? 'bolt' : 'melee');
    if (isRage) h.res = Math.min(100, h.res + 14);
    if (b.fx && Hooks.fx) Hooks.fx.attack('hero');
  }
  // skills: the player casts them from the action bar; only a headless quick fight casts them by itself
  if (b.auto) {
    for (const id of CLASSES[S.cls].skills) {
      const sk = SKILLS[id];
      if (S.level < sk.lvl || (b.cd[id] || 0) > 0 || h.res < sk.cost) continue;
      if (sk.kind === 'heal' && h.hp > st.hp * 0.6) continue;
      castSkill(b, st, id, sk);
      b.cd[id] = sk.cd * (1 - st.cdr / 100);
      h.res -= sk.cost;
      if (e.hp <= 0) break;
    }
  }
  // dots
  for (const d of e.dots) {
    const step = Math.min(dt, d.t);
    d.t -= step;
    d.acc += d.dps * step;
    if (d.acc >= d.tick) {
      const amt = d.acc;
      d.acc = 0;
      e.hp -= amt;
      if (b.fx && Hooks.fx) Hooks.fx.hit('enemy', amt, false, 'dot');
    }
  }
  e.dots = e.dots.filter((d) => d.t > 0);
  if (e.slow > 0) e.slow -= dt;
  // companions
  for (const c of COMPANIONS) {
    const lv = S.comp[c.id];
    if (!lv) continue;
    b.comp[c.id] = (b.comp[c.id] || rnd(0.5, 1.5)) - dt;
    if (b.comp[c.id] > 0) continue;
    const pw = compPower(c.id);
    if (c.type === 'heal') {
      b.comp[c.id] = 2;
      const amt = st.hp * 0.03 * (1 + st.compP / 100);
      if (h.hp < st.hp) { h.hp = Math.min(st.hp, h.hp + amt); if (b.fx && Hooks.fx) Hooks.fx.heal(amt, 'comp'); }
      e.hp -= pw * 0.6 * b.dmgMul;
    } else {
      const ivl = c.type === 'tank' ? 2 : 1.5;
      b.comp[c.id] = ivl;
      const d = pw * ivl * (c.type === 'tank' ? 0.6 : 1.6) * b.dmgMul * rnd(0.9, 1.1);
      e.hp -= d;
      if (b.fx && Hooks.fx) Hooks.fx.compAttack(c.id, d);
    }
  }
  if (e.hp <= 0) { enemyDies(b); return; }
  // enemy attacks
  const dr = Math.min(0.75, st.def / (st.def + 22 * g(e.level)));
  const tank = S.comp.thorga ? 0.18 : 0;
  e.timer -= dt * (e.slow > 0 ? 0.6 : 1);
  if (e.timer <= 0) {
    e.timer += e.iv;
    let d = e.atk * rnd(0.9, 1.1) * (1 - dr) * (1 - tank);
    if (e.crit && Math.random() * 100 < e.crit) d *= 1.5;
    h.hp -= d;
    if (isRage) h.res = Math.min(100, h.res + 6);
    if (b.fx && Hooks.fx) { Hooks.fx.attack('enemy'); Hooks.fx.hit('hero', d, false, 'melee'); }
  }
  // boss special
  const kd = KIND[e.kind];
  if (kd.special) {
    e.spT -= dt;
    if (e.spT <= 1.6 && !e.warn) {
      e.warn = 1;
      if (b.fx && Hooks.fx) Hooks.fx.warn(`${e.name} wirkt ${e.special || 'einen mächtigen Angriff'}!`);
    }
    if (e.spT <= 0) {
      e.spT = kd.special;
      e.warn = 0;
      const d = st.hp * kd.spMul * (1 - tank) * rnd(0.9, 1.1);
      h.hp -= d;
      if (b.fx && Hooks.fx) { Hooks.fx.special(); Hooks.fx.hit('hero', d, true, 'special'); }
    }
  }
  // potion
  if (h.hp > 0 && h.hp < st.hp * 0.35 && h.potionCd <= 0 && (S.cons.potion_heal || 0) > 0) {
    S.cons.potion_heal--;
    h.potionCd = 12;
    const amt = st.hp * 0.4 * (1 + st.potion / 100);
    h.hp = Math.min(st.hp, h.hp + amt);
    if (b.fx && Hooks.fx) Hooks.fx.heal(amt, 'potion');
    Hooks.log('Du trinkst einen <span class="q1">[Heiltrank]</span>.');
  }
  if (h.hp <= 0) { heroDies(b); return; }
  // time limit
  const lim = b.mode === 'arena' ? KIND.arena.limit : kd.limit;
  if (lim && b.t >= lim) {
    if (b.fx && Hooks.fx) Hooks.fx.warn(b.mode === 'arena' ? 'Zeit abgelaufen!' : `${e.name} gerät in Raserei!`);
    Hooks.log(`<span class="bad">${b.mode === 'arena' ? 'Die Zeit ist abgelaufen.' : e.name + ' gerät in Raserei. Der Kampf ist verloren.'}</span>`);
    endBattle(false);
  }
}

function castSkill(b, st, id, sk) {
  const h = b.h, e = b.enemy;
  if (b.fx && Hooks.fx) Hooks.fx.cast(id, sk);
  if (sk.kind === 'dmg') {
    heroHit(b, st, sk.mult, 'skill', sk.fx);
    if (sk.slow) e.slow = sk.slow;
  } else if (sk.kind === 'dot') {
    const total = st.atk * sk.mult * (1 + st.skillP / 100) * (e.kind !== 'normal' ? 1 + st.bossP / 100 : 1) * b.dmgMul * (h.buffT > 0 ? 1 + h.buffMul : 1);
    e.dots.push({ t: sk.dur, dps: total / sk.dur, acc: 0, tick: total / sk.dur });
  } else if (sk.kind === 'heal') {
    const amt = st.hp * sk.mult;
    h.hp = Math.min(st.hp, h.hp + amt);
    if (b.fx && Hooks.fx) Hooks.fx.heal(amt, 'skill');
  } else if (sk.kind === 'buff') {
    h.buffT = sk.dur;
    h.buffMul = sk.mult;
  }
}

// What a skill button can do right now: locked | cd | res | target | ready
function skillState(id) {
  const b = battle, sk = SKILLS[id];
  if (S.level < sk.lvl) return 'locked';
  if (!b || b.result || b.h.dead > 0) return 'target';
  if ((b.cd[id] || 0) > 0) return 'cd';
  if (b.h.res < sk.cost) return 'res';
  if (sk.kind !== 'heal' && sk.kind !== 'buff' && (!b.enemy || b.enemy.dead)) return 'target';
  return 'ready';
}

function castManual(id) {
  const state = skillState(id);
  if (state !== 'ready') return state;
  const b = battle, sk = SKILLS[id], st = heroStats();
  castSkill(b, st, id, sk);
  b.cd[id] = sk.cd * (1 - st.cdr / 100);
  b.h.res -= sk.cost;
  S.stats.casts = (S.stats.casts || 0) + 1;
  if (b.enemy && !b.enemy.dead && b.enemy.hp <= 0) enemyDies(b);
  return 'ok';
}

let lastTap = 0;
function tapAttack() {
  const b = battle;
  if (!b || !b.enemy || b.enemy.dead || b.h.dead > 0 || b.result) return 0;
  const t = now();
  if (t - lastTap < 70) return 0;
  lastTap = t;
  S.stats.taps++;
  const st = heroStats();
  const d = heroHit(b, st, 0.35, 'tap', 'tap');
  if (b.enemy.hp <= 0) enemyDies(b);
  return d;
}

// Fast headless run of a whole instance (for "Schnellkampf"). Returns true on win.
function simulateInstance(mode, opts) {
  const saved = battle;
  const sim = newBattle(mode, Object.assign({}, opts, { headless: true }));
  sim.auto = true;
  sim.h.hp = heroStats().hp;
  battle = sim;
  let steps = 0;
  let win = null;
  sim.onEnd = (w, bb) => { win = w; return opts.onEnd ? opts.onEnd(w, bb) : null; };
  while (!sim.result && steps < 20000) { tickBattle(sim, 0.1); steps++; }
  battle = saved;
  return win === null ? false : win;
}

// ------------------------------------------------------------------------------------------ instances
function dungeonLevel(d, mythic) { return d.lvl + mythic * 2; }
function dungeonQueue(d, mythic) {
  const L = dungeonLevel(d, mythic);
  return d.bosses.map(([sprite, name], i) => ({ key: sprite, sprite, name, level: L + (i === 2 ? 1 : 0), kind: 'dboss', special: 'Verheerung', hpMul: 1 + mythic * 0.04 }));
}

function dungeonRewards(d, mythic, killed, full) {
  const L = dungeonLevel(d, mythic);
  const st = heroStats();
  const out = { items: [], badges: 0, gold: 0, xp: 0 };
  for (let i = 0; i < killed; i++) {
    out.items.push(dropItem(L + 2, 'dboss'));
    out.badges += 4 + Math.floor(mythic / 2);
    out.gold += gpk(L) * 30 * (1 + st.goldP / 100);
    out.xp += killXP(L) * KIND.dboss.xp * (1 + st.xpP / 100);
  }
  if (full) { out.badges += 8 + mythic; out.gold *= 1.5; if (mythic >= 5 && chance(0.25)) out.items.push(dropItem(L + 4, 'dboss')); }
  return out;
}

let lastInstanceOut = null;
function grantInstanceRewards(out) {
  lastInstanceOut = out;
  for (const it of out.items) giveItem(it, false);
  gainGold(out.gold);
  gainXP(out.xp, true);
  S.badges += out.badges;
  if (out.raidmarks) S.raidmarks += out.raidmarks;
  if (out.honor) S.honor += out.honor;
}

function startDungeon(id, mythic, quick) {
  const d = DUNGEONS.find((x) => x.id === id);
  if (!d || S.keys < 1 || S.level < d.lvl - 2) return false;
  S.keys--;
  if (S.keys < KEY_MAX && S.keys + 1 >= KEY_MAX) S.keyT = now();
  let killed = 0;
  const opts = {
    bg: d.bg, title: d.name + (mythic ? ` (Mythisch +${mythic})` : ''), queue: dungeonQueue(d, mythic), meta: { dungeon: id, mythic },
    onKill: () => { killed++; },
    onEnd: (win) => {
      const out = dungeonRewards(d, mythic, killed, win);
      grantInstanceRewards(out);
      if (win) {
        S.stats.dungeons++;
        S.stats.bosses += killed;
        const ds = S.dungeons[id] || (S.dungeons[id] = { clears: 0, best: -1 });
        ds.clears++;
        if (mythic > ds.best) ds.best = mythic;
        S.stats.mythic = Math.max(S.stats.mythic, mythic);
      } else S.stats.bosses += killed;
      return out;
    },
  };
  if (quick) {
    const win = simulateInstance('dungeon', opts);
    const out = lastInstanceOut;
    Hooks.battleEnd({ mode: 'dungeon', title: opts.title, quick: true, meta: opts.meta }, win, out);
    return true;
  }
  startInstance('dungeon', opts);
  return true;
}

function raidLocked(rid, diff, bi) {
  checkWeekly();
  const k = S.raids.kills[`${rid}:${diff}`];
  return !!(k && k[bi]);
}
function raidLevel(r, diff) { return r.lvl + diff * 10; }

function startRaidBoss(rid, diff, bi) {
  const r = RAIDS.find((x) => x.id === rid);
  if (!r || raidLocked(rid, diff, bi)) return false;
  if (bi > 0 && !raidLocked(rid, diff, bi - 1)) return false;
  const boss = r.bosses[bi];
  const L = raidLevel(r, diff) + Math.floor(bi / 2);
  startInstance('raid', {
    bg: r.bg, title: `${r.name} — ${['Normal', 'Heroisch', 'Mythisch'][diff]}`, dmgMul: 3, healPct: 1.4,
    queue: [{ key: boss.sprite, sprite: boss.sprite, name: boss.name, level: L, kind: 'rboss', special: boss.special }],
    meta: { raid: rid, diff, bi },
    onEnd: (win) => {
      if (!win) return null;
      const key = `${rid}:${diff}`;
      (S.raids.kills[key] = S.raids.kills[key] || [])[bi] = true;
      S.raidEver[`${rid}:${bi}`] = true;
      S.stats.raidBoss++;
      S.stats.bosses++;
      bumpWeekly('raidKills');
      const st = heroStats();
      const out = { items: [dropItem(L + 3, 'rboss'), dropItem(L + 3, 'rboss')], badges: 10, raidmarks: 2 + diff, gold: gpk(L) * 80 * (1 + st.goldP / 100),
        xp: killXP(L) * KIND.rboss.xp * (1 + st.xpP / 100) };
      if (boss.mount && !S.mounts.includes(boss.mount) && chance(boss.mount === 'glutross' ? 0.06 : 0.04)) {
        S.mounts.push(boss.mount);
        out.mount = boss.mount;
        Hooks.toast(`Reittier erbeutet: ${MOUNTS.find((m) => m.id === boss.mount).name}!`, MOUNTS.find((m) => m.id === boss.mount).icon, '#ff8000');
      }
      grantInstanceRewards(out);
      return out;
    },
  });
  return true;
}

function worldBossInfo(t = now()) {
  const d = new Date(t);
  const idx = Math.floor((d.getTime() - d.getTimezoneOffset() * MIN) / (3 * HOUR));
  const start = idx * 3 * HOUR + d.getTimezoneOffset() * MIN;
  const active = t - start < HOUR;
  return { idx, boss: WORLD_BOSSES[idx % WORLD_BOSSES.length], active, endsIn: (start + HOUR - t) / 1000, nextIn: (start + 3 * HOUR - t) / 1000, killed: S.wbKilled === idx };
}

function startWorldBoss() {
  const w = worldBossInfo();
  if (!w.active || w.killed) return false;
  const L = Math.max(mobLevel(S.zoneMax), S.level) + 2;
  startInstance('world', {
    bg: w.boss.bg, title: 'Weltboss', dmgMul: 2.5, healPct: 1,
    queue: [{ key: w.boss.sprite, sprite: w.boss.sprite, name: w.boss.name, level: L, kind: 'wboss', special: w.boss.special }],
    meta: { world: w.idx },
    onEnd: (win) => {
      if (!win) return null;
      S.wbKilled = w.idx;
      S.stats.worldBoss++;
      S.stats.bosses++;
      bumpWeekly('raidKills');
      const st = heroStats();
      const out = { items: [dropItem(L + 3, 'wboss'), dropItem(L + 3, 'wboss')], badges: 15, raidmarks: 2, gold: gpk(L) * 100 * (1 + st.goldP / 100), xp: xpNeed(Math.min(S.level, 59)) * 0.3 };
      grantInstanceRewards(out);
      return out;
    },
  });
  return true;
}

// ------------------------------------------------------------------------------------------ arena
function arenaRank(r) { let n = ARENA_RANKS[0][1]; for (const [v, name] of ARENA_RANKS) if (r >= v) n = name; return n; }
function arenaOpponent() {
  const a = S.arena;
  if (a.opp) return a.opp;
  const st = heroStats();
  const q = clamp((a.rating - 1000) / 1000, 0, 2);
  const ref = refPower(S.level, Math.min(S.level, 60) + (S.worldTier * 8), q < 0.5 ? 2 : q < 1.2 ? 3 : 4, Math.floor(S.level * (0.4 + q * 0.5)));
  const f = clamp(ref / Math.max(1, st.power), 0.45, 2.2) * rnd(0.85, 1.12);
  const cls = pick(Object.keys(CLASSES));
  a.opp = { name: pick(ARENA_NAMES), cls, f, rating: Math.round(a.rating + rnd(-60, 80)), power: Math.round(st.power * f) };
  return a.opp;
}
function startArena() {
  checkDaily();
  const a = S.arena;
  if (a.tickets < 1) return false;
  const o = arenaOpponent();
  a.tickets--;
  const st = heroStats();
  const stats = { maxHp: st.hp * o.f * 1.5, atk: st.hp * 0.075 * o.f, iv: 1.7, crit: 15 };
  startInstance('arena', {
    bg: 'bg_arena', title: 'Arena',
    queue: [{ key: 'rival_' + o.cls, sprite: 'rival_' + o.cls, name: `${o.name} (${CLASSES[o.cls].name})`, level: S.level, kind: 'arena', stats }],
    meta: { arena: true },
    onEnd: (win) => {
      S.stats.arena++;
      const diff = clamp(Math.round(16 + (o.rating - a.rating) / 25), 6, 30);
      const out = { honor: win ? 20 + Math.floor(a.rating / 100) : 6, rating: win ? diff : -Math.round(diff * 0.7), items: [], gold: 0, xp: 0, badges: 0 };
      a.rating = Math.max(0, a.rating + out.rating);
      a.best = Math.max(a.best, a.rating);
      if (win) a.wins++;
      a.opp = null;
      grantInstanceRewards(out);
      return out;
    },
  });
  return true;
}

// ------------------------------------------------------------------------------------------ dailies, weeklies, login
function checkDaily() {
  const t = now();
  const dk = dayKey(t);
  if (!S.daily || S.daily.day !== dk) {
    const r = seeded(dk + S.name);
    const pool = DAILY_POOL.slice();
    const list = [];
    while (list.length < 3) {
      const i = Math.floor(r() * pool.length);
      const q = pool.splice(i, 1)[0];
      if (q.id === 'arena' && S.level < 10) continue;
      if (q.id === 'dungeon' && S.level < 8) continue;
      list.push({ id: q.id, base: S.stats[q.stat] || 0, claimed: false });
    }
    S.daily = { day: dk, list, bonus: false };
    if (S.arena.day !== dk) { S.arena.day = dk; S.arena.tickets = ARENA_TICKETS; S.arena.opp = null; }
    Hooks.dirty('daily');
  }
  checkWeekly();
}
function checkWeekly() {
  const wk = weekKey(now());
  if (!S.weekly || S.weekly.week !== wk) {
    S.weekly = { week: wk, list: WEEKLY.map((w) => ({ id: w.id, base: S.stats[w.stat] || 0, claimed: false })) };
  }
  if (S.raids.week !== wk) S.raids = { week: wk, kills: {} };
}
function bumpWeekly() { /* weekly progress is derived from stats deltas */ }
function questDef(id) { return DAILY_POOL.find((q) => q.id === id) || WEEKLY.find((q) => q.id === id); }
function dqProgress(entry) { const d = questDef(entry.id); return Math.min(d.n, (S.stats[d.stat] || 0) - entry.base); }
function dailyReward(id) {
  const L = Math.min(S.level, 60) + S.worldTier * 8;
  if (id.startsWith('w_')) return { gold: Math.ceil(gpk(L) * 600), raidmarks: 3, badges: 30, chest: 4 };
  return { gold: Math.ceil(gpk(L) * 120), badges: 8, keys: 1 };
}
function claimDaily(entry) {
  if (entry.claimed || dqProgress(entry) < questDef(entry.id).n) return null;
  entry.claimed = true;
  const rw = dailyReward(entry.id);
  grantReward(rw);
  Hooks.sound('quest');
  return rw;
}
function claimDailyBonus() {
  if (!S.daily || S.daily.bonus || !S.daily.list.every((e) => e.claimed)) return null;
  S.daily.bonus = true;
  const rw = { chest: 4, keys: 1 };
  grantReward(rw);
  return rw;
}

function grantReward(rw) {
  const L = Math.min(S.level, 60) + S.worldTier * 8;
  const out = [];
  if (rw.gold) { gainGold(rw.gold); out.push(['gold', fmt(rw.gold)]); }
  if (rw.goldKills) { const v = gainGold(gpk(L) * rw.goldKills); out.push(['gold', fmt(v)]); }
  if (rw.badges) { S.badges += rw.badges; out.push(['badge', rw.badges]); }
  if (rw.raidmarks) { S.raidmarks += rw.raidmarks; out.push(['raidmark', rw.raidmarks]); }
  if (rw.honor) { S.honor += rw.honor; out.push(['honor', rw.honor]); }
  if (rw.keys) { S.keys += rw.keys; out.push(['key', rw.keys]); }
  if (rw.cons) for (const k in rw.cons) { S.cons[k] = (S.cons[k] || 0) + rw.cons[k]; out.push([k, rw.cons[k]]); }
  if (rw.chest) {
    const it = makeItem(L + 1, rollRarity(rw.chest === 5 ? [0, 0, 0, 0, 85, 15] : DROP_TABLE.chest.map((v, i) => (i >= 4 ? v * 2 : v))));
    giveItem(it);
    out.push([itemIcon(it), it.name, it.r]);
  }
  if (rw.mount && !S.mounts.includes(rw.mount)) { S.mounts.push(rw.mount); out.push([MOUNTS.find((m) => m.id === rw.mount).icon, 'Reittier']); }
  Hooks.dirty('reward');
  return out;
}

function checkLogin() {
  const t = now();
  const dk = dayKey(t);
  const L = S.login;
  if (L.last !== dk) {
    const y = dayKey(t - DAY);
    L.streak = L.last === y ? L.streak + 1 : 1;
    L.best = Math.max(L.best, L.streak);
    L.last = dk;
    L.claimed = false;
    S.stats.streak = L.streak;
  }
}
function claimLogin() {
  checkLogin();
  if (S.login.claimed) return null;
  S.login.claimed = true;
  const r = LOGIN_REWARDS[S.login.cycle % 7];
  S.login.cycle++;
  Hooks.sound('quest');
  return { def: r, got: grantReward(r.give) };
}

function chestReady() { return now() >= S.chestT; }
function claimChest() {
  if (!chestReady()) return null;
  S.chestT = now() + 4 * HOUR;
  const L = Math.min(S.level, 60) + S.worldTier * 8;
  const rw = { gold: Math.ceil(gpk(L) * 60), cons: { potion_heal: 2 } };
  const got = grantReward(rw);
  const tier = clamp(Math.floor((S.worldTier > 0 ? 7 : S.zoneMax) / 1.6), 0, 4);
  addMat(ORES[tier], 3); addMat(HERBS[tier], 3);
  got.push([ORES[tier], 3], [HERBS[tier], 3]);
  if (chance(0.5)) { const it = dropItem(L, 'chest'); giveItem(it); got.push([itemIcon(it), it.name, it.r]); }
  Hooks.sound('coin');
  return got;
}

// ------------------------------------------------------------------------------------------ professions
function gatherTier(skill) { return clamp(Math.floor(skill / 60), 0, 4); }
function doGather(kind, active) {
  const p = S.prof[kind === 'ore' ? 'mining' : 'herb'];
  const tier = gatherTier(p.skill);
  const id = (kind === 'ore' ? ORES : HERBS)[tier];
  const n = active ? irnd(2, 3) : 1;
  addMat(id, n);
  if (tier > 0 && chance(0.3)) addMat((kind === 'ore' ? ORES : HERBS)[tier - 1], 1);
  if (p.skill < 300) p.skill++;
  S.stats.gathers += n;
  return [id, n];
}
function activeGather() {
  if (now() < S.gatherCd) return null;
  S.gatherCd = now() + 30000;
  const a = doGather('ore', true), b = doGather('herb', true);
  Hooks.sound('gather');
  return [a, b];
}
function passiveGather(n) {
  const got = {};
  for (let i = 0; i < n; i++) {
    for (const k of ['ore', 'herb']) { const [id, c] = doGather(k, false); got[id] = (got[id] || 0) + c; }
  }
  return got;
}

function smithRecipes() {
  const sk = S.prof.smith.skill;
  return [0, 1, 2, 3, 4].map((t) => ({ tier: t, skill: t * 60, ilvl: TIER_ILVL[t] + S.worldTier * 8, ore: ORES[t], n: 4 + t * 2, gold: Math.ceil(gpk(TIER_ILVL[t]) * 25), ok: sk >= t * 60 }));
}
function craftSmith(tier, slot) {
  const rc = smithRecipes()[tier];
  if (!rc.ok || (S.mats[rc.ore] || 0) < rc.n || S.gold < rc.gold) return null;
  S.mats[rc.ore] -= rc.n;
  S.gold -= rc.gold;
  const sk = S.prof.smith.skill;
  const bonus = clamp((sk - tier * 60) / 60, 0, 1);
  const r = rollRarity([0, 0, 50 - bonus * 20, 38, 11 + bonus * 18, 1 + bonus * 2]);
  const it = makeItem(rc.ilvl + irnd(0, 2), r, slot);
  if (sk < 300 && sk < tier * 60 + 90) S.prof.smith.skill = Math.min(300, sk + 3);
  S.stats.crafts++;
  giveItem(it);
  Hooks.sound('anvil');
  return it;
}
function craftAlchemy(id) {
  const rc = ALCHEMY.find((x) => x.id === id);
  if (!rc || S.prof.alch.skill < rc.skill) return false;
  for (const k in rc.cost) if ((S.mats[k] || 0) < rc.cost[k]) return false;
  for (const k in rc.cost) S.mats[k] -= rc.cost[k];
  S.cons[id] = (S.cons[id] || 0) + rc.out;
  const sk = S.prof.alch.skill;
  if (sk < 300 && sk < rc.skill + 90) S.prof.alch.skill = Math.min(300, sk + 3);
  S.stats.crafts++;
  Hooks.sound('brew');
  return true;
}
function fishCounts() {
  let common = 0, rare = 0;
  for (const f of FISH) { const c = S.mats[f.id] || 0; if (f.rar === 0) common += c; else rare += c; }
  return { common, rare };
}
function takeFish(kind, n) {
  for (const f of FISH) {
    if (n <= 0) break;
    if ((kind === 'common') !== (f.rar === 0)) continue;
    const c = Math.min(n, S.mats[f.id] || 0);
    S.mats[f.id] -= c;
    n -= c;
  }
}
function craftCooking(id) {
  const rc = COOKING.find((x) => x.id === id);
  if (!rc || S.prof.cook.skill < rc.skill) return false;
  const fc = fishCounts();
  if (fc.common < (rc.cost.fishCommon || 0) || fc.rare < (rc.cost.fishRare || 0)) return false;
  takeFish('common', rc.cost.fishCommon || 0);
  takeFish('rare', rc.cost.fishRare || 0);
  S.cons[id] = (S.cons[id] || 0) + rc.out;
  const sk = S.prof.cook.skill;
  if (sk < 300) S.prof.cook.skill = Math.min(300, sk + 4);
  S.stats.crafts++;
  Hooks.sound('brew');
  return true;
}
function useConsumable(id) {
  const c = CONSUMABLES[id];
  if (!c || !c.buff || (S.cons[id] || 0) < 1) return false;
  S.cons[id]--;
  const t = now();
  if (c.buff === 'food') { S.buffs.food = Math.max(S.buffs.foodId === id ? S.buffs.food || t : t, t) + c.dur * 1000; S.buffs.foodId = id; }
  else S.buffs[c.buff] = Math.max(S.buffs[c.buff] || t, t) + c.dur * 1000;
  statsDirty = true;
  Hooks.sound('brew');
  Hooks.dirty('buff');
  return true;
}

function fishTable() {
  const tier = clamp(Math.floor((S.worldTier > 0 ? 7 : S.zone) / 1.6), 0, 4);
  const sk = S.prof.fish.skill;
  const pool = FISH.filter((f) => f.tier === tier);
  const r = Math.random();
  if (r < 0.005 + sk / 300 * 0.01) return FISH.find((f) => f.id === 'fisch_sternenwal');
  if (r < 0.03 + sk / 300 * 0.04) return FISH.find((f) => f.id === 'fisch_goldschuppe');
  if (Math.random() < 0.18 + sk / 300 * 0.2) return pool.find((f) => f.rar === 1);
  return pool.find((f) => f.rar === 0);
}
function catchFish() {
  const f = fishTable();
  addMat(f.id, 1);
  S.fishLog[f.id] = (S.fishLog[f.id] || 0) + 1;
  S.stats.fish++;
  S.stats.fishSpecies = Object.keys(S.fishLog).length;
  if (S.prof.fish.skill < 300) S.prof.fish.skill = Math.min(300, S.prof.fish.skill + 2);
  if (f.rar >= 2) {
    const L = Math.min(S.level, 60) + S.worldTier * 8;
    gainGold(gpk(L) * (f.rar === 3 ? 400 : 100));
  }
  return f;
}
const fishSellValue = (f) => Math.ceil(gpk(Math.min(S.level, 60)) * [2, 6, 50, 200][f.rar]);

// ------------------------------------------------------------------------------------------ expeditions
function makeOffer() {
  const dur = pick(EXP_DURATIONS);
  const type = pick(['gold', 'gold', 'mats', 'item', 'keys', 'badges', 'cons']);
  return { id: Math.random().toString(36).slice(2, 8), name: pick(EXPEDITIONS), dur, type };
}
function offerReward(o) {
  const L = Math.min(S.level, 60) + S.worldTier * 8;
  const m = o.dur / 15;
  const tier = clamp(Math.floor((S.worldTier > 0 ? 7 : S.zoneMax) / 1.6), 0, 4);
  switch (o.type) {
    case 'gold': return { gold: Math.ceil(gpk(L) * 40 * Math.pow(m, 0.9)) };
    case 'mats': return { mats: { [ORES[tier]]: Math.ceil(2 * Math.pow(m, 0.8)), [HERBS[tier]]: Math.ceil(2 * Math.pow(m, 0.8)) } };
    case 'item': return { item: { ilvl: L + 1, r: o.dur >= 240 ? 4 : 3 } };
    case 'keys': return { keys: Math.max(1, Math.floor(Math.pow(m, 0.5))) };
    case 'badges': return { badges: Math.ceil(4 * Math.pow(m, 0.75)) };
    default: return { cons: { potion_heal: Math.ceil(m), [o.dur >= 120 ? 'elixir_xp' : 'elixir_atk']: o.dur >= 60 ? 1 : 0 } };
  }
}
function expSlots() { return 2 + (S.level >= 30 ? 1 : 0); }
function checkOffers() {
  while (S.exp.offers.length < 3) S.exp.offers.push(makeOffer());
}
function sendExpedition(oid) {
  checkOffers();
  if (S.exp.active.length >= expSlots()) return false;
  const i = S.exp.offers.findIndex((o) => o.id === oid);
  if (i < 0) return false;
  const o = S.exp.offers.splice(i, 1)[0];
  o.end = now() + o.dur * MIN;
  o.reward = offerReward(o);
  S.exp.active.push(o);
  S.stats.expeds++;
  checkOffers();
  Hooks.sound('click');
  return true;
}
function collectExpedition(oid) {
  const i = S.exp.active.findIndex((o) => o.id === oid);
  if (i < 0 || S.exp.active[i].end > now()) return null;
  const o = S.exp.active.splice(i, 1)[0];
  const rw = o.reward;
  const got = [];
  if (rw.mats) for (const k in rw.mats) { addMat(k, rw.mats[k]); got.push([k, rw.mats[k]]); }
  if (rw.item) { const it = makeItem(rw.item.ilvl, chance(0.15) ? rw.item.r + 1 : rw.item.r); giveItem(it); got.push([itemIcon(it), it.name, it.r]); }
  const rest = Object.assign({}, rw);
  delete rest.mats; delete rest.item;
  if (rest.cons) for (const k in rest.cons) if (!rest.cons[k]) delete rest.cons[k];
  got.push(...grantReward(rest));
  Hooks.sound('coin');
  return got;
}
function rerollOffers() {
  const cost = Math.ceil(gpk(Math.min(S.level, 60)) * 20);
  if (S.gold < cost) return false;
  S.gold -= cost;
  S.exp.offers = [];
  checkOffers();
  return true;
}

// ------------------------------------------------------------------------------------------ achievements
function achValue(a) {
  switch (a.stat) {
    case 'level': return S.level;
    case 'zones': return S.zonesDone;
    case 'rating': return S.arena.best;
    case 'streak': return S.login.best;
    case 'companions': return COMPANIONS.filter((c) => S.comp[c.id]).length;
    case 'mounts': return S.mounts.length;
    case 'worldTier': return S.wtMax;
    case 'raidUnique': return Object.keys(S.raidEver).length;
    case 'fishSpecies': return Object.keys(S.fishLog).length;
    default: return S.stats[a.stat] || 0;
  }
}
function checkAchievements() {
  for (const a of ACHIEVEMENTS) {
    if (S.ach[a.id]) continue;
    if (achValue(a) >= a.n) {
      S.ach[a.id] = now();
      Hooks.toast(`Erfolg errungen: ${a.name}`, 'trophy', '#ffd200');
      Hooks.log(`<span class="ach">Erfolg errungen: [${a.name}]</span>`);
      Hooks.sound('achievement');
    }
  }
}
function claimAchievement(id) {
  const a = ACHIEVEMENTS.find((x) => x.id === id);
  if (!a || !S.ach[id] || S.achClaimed[id]) return null;
  S.achClaimed[id] = true;
  return grantReward(a.reward);
}

// ------------------------------------------------------------------------------------------ periodic / offline
function regenKeys() {
  const t = now();
  if (S.keys >= KEY_MAX) { S.keyT = t; return; }
  while (S.keys < KEY_MAX && t - S.keyT >= KEY_REGEN) { S.keys++; S.keyT += KEY_REGEN; }
  if (S.keys >= KEY_MAX) S.keyT = t;
}
function nextKeyIn() { return S.keys >= KEY_MAX ? 0 : (S.keyT + KEY_REGEN - now()) / 1000; }

function maxOfflineSec() { return (8 * 3600) + (S.training.offline || 0) * 1200; }

function estimateKillRate() {
  const st = heroStats();
  const L = mobLevel(S.zone);
  const hp = mobBase(L).hp, atk = mobBase(L).atk;
  let compDps = 0;
  for (const c of COMPANIONS) if (S.comp[c.id]) compDps += compPower(c.id) * (c.type === 'dps' ? 1.6 : c.type === 'tank' ? 0.6 : 0.3);
  const dps = st.atk / st.interval * (1 + st.crit / 100 * st.critDmg / 100) + compDps;
  const ttk = hp / dps;
  const dr = Math.min(0.75, st.def / (st.def + 22 * g(L)));
  const taken = atk / 2 * (1 - dr) * ttk;
  let rate = 1 / (ttk + 1.1);
  if (taken > st.hp * 0.7) rate *= 0.35;
  return { rate, L };
}

// Grants progress for `sec` seconds away, in slices so levels gained on the way change the rates.
function offlineProgress(sec, eff) {
  const capped = Math.min(sec, maxOfflineSec());
  const out = { sec: capped, kills: 0, xp: 0, gold: 0, items: 0, sold: 0, best: null, mats: {}, rested: 0, quest: null, levels: 0 };
  const lvl0 = S.level;
  const slices = clamp(Math.ceil(capped / 600), 1, 24);
  const per = capped / slices;
  let made = 0;
  const q0 = currentQuest(S.zone), qs0 = questState(S.zone), p0 = qs0.p;
  for (let i = 0; i < slices; i++) {
    statsDirty = true;
    const st = heroStats();
    const { rate, L } = estimateKillRate();
    const kills = Math.floor(rate * per * eff);
    if (kills <= 0) continue;
    const pen = xpPenalty(S.level, L);
    out.kills += kills;
    out.xp += gainXP(killXP(L) * (1 + st.xpP / 100) * pen * kills);
    out.gold += gainGold(gpk(L) * kills * (1 + st.goldP / 100));
    S.stats.kills += kills;
    const q = currentQuest(S.zone);
    const qs = questState(S.zone);
    if (q && !qs.done) {
      const z = zoneOf(S.zone);
      let n = 0;
      if (q.kind === 'any') n = kills;
      else if (q.kind === 'kill') n = Math.floor(kills * (0.5 + 0.5 / z.mobs.length));
      else if (q.kind === 'collect') n = Math.floor(kills * (0.5 + 0.5 / z.mobs.length) * 0.6);
      if (n > 0) questProgress(q.kind === 'collect' ? 'collect' : 'kill', q.target, S.zone, n);
    }
    const drops = Math.floor(kills * 0.07 * (1 + st.lootP / 100) + Math.random());
    for (let d = 0; d < drops; d++) {
      if (made >= 30) { out.gold += gainGold(gpk(L) * 3); out.sold++; continue; }
      made++;
      const it = dropItem(L, 'normal');
      const res = giveItem(it, true);
      if (res === 'sold') out.sold++; else out.items++;
      if (!out.best || it.r > out.best.r) out.best = it;
    }
    const matDrops = Math.floor(kills * 0.045);
    if (matDrops) {
      const tier = clamp(Math.floor((S.worldTier > 0 ? 7 : S.zone) / 1.6), 0, 4);
      const a = Math.ceil(matDrops / 2), b = Math.floor(matDrops / 2);
      addMat(ORES[tier], a); addMat(HERBS[tier], b);
      out.mats[ORES[tier]] = (out.mats[ORES[tier]] || 0) + a;
      out.mats[HERBS[tier]] = (out.mats[HERBS[tier]] || 0) + b;
    }
  }
  out.levels = S.level - lvl0;
  if (q0 && currentQuest(S.zone) === q0) {
    const qs = questState(S.zone);
    if (qs.p > p0) out.quest = { t: q0.t, gained: qs.p - p0, done: qs.done };
  }
  // rested xp
  if (S.level < MAX_LEVEL && sec > 600) {
    const add = xpNeed(S.level) * 0.05 * (sec / 3600);
    const before = S.rested;
    S.rested = Math.min(xpNeed(S.level) * 1.5, S.rested + add);
    out.rested = S.rested - before;
  }
  statsDirty = true;
  return out;
}

function catchUpProfessions() {
  const t = now();
  let n = 0;
  while (S.gatherT <= t && n < 300) { S.gatherT += 120000; n++; }
  if (S.gatherT <= t) S.gatherT = t + 120000;
  return n ? passiveGather(n) : null;
}

let achTimer = 0;
function periodic(dt) {
  S.stats.playTime += dt;
  regenKeys();
  checkDaily();
  checkLogin();
  checkOffers();
  const got = catchUpProfessions();
  if (got) Hooks.dirty('mats');
  achTimer -= dt;
  if (achTimer <= 0) { achTimer = 2; checkAchievements(); statsDirty = true; }
}

// ------------------------------------------------------------------------------------------ badges for nav
function notifications() {
  const n = { kampf: 0, held: 0, quests: 0, inst: 0, berufe: 0, stadt: 0 };
  if (!S) return n;
  for (let zi = 0; zi <= S.zoneMax; zi++) if (questState(zi).done) n.quests++;
  if (S.daily) for (const e of S.daily.list) if (!e.claimed && dqProgress(e) >= questDef(e.id).n) n.quests++;
  if (S.daily && !S.daily.bonus && S.daily.list.every((e) => e.claimed)) n.quests++;
  if (S.weekly) for (const e of S.weekly.list) if (!e.claimed && dqProgress(e) >= questDef(e.id).n) n.quests++;
  for (const a of ACHIEVEMENTS) if (S.ach[a.id] && !S.achClaimed[a.id]) n.quests++;
  if (talentPoints() > talentSpent()) n.held++;
  if (S.bag.some((it) => itemUpgrade(it) > 0)) n.held++;
  if (S.keys >= KEY_MAX) n.inst++;
  const w = worldBossInfo();
  if (w.active && !w.killed && S.level >= 10) n.inst++;
  if (S.level >= 10 && S.arena.tickets >= ARENA_TICKETS) n.inst++;
  for (const o of S.exp.active) if (o.end <= now()) n.berufe++;
  if (S.exp.active.length < expSlots()) n.berufe++;
  if (now() >= S.gatherCd) n.berufe++;
  if (!S.login.claimed) n.stadt++;
  if (chestReady()) n.stadt++;
  return n;
}
