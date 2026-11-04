// Valdoran — DOM: header frames, action bar, tabbed panel, modals, toasts.
'use strict';

const UI = (() => {
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let tab = 'kampf';
  const sub = { held: 'gear', quests: 'camp', inst: 'dungeon', berufe: 'gather', stadt: 'home' };
  let dirty = true, lastHtml = '', renderT = 0, secT = 0, holding = false, chatDirty = true;
  const logLines = [];
  const U = { mythic: {}, raidDiff: 0, smithTier: 0, vslot: 'weapon', fish: { st: 'idle', t: 0, msg: 'Tippe aufs Wasser, um die Angel auszuwerfen.', last: null },
    confirmReset: false, cls: 'krieger', modal: null };

  // --------------------------------------------------------------------------------------- html helpers
  const CELL = ATLAS.icons.cell || 32, SSC = ATLAS.sprites.scale || 1;
  function ico(name, size = 32, extra = '') {
    const p = ATLAS.icons.map[name];
    if (!p) return '';
    const s = size / CELL, [W, H] = ATLAS.icons.size;
    return `<i class="ico ${extra}" style="width:${size}px;height:${size}px;background-size:${W * s}px ${H * s}px;background-position:-${p[0] * s}px -${p[1] * s}px"></i>`;
  }
  function spr(name, scale = 1, style = '') {
    const r = ATLAS.sprites.map[name];
    if (!r) return '';
    const [W, H] = ATLAS.sprites.size;
    const f = scale / SSC;
    return `<i class="spr" style="width:${(r[2] * f).toFixed(1)}px;height:${(r[3] * f).toFixed(1)}px;background-size:${(W * f).toFixed(1)}px ${(H * f).toFixed(1)}px;background-position:-${(r[0] * f).toFixed(1)}px -${(r[1] * f).toFixed(1)}px;${style}"></i>`;
  }
  const FACES = ATLAS.sprites.faces || {};
  function face(name, box, scale, fx = 0.5, fy = 0.35) {
    const r = ATLAS.sprites.map[name];
    if (!r) return '';
    const f = FACES[name];
    if (f) { fx = f[0]; fy = f[1]; scale = box / Math.max(r[2], r[3]) * SSC * f[2]; }
    if (!scale) scale = box / Math.max(r[2], r[3]) * SSC * 1.5;
    const w = r[2] / SSC * scale, h = r[3] / SSC * scale;
    return spr(name, scale, `left:${Math.round(box / 2 - w * fx)}px;top:${Math.round(box / 2 - h * fy)}px`);
  }
  function heroFace(box) { return face(CLASSES[S.cls].sprite, box, box / 23, 0.53, 0.2); }
  function uiImg(name, w, h, extra = '') { return `<i class="ui-img" style="width:${w}px;height:${h}px;background-image:url(assets/ui/${name}.png);${extra}"></i>`; }
  function bar(cls, frac, label = '', thin = false) {
    return `<div class="bar ${cls}${thin ? ' thin' : ''}"><i style="width:${clamp(frac, 0, 1) * 100}%"></i>${label ? `<span>${label}</span>` : ''}</div>`;
  }
  function btn(label, act, data = {}, cls = '', disabled = false) {
    const d = Object.entries(data).map(([k, v]) => ` data-${k}="${esc(v)}"`).join('');
    return `<button class="btn ${cls}" data-act="${act}"${d}${disabled ? ' disabled' : ''}>${label}</button>`;
  }
  const tm = (endMs, prefix = '') => `<span data-tm="${Math.round(endMs)}" data-pre="${esc(prefix)}"></span>`;
  const curIcon = { gold: 'gold', badges: 'badge', raidmarks: 'raidmark', honor: 'honor', keys: 'key' };
  function rewardHTML(list) {
    return `<div class="rewards">${list.map((x) => {
      const [icon, val, r] = x;
      if (ATLAS.icons.map[icon]) return `<span>${ico(icon, 20)}<span class="${r !== undefined ? 'q' + r : ''}">${typeof val === 'number' ? fmt(val) : esc(val)}</span></span>`;
      return `<span>${esc(val)}</span>`;
    }).join('')}</div>`;
  }
  function rwList(rw) {
    const out = [];
    if (rw.xp) out.push(['xp', fmt(rw.xp) + ' EP']);
    if (rw.gold) out.push(['gold', fmt(rw.gold)]);
    if (rw.badges) out.push(['badge', rw.badges]);
    if (rw.raidmarks) out.push(['raidmark', rw.raidmarks]);
    if (rw.honor) out.push(['honor', rw.honor]);
    if (rw.keys) out.push(['key', rw.keys]);
    if (rw.chest) out.push([rw.chest === 5 ? 'chest_gold' : 'chest_epic', rw.chest === 5 ? 'Champion-Truhe' : 'Epische Truhe']);
    if (rw.item) out.push([rw.item.r >= 4 ? 'chest_epic' : 'chest', `${RARITY[rw.item.r].name}er Gegenstand`]);
    if (rw.mats) for (const k in rw.mats) out.push([k, `${rw.mats[k]}× ${MAT_NAME[k]}`]);
    if (rw.cons) for (const k in rw.cons) if (rw.cons[k]) out.push([k, `${rw.cons[k]}× ${CONSUMABLES[k].name}`]);
    if (rw.mount) out.push([MOUNTS.find((m) => m.id === rw.mount).icon, 'Reittier']);
    return out;
  }
  const L = () => Math.min(S.level, 60) + S.worldTier * 8;

  function itemSlot(it, opts = {}) {
    if (!it) return `<div class="slot empty"><span>${opts.label || ''}</span></div>`;
    const up = opts.noUp ? 0 : itemUpgrade(it);
    return `<div class="slot q${it.r}" data-act="item" data-id="${it.id}" tabindex="0">${ico(itemIcon(it), opts.size || 64)}${it.up ? `<span class="plus">+${it.up}</span>` : ''}<span class="il">${it.ilvl}</span>${up > 0 ? '<b class="upg"></b>' : ''}</div>`;
  }

  function itemTip(it, cmpPower) {
    const st = itemStats(it);
    const lines = [];
    lines.push(`<div class="nm q${it.r}">${esc(it.name)}${it.up ? ` +${it.up}` : ''}</div>`);
    lines.push(`<div class="y">Gegenstandsstufe ${it.ilvl}</div>`);
    lines.push(`<div class="w row between"><span>${SLOT_NAME[it.slot]}</span><span class="d">${RARITY[it.r].name}</span></div>`);
    if (st.atk) lines.push(`<div class="w">+${fmt(st.atk)} Angriff</div>`);
    if (st.hp) lines.push(`<div class="w">+${fmt(st.hp)} Leben</div>`);
    if (st.def) lines.push(`<div class="w">+${fmt(st.def)} Rüstung</div>`);
    for (const [k, v] of it.sec) lines.push(`<div class="g">+${String(v).replace('.', ',')}% ${SECONDARY[k].name}</div>`);
    if (it.r === 5) lines.push('<div class="flavor">„Geschmiedet, als die Sterne noch jung waren.“</div>');
    if (cmpPower !== undefined) {
      const d = cmpPower;
      lines.push(`<div class="${d > 0 ? 'g' : d < 0 ? 'r' : 'd'}" style="margin-top:4px">Kampfkraft ${d > 0 ? '+' : ''}${fmt(d)} gegenüber angelegt</div>`);
    }
    lines.push(`<div class="d" style="margin-top:4px">Verkaufspreis: ${fmt(sellValue(it))} Gold</div>`);
    return `<div class="tip">${lines.join('')}</div>`;
  }

  // --------------------------------------------------------------------------------------- toasts, log
  function toast(text, icon, color) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.style.setProperty('--tc', color || '#c8a050');
    el.innerHTML = `${icon ? ico(icon, 24) : ''}<span>${esc(text)}</span>`;
    $('toasts').appendChild(el);
    while ($('toasts').children.length > 3) $('toasts').firstChild.remove();
    setTimeout(() => el.classList.add('out'), 2600);
    setTimeout(() => el.remove(), 3100);
  }
  function log(html) {
    logLines.push(html);
    if (logLines.length > 60) logLines.shift();
    chatDirty = true;
  }

  // --------------------------------------------------------------------------------------- static shell
  const TABS = [
    ['kampf', 'Kampf', 'swords'], ['held', 'Held', 'a_head_2'], ['quests', 'Quests', 'scroll'],
    ['inst', 'Instanzen', 'portal'], ['berufe', 'Berufe', 'tools'], ['stadt', 'Stadt', 'castle'],
  ];
  function buildShell() {
    $('tabs').innerHTML = TABS.map(([id, label, icon]) => `<button data-act="tab" data-t="${id}" id="tab-${id}">${ico(icon, 32)}<span class="lbl">${label}</span></button>`).join('');
    $('cGoldI').innerHTML = ico('gold', 16);
    $('cBadgeI').innerHTML = ico('badge', 16);
    $('cKeyI').innerHTML = ico('key', 16);
    $('btnMenu').innerHTML = ico('cog', 22);
    if (S) buildActionbar();
  }
  function buildActionbar() {
    const cls = CLASSES[S.cls];
    let h = '';
    cls.skills.forEach((id, i) => {
      const sk = SKILLS[id];
      h += `<button class="abtn" id="sk-${id}" data-act="cast" data-id="${id}" aria-label="${esc(sk.name)} wirken">${ico(sk.icon, 44)}<span class="cd"></span><span class="cdt"></span><span class="key">${i + 1}</span></button>`;
    });
    h += `<button class="abtn" id="ab-potion" data-act="potioninfo" aria-label="Heiltrank">${ico('potion_heal', 44)}<span class="cnt" id="potCnt"></span></button>`;
    h += '<span class="spacer"></span>';
    h += '<span id="abExtra"></span>';
    $('actionbar').innerHTML = h;
  }
  function pulseSkill(id) {
    const el = $('sk-' + id);
    if (!el) return;
    el.classList.remove('pulse');
    void el.offsetWidth;
    el.classList.add('pulse');
  }

  // --------------------------------------------------------------------------------------- per-frame updates
  let lastTarget = null, lastHeroFace = null, abExtra = '';
  function frameUpdate() {
    if (!S) return;
    const st = heroStats();
    const b = battle;
    // player frame
    if (lastHeroFace !== S.cls) { $('pFace').innerHTML = heroFace(52); lastHeroFace = S.cls; $('pResBar').className = 'bar thin ' + CLASSES[S.cls].resBar; }
    $('pLvl').textContent = S.level;
    $('pName').textContent = S.name;
    $('pTitle').textContent = S.title || CLASSES[S.cls].name;
    const hp = b ? Math.max(0, b.h.hp) : st.hp;
    $('pHp').style.width = (hp / st.hp * 100) + '%';
    $('pHpT').textContent = `${fmt(hp)} / ${fmt(st.hp)}`;
    const res = b ? b.h.res : 100;
    $('pRes').style.width = res + '%';
    $('pResT').textContent = `${Math.floor(res)} ${CLASSES[S.cls].res}`;
    $('cGold').textContent = fmt(S.gold);
    $('cBadge').textContent = fmt(S.badges);
    $('cKey').textContent = S.keys;
    // xp
    if (S.level >= MAX_LEVEL) {
      const need = paragonNeed(S.paragon);
      $('xpFill').style.width = (S.pxp / need * 100) + '%';
      $('xpRested').style.width = '0';
      $('xpText').textContent = `Ruhmstufe ${S.paragon} — ${fmt(S.pxp)} / ${fmt(need)}`;
    } else {
      const need = xpNeed(S.level);
      $('xpFill').style.width = (S.xp / need * 100) + '%';
      $('xpRested').style.width = Math.min(100, (S.xp + S.rested) / need * 100) + '%';
      $('xpText').textContent = `EP ${fmt(S.xp)} / ${fmt(need)} (${(S.xp / need * 100).toFixed(1).replace('.', ',')}%)${S.rested > 0 ? ' · Erholt' : ''}`;
    }
    // target frame
    const e = b && b.enemy;
    const tf = $('targetFrame');
    if (e && !e.dead && b.h.dead <= 0) {
      tf.hidden = false;
      if (lastTarget !== e) {
        lastTarget = e;
        tf.className = 'unit target ' + (e.kind === 'normal' || e.kind === 'arena' ? '' : e.kind === 'elite' ? 'elite' : 'boss');
        mmKey = '';
        $('tFace').innerHTML = face(e.sprite, 36);
        $('tName').textContent = e.name;
        $('tName').parentElement.className = 'uname ' + (e.kind === 'elite' ? 'elite' : e.kind === 'normal' || e.kind === 'arena' ? '' : 'boss');
        $('tLvl').textContent = e.kind === 'normal' || e.kind === 'arena' ? e.level : e.kind === 'elite' ? e.level + '+' : '??';
        $('tKind').textContent = { normal: '', elite: 'Elite', boss: 'Boss', dboss: 'Dungeonboss', rboss: 'Raidboss', wboss: 'Weltboss', arena: 'Gegner' }[e.kind];
      }
      $('tHp').style.width = (Math.max(0, e.hp) / e.maxHp * 100) + '%';
      $('tHpT').textContent = `${fmt(Math.max(0, e.hp))} (${Math.ceil(Math.max(0, e.hp) / e.maxHp * 100)}%)`;
    } else tf.hidden = true;
    // instance bar / zone tag
    const inst = b && b.mode !== 'adventure';
    $('instBar').hidden = !inst;
    $('zoneTag').hidden = inst;
    $('leaveBtn').hidden = !inst || !!b.result;
    if (inst) {
      const lim = e ? (b.mode === 'arena' ? KIND.arena.limit : KIND[e.kind].limit) : 0;
      const done = b.total - b.queue.length - (e && !e.dead ? 1 : 0);
      $('instTitle').textContent = b.title;
      $('instInfo').innerHTML = lim && e ? `Boss ${Math.min(b.total, done + 1)}/${b.total} · Zeit ${Math.max(0, Math.ceil(lim - b.t))}s` : `Boss ${done}/${b.total}`;
      $('instTime').style.width = lim && e ? (Math.max(0, 1 - b.t / lim) * 100) + '%' : '100%';
    }
    minimap(b);
    // skill cooldowns
    for (const id of CLASSES[S.cls].skills) {
      const el = $('sk-' + id);
      if (!el) continue;
      const sk = SKILLS[id];
      const locked = S.level < sk.lvl;
      el.classList.toggle('locked', locked);
      const state = locked ? 'locked' : skillState(id);
      el.classList.toggle('ready', state === 'ready');
      el.classList.toggle('nores', state === 'res');
      const cd = b ? Math.max(0, b.cd[id] || 0) : 0;
      const full = sk.cd * (1 - st.cdr / 100);
      el.children[1].style.setProperty('--p', locked ? 1 : cd / full);
      el.children[2].textContent = locked ? sk.lvl : cd > 0.05 ? Math.ceil(cd) : '';
    }
    $('potCnt').textContent = S.cons.potion_heal || 0;
    // extra action button (boss / leave)
    let ex = '';
    if (!inst && bossAvailable(S.zone)) ex = btn(`${ico('skull', 18)} Boss`, 'boss', { z: S.zone }, 'sm');
    if (ex !== abExtra) { $('abExtra').innerHTML = ex; abExtra = ex; }
    document.body.classList.toggle('compact', tab !== 'kampf');
  }

  let mmKey = '';
  function minimap(b) {
    const inst = b && b.mode !== 'adventure';
    const z = zoneOf(S.zone);
    const bg = b ? b.bg : z.bg;
    const q = currentQuest(S.zone), qs = questState(S.zone);
    const key = bg + (inst ? b.title : z.name) + S.worldTier + (q ? qs.i + ':' + qs.done : 'x');
    if (key === mmKey) return;
    mmKey = key;
    $('mmZone').textContent = inst ? b.title : z.name;
    $('mmMap').style.backgroundImage = `url(assets/bg/${bg}.webp)`;
    const r = seeded(bg);
    let dots = '';
    for (let i = 0; i < 4; i++) {
      const a = r() * Math.PI * 2, d = 0.35 + r() * 0.5;
      dots += `<i class="mm-dot" style="left:${50 + Math.cos(a) * d * 42}%;top:${50 + Math.sin(a) * d * 42}%"></i>`;
    }
    if (!inst && q) {
      const a = r() * Math.PI * 2;
      dots += `<i class="mm-q" style="left:${50 + Math.cos(a) * 26}%;top:${50 + Math.sin(a) * 26}%;background-image:url(assets/ui/${qs.done ? 'q_turnin' : 'q_bang'}.png)"></i>`;
    }
    $('mmDots').innerHTML = dots;
  }

  function secondUpdate() {
    const d = new Date();
    $('mmClock').textContent = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    const t = now();
    document.querySelectorAll('[data-tm]').forEach((el) => {
      const left = (+el.dataset.tm - t) / 1000;
      el.textContent = left > 0 ? el.dataset.pre + fmtTime(left) : 'Bereit!';
    });
    document.querySelectorAll('[data-pg]').forEach((el) => {
      const [a, b] = el.dataset.pg.split(',').map(Number);
      el.style.width = clamp((t - a) / (b - a), 0, 1) * 100 + '%';
    });
    const n = notifications();
    for (const [id] of TABS) {
      const tb = $('tab-' + id);
      const has = n[id] > 0;
      let d = tb.querySelector('.dot');
      if (has && !d) { d = document.createElement('b'); d.className = 'dot'; tb.appendChild(d); }
      if (!has && d) d.remove();
      tb.classList.toggle('on', tab === id);
    }
  }

  function update(dt) {
    if (!S) return;
    frameUpdate();
    renderT -= dt;
    secT -= dt;
    if (secT <= 0) { secT = 1; secondUpdate(); dirty = true; }
    if (renderT <= 0 && dirty && !holding) { renderT = 0.35; dirty = false; renderPanel(); }
    if (chatDirty) renderChat();
    if (tab === 'berufe' && sub.berufe === 'fish') fishUpdate(dt);
  }

  function renderPanel() {
    const html = (VIEWS[tab] || VIEWS.kampf)();
    if (html !== lastHtml) {
      const p = $('panel');
      p.innerHTML = html;
      lastHtml = html;
      chatDirty = true;
      secondUpdate();
    }
  }
  function renderChat() {
    const c = $('chat');
    if (!c) return;
    chatDirty = false;
    c.innerHTML = logLines.slice(-30).map((l) => `<div>${l}</div>`).join('');
    c.scrollTop = c.scrollHeight;
  }
  function forceRender() { lastHtml = ''; dirty = true; renderT = 0; }

  function subtabs(group, items) {
    const n = notifications();
    return `<div class="subtabs">${items.map(([id, label, flag]) => `<button class="${sub[group] === id ? 'on' : ''}" data-act="sub" data-g="${group}" data-s="${id}">${label}${flag ? '<b class="dot"></b>' : ''}</button>`).join('')}</div>`;
    void n;
  }

  // --------------------------------------------------------------------------------------- views
  const VIEWS = {};

  VIEWS.kampf = () => {
    const z = zoneOf(S.zone);
    const q = currentQuest(S.zone);
    const qs = questState(S.zone);
    let h = '';
    if (!S.tut.skills) h += `<div class="card plain"><div class="row">${ico(SKILLS[CLASSES[S.cls].skills[0]].icon, 32)}<div class="grow small"><b class="goldtxt">Tipp:</b> Deine Fähigkeiten wirkst du selbst: Tippe auf einen leuchtenden Knopf in der Aktionsleiste (am Computer auch 1, 2, 3). Gedrückt halten zeigt, was er tut. Den Waffenangriff macht dein Held von allein, auch offline. Ein Tipp auf die Kampfszene gibt Extraschaden.</div>${btn('OK', 'tut', { k: 'skills' }, 'sm')}</div></div>`;
    // quest tracker
    if (q) {
      const need = questN(S.zone, q);
      h += `<div class="card"><div class="row">${uiImg(qs.done ? 'q_turnin' : 'q_bang', 20, 32)}<div class="grow"><h3 style="margin:0">${esc(q.t)}</h3><div class="small muted">${esc(z.giver)} · ${esc(z.name)} (${qs.i + 1}/6)</div></div></div>
        <div class="small" style="margin:6px 0 4px">${questObjective(q, qs, need)}</div>${bar('yellow', qs.p / need, `${qs.p} / ${need}`, true)}
        <div class="row wrap" style="margin-top:8px">${qs.done ? btn(`${uiImg('q_turnin', 10, 16)} Quest abgeben`, 'turnin', { z: S.zone }, 'gold') : ''}${q.kind === 'boss' && !qs.done ? btn(`${ico('skull', 18)} ${esc(MOBS[q.target])} herausfordern`, 'boss', { z: S.zone }) : ''}</div></div>`;
    } else if (S.zone < ZONES.length - 1 && S.zoneMax > S.zone) {
      h += `<div class="card plain"><div class="row">${ico('map', 32)}<div class="grow small">Die Kampagne in ${esc(z.name)} ist abgeschlossen. Neue Abenteuer warten in <b class="goldtxt">${esc(ZONES[S.zoneMax].name)}</b>.</div>${btn('Reisen', 'travel', { z: S.zoneMax }, 'sm gold')}</div></div>`;
    } else if (S.wtMax > 0) {
      h += `<div class="card plain"><div class="row">${ico('star', 32)}<div class="grow small">Du hast die Welt gerettet. In den <b class="goldtxt">Weltstufen</b> werden alle Gebiete stärker und die Beute besser.</div></div></div>`;
    }
    // zone + world tier
    h += `<div class="row">${btn(`${ico('map', 18)} Karte`, 'zones', {}, 'sm')}${S.wtMax > 0 ? `<span class="stepper">${btn('−', 'wt', { d: -1 }, 'sm', S.worldTier <= 0)}<b>Weltstufe ${S.worldTier}</b>${btn('+', 'wt', { d: 1 }, 'sm', S.worldTier >= S.wtMax)}</span>` : ''}<span class="grow"></span><span class="small muted">${fmt(estimateKillRate().rate * 3600)} Siege/Std</span></div>`;
    // events
    h += `<div class="section-title">Ereignisse</div><div class="events">${eventTiles()}</div>`;
    // buffs & consumables
    const cons = Object.keys(CONSUMABLES).filter((k) => k !== 'potion_heal' && (S.cons[k] || 0) > 0);
    const buffs = activeBuffs();
    if (cons.length || buffs.length) {
      h += `<div class="section-title">Stärkungen</div><div class="stack">`;
      for (const bf of buffs) h += `<div class="li">${ico(bf.icon, 28)}<div class="grow"><div class="ttl">${esc(bf.name)}</div><div class="small muted">${esc(bf.desc)}</div></div><span class="small goldtxt">${tm(bf.end)}</span></div>`;
      if (cons.length) h += `<div class="row wrap">${cons.map((k) => `<button class="ev" style="flex:1 1 140px" data-act="usecons" data-id="${k}">${ico(k, 28)}<div><b>${esc(CONSUMABLES[k].name)} ×${S.cons[k]}</b><small>Benutzen</small></div></button>`).join('')}</div>`;
      h += '</div>';
    }
    h += `<div class="section-title">Chronik</div><div class="chat" id="chat"></div>`;
    return h;
  };

  function questObjective(q, qs, need) {
    switch (q.kind) {
      case 'kill': return `${esc(MOBS[q.target])} getötet: ${qs.p}/${need}`;
      case 'collect': return `${esc(q.item)}: ${qs.p}/${need} <span class="muted">(von ${esc(MOBS[q.target])})</span>`;
      case 'elite': return `${esc(MOBS[q.target])} besiegt <span class="muted">(Elite, erscheint im Gebiet)</span>`;
      case 'any': return `Kreaturen in ${esc(zoneOf(S.zone).name)} besiegt: ${qs.p}/${need}`;
      case 'boss': return `${esc(MOBS[q.target])} besiegt <span class="muted">(Boss, 60 Sek. Zeitlimit)</span>`;
    }
    return '';
  }

  function activeBuffs() {
    const t = now(), out = [];
    const b = S.buffs;
    const map = { atk: 'elixir_atk', xp: 'elixir_xp', luck: 'elixir_luck', titan: 'flask_titan' };
    for (const k in map) if (b[k] > t) out.push({ icon: map[k], name: CONSUMABLES[map[k]].name, desc: CONSUMABLES[map[k]].desc, end: b[k] });
    if (b.food > t && b.foodId) out.push({ icon: b.foodId, name: CONSUMABLES[b.foodId].name, desc: CONSUMABLES[b.foodId].desc, end: b.food });
    return out;
  }

  function eventTiles() {
    const t = now();
    const tiles = [];
    if (!S.login.claimed) tiles.push(`<button class="ev hot" data-act="login">${ico('gift', 32)}<div><b>Tagesbelohnung</b><small>Tag ${S.login.cycle % 7 + 1} abholen</small></div></button>`);
    tiles.push(chestReady() ? `<button class="ev hot" data-act="chest">${ico('chest', 32)}<div><b>Versorgungskiste</b><small>Jetzt öffnen!</small></div></button>`
      : `<button class="ev" data-act="noop">${ico('chest', 32)}<div><b>Versorgungskiste</b><small>${tm(S.chestT, 'in ')}</small></div></button>`);
    if (S.level >= 10) {
      const w = worldBossInfo(t);
      tiles.push(w.active && !w.killed ? `<button class="ev hot" data-act="gotoinst" data-s="world">${ico('raid', 32)}<div><b>${esc(w.boss.name)}</b><small>Weltboss aktiv · ${tm(t + w.endsIn * 1000)}</small></div></button>`
        : `<button class="ev" data-act="gotoinst" data-s="world">${ico('raid', 32)}<div><b>Weltboss</b><small>${w.killed && w.active ? 'Besiegt · nächster ' : 'Nächster '}${tm(t + w.nextIn * 1000, 'in ')}</small></div></button>`);
    }
    const doneEx = S.exp.active.filter((o) => o.end <= t).length;
    tiles.push(`<button class="ev ${doneEx ? 'hot' : ''}" data-act="gotoberufe" data-s="exp">${ico('flag', 32)}<div><b>Expeditionen</b><small>${doneEx ? `${doneEx} zurückgekehrt!` : `${S.exp.active.length}/${expSlots()} unterwegs`}</small></div></button>`);
    tiles.push(`<button class="ev ${S.keys >= KEY_MAX ? 'hot' : ''}" data-act="gotoinst" data-s="dungeon">${ico('key', 32)}<div><b>Schlüssel ${S.keys}/${KEY_MAX}</b><small>${S.keys >= KEY_MAX ? 'Voll – ab in den Dungeon!' : tm(t + nextKeyIn() * 1000, 'nächster in ')}</small></div></button>`);
    const gReady = t >= S.gatherCd;
    tiles.push(`<button class="ev ${gReady ? 'hot' : ''}" data-act="gotoberufe" data-s="gather">${ico('pickaxe', 32)}<div><b>Sammeln</b><small>${gReady ? 'Bereit' : tm(S.gatherCd, 'in ')}</small></div></button>`);
    return tiles.join('');
  }

  // ------------------------------------------------------------------ Held
  VIEWS.held = () => {
    const n = talentPoints() - talentSpent();
    let h = subtabs('held', [['gear', 'Ausrüstung'], ['bag', `Taschen ${S.bag.length}/${BAG_SIZE}`, S.bag.some((it) => itemUpgrade(it) > 0)], ['tal', 'Talente', n > 0]]);
    if (sub.held === 'gear') h += viewGear();
    else if (sub.held === 'bag') h += viewBag();
    else h += viewTalents();
    return h;
  };
  function viewGear() {
    const st = heroStats();
    const left = ['head', 'shoulder', 'chest', 'legs'], right = ['weapon', 'hands', 'feet', 'trinket'];
    const col = (slots) => `<div class="col">${slots.map((s) => itemSlot(S.gear[s], { label: SLOT_NAME[s], noUp: true })).join('')}</div>`;
    const il = SLOTS.reduce((a, s) => a + (S.gear[s] ? S.gear[s].ilvl : 0), 0) / SLOTS.length;
    const canBest = S.bag.some((it) => itemUpgrade(it) > 0);
    const mount = MOUNTS.find((m) => m.id === S.mount);
    let h = `<div class="card"><div class="doll">${col(left)}<div class="center">
      <div class="power"><span>Kampfkraft</span><b>${fmt(st.power)}</b></div>
      ${spr(CLASSES[S.cls].sprite, 2)}
      <div class="small muted" style="text-align:center">${esc(CLASSES[S.cls].name)} · Stufe ${S.level}<br>Ø Gegenstandsstufe ${il.toFixed(1).replace('.', ',')}${mount ? `<br>Reittier: ${esc(mount.name)}` : ''}</div>
    </div>${col(right)}</div>
    <div style="margin-top:8px">${btn(`${ico('star', 18)} Beste Ausrüstung anlegen`, 'bestgear', {}, `wide ${canBest ? 'gold' : ''}`, !canBest)}</div></div>`;
    const P = (v) => v.toFixed(1).replace('.', ',') + '%';
    h += `<div class="card"><h3>Werte</h3><div class="stats">
      <div><span>Angriff</span><b>${fmt(st.atk)}</b></div><div><span>Leben</span><b>${fmt(st.hp)}</b></div>
      <div><span>Rüstung</span><b>${fmt(st.def)}</b></div><div><span>Angriffe/Sek.</span><b>${(1 / st.interval).toFixed(2).replace('.', ',')}</b></div>
      <div><span>Kritisch</span><b>${P(st.crit)}</b></div><div><span>Krit.-Schaden</span><b>${P(100 + st.critDmg)}</b></div>
      <div><span>Tempo</span><b>${P(st.haste)}</b></div><div><span>Fähigkeiten</span><b>+${P(st.skillP)}</b></div>
      <div><span>Bossschaden</span><b>+${P(st.bossP)}</b></div><div><span>Abklingzeit</span><b>−${P(st.cdr)}</b></div>
      <div><span>Goldfund</span><b>+${P(st.goldP)}</b></div><div><span>Erfahrung</span><b>+${P(st.xpP)}</b></div>
      <div><span>Beutechance</span><b>+${P(st.lootP)}</b></div><div><span>Regeneration</span><b>${P(st.regen + 0.4)}/s</b></div>
      <div><span>Tippschaden</span><b>${fmt(st.atk * 0.35 * (1 + st.tapP / 100))}</b></div><div><span>Ruhmstufe</span><b>${S.paragon}</b></div>
    </div><div class="small muted" style="margin-top:6px">Treuebonus: +${Math.min(30, S.login.streak)}% Gold (${S.login.streak} Tage in Folge)</div></div>`;
    return h;
  }
  function viewBag() {
    let h = '';
    const cons = Object.keys(CONSUMABLES).filter((k) => (S.cons[k] || 0) > 0);
    h += `<div class="card plain"><div class="row between"><b class="h3" style="margin:0">Verbrauchbares</b><span class="small muted">${ico('dust', 18)} ${fmt(S.mats.dust || 0)} Arkanstaub</span></div>
      <div class="row wrap" style="margin-top:6px">${cons.length ? cons.map((k) => `<button class="ev" style="flex:1 1 130px" data-act="usecons" data-id="${k}">${ico(k, 28)}<div><b>${esc(CONSUMABLES[k].name)} ×${S.cons[k]}</b><small>${k === 'potion_heal' ? 'automatisch' : 'Benutzen'}</small></div></button>`).join('') : '<span class="small muted">Nichts dabei. Tränke stellst du mit Alchemie her.</span>'}</div></div>`;
    const sorted = S.bag.slice().sort((a, b) => b.r - a.r || b.ilvl - a.ilvl);
    h += `<div class="row wrap">${btn('Graues & Weißes verkaufen', 'sellall', { r: 1 }, 'sm')}${btn('Grünes entzaubern', 'salvageall', { r: 2 }, 'sm')}${btn('Beste anlegen', 'bestgear', {}, 'sm gold')}</div>`;
    h += `<div class="grid">${sorted.map((it) => itemSlot(it)).join('')}${Array.from({ length: Math.max(0, 10 - sorted.length) }, () => itemSlot(null)).join('')}</div>`;
    h += '<div class="small muted">Grüner Pfeil: besser als dein angelegtes Teil. Tippe auf einen Gegenstand für Details.</div>';
    return h;
  }
  function viewTalents() {
    const tal = TALENTS[S.cls];
    const spent = talentSpent(), pts = talentPoints();
    let h = `<div class="card plain"><div class="row between"><div><b class="h3">${esc(CLASSES[S.cls].name)}-Talente</b><div class="small muted">1 Punkt pro Stufe ab Stufe 5. Jede Reihe braucht 5 Punkte mehr.</div></div><div style="text-align:right"><b class="goldtxt" style="font:700 20px var(--f-display)">${pts - spent}</b><div class="small muted">verfügbar</div></div></div></div>`;
    h += '<div class="card"><div class="talents">';
    for (let i = 0; i < tal.length; i++) {
      if (i % 3 === 0) h += `<div class="tier-lbl">Reihe ${i / 3 + 1}${spent < i / 3 * 5 ? ` · ab ${i / 3 * 5} Punkten` : ''}</div>`;
      const [name, , , max, icon] = tal[i];
      const rk = S.talents[i] || 0;
      const tierOk = spent >= Math.floor(i / 3) * 5;
      const cls = rk >= max ? 'max' : !tierOk ? 'lock' : pts > spent ? 'av' : '';
      h += `<div class="tal ${cls}" data-act="tal" data-i="${i}">${ico(icon, 48)}<span class="rk">${rk}/${max}</span><small>${esc(name)}</small></div>`;
    }
    h += `</div><div style="margin-top:8px">${btn(`Talente zurücksetzen (${fmt(talentResetCost())} Gold)`, 'talreset', {}, 'sm wide', spent === 0)}</div></div>`;
    return h;
  }

  // ------------------------------------------------------------------ Quests
  VIEWS.quests = () => {
    const n = notifications();
    let campReady = false;
    for (let zi = 0; zi <= S.zoneMax; zi++) if (questState(zi).done) campReady = true;
    const dailyReady = S.daily && (S.daily.list.some((e) => !e.claimed && dqProgress(e) >= questDef(e.id).n) || (!S.daily.bonus && S.daily.list.every((e) => e.claimed)) || S.weekly.list.some((e) => !e.claimed && dqProgress(e) >= questDef(e.id).n));
    const achReady = ACHIEVEMENTS.some((a) => S.ach[a.id] && !S.achClaimed[a.id]);
    void n;
    let h = subtabs('quests', [['camp', 'Kampagne', campReady], ['daily', 'Täglich', dailyReady], ['ach', 'Erfolge', achReady]]);
    if (sub.quests === 'camp') h += viewCampaign();
    else if (sub.quests === 'daily') h += viewDaily();
    else h += viewAch();
    return h;
  };
  function viewCampaign() {
    let h = '';
    for (let zi = S.zoneMax; zi >= 0; zi--) {
      const z = ZONES[zi];
      const qs = questState(zi);
      const q = currentQuest(zi);
      if (!q) {
        h += `<div class="li done">${ico('trophy', 28)}<div class="grow"><div class="ttl gold">${esc(z.name)}</div><div class="small muted">Kampagne abgeschlossen · Stufe ${z.lvl[0]}–${z.lvl[1]}</div></div>${zi !== S.zone ? btn('Reisen', 'travel', { z: zi }, 'sm') : '<span class="small muted">Hier</span>'}</div>`;
        continue;
      }
      const need = questN(zi, q);
      const rw = questRewards(zi, qs.i);
      h += `<div class="parch"><div class="row">${uiImg(qs.done ? 'q_turnin' : 'q_bang', 20, 32)}<div class="grow"><h3 style="margin:0">${esc(q.t)}</h3><div class="small muted">${esc(z.giver)} · ${esc(z.name)} · Quest ${qs.i + 1}/6</div></div></div>
        <p>${esc(q.txt)}</p><div class="obj small">${questObjectiveFor(zi, q, qs, need)}</div>
        <div class="small" style="margin:6px 0 2px"><b>Belohnung:</b></div>${rewardHTML(rwList(rw))}
        <div class="row wrap" style="margin-top:8px">${qs.done ? btn('Quest abgeben', 'turnin', { z: zi }, 'gold') : ''}${q.kind === 'boss' && !qs.done ? btn('Boss herausfordern', 'boss', { z: zi }) : ''}${zi !== S.zone ? btn('Hinreisen', 'travel', { z: zi }, 'sm') : ''}</div></div>`;
    }
    if (S.zoneMax < ZONES.length - 1) h += `<div class="li done">${ico('lock', 28)}<div class="grow"><div class="ttl">${esc(ZONES[S.zoneMax + 1].name)}</div><div class="small muted">Schließe die Kampagne in ${esc(ZONES[S.zoneMax].name)} ab.</div></div></div>`;
    return h;
  }
  function questObjectiveFor(zi, q, qs, need) {
    const z = ZONES[zi];
    switch (q.kind) {
      case 'kill': return `${esc(MOBS[q.target])} getötet: ${qs.p}/${need}`;
      case 'collect': return `${esc(q.item)}: ${qs.p}/${need}`;
      case 'elite': return `${esc(MOBS[q.target])} besiegt: ${qs.p}/1`;
      case 'any': return `Kreaturen in ${esc(z.name)} besiegt: ${qs.p}/${need}`;
      case 'boss': return `${esc(MOBS[q.target])} besiegt: ${qs.p}/1`;
    }
    return '';
  }
  function dqRow(e, i, weekly) {
    const d = questDef(e.id);
    const p = dqProgress(e);
    const ok = p >= d.n;
    const rw = dailyReward(e.id);
    return `<div class="li ${e.claimed ? 'done' : ok ? 'claim' : ''}">${ico(d.icon, 32)}<div class="grow"><div class="ttl gold">${esc(d.name)}</div><div class="small">${esc(d.desc.replace('{n}', fmt(d.n)))}</div>
      ${bar('yellow', p / d.n, `${fmt(p)} / ${fmt(d.n)}`, true)}<div style="margin-top:4px">${rewardHTML(rwList(rw))}</div></div>
      ${e.claimed ? '<span class="small muted">Erledigt</span>' : btn('Abholen', weekly ? 'wq' : 'dq', { i }, 'sm gold', !ok)}</div>`;
  }
  function viewDaily() {
    checkDaily();
    let h = `<div class="row between"><div class="section-title" style="flex:1">Tagesquests</div><span class="small muted">Neu in ${tm(nextMidnight(now()))}</span></div>`;
    h += `<div class="stack">${S.daily.list.map((e, i) => dqRow(e, i, false)).join('')}</div>`;
    const all = S.daily.list.every((e) => e.claimed);
    h += `<div class="li ${S.daily.bonus ? 'done' : all ? 'claim' : ''}">${ico('chest_epic', 32)}<div class="grow"><div class="ttl gold">Tagesbonus</div><div class="small">Erledige alle drei Tagesquests.</div>${rewardHTML([['chest_epic', 'Epische Truhe'], ['key', 1]])}</div>${S.daily.bonus ? '<span class="small muted">Erledigt</span>' : btn('Öffnen', 'dqbonus', {}, 'sm gold', !all)}</div>`;
    h += `<div class="row between"><div class="section-title" style="flex:1">Wochenquests</div><span class="small muted">Neu in ${tm(weekStart(now()) + 7 * DAY)}</span></div>`;
    h += `<div class="stack">${S.weekly.list.map((e, i) => dqRow(e, i, true)).join('')}</div>`;
    return h;
  }
  function viewAch() {
    const done = Object.keys(S.ach).length;
    const titles = ACHIEVEMENTS.filter((a) => a.title && S.ach[a.id]);
    let h = `<div class="card plain"><div class="row between"><b class="h3" style="margin:0">${done} / ${ACHIEVEMENTS.length} Erfolge</b>${titles.length ? `<select id="titleSel" data-act="titlesel"><option value="">Kein Titel</option>${titles.map((a) => `<option ${S.title === a.title ? 'selected' : ''}>${esc(a.title)}</option>`).join('')}</select>` : ''}</div></div>`;
    const list = ACHIEVEMENTS.slice().sort((a, b) => (!!S.achClaimed[a.id] - !!S.achClaimed[b.id]) || (!!S.ach[b.id] - !!S.ach[a.id]));
    h += '<div class="stack">';
    for (const a of list) {
      const v = Math.min(a.n, achValue(a));
      const got = !!S.ach[a.id], claimed = !!S.achClaimed[a.id];
      h += `<div class="li ${claimed ? 'done' : got ? 'claim' : ''}">${ico(got ? 'trophy' : 'lock', 32)}<div class="grow"><div class="ttl gold">${esc(a.name)}</div><div class="small">${esc(a.desc)}${a.title ? ` · Titel: <i>${esc(a.title)}</i>` : ''}</div>
        ${got ? '' : bar('yellow', v / a.n, `${fmt(v)} / ${fmt(a.n)}`, true)}<div style="margin-top:3px">${rewardHTML(rwList(a.reward))}</div></div>${claimed ? '' : btn('Abholen', 'ach', { id: a.id }, 'sm gold', !got)}</div>`;
    }
    return h + '</div>';
  }

  // ------------------------------------------------------------------ Instanzen
  VIEWS.inst = () => {
    const w = worldBossInfo();
    let h = subtabs('inst', [['dungeon', 'Dungeons', S.keys >= KEY_MAX], ['raid', 'Raids'], ['world', 'Weltboss', w.active && !w.killed && S.level >= 10], ['arena', 'Arena', S.level >= 10 && S.arena.tickets >= ARENA_TICKETS]]);
    if (sub.inst === 'dungeon') h += viewDungeons();
    else if (sub.inst === 'raid') h += viewRaids();
    else if (sub.inst === 'world') h += viewWorld();
    else h += viewArena();
    return h;
  };
  function bossFaces(list) { return list.map((n) => `<span class="bp">${face(n, 40)}</span>`).join(''); }
  function viewDungeons() {
    const t = now();
    let h = `<div class="card plain"><div class="row">${ico('key', 32)}<div class="grow"><b class="goldtxt">Dungeonschlüssel: ${S.keys}/${KEY_MAX}</b><div class="small muted">${S.keys >= KEY_MAX ? 'Schlüsselbund voll.' : `Nächster Schlüssel ${tm(t + nextKeyIn() * 1000, 'in ')}`} Jeder Lauf kostet 1 Schlüssel.</div></div></div></div>`;
    for (const d of DUNGEONS) {
      const ds = S.dungeons[d.id] || { clears: 0, best: -1 };
      const m = U.mythic[d.id] !== undefined ? U.mythic[d.id] : Math.max(0, ds.best);
      const lvl = dungeonLevel(d, m);
      const locked = S.level < d.lvl - 2;
      const rec = refPower(lvl, lvl + 1, 3, Math.floor(lvl * 0.7));
      const pw = heroStats().power;
      h += `<div class="inst"><div class="hero-img" style="background-image:url(assets/bg/${d.bg}.webp)"><div class="sprs">${d.bosses.map(([s]) => spr(s, 0.75)).join('')}</div>
        <div class="t"><b>${esc(d.name)}</b><small>Stufe ${lvl}${m ? ` · Mythisch +${m}` : ''} · ${ds.clears}× abgeschlossen</small></div></div><div class="body">
        <div class="small">${esc(d.desc)}</div>
        <div class="row wrap">${d.bosses.map(([s, n]) => `<span class="row small" style="gap:4px"><span class="bp" style="width:28px;height:28px;border-radius:50%;overflow:hidden;position:relative;display:inline-block;box-shadow:0 0 0 1px #000,0 0 0 2px #8a6a3a">${face(s, 28)}</span>${esc(n)}</span>`).join('')}</div>
        <div class="row between small"><span>Empfohlene Kampfkraft: <b class="${pw >= rec ? 'good' : 'bad'}">${fmt(rec)}</b></span><span class="muted">Deine: ${fmt(pw)}</span></div>
        ${locked ? `<div class="small bad">Benötigt Stufe ${d.lvl - 2}.</div>` : `<div class="row wrap between"><span class="stepper">${btn('−', 'myth', { id: d.id, d: -1 }, 'sm', m <= 0)}<b>${m ? 'Mythisch +' + m : 'Normal'}</b>${btn('+', 'myth', { id: d.id, d: 1 }, 'sm', m > ds.best || ds.clears === 0)}</span>
        <span class="row">${btn('Schnellkampf', 'dquick', { id: d.id }, 'sm', S.keys < 1 || m > ds.best || ds.clears === 0)}${btn(`Betreten ${ico('key', 16)}`, 'dungeon', { id: d.id }, 'sm gold', S.keys < 1)}</span></div>`}
        </div></div>`;
    }
    return h;
  }
  function viewRaids() {
    checkWeekly();
    const diff = U.raidDiff;
    let h = `<div class="card plain"><div class="row between wrap"><div><b class="goldtxt">Schlachtzüge</b><div class="small muted">Jeder Boss einmal pro Woche und Schwierigkeit. Reset ${tm(weekStart(now()) + 7 * DAY, 'in ')} (Mittwoch 5 Uhr).</div></div>
      <span class="stepper">${btn('−', 'raiddiff', { d: -1 }, 'sm', diff <= 0)}<b>${['Normal', 'Heroisch', 'Mythisch'][diff]}</b>${btn('+', 'raiddiff', { d: 1 }, 'sm', diff >= 2)}</span></div></div>`;
    const il = SLOTS.reduce((a, s) => a + (S.gear[s] ? S.gear[s].ilvl : 0), 0) / SLOTS.length;
    for (const r of RAIDS) {
      const lvl = raidLevel(r, diff);
      const needIl = r.ilvl + diff * 10;
      const ok = S.level >= Math.min(60, r.lvl) && il >= needIl;
      h += `<div class="inst"><div class="hero-img" style="background-image:url(assets/bg/${r.bg}.webp)"><div class="sprs">${spr(r.bosses[3].sprite, 0.85)}</div><div class="t"><b>${esc(r.name)}</b><small>Stufe ${lvl} · ab Gegenstandsstufe ${needIl}</small></div></div><div class="body">
        <div class="small">${esc(r.desc)}</div>${ok ? '' : `<div class="small bad">Benötigt Stufe ${Math.min(60, r.lvl)} und Ø Gegenstandsstufe ${needIl} (du: ${il.toFixed(0)}).</div>`}`;
      r.bosses.forEach((b, i) => {
        const dead = raidLocked(r.id, diff, i);
        const prev = i === 0 || raidLocked(r.id, diff, i - 1);
        h += `<div class="boss-row ${dead ? 'dead' : ''}"><span class="bp">${face(b.sprite, 40)}</span><div class="grow"><div class="ttl" style="font-weight:700">${esc(b.name)}</div><div class="small muted">${dead ? 'Diese Woche besiegt' : `Fähigkeit: ${esc(b.special)}`}${b.mount ? ' · kann ein Reittier fallen lassen' : ''}</div></div>
          ${dead ? '' : btn('Angreifen', 'raid', { id: r.id, b: i }, 'sm gold', !ok || !prev)}</div>`;
      });
      h += '</div></div>';
    }
    return h;
  }
  function viewWorld() {
    const t = now();
    const w = worldBossInfo(t);
    if (S.level < 10) return '<div class="card plain small">Weltbosse erscheinen ab Stufe 10.</div>';
    let h = `<div class="inst"><div class="hero-img" style="height:170px;background-image:url(assets/bg/${w.boss.bg}.webp)"><div class="sprs" style="right:50%;transform:translateX(50%)">${spr(w.boss.sprite, 1.5)}</div><div class="t"><b>${esc(w.boss.name)}</b><small>${w.active ? (w.killed ? 'Von dir besiegt' : 'Jetzt aktiv') : 'Noch nicht erschienen'}</small></div></div>
      <div class="body"><div class="small">Alle drei Stunden erscheint ein Weltboss für eine Stunde. Andere Abenteurer kämpfen an deiner Seite (+150% Schaden). Belohnung: zwei epische Gegenstände, Raidmarken und viel Gold.</div>
      <div class="row between"><span class="small">${w.active && !w.killed ? `Verschwindet ${tm(t + w.endsIn * 1000, 'in ')}` : `Nächster Weltboss ${tm(t + w.nextIn * 1000, 'in ')}`}</span>${btn('Angreifen', 'wb', {}, 'gold', !w.active || w.killed)}</div></div></div>`;
    h += '<div class="section-title">Rotation</div><div class="grid g4">';
    for (let i = 1; i <= 4; i++) {
      const b = WORLD_BOSSES[(w.idx + i) % WORLD_BOSSES.length];
      h += `<div class="li" style="flex-direction:column;gap:2px;padding:6px 2px;text-align:center"><span class="bp" style="width:40px;height:40px;border-radius:50%;overflow:hidden;position:relative;display:block">${face(b.sprite, 40)}</span><span class="small">${esc(b.name)}</span><span class="small muted">in ${i * 3 - 3 + Math.ceil(w.nextIn / 3600)} Std</span></div>`;
    }
    return h + '</div>';
  }
  function viewArena() {
    if (S.level < 10) return '<div class="card plain small">Die Arena öffnet ab Stufe 10.</div>';
    checkDaily();
    const a = S.arena;
    const o = arenaOpponent();
    const pw = heroStats().power;
    let h = `<div class="card"><div class="row">${ico('honor', 40)}<div class="grow"><h3 style="margin:0">${esc(arenaRank(a.rating))}</h3><div class="small">Wertung <b class="goldtxt">${a.rating}</b> · Bestwert ${a.best} · ${a.wins} Siege</div><div class="small muted">Kampfkarten: ${a.tickets}/${ARENA_TICKETS} (täglich neu)</div></div><div style="text-align:right">${ico('honor', 18)} <b>${fmt(S.honor)}</b><div class="small muted">Ehre</div></div></div></div>`;
    h += `<div class="inst"><div class="hero-img" style="height:120px;background-image:url(assets/bg/bg_arena.webp)"><div class="sprs" style="left:20px;right:auto">${spr(CLASSES[S.cls].sprite, 1)}</div><div class="sprs">${spr('rival_' + o.cls, 1)}</div><div class="t" style="text-align:center"><b>${esc(S.name)} gegen ${esc(o.name)}</b><small>${esc(CLASSES[o.cls].name)} · Wertung ${o.rating}</small></div></div>
      <div class="body"><div class="row between small"><span>Gegnerische Kampfkraft: <b class="${o.power <= pw ? 'good' : 'bad'}">${fmt(o.power)}</b></span><span class="muted">Deine: ${fmt(pw)}</span></div>
      <div class="row between">${btn('Neuer Gegner', 'arenanew', {}, 'sm', S.gold < gpk(L()) * 5)}${btn('Kämpfen', 'arena', {}, 'gold', a.tickets < 1)}</div><div class="small muted">Neuer Gegner kostet ${fmt(gpk(L()) * 5)} Gold. Sieg: Ehre und Wertung. 60 Sekunden Zeitlimit.</div></div></div>`;
    h += vendorHTML('honor');
    return h;
  }

  // ------------------------------------------------------------------ vendors
  function vendorItems(kind) {
    const lv = L();
    if (kind === 'badges') return [
      { n: `Heldenausrüstung (${SLOT_NAME[U.vslot]})`, icon: U.vslot === 'weapon' ? `w_${S.cls}_3` : `a_${U.vslot}_3`, cost: U.vslot === 'weapon' ? 140 : 90, give: { item: { ilvl: lv + 2, r: 4, slot: U.vslot } }, d: `Episch, Gegenstandsstufe ${lv + 2}` },
      { n: 'Dungeonschlüssel', icon: 'key', cost: 20, give: { keys: 1 } },
      { n: '5 Heiltränke', icon: 'potion_heal', cost: 12, give: { cons: { potion_heal: 5 } } },
      { n: 'Glückselixier', icon: 'elixir_luck', cost: 30, give: { cons: { elixir_luck: 1 } } },
    ];
    if (kind === 'honor') return [
      { n: `Gladiatorenrüstung (${SLOT_NAME[U.vslot]})`, icon: U.vslot === 'weapon' ? `w_${S.cls}_4` : `a_${U.vslot}_4`, cost: U.vslot === 'weapon' ? 600 : 380, give: { item: { ilvl: lv + 4 + Math.floor(Math.max(0, S.arena.best - 1200) / 200) * 2, r: 4, slot: U.vslot } }, d: `Episch, Stufe ${lv + 4 + Math.floor(Math.max(0, S.arena.best - 1200) / 200) * 2} (steigt mit deinem Wertungs-Bestwert)` },
      { n: 'Elixier der Macht', icon: 'elixir_atk', cost: 60, give: { cons: { elixir_atk: 1 } } },
    ];
    return [
      { n: `Raidausrüstung (${SLOT_NAME[U.vslot]})`, icon: U.vslot === 'weapon' ? `w_${S.cls}_4` : `a_${U.vslot}_4`, cost: U.vslot === 'weapon' ? 20 : 12, give: { item: { ilvl: lv + 8, r: 4, slot: U.vslot } }, d: `Episch, Gegenstandsstufe ${lv + 8}` },
      { n: `Legendärer Kern (${SLOT_NAME[U.vslot]})`, icon: U.vslot === 'weapon' ? `w_${S.cls}_5` : `a_${U.vslot}_5`, cost: 90, give: { item: { ilvl: lv + 10, r: 5, slot: U.vslot } }, d: `Legendär, Gegenstandsstufe ${lv + 10}` },
      { n: 'Fläschchen der Titanen', icon: 'flask_titan', cost: 4, give: { cons: { flask_titan: 1 } } },
    ];
  }
  const VENDOR = { badges: ['Rüstmeisterin Hilde', 'badge', 'Heldenabzeichen', 'badges'], honor: ['Kampfmeister Ragnar', 'honor', 'Ehre', 'honor'], raidmarks: ['Schatzmeister Aldous', 'raidmark', 'Raidmarken', 'raidmarks'] };
  function vendorHTML(kind) {
    const [name, icon, cur, key] = VENDOR[kind];
    let h = `<div class="card"><div class="row between"><h3 style="margin:0">${esc(name)}</h3><span>${ico(icon, 20)} <b>${fmt(S[key])}</b> <span class="small muted">${cur}</span></span></div>`;
    h += `<div class="row wrap" style="gap:4px;margin:6px 0">${SLOTS.map((s) => `<button class="slot ${U.vslot === s ? 'q4' : ''}" style="width:38px" data-act="vslot" data-s="${s}" title="${SLOT_NAME[s]}">${ico(s === 'weapon' ? `w_${S.cls}_2` : `a_${s}_2`, 38)}</button>`).join('')}</div><div class="stack">`;
    vendorItems(kind).forEach((v, i) => {
      h += `<div class="li">${ico(v.icon, 36)}<div class="grow"><div class="ttl">${esc(v.n)}</div>${v.d ? `<div class="small muted">${esc(v.d)}</div>` : ''}</div>${btn(`${v.cost} ${ico(icon, 16)}`, 'buy', { k: kind, i }, 'sm', S[key] < v.cost)}</div>`;
    });
    return h + '</div></div>';
  }

  // ------------------------------------------------------------------ Berufe
  VIEWS.berufe = () => {
    const t = now();
    let h = subtabs('berufe', [['gather', 'Sammeln', t >= S.gatherCd], ['craft', 'Handwerk'], ['fish', 'Angeln'], ['exp', 'Expedition', S.exp.active.some((o) => o.end <= t) || S.exp.active.length < expSlots()]]);
    if (sub.berufe === 'gather') h += viewGather();
    else if (sub.berufe === 'craft') h += viewCraft();
    else if (sub.berufe === 'fish') h += viewFish();
    else h += viewExp();
    return h;
  };
  function profBar(p, label) { return `<div class="row between small"><span>${label}</span><span class="num">${p.skill}/300</span></div>${bar('teal', p.skill / 300, '', true)}`; }
  function viewGather() {
    const t = now();
    const mi = S.prof.mining, he = S.prof.herb;
    let h = `<div class="card"><div class="row">${ico('pickaxe', 40)}<div class="grow"><h3 style="margin:0">Bergbau & Kräuterkunde</h3><div class="small muted">Dein Held sammelt alle 2 Minuten von selbst – auch offline.</div></div></div>
      <div class="stack" style="margin-top:6px">${profBar(mi, `Bergbau · ${MAT_NAME[ORES[gatherTier(mi.skill)]]}`)}${profBar(he, `Kräuterkunde · ${MAT_NAME[HERBS[gatherTier(he.skill)]]}`)}</div>
      <div class="row between" style="margin-top:8px"><span class="small muted">Nächste Ernte ${tm(S.gatherT, 'in ')}</span>${btn(t >= S.gatherCd ? 'Jetzt sammeln' : `Sammeln ${tm(S.gatherCd, '')}`, 'gather', {}, t >= S.gatherCd ? 'gold' : '', t < S.gatherCd)}</div></div>`;
    h += '<div class="section-title">Material</div><div class="grid">';
    const mats = [...ORES, ...HERBS, 'dust'];
    for (const m of mats) h += `<div class="slot ${S.mats[m] ? '' : 'empty'}" title="${esc(MAT_NAME[m])}">${ico(m, 64)}<span class="il">${fmt(S.mats[m] || 0)}</span></div>`;
    h += '</div><div class="small muted">Erze braucht die Schmiedekunst, Kräuter die Alchemie. Arkanstaub entsteht beim Entzaubern.</div>';
    return h;
  }
  function costHTML(cost) { return Object.entries(cost).map(([k, v]) => `<span class="${(S.mats[k] || 0) >= v ? '' : 'bad'}">${ico(k, 18)}${v}</span>`).join(' '); }
  function viewCraft() {
    let h = '';
    const rcs = smithRecipes();
    const rc = rcs[U.smithTier];
    h += `<div class="card"><div class="row">${ico('anvil', 40)}<div class="grow"><h3 style="margin:0">Schmiedekunst</h3>${profBar(S.prof.smith, 'Fertigkeit')}</div></div>
      <div class="row wrap" style="gap:4px;margin:8px 0">${rcs.map((r) => `<button class="btn sm ${U.smithTier === r.tier ? 'gold' : ''}" data-act="smithtier" data-t="${r.tier}" ${r.ok ? '' : 'disabled'}>${ico(r.ore, 16)} ${r.ok ? 'Stufe ' + r.ilvl : r.skill}</button>`).join('')}</div>
      <div class="small">Kosten pro Teil: <span class="rewards" style="display:inline-flex">${costHTML({ [rc.ore]: rc.n })} <span class="${S.gold >= rc.gold ? '' : 'bad'}">${ico('gold', 18)}${fmt(rc.gold)}</span></span></div>
      <div class="small muted">Ergebnis: Gegenstandsstufe ${rc.ilvl}–${rc.ilvl + 2}, Selten bis Legendär. Höhere Fertigkeit erhöht die Chance auf Episch.</div>
      <div class="grid g4" style="margin-top:8px">${SLOTS.map((s) => `<button class="slot" data-act="smith" data-s="${s}" title="${SLOT_NAME[s]}">${ico(s === 'weapon' ? `w_${S.cls}_${rc.tier}` : `a_${s}_${rc.tier}`, 56)}</button>`).join('')}</div></div>`;
    h += `<div class="card"><div class="row">${ico('cauldron', 40)}<div class="grow"><h3 style="margin:0">Alchemie</h3>${profBar(S.prof.alch, 'Fertigkeit')}</div></div><div class="stack" style="margin-top:6px">`;
    for (const r of ALCHEMY) {
      const c = CONSUMABLES[r.id];
      const can = S.prof.alch.skill >= r.skill && Object.entries(r.cost).every(([k, v]) => (S.mats[k] || 0) >= v);
      h += `<div class="li">${ico(r.id, 36)}<div class="grow"><div class="ttl">${esc(c.name)}${r.out > 1 ? ` ×${r.out}` : ''} <span class="small muted">(${S.cons[r.id] || 0})</span></div><div class="small muted">${esc(c.desc)}</div><div class="rewards small">${S.prof.alch.skill >= r.skill ? costHTML(r.cost) : `<span class="bad">Benötigt Fertigkeit ${r.skill}</span>`}</div></div>${btn('Brauen', 'alch', { id: r.id }, 'sm', !can)}</div>`;
    }
    h += '</div></div>';
    const fc = fishCounts();
    h += `<div class="card"><div class="row">${ico('food_fish', 40)}<div class="grow"><h3 style="margin:0">Kochkunst</h3>${profBar(S.prof.cook, 'Fertigkeit')}<div class="small muted">Fische: ${fc.common} gewöhnlich, ${fc.rare} selten</div></div></div><div class="stack" style="margin-top:6px">`;
    for (const r of COOKING) {
      const c = CONSUMABLES[r.id];
      const can = S.prof.cook.skill >= r.skill && fc.common >= (r.cost.fishCommon || 0) && fc.rare >= (r.cost.fishRare || 0);
      const cost = `${r.cost.fishCommon ? `${r.cost.fishCommon} gewöhnliche` : ''}${r.cost.fishRare ? ` + ${r.cost.fishRare} seltene` : ''} Fische`;
      h += `<div class="li">${ico(r.id, 36)}<div class="grow"><div class="ttl">${esc(c.name)} <span class="small muted">(${S.cons[r.id] || 0})</span></div><div class="small muted">${esc(c.desc)}</div><div class="small ${S.prof.cook.skill >= r.skill ? '' : 'bad'}">${S.prof.cook.skill >= r.skill ? cost : `Benötigt Fertigkeit ${r.skill}`}</div></div>${btn('Kochen', 'cook', { id: r.id }, 'sm', !can)}</div>`;
    }
    return h + '</div></div>';
  }
  function viewFish() {
    const z = zoneOf(S.zone);
    let h = `<div class="card plain"><div class="row">${ico('rod', 32)}<div class="grow"><b class="goldtxt">Angeln in ${esc(z.name)}</b>${profBar(S.prof.fish, 'Fertigkeit')}</div></div></div>`;
    h += `<div class="pond" id="pond" data-act="fish" style="background-image:url(assets/bg/${z.bg}.webp)"><div class="water"></div><div id="pondInner"></div></div>`;
    h += '<div class="section-title">Angeltagebuch</div><div class="grid g4">';
    for (const f of FISH) {
      const c = S.fishLog[f.id] || 0;
      h += `<div class="li" style="flex-direction:column;gap:2px;padding:6px 2px;text-align:center;${c ? '' : 'opacity:.45'}">${ico(c ? f.id : 'lock', 36)}<span class="small q${f.rar + 1}">${c ? esc(f.name) : '???'}</span><span class="small muted">${c}× · ${S.mats[f.id] || 0} da</span></div>`;
    }
    h += `</div><div class="row between"><span class="small muted">Fische sind Zutaten für die Kochkunst.</span>${btn('Gewöhnliche verkaufen', 'sellfish', {}, 'sm', !fishCounts().common)}</div>`;
    return h;
  }
  function fishUpdate(dt) {
    const F = U.fish;
    const el = $('pondInner');
    if (!el) return;
    if (F.st === 'wait' || F.st === 'bite' || F.st === 'msg') {
      F.t -= dt;
      if (F.st === 'wait' && F.t <= 0) { F.st = 'bite'; F.t = 1.0; Snd.play('splash'); }
      else if (F.st === 'bite' && F.t <= 0) { F.st = 'msg'; F.t = 1.4; F.msg = 'Der Fisch ist entkommen …'; }
      else if (F.st === 'msg' && F.t <= 0) { F.st = 'idle'; F.msg = 'Tippe aufs Wasser, um die Angel auszuwerfen.'; }
    }
    const key = F.st + F.msg + (F.last ? F.last.id : '');
    if (el.dataset.k === key) return;
    el.dataset.k = key;
    let h = '';
    if (F.st === 'wait') h = `<div class="msg" style="font-size:13px">Warte auf einen Biss …</div><div class="bob">${spr('fx_bobber', 3)}</div>`;
    else if (F.st === 'bite') h = `<div class="msg" style="color:#ffd100">Jetzt tippen!</div><div class="splash"></div><div class="bob bite">${spr('fx_bobber', 3)}</div>`;
    else if (F.st === 'msg' && F.last && F.msg.startsWith('Gefangen')) h = `<div class="msg">${esc(F.msg)}</div><div class="bob" style="top:62%">${ico(F.last.id, 48)}</div>`;
    else h = `<div class="msg" style="font-size:13px">${esc(F.msg)}</div>`;
    el.innerHTML = h;
  }
  function fishTap() {
    const F = U.fish;
    if (F.st === 'idle') { F.st = 'wait'; F.t = rnd(2.2, 6.5); F.last = null; Snd.play('click'); }
    else if (F.st === 'wait') { F.st = 'msg'; F.t = 1.2; F.msg = 'Zu früh! Der Köder ist weg.'; F.last = null; }
    else if (F.st === 'bite') {
      const f = catchFish();
      F.last = f;
      F.st = 'msg';
      F.t = 1.8;
      F.msg = `Gefangen: ${f.name}!`;
      Snd.play(f.rar >= 2 ? 'epic' : 'catch');
      if (f.rar >= 2) toast(`Seltener Fang: ${f.name}!`, f.id, '#ff8000');
      forceRender();
    }
  }
  function viewExp() {
    checkOffers();
    const t = now();
    let h = `<div class="card plain"><div class="row">${ico('flag', 32)}<div class="grow"><b class="goldtxt">Expeditionen ${S.exp.active.length}/${expSlots()}</b><div class="small muted">Schicke Söldnertrupps los. Sie kehren auch zurück, während du offline bist.${S.level < 30 ? ' Ab Stufe 30: drittes Lager.' : ''}</div></div></div></div>`;
    for (const o of S.exp.active) {
      const ready = o.end <= t;
      h += `<div class="li ${ready ? 'claim' : ''}">${ico(ready ? 'chest' : 'clock', 36)}<div class="grow"><div class="ttl gold">${esc(o.name)}</div>
        ${ready ? '<div class="small good">Zurückgekehrt!</div>' : `<div class="bar teal thin"><i data-pg="${o.end - o.dur * MIN},${o.end}"></i></div><div class="small muted">${tm(o.end, 'Rückkehr in ')}</div>`}${rewardHTML(rwList(o.reward))}</div>
        ${btn('Abholen', 'exget', { id: o.id }, 'sm gold', !ready)}</div>`;
    }
    h += '<div class="section-title">Aufträge</div><div class="stack">';
    for (const o of S.exp.offers) {
      h += `<div class="li">${ico('map', 36)}<div class="grow"><div class="ttl">${esc(o.name)}</div><div class="small muted">Dauer: ${fmtTime(o.dur * 60)}</div>${rewardHTML(rwList(offerReward(o)))}</div>${btn('Losschicken', 'exsend', { id: o.id }, 'sm', S.exp.active.length >= expSlots())}</div>`;
    }
    h += `</div>${btn(`Neue Aufträge (${fmt(Math.ceil(gpk(Math.min(S.level, 60)) * 20))} Gold)`, 'exreroll', {}, 'sm wide')}`;
    return h;
  }

  // ------------------------------------------------------------------ Stadt
  VIEWS.stadt = () => {
    let h = subtabs('stadt', [['home', 'Stadt', !S.login.claimed || chestReady()], ['train', 'Lehrer'], ['comp', 'Gefolge'], ['stall', 'Stall'], ['shop', 'Händler']]);
    if (sub.stadt === 'home') h += viewHome();
    else if (sub.stadt === 'train') h += viewTrain();
    else if (sub.stadt === 'comp') h += viewComp();
    else if (sub.stadt === 'stall') h += viewStall();
    else h += vendorHTML('badges') + vendorHTML('raidmarks');
    return h;
  };
  function viewHome() {
    const cyc = S.login.cycle;
    const todayIdx = S.login.claimed ? (cyc - 1) % 7 : cyc % 7;
    let h = `<div class="inst"><div class="hero-img" style="height:110px;background-image:url(assets/bg/bg_town.webp)"><div class="t"><b>Hohenmark</b><small>Hauptstadt des Königreichs Valdoran</small></div></div></div>`;
    h += `<div class="card"><div class="row between"><h3 style="margin:0">Tägliche Anmeldung</h3><span class="small muted">Serie: ${S.login.streak} ${S.login.streak === 1 ? 'Tag' : 'Tage'}</span></div><div class="cal" style="margin-top:6px">`;
    LOGIN_REWARDS.forEach((r, i) => {
      const got = i < todayIdx || (i === todayIdx && S.login.claimed);
      h += `<div class="d ${i === todayIdx ? 'today' : ''} ${got ? 'got' : ''}">${ico(r.icon, 28)}Tag ${i + 1}</div>`;
    });
    h += `</div><div class="row between" style="margin-top:8px"><span class="small">${S.login.claimed ? 'Heute abgeholt. Komm morgen wieder!' : `Heute: <b class="goldtxt">${esc(LOGIN_REWARDS[todayIdx].label)}</b>`}</span>${btn('Abholen', 'login', {}, 'gold', S.login.claimed)}</div>
      <div class="small muted" style="margin-top:4px">Jeder Tag in Folge gibt +1% Gold (bis 30%). Nach 14 Tagen in Folge wartet ein besonderes Reittier.</div></div>`;
    h += `<div class="card"><div class="row">${ico('chest', 40)}<div class="grow"><h3 style="margin:0">Versorgungskiste</h3><div class="small muted">Alle 4 Stunden: Gold, Tränke, Material und vielleicht ein Gegenstand.</div></div>${chestReady() ? btn('Öffnen', 'chest', {}, 'gold') : `<span class="small goldtxt">${tm(S.chestT)}</span>`}</div></div>`;
    const s = S.stats;
    h += `<div class="card"><h3>Chronik deines Helden</h3><div class="stats">
      <div><span>Spielzeit</span><b>${fmtTime(s.playTime)}</b></div><div><span>Monster besiegt</span><b>${fmt(s.kills)}</b></div>
      <div><span>Bosse besiegt</span><b>${fmt(s.bosses)}</b></div><div><span>Dungeons</span><b>${fmt(s.dungeons)}</b></div>
      <div><span>Raidbosse</span><b>${fmt(s.raidBoss)}</b></div><div><span>Tode</span><b>${fmt(s.deaths)}</b></div>
      <div><span>Gold verdient</span><b>${fmt(s.goldEarned)}</b></div><div><span>Epische Beute</span><b>${fmt(s.epics)}</b></div>
      <div><span>Legendäre Beute</span><b>${fmt(s.legendaries)}</b></div><div><span>Fische</span><b>${fmt(s.fish)}</b></div>
    </div></div>`;
    h += btn(`${ico('cog', 18)} Einstellungen & Spielstand`, 'settings', {}, 'wide');
    return h;
  }
  function viewTrain() {
    let h = '<div class="card plain small">Die Lehrer von Hohenmark bilden dich gegen Gold aus. Die meisten Ränge sind durch deine Stufe begrenzt.</div><div class="stack">';
    for (const tr of TRAINING) {
      const r = S.training[tr.id] || 0;
      const cap = trainCap(tr);
      const cost = trainCost(tr, r);
      const maxed = r >= cap;
      h += `<div class="li">${ico(tr.icon, 40)}<div class="grow"><div class="ttl gold">${esc(tr.name)} <span class="small muted">Rang ${r}/${cap}</span></div>
        <div class="small">+${String(tr.per).replace('.', ',')}% ${STAT_NAME[tr.key]} pro Rang${tr.extra ? ' · ' + esc(tr.extra) : ''} · jetzt +${String(Math.round(tr.per * r * 10) / 10).replace('.', ',')}%</div><div class="small muted">${esc(tr.teacher)}</div></div>
        ${maxed ? `<span class="small muted">${tr.max ? 'Gemeistert' : 'Stufe zu niedrig'}</span>` : btn(`${ico('gold', 16)} ${fmt(cost)}`, 'train', { id: tr.id }, 'sm', S.gold < cost)}</div>`;
    }
    return h + '</div>';
  }
  function viewComp() {
    let h = '<div class="card plain small">Gefährten kämpfen an deiner Seite – in der Wildnis, in Dungeons und Raids. Ihre Stufe kann deine nicht übersteigen.</div>';
    for (const c of COMPANIONS) {
      const lv = S.comp[c.id] || 0;
      const unlocked = S.level >= c.unlock;
      const cost = lv ? compUpCost(lv) : compRecruitCost(c);
      h += `<div class="li" style="align-items:flex-end">${spr(c.sprite, 1.5)}<div class="grow"><div class="ttl gold">${esc(c.name)}</div><div class="small">${esc(c.role)}${lv ? ` · Stufe ${lv}` : ''}</div><div class="small muted">${esc(c.desc)}</div>
        ${lv ? `<div class="small">Stärke: ${fmt(compPower(c.id) * (c.type === 'dps' ? 1.6 : c.type === 'tank' ? 0.6 : 0.3))} Schaden/Sek.</div>` : ''}</div>
        ${!unlocked ? `<span class="small bad">Ab Stufe ${c.unlock}</span>` : lv >= S.level ? '<span class="small muted">Max. Stufe</span>' : btn(`${lv ? 'Ausbilden' : 'Anheuern'} ${ico('gold', 16)} ${fmt(cost)}`, 'comp', { id: c.id }, `sm ${lv ? '' : 'gold'}`, S.gold < cost)}</div>`;
    }
    return h;
  }
  function viewStall() {
    let h = '<div class="card plain small">Reittiere bringen dich schneller zum nächsten Kampf: Der Bonus gilt für Gold und Erfahrung aus allen Kämpfen. Nur das aktive Reittier zählt.</div><div class="stack">';
    for (const m of MOUNTS) {
      const own = S.mounts.includes(m.id);
      const act = S.mount === m.id;
      let right;
      if (own) right = act ? '<span class="small goldtxt">Aktiv</span>' : btn('Reiten', 'mount', { id: m.id }, 'sm');
      else if (m.source) right = '<span class="small muted" style="max-width:110px;text-align:right">Selten</span>';
      else right = S.level < m.lvl ? `<span class="small bad">Ab Stufe ${m.lvl}</span>` : btn(`${ico('gold', 16)} ${fmt(mountCost(m))}`, 'mountbuy', { id: m.id }, 'sm', S.gold < mountCost(m));
      h += `<div class="li ${act ? 'claim' : ''}">${ico(m.icon, 48)}<div class="grow"><div class="ttl ${own ? 'gold' : ''}">${esc(m.name)}</div><div class="small">+${m.bonus}% Gold und Erfahrung</div>${m.source ? `<div class="small muted">${esc(m.source)}</div>` : ''}</div>${right}</div>`;
    }
    return h + '</div>';
  }

  // --------------------------------------------------------------------------------------- modals
  function modal(html, opts = {}) {
    const m = $('modal');
    m.hidden = false;
    m.innerHTML = `<div class="mbox" role="dialog" aria-modal="true">${opts.noClose ? '' : '<button class="x" data-act="close" aria-label="Schließen">×</button>'}${html}</div>`;
    U.modal = opts.id || 'x';
  }
  function closeModal() { $('modal').hidden = true; $('modal').innerHTML = ''; U.modal = null; }

  function showItem(it) {
    const equipped = S.gear[it.slot] === it;
    const cmp = equipped ? undefined : itemUpgrade(it);
    const uc = upgradeCost(it);
    let h = itemTip(it, cmp);
    const cur = S.gear[it.slot];
    if (!equipped && cur) h += `<div class="small muted" style="margin:8px 0 4px">Derzeit angelegt:</div>${itemTip(cur)}`;
    h += `<div class="small" style="margin-top:8px">Aufwerten (+${(it.up || 0) + 1}): ${ico('gold', 16)} ${fmt(uc.gold)} · ${ico('dust', 16)} ${uc.dust} <span class="muted">(+10% Grundwerte)</span></div>`;
    h += '<div class="mfoot">';
    if (!equipped) h += btn('Anlegen', 'equip', { id: it.id }, 'gold');
    h += btn('Aufwerten', 'upgrade', { id: it.id }, '', (it.up || 0) >= MAX_UP || S.gold < uc.gold || (S.mats.dust || 0) < uc.dust);
    if (!equipped) h += btn(`Verkaufen (${fmt(sellValue(it))})`, 'sell', { id: it.id }, 'sm') + btn(`Entzaubern (+${dustValue(it)} Staub)`, 'salvage', { id: it.id }, 'sm');
    h += '</div>';
    modal(h, { id: 'item' });
  }
  function findItem(id) {
    id = +id;
    for (const s of SLOTS) if (S.gear[s] && S.gear[s].id === id) return S.gear[s];
    return S.bag.find((it) => it.id === id);
  }

  function showZones() {
    let h = '<h2>Karte von Valdoran</h2><div class="stack">';
    ZONES.forEach((z, i) => {
      const open = i <= S.zoneMax;
      const qs = questState(i);
      h += `<div class="li ${i === S.zone ? 'claim' : ''}" style="padding:0;overflow:hidden"><div style="width:96px;height:64px;flex:none;background:url(assets/bg/${z.bg}.webp) 50% 80%/cover;${open ? '' : 'filter:grayscale(1) brightness(.4)'}"></div>
        <div class="grow" style="padding:4px 0"><div class="ttl ${open ? 'gold' : ''}">${esc(z.name)}</div><div class="small muted">Stufe ${z.lvl[0]}–${z.lvl[1]} · ${qs.i >= 6 ? 'Kampagne abgeschlossen' : open ? `Quest ${qs.i + 1}/6` : 'Gesperrt'}</div></div>
        <div style="padding-right:8px">${i === S.zone ? '<span class="small goldtxt">Hier</span>' : open ? btn('Reisen', 'travel', { z: i }, 'sm') : ico('lock', 24)}</div></div>`;
    });
    modal(h + '</div>', { id: 'zones' });
  }

  function showTalent(i) {
    const t = TALENTS[S.cls][i];
    const rk = S.talents[i] || 0;
    const spent = talentSpent();
    const tierOk = spent >= Math.floor(i / 3) * 5;
    const can = rk < t[3] && tierOk && talentPoints() > spent;
    const v = (x) => String(Math.round(x * 100) / 100).replace('.', ',');
    modal(`<div class="row">${ico(t[4], 48)}<div class="grow"><h2 style="text-align:left;margin:0">${esc(t[0])}</h2><div class="small muted">Rang ${rk}/${t[3]}</div></div></div>
      <div class="tip" style="margin-top:8px"><div>${rk ? `Aktuell: +${v(t[2] * rk)}% ${STAT_NAME[t[1]]}` : 'Noch nicht erlernt.'}</div>${rk < t[3] ? `<div class="g">Nächster Rang: +${v(t[2] * (rk + 1))}% ${STAT_NAME[t[1]]}</div>` : ''}${tierOk ? '' : `<div class="r">Benötigt ${Math.floor(i / 3) * 5} verteilte Punkte.</div>`}</div>
      <div class="mfoot">${btn('Erlernen', 'tallearn', { i }, 'gold', !can)}</div>`, { id: 'tal' });
  }

  function showResult(b, win, out) {
    if (!out && b.mode === 'boss') {
      if (win) { Scene.FX.banner('Sieg!', 'Boss besiegt', '#ffd84a'); Snd.play('win'); }
      else showLoss(b);
      return;
    }
    if (!win && (!out || (!out.items.length && !out.honor))) { showLoss(b); return; }
    Snd.play(win ? 'win' : 'lose');
    if (b.fx !== false && Scene) Scene.FX.banner(win ? 'Sieg!' : 'Niederlage', b.title, win ? '#ffd84a' : '#ff6a4a');
    let h = `<h2>${win ? 'Sieg!' : 'Rückzug'}</h2><div class="small muted" style="text-align:center;margin-top:-6px">${esc(b.title)}${b.quick ? ' · Schnellkampf' : ''}</div><div class="loot-list" style="margin-top:10px">`;
    if (out) {
      for (const it of out.items || []) h += `<div class="li">${ico(itemIcon(it), 36)}<div class="grow"><div class="ttl q${it.r}">${esc(it.name)}</div><div class="small muted">Gegenstandsstufe ${it.ilvl} · ${SLOT_NAME[it.slot]}</div></div></div>`;
      const extra = [];
      if (out.gold) extra.push(['gold', fmt(out.gold)]);
      if (out.xp) extra.push(['xp', fmt(out.xp) + ' EP']);
      if (out.badges) extra.push(['badge', out.badges]);
      if (out.raidmarks) extra.push(['raidmark', out.raidmarks]);
      if (out.honor) extra.push(['honor', out.honor]);
      if (out.rating !== undefined) extra.push(['honor', `Wertung ${out.rating > 0 ? '+' : ''}${out.rating}`]);
      if (out.mount) extra.push([MOUNTS.find((m) => m.id === out.mount).icon, 'Neues Reittier!']);
      if (extra.length) h += rewardHTML(extra);
    }
    h += `</div><div class="mfoot">${btn('Weiter', 'close', {}, 'gold')}</div>`;
    setTimeout(() => modal(h, { id: 'result' }), b.quick ? 0 : 900);
  }
  function showLoss(b) {
    Snd.play('lose');
    if (Scene) Scene.FX.banner('Niederlage', b.title, '#ff6a4a');
    setTimeout(() => modal(`<h2>Niederlage</h2><div class="small" style="text-align:center">${esc(b.title || 'Der Gegner')} war zu stark. So wirst du stärker:</div>
      <div class="stack" style="margin-top:10px">
      <div class="li">${ico('st_atk', 32)}<div class="grow small"><b>Lehrer in Hohenmark</b><br>Trainiere Angriff, Leben und Rüstung.</div>${btn('Hin', 'goto', { t: 'stadt', s: 'train' }, 'sm')}</div>
      <div class="li">${ico('a_chest_3', 32)}<div class="grow small"><b>Ausrüstung</b><br>Lege bessere Teile an oder werte sie auf.</div>${btn('Hin', 'goto', { t: 'held', s: 'bag' }, 'sm')}</div>
      <div class="li">${ico('potion_heal', 32)}<div class="grow small"><b>Heiltränke</b><br>Braue Tränke aus Wiesenklee.</div>${btn('Hin', 'goto', { t: 'berufe', s: 'craft' }, 'sm')}</div>
      <div class="li">${ico('flag', 32)}<div class="grow small"><b>Gefährten</b><br>Heuere Mitstreiter an.</div>${btn('Hin', 'goto', { t: 'stadt', s: 'comp' }, 'sm')}</div></div>
      <div class="mfoot">${btn('Weiter', 'close', {}, 'gold')}</div>`, { id: 'loss' }), 900);
  }

  function showOffline(o, sec) {
    const lines = [];
    lines.push(['clock', `${fmtTime(sec)} unterwegs${o.sec < sec ? ` (max. ${fmtTime(o.sec)})` : ''}`]);
    if (o.kills) lines.push(['swords', `${fmt(o.kills)} Monster besiegt`]);
    if (o.xp) lines.push(['xp', `+${fmt(o.xp)} Erfahrung${o.levels ? ` · ${o.levels} Stufenaufstieg${o.levels > 1 ? 'e' : ''}!` : ''}`]);
    if (o.gold) lines.push(['gold', `+${fmt(o.gold)} Gold`]);
    if (o.items) lines.push(['bag', `${o.items} Gegenstände in den Taschen${o.sold ? `, ${o.sold} verkauft` : ''}`]);
    if (o.best && o.best.r >= 3) lines.push([itemIcon(o.best), `Bester Fund: ${o.best.name}`, o.best.r]);
    const mats = Object.assign({}, o.mats);
    if (o.gathered) for (const k in o.gathered) mats[k] = (mats[k] || 0) + o.gathered[k];
    const matList = Object.keys(mats).filter((k) => mats[k]).map((k) => [k, mats[k]]);
    if (o.quest) lines.push(['scroll', `${o.quest.t}: +${o.quest.gained}${o.quest.done ? ' — abgeschlossen!' : ''}`]);
    if (o.rested > 0) lines.push(['star', 'Du bist erholt: doppelte Erfahrung für eine Weile']);
    const exp = S.exp.active.filter((x) => x.end <= now()).length;
    if (exp) lines.push(['flag', `${exp} Expedition${exp > 1 ? 'en' : ''} zurückgekehrt`]);
    let h = `<h2>Willkommen zurück, ${esc(S.name)}!</h2><div class="small muted" style="text-align:center;margin-top:-4px">Während du weg warst, hat dein Held weitergekämpft.</div><div class="loot-list" style="margin-top:10px">`;
    for (const [icon, txt, r] of lines) h += `<div class="li">${ico(icon, 28)}<div class="grow small ${r !== undefined ? 'q' + r : ''}">${esc(txt)}</div></div>`;
    if (matList.length) h += `<div class="li">${ico('pickaxe', 28)}<div class="grow"><div class="small">Material gesammelt</div>${rewardHTML(matList)}</div></div>`;
    h += `</div><div class="mfoot">${btn('Weiter kämpfen', 'close', {}, 'gold')}</div>`;
    modal(h, { id: 'offline' });
  }

  function showGot(title, got, sub = '') {
    modal(`<h2>${esc(title)}</h2>${sub ? `<div class="small muted" style="text-align:center">${esc(sub)}</div>` : ''}<div class="loot-list" style="margin-top:8px">${got.map(([icon, val, r]) => `<div class="li">${ico(icon, 32)}<div class="grow ${r !== undefined ? 'q' + r : ''}" style="font-weight:700">${typeof val === 'number' ? '+' + fmt(val) : esc(val)}</div></div>`).join('')}</div><div class="mfoot">${btn('Super!', 'close', {}, 'gold')}</div>`, { id: 'got' });
  }

  function showSettings() {
    const st = S.settings;
    modal(`<h2>Einstellungen</h2><div class="stack">
      <div class="toggle"><span>Soundeffekte</span>${btn(st.sound ? 'An' : 'Aus', 'set', { k: 'sound' }, 'sm ' + (st.sound ? 'gold' : ''))}</div>
      <div class="toggle"><span>Bessere Ausrüstung automatisch anlegen</span>${btn(st.autoEquip ? 'An' : 'Aus', 'set', { k: 'autoEquip' }, 'sm ' + (st.autoEquip ? 'gold' : ''))}</div>
      <div class="toggle"><span>Automatisch verkaufen</span><select id="autoSell" data-act="autosell">${['Nur Schlecht', 'Bis Verbreitet', 'Bis Selten'].map((l, i) => `<option value="${i === 0 ? 0 : i + 1}" ${(st.autoSell === 0 && i === 0) || st.autoSell === i + 1 ? 'selected' : ''}>${l}</option>`).join('')}</select></div>
      <div class="sep"></div>
      <div class="small">Dein Spielstand wird automatisch im Browser gespeichert${Save.cloud ? ' und in deinem Claude-Konto gesichert' : ''}. Als Sicherung kannst du ihn exportieren:</div>
      <textarea id="saveBox" readonly></textarea>
      <div class="row wrap">${btn('Exportieren', 'export', {}, 'sm')}${btn('Importieren', 'import', {}, 'sm')}${btn('Kopieren', 'copysave', {}, 'sm')}</div>
      <div class="sep"></div>
      ${U.confirmReset ? `<div class="small bad">Wirklich alles löschen? Das kann nicht rückgängig gemacht werden.</div><div class="row">${btn('Ja, neu beginnen', 'resetyes', {}, 'sm')}${btn('Abbrechen', 'resetno', {}, 'sm gold')}</div>` : btn('Spiel zurücksetzen', 'reset', {}, 'sm')}
      <div class="small muted" style="margin-top:6px">Valdoran Idle · ein eigenständiges Fan-Idle-RPG im Stil klassischer Fantasy-MMOs. Alle Grafiken sind prozedural gemalte Rastergrafiken.</div>
    </div>`, { id: 'settings' });
  }

  function showCreate() {
    const opts = Object.entries(CLASSES).map(([id, c]) => `<button class="cls ${U.cls === id ? 'on' : ''}" data-act="pickcls" data-c="${id}">${spr(c.sprite, 1.5)}<b style="color:${c.color}">${c.name}</b><small>${esc(c.desc)}</small></button>`).join('');
    modal(`<h2>Erschaffe deinen Helden</h2><div class="small muted" style="text-align:center;margin:-4px 0 8px">Das Königreich Valdoran braucht dich. Wähle deine Klasse:</div>
      <div class="classes">${opts}</div>
      <div style="margin-top:10px"><label class="small" for="heroName">Name</label><input type="text" id="heroName" maxlength="16" value="${esc(U.newName || randomName())}" autocomplete="off"></div>
      <div class="mfoot">${btn('Abenteuer beginnen', 'create', {}, 'gold wide')}</div>`, { id: 'create', noClose: true });
  }
  function randomName() { return pick(NAME_PARTS[0]) + pick(NAME_PARTS[1]); }

  // --------------------------------------------------------------------------------------- actions
  const ACT = {
    noop() {},
    tab(d) { tab = d.t; forceRender(); Snd.play('click'); $('panel').scrollTop = 0; },
    sub(d) { sub[d.g] = d.s; forceRender(); Snd.play('click'); },
    goto(d) { closeModal(); tab = d.t; if (d.s) sub[d.t] = d.s; forceRender(); },
    gotoinst(d) { tab = 'inst'; sub.inst = d.s; forceRender(); },
    gotoberufe(d) { tab = 'berufe'; sub.berufe = d.s; forceRender(); },
    tut(d) { S.tut[d.k] = 1; forceRender(); },
    zones() { showZones(); },
    travel(d) { travel(+d.z); closeModal(); forceRender(); toast(`Reise nach ${zoneOf(+d.z).name}`, 'map'); },
    wt(d) { setWorldTier(S.worldTier + +d.d); forceRender(); },
    boss(d) {
      if (battle && battle.mode !== 'adventure') return;
      startBossFight(+d.z);
      tab = 'kampf';
      forceRender();
    },
    leave() { leaveInstance(); toast('Instanz verlassen'); },
    turnin(d) {
      const zi = +d.z;
      const q = currentQuest(zi);
      const res = turnInQuest(zi);
      if (!res) return;
      const got = rwList(res.rw).filter((x) => x[0] !== 'chest' && x[0] !== 'chest_epic');
      if (res.itemTxt) got.push(['bag', res.itemTxt]);
      showGot('Quest abgeschlossen', got, q.t);
      forceRender();
    },
    skillinfo(d) { const sk = SKILLS[d.id]; modal(`<div class="row">${ico(sk.icon, 48)}<div class="grow"><h2 style="text-align:left;margin:0">${esc(sk.name)}</h2><div class="small muted">Ab Stufe ${sk.lvl} · Abklingzeit ${sk.cd} Sek. · Kosten ${sk.cost} ${CLASSES[S.cls].res}</div></div></div><div class="tip" style="margin-top:8px">${esc(sk.desc)}<div class="d" style="margin-top:4px">Tippe den Knopf in der Aktionsleiste, um sie zu wirken. Leuchtet er, ist sie bereit.</div></div>`); },
    cast(d) {
      const r = castManual(d.id);
      if (r === 'locked') { ACT.skillinfo(d); return; }
      if (r === 'res') toast(`Nicht genug ${CLASSES[S.cls].res}`, SKILLS[d.id].icon, '#3a7ad8');
      else if (r === 'cd') Snd.play('click');
    },
    potioninfo() { modal(`<div class="row">${ico('potion_heal', 48)}<div class="grow"><h2 style="text-align:left;margin:0">Heiltrank ×${S.cons.potion_heal || 0}</h2></div></div><div class="tip" style="margin-top:8px">${esc(CONSUMABLES.potion_heal.desc)}<div class="d" style="margin-top:4px">Braue Nachschub mit Alchemie oder kaufe ihn beim Händler.</div></div><div class="mfoot">${btn('Zur Alchemie', 'goto', { t: 'berufe', s: 'craft' })}</div>`); },
    item(d) { const it = findItem(d.id); if (it) showItem(it); },
    equip(d) { const it = findItem(d.id); if (it) { equipItem(it); Snd.play('equip'); closeModal(); forceRender(); } },
    sell(d) { const it = findItem(d.id); if (it) { const v = sellItem(it); toast(`Verkauft für ${fmt(v)} Gold`, 'gold'); closeModal(); forceRender(); } },
    salvage(d) { const it = findItem(d.id); if (it) { const v = salvageItem(it); toast(`+${v} Arkanstaub`, 'dust'); Snd.play('brew'); closeModal(); forceRender(); } },
    upgrade(d) { const it = findItem(d.id); if (it && upgradeItem(it)) { toast(`${it.name} ist jetzt +${it.up}`, itemIcon(it), RARITY[it.r].color); showItem(it); forceRender(); } },
    bestgear() { const n = equipBest(); if (n) { toast(`${n} Teil${n > 1 ? 'e' : ''} angelegt`, 'star'); Snd.play('equip'); } forceRender(); },
    sellall(d) { let g = 0, n = 0; for (const it of S.bag.slice()) if (it.r <= +d.r && itemUpgrade(it) <= 0) { g += sellItem(it); n++; } if (n) toast(`${n} Gegenstände für ${fmt(g)} Gold verkauft`, 'gold'); forceRender(); },
    salvageall(d) { let s = 0, n = 0; for (const it of S.bag.slice()) if (it.r === +d.r && itemUpgrade(it) <= 0) { s += salvageItem(it); n++; } if (n) { toast(`${n} entzaubert: +${s} Arkanstaub`, 'dust'); Snd.play('brew'); } forceRender(); },
    tal(d) { showTalent(+d.i); },
    tallearn(d) {
      const i = +d.i;
      const t = TALENTS[S.cls][i];
      const rk = S.talents[i] || 0;
      if (rk < t[3] && talentSpent() >= Math.floor(i / 3) * 5 && talentPoints() > talentSpent()) {
        S.talents[i] = rk + 1;
        statsDirty = true;
        Snd.play('upgrade');
        showTalent(i);
        forceRender();
      }
    },
    talreset() {
      const c = talentResetCost();
      if (S.gold < c) { toast('Nicht genug Gold'); return; }
      S.gold -= c; S.talents = {}; statsDirty = true; forceRender(); toast('Talente zurückgesetzt');
    },
    usecons(d) { if (d.id === 'potion_heal') { ACT.potioninfo(); return; } if (useConsumable(d.id)) { toast(`${CONSUMABLES[d.id].name} wirkt`, d.id, '#5cff6a'); forceRender(); } },
    dq(d) { const rw = claimDaily(S.daily.list[+d.i]); if (rw) { showGot('Tagesquest erledigt', rwList(rw)); forceRender(); } },
    wq(d) { const rw = claimDaily(S.weekly.list[+d.i]); if (rw) { showGot('Wochenquest erledigt', rwList(rw)); forceRender(); } },
    dqbonus() { const rw = claimDailyBonus(); if (rw) { showGot('Tagesbonus', rw); forceRender(); } },
    ach(d) { const got = claimAchievement(d.id); if (got) { showGot('Erfolgsbelohnung', got); forceRender(); } },
    titlesel(d, el) { S.title = el.value; forceRender(); },
    dungeon(d) { if (startDungeon(d.id, U.mythic[d.id] || 0, false)) { tab = 'kampf'; forceRender(); } },
    dquick(d) { startDungeon(d.id, U.mythic[d.id] || 0, true); forceRender(); },
    myth(d) {
      const ds = S.dungeons[d.id] || { best: -1 };
      const cur = U.mythic[d.id] !== undefined ? U.mythic[d.id] : Math.max(0, ds.best);
      U.mythic[d.id] = clamp(cur + +d.d, 0, ds.best + 1);
      forceRender();
    },
    raiddiff(d) { U.raidDiff = clamp(U.raidDiff + +d.d, 0, 2); forceRender(); },
    raid(d) { if (startRaidBoss(d.id, U.raidDiff, +d.b)) { tab = 'kampf'; forceRender(); } },
    wb() { if (startWorldBoss()) { tab = 'kampf'; forceRender(); } },
    arena() { if (startArena()) { tab = 'kampf'; forceRender(); } },
    arenanew() { const c = Math.ceil(gpk(L()) * 5); if (S.gold >= c) { S.gold -= c; S.arena.opp = null; forceRender(); } },
    vslot(d) { U.vslot = d.s; forceRender(); },
    buy(d) {
      const v = vendorItems(d.k)[+d.i];
      const key = VENDOR[d.k][3];
      if (!v || S[key] < v.cost) return;
      S[key] -= v.cost;
      if (v.give.item) {
        const it = makeItem(v.give.item.ilvl, v.give.item.r, v.give.item.slot);
        giveItem(it);
        showGot('Gekauft', [[itemIcon(it), it.name, it.r]]);
      } else { grantReward(v.give); toast(`Gekauft: ${v.n}`, v.icon); }
      Snd.play('coin');
      forceRender();
    },
    gather() { const r = activeGather(); if (r) { toast(`+${r[0][1]} ${MAT_NAME[r[0][0]]}, +${r[1][1]} ${MAT_NAME[r[1][0]]}`, r[0][0]); forceRender(); } },
    smithtier(d) { U.smithTier = +d.t; forceRender(); },
    smith(d) {
      const it = craftSmith(U.smithTier, d.s);
      if (it) showGot('Geschmiedet!', [[itemIcon(it), it.name, it.r]], `Gegenstandsstufe ${it.ilvl}`);
      else toast('Nicht genug Material oder Gold', 'anvil', '#ff4a3a');
      forceRender();
    },
    alch(d) { if (craftAlchemy(d.id)) { toast(`${CONSUMABLES[d.id].name} gebraut`, d.id, '#5cff6a'); forceRender(); } },
    cook(d) { if (craftCooking(d.id)) { toast(`${CONSUMABLES[d.id].name} gekocht`, d.id, '#5cff6a'); forceRender(); } },
    fish() { fishTap(); },
    sellfish() {
      let g = 0;
      for (const f of FISH) if (f.rar === 0 && S.mats[f.id]) { g += fishSellValue(f) * S.mats[f.id]; S.mats[f.id] = 0; }
      S.gold += g; toast(`Fisch verkauft: ${fmt(g)} Gold`, 'gold'); Snd.play('coin'); forceRender();
    },
    exsend(d) { if (sendExpedition(d.id)) forceRender(); },
    exget(d) { const got = collectExpedition(d.id); if (got) { showGot('Expedition zurück', got); forceRender(); } },
    exreroll() { if (rerollOffers()) forceRender(); },
    login() { const r = claimLogin(); if (r) { showGot(`Tag ${(S.login.cycle - 1) % 7 + 1}: ${r.def.label}`, r.got, `Serie: ${S.login.streak} Tage`); forceRender(); } },
    chest() { const got = claimChest(); if (got) { showGot('Versorgungskiste', got); forceRender(); } },
    train(d) {
      const tr = TRAINING.find((x) => x.id === d.id);
      const r = S.training[tr.id] || 0;
      const c = trainCost(tr, r);
      if (r >= trainCap(tr) || S.gold < c) return;
      S.gold -= c;
      S.training[tr.id] = r + 1;
      statsDirty = true;
      Snd.play('upgrade');
      forceRender();
    },
    comp(d) {
      const c = COMPANIONS.find((x) => x.id === d.id);
      const lv = S.comp[c.id] || 0;
      if (S.level < c.unlock || lv >= S.level) return;
      const cost = lv ? compUpCost(lv) : compRecruitCost(c);
      if (S.gold < cost) return;
      S.gold -= cost;
      S.comp[c.id] = lv + 1;
      if (!lv) { toast(`${c.name} schließt sich dir an!`, 'flag', '#ffd200'); Snd.play('quest'); } else Snd.play('upgrade');
      statsDirty = true;
      forceRender();
    },
    mount(d) { S.mount = d.id; statsDirty = true; Snd.play('click'); forceRender(); },
    mountbuy(d) {
      const m = MOUNTS.find((x) => x.id === d.id);
      const c = mountCost(m);
      if (S.gold < c || S.level < m.lvl) return;
      S.gold -= c; S.mounts.push(m.id); S.mount = m.id; statsDirty = true;
      showGot('Neues Reittier', [[m.icon, m.name]], `+${m.bonus}% Gold und Erfahrung`);
      forceRender();
    },
    settings() { U.confirmReset = false; showSettings(); },
    set(d) { S.settings[d.k] = !S.settings[d.k]; showSettings(); },
    autosell(d, el) { S.settings.autoSell = +el.value; },
    export() { $('saveBox').value = Save.exportString(); },
    copysave() {
      const v = Save.exportString();
      $('saveBox').value = v;
      try { navigator.clipboard.writeText(v).then(() => toast('Kopiert'), () => { $('saveBox').select(); }); } catch (e) { $('saveBox').select(); }
    },
    import() {
      const box = $('saveBox');
      if (box.readOnly) { box.readOnly = false; box.value = ''; box.placeholder = 'Spielstand hier einfügen und erneut auf Importieren tippen'; box.focus(); return; }
      if (Save.importString(box.value.trim())) { closeModal(); toast('Spielstand geladen', 'scroll'); }
      else toast('Das ist kein gültiger Spielstand', 'lock', '#ff4a3a');
    },
    reset() { U.confirmReset = true; showSettings(); },
    resetno() { U.confirmReset = false; showSettings(); },
    resetyes() { Save.wipe(); closeModal(); U.confirmReset = false; showCreate(); },
    pickcls(d) { U.cls = d.c; const n = $('heroName'); if (n) U.newName = n.value; showCreate(); },
    create() {
      const n = ($('heroName').value || '').trim().slice(0, 16) || randomName();
      Game.create(U.cls, n);
      closeModal();
    },
    close() { closeModal(); },
  };

  function onClick(ev) {
    const el = ev.target.closest('[data-act]');
    if (!el || el.disabled) return;
    if (el.tagName === 'SELECT') return;
    const a = ACT[el.dataset.act];
    if (a) { Snd.unlock(); a(el.dataset, el); }
  }
  function onChange(ev) {
    const el = ev.target.closest('select[data-act]');
    if (!el) return;
    const a = ACT[el.dataset.act];
    if (a) a(el.dataset, el);
  }

  function init() {
    buildShell();
    document.addEventListener('click', onClick);
    document.addEventListener('change', onChange);
    document.addEventListener('pointerdown', () => { holding = true; Snd.unlock(); }, true);
    document.addEventListener('pointerup', () => { setTimeout(() => { holding = false; }, 60); }, true);
    document.addEventListener('pointercancel', () => { holding = false; }, true);
    $('modal').addEventListener('click', (e) => { if (e.target.id === 'modal' && U.modal !== 'create') closeModal(); });
    let pressT = null, pressed = null;
    $('actionbar').addEventListener('pointerdown', (e) => {
      const el = e.target.closest('[data-act=cast]');
      if (!el) return;
      pressed = null;
      clearTimeout(pressT);
      pressT = setTimeout(() => { pressed = el; ACT.skillinfo(el.dataset); }, 550);
    });
    for (const ev of ['pointerup', 'pointercancel', 'pointerleave']) $('actionbar').addEventListener(ev, () => clearTimeout(pressT));
    $('actionbar').addEventListener('contextmenu', (e) => { const el = e.target.closest('[data-act=cast]'); if (el) { e.preventDefault(); clearTimeout(pressT); ACT.skillinfo(el.dataset); } });
    $('actionbar').addEventListener('click', (e) => { if (pressed && e.target.closest('[data-act=cast]') === pressed) { e.stopPropagation(); pressed = null; } }, true);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && U.modal && U.modal !== 'create') closeModal();
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === ' ' && S) { e.preventDefault(); tapAttack(); }
      if (S && /^[1-3]$/.test(e.key)) { const id = CLASSES[S.cls].skills[+e.key - 1]; if (id) ACT.cast({ id }); }
    });
    Hooks.toast = toast;
    Hooks.log = log;
    Hooks.dirty = () => { dirty = true; };
    Hooks.levelUp = (lv) => {
      Scene.FX.levelUp(lv);
      Snd.play('levelup');
      log(`<span class="lvup">Stufenaufstieg! Du bist jetzt Stufe ${lv}.</span>`);
      for (const id of CLASSES[S.cls].skills) if (SKILLS[id].lvl === lv) toast(`Neue Fähigkeit: ${SKILLS[id].name}`, SKILLS[id].icon, '#ffd200');
      if (lv === 5) toast('Talentpunkte verfügbar!', 'book', '#ffd200');
      for (const c of COMPANIONS) if (c.unlock === lv) toast(`Gefährte verfügbar: ${c.name}`, 'flag', '#ffd200');
      dirty = true;
    };
    Hooks.battleEnd = (b, win, out) => { showResult(b, win, out); dirty = true; };
    Hooks.sound = (n) => Snd.play(n);
    Hooks.fx = Scene.FX;
    log('<span class="sys">Willkommen in Valdoran!</span>');
  }

  function rebuild() { buildActionbar(); lastHeroFace = null; abExtra = ''; forceRender(); }

  return { init, update, toast, log, pulseSkill, showOffline, showCreate, showGot, rebuild, forceRender, closeModal, ico, get tab() { return tab; } };
})();
