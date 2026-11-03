// Valdoran — the battle scene: a 240x160 pixel-art canvas scaled up with nearest-neighbour.
'use strict';

const Scene = (() => {
  const W = 240, H = 160, FEET = 148;
  let canvas, ctx, k = 2;
  const IMG = { sprites: null, icons: null, bg: {} };
  const flashCache = new Map();
  let texts = [], projs = [], effects = [], parts = [];
  let shake = 0, redFlash = 0, warnText = null, banner = null, t = 0;
  let curBg = null, weather = null, lastBattle = null;
  const A = {
    hero: { x: 74, y: FEET, lunge: 0, flash: 0, alpha: 1, dead: 0 },
    enemy: { x: 178, y: FEET, lunge: 0, flash: 0, alpha: 0, dying: 0, spawn: 0, sprite: null },
    comps: {},
    pet: { x: 100, y: 158, lunge: 0 },
  };
  const COMP_POS = { thorga: [108, 143], elyra: [42, 140], varrik: [16, 145], mirra: [30, 152] };
  const COMP_SPRITE = { thorga: 'comp_tank', elyra: 'comp_heiler', varrik: 'comp_schuetze', mirra: 'comp_zauberin' };
  const RAR_COL = RARITY.map((r) => r.color);

  function loadImage(src) {
    return new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
  }

  async function init(c) {
    canvas = c;
    ctx = canvas.getContext('2d');
    const [s, i] = await Promise.all([loadImage('assets/sprites.webp'), loadImage('assets/icons.webp')]);
    IMG.sprites = s;
    IMG.icons = i;
    resize();
    window.addEventListener('resize', resize);
    canvas.addEventListener('pointerdown', onTap);
  }

  function bg(name) {
    if (!IMG.bg[name]) { IMG.bg[name] = new Image(); IMG.bg[name].src = `assets/bg/${name}.webp`; }
    return IMG.bg[name];
  }

  function resize() {
    const dpr = Math.min(3, window.devicePixelRatio || 1);
    const cw = canvas.clientWidth || 360;
    const pw = Math.max(W, Math.round(cw * dpr));
    canvas.width = pw;
    canvas.height = Math.round(pw * H / W);
    k = pw / W;
  }
  const SC = (ATLAS.sprites.scale || 1), IC = (ATLAS.icons.cell || 32);

  function spr(name) { return ATLAS.sprites.map[name]; }

  function flashOf(name) {
    if (flashCache.has(name)) return flashCache.get(name);
    const r = spr(name);
    if (!r || !IMG.sprites) return null;
    const c = document.createElement('canvas');
    c.width = r[2]; c.height = r[3];
    const x = c.getContext('2d');
    x.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], 0, 0, r[2], r[3]);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = '#ffffff';
    x.fillRect(0, 0, r[2], r[3]);
    flashCache.set(name, c);
    return c;
  }

  // draw sprite with its feet at (x, y), centred horizontally
  function drawSprite(name, x, y, o = {}) {
    const r = spr(name);
    if (!r || !IMG.sprites) return;
    const w = r[2] / SC * (o.scale || 1), h = r[3] / SC * (o.scale || 1);
    const dx = x - w / 2, dy = y - h;
    ctx.save();
    ctx.globalAlpha = o.alpha === undefined ? 1 : o.alpha;
    if (o.rot) {
      ctx.translate(dx + w / 2, dy + h);
      ctx.rotate(o.rot);
      ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], -w / 2, -h, w, h);
    } else if (o.flip) {
      ctx.translate(dx + w, dy);
      ctx.scale(-1, 1);
      ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], 0, 0, w, h);
    } else ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], dx, dy, w, h);
    if (o.flash > 0) {
      const f = flashOf(name);
      if (f) {
        ctx.globalAlpha = Math.min(1, o.flash * 6) * (o.alpha === undefined ? 1 : o.alpha) * 0.8;
        if (o.rot || o.flip) ctx.drawImage(f, o.flip ? 0 : -w / 2, o.flip ? 0 : -h, w, h);
        else ctx.drawImage(f, dx, dy, w, h);
      }
    }
    if (o.grey) {
      ctx.globalAlpha = 0.55;
      ctx.globalCompositeOperation = 'source-atop';
      ctx.fillStyle = '#556';
      ctx.fillRect(o.rot ? -w / 2 : dx, o.rot ? -h : dy, w, h);
    }
    ctx.restore();
  }

  function drawIcon(name, x, y, size) {
    const p = ATLAS.icons.map[name];
    if (!p || !IMG.icons) return;
    ctx.drawImage(IMG.icons, p[0], p[1], IC, IC, x - size / 2, y - size / 2, size, size);
  }

  function shadow(x, y, w) {
    ctx.fillStyle = 'rgba(0,0,0,0.28)';
    ctx.beginPath();
    ctx.ellipse(x, y - 1, w / 2, 2.6, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  function spriteHeight(name) { const r = spr(name); return r ? r[3] / SC : 48; }

  // ------------------------------------------------------------------------------- text & fx
  function text(str, x, y, o = {}) {
    texts.push({ str, x: x + rnd(-6, 6), y, vy: o.vy || -22, life: o.life || 1.1, max: o.life || 1.1, color: o.color || '#fff',
      size: o.size || 9, delay: o.delay || 0, bold: o.bold !== false });
  }
  function enemyTop() { return A.enemy.y - spriteHeight(A.enemy.sprite || 'waldwolf') + 6; }
  function heroTop() { return A.hero.y - 50; }

  function projectile(sprite, from, to, dur, onArrive, opt = {}) {
    projs.push({ sprite, x0: from[0], y0: from[1], x1: to[0], y1: to[1], t: 0, dur, onArrive, arc: opt.arc || 0, flip: opt.flip });
  }

  function effect(kind, x, y, o = {}) { effects.push(Object.assign({ kind, x, y, t: 0, dur: o.dur || 0.35 }, o)); }

  const FX = {
    hit(target, amount, crit, kind) {
      if (!lastBattle) return;
      if (target === 'enemy') {
        const ex = A.enemy.x, ey = A.enemy.y - spriteHeight(A.enemy.sprite) * 0.5;
        const show = () => {
          A.enemy.flash = 0.12;
          text(fmt(amount) + (crit ? '!' : ''), ex, enemyTop(), { color: crit ? '#ffb020' : kind === 'dot' ? '#e0a0ff' : kind === 'tap' ? '#ffffff' : '#fff36a', size: crit ? 13 : kind === 'tap' ? 7 : 9 });
          if (crit) shake = Math.max(shake, 0.12);
        };
        const hx = A.hero.x + 12, hy = A.hero.y - 30;
        if (kind === 'arrow' || kind === 'fx_arrow') projectile('fx_arrow', [hx, hy], [ex, ey], 0.22, show);
        else if (kind === 'bolt') projectile(S.cls === 'priester' ? 'fx_holy' : 'fx_arcane', [hx, hy], [ex, ey], 0.3, show);
        else if (kind && kind.startsWith('fx_')) projectile(kind, [hx, hy], [ex, ey], 0.35, () => { show(); effect('burst', ex, ey, { col: kind }); });
        else if (kind === 'slash') { show(); effect('slash', ex, ey); }
        else if (kind === 'whirl') { show(); effect('whirl', ex, ey, { dur: 0.5 }); }
        else if (kind === 'tap') { show(); }
        else { show(); if (kind === 'melee') effect('slash', ex, ey, { small: true }); }
      } else {
        A.hero.flash = 0.12;
        text('-' + fmt(amount), A.hero.x, heroTop(), { color: kind === 'special' ? '#ff4040' : '#ff6a5a', size: kind === 'special' ? 12 : 8 });
        if (kind === 'special') { shake = 0.35; redFlash = 0.35; }
      }
    },
    heal(amount, src) {
      text('+' + fmt(amount), A.hero.x, heroTop(), { color: '#5cff6a', size: src === 'skill' ? 11 : 8 });
      effect('ring', A.hero.x, A.hero.y - 22, { sprite: 'fx_ring_green', dur: 0.5 });
      for (let i = 0; i < 5; i++) parts.push({ x: A.hero.x + rnd(-10, 10), y: A.hero.y - rnd(4, 40), vx: 0, vy: -18, life: 0.7, col: '#90ff90', size: 1 });
    },
    attack(who) { if (who === 'hero') A.hero.lunge = 0.2; else A.enemy.lunge = 0.2; },
    cast(id, sk) {
      text(sk.name, A.hero.x, heroTop() - 8, { color: '#ffe8a0', size: 7, vy: -10, life: 0.9 });
      if (sk.fx === 'ring') effect('ring', A.hero.x, A.hero.y - 22, { sprite: 'fx_ring', dur: 0.6 });
      if (sk.kind === 'dot') {
        const ex = A.enemy.x, ey = A.enemy.y - spriteHeight(A.enemy.sprite) * 0.5;
        if (sk.fx.startsWith('fx_')) projectile(sk.fx, [A.hero.x + 12, A.hero.y - 30], [ex, ey], 0.4, () => effect('burst', ex, ey, { col: sk.fx }));
        else { A.pet.lunge = 0.25; effect('slash', ex, ey); }
      }
      if (typeof UI !== 'undefined') UI.pulseSkill(id);
    },
    compAttack(id, d) {
      const p = A.comps[id];
      if (!p) return;
      const ex = A.enemy.x, ey = A.enemy.y - spriteHeight(A.enemy.sprite) * 0.45;
      const show = () => text(fmt(d), ex + 8, enemyTop() + 6, { color: '#d8d8d8', size: 7 });
      if (id === 'varrik') projectile('fx_arrow', [p.x + 10, p.y - 28], [ex, ey], 0.28, show);
      else if (id === 'mirra') projectile('fx_fire', [p.x + 10, p.y - 30], [ex, ey], 0.35, show);
      else if (id === 'elyra') projectile('fx_holy', [p.x + 10, p.y - 30], [ex, ey], 0.35, show);
      else { p.lunge = 0.2; show(); }
    },
    death(who) {
      if (who === 'enemy') { A.enemy.dying = 0.6; }
      else { A.hero.dead = 1; }
    },
    revive() { A.hero.dead = 0; A.hero.flash = 0.3; effect('ring', A.hero.x, A.hero.y - 22, { sprite: 'fx_ring', dur: 0.6 }); },
    spawn(e) {
      A.enemy.sprite = e.sprite;
      A.enemy.alpha = 0;
      A.enemy.spawn = 0.35;
      A.enemy.dying = 0;
      A.enemy.flash = 0;
    },
    reward(xp, gold) {
      const y = enemyTop();
      if (xp > 0) text(`+${fmt(xp)} EP`, A.enemy.x - 14, y - 4, { color: '#c890ff', size: 7, vy: -16, life: 1.3, delay: 0.15 });
      if (gold > 0) text(`+${fmt(gold)} Gold`, A.enemy.x + 14, y + 4, { color: '#ffd24a', size: 7, vy: -16, life: 1.3, delay: 0.25 });
    },
    loot(icon, r) {
      effect('loot', A.enemy.x, A.enemy.y - 16, { icon, col: RAR_COL[r], dur: 1.6, r });
    },
    warn(str) { warnText = { str, t: 2.2 }; if (typeof Snd !== 'undefined') Snd.play('warn'); },
    special() { shake = 0.4; redFlash = 0.4; },
    levelUp(level) {
      effect('pillar', A.hero.x, A.hero.y, { dur: 1.6 });
      banner = { str: `Stufe ${level}!`, sub: 'Stufenaufstieg', t: 2.4, col: '#ffd84a' };
      for (let i = 0; i < 24; i++) parts.push({ x: A.hero.x + rnd(-14, 14), y: A.hero.y - rnd(0, 50), vx: rnd(-8, 8), vy: -rnd(20, 50), life: rnd(0.8, 1.6), col: '#fff2a0', size: 1 });
    },
    banner(str, sub, col) { banner = { str, sub, t: 2.6, col: col || '#ffd84a' }; },
  };

  function onTap(ev) {
    if (!S || !battle) return;
    if (typeof Snd !== 'undefined') Snd.unlock();
    const d = tapAttack();
    if (d > 0) {
      const rect = canvas.getBoundingClientRect();
      const lx = (ev.clientX - rect.left) / rect.width * W;
      const ly = (ev.clientY - rect.top) / rect.height * H;
      effect('slash', lx, ly, { small: true, dur: 0.22 });
      if (typeof Snd !== 'undefined') Snd.play('tap');
      shake = Math.max(shake, 0.05);
    }
  }

  // ------------------------------------------------------------------------------- weather
  function spawnWeather(dt) {
    if (!weather) return;
    const rate = { leaves: 3, fireflies: 2, dust: 8, heat: 3, snow: 22, mist: 1.2, embers: 10, void: 6, torch: 4 }[weather] || 0;
    let n = rate * dt;
    while (n > 0) {
      if (Math.random() > n) break;
      n -= 1;
      const p = { life: 6, size: 1 };
      switch (weather) {
        case 'leaves': Object.assign(p, { x: rnd(0, W + 40), y: -4, vx: -rnd(8, 18), vy: rnd(10, 20), col: pick(['#d8a030', '#80b040', '#c06020']), size: 2, wob: rnd(0, 6) }); break;
        case 'fireflies': Object.assign(p, { x: rnd(0, W), y: rnd(80, 150), vx: rnd(-4, 4), vy: rnd(-4, 4), col: '#e8ff80', blink: rnd(0, 6), life: rnd(2, 5) }); break;
        case 'dust': Object.assign(p, { x: -4, y: rnd(60, 155), vx: rnd(30, 60), vy: rnd(-3, 3), col: 'rgba(230,190,140,0.6)', life: 6 }); break;
        case 'heat': Object.assign(p, { x: rnd(0, W), y: rnd(100, 150), vx: 0, vy: -rnd(4, 10), col: 'rgba(255,240,200,0.35)', life: rnd(1, 3) }); break;
        case 'snow': Object.assign(p, { x: rnd(0, W + 30), y: -3, vx: -rnd(4, 14), vy: rnd(14, 28), col: '#ffffff', size: Math.random() < 0.3 ? 2 : 1, wob: rnd(0, 6) }); break;
        case 'mist': Object.assign(p, { x: -40, y: rnd(110, 150), vx: rnd(4, 9), vy: 0, col: 'rgba(170,150,210,0.12)', size: 30, life: 40 }); break;
        case 'embers': Object.assign(p, { x: rnd(0, W), y: H + 2, vx: rnd(-6, 6), vy: -rnd(14, 34), col: pick(['#ffb040', '#ff7020', '#ffe080']), life: rnd(2, 6) }); break;
        case 'void': Object.assign(p, { x: rnd(0, W), y: rnd(0, 150), vx: 0, vy: -rnd(1, 4), col: pick(['#c080ff', '#80ffff', '#ffffff']), blink: rnd(0, 6), life: rnd(1, 3) }); break;
        case 'torch': Object.assign(p, { x: rnd(0, W), y: H + 2, vx: rnd(-3, 3), vy: -rnd(8, 20), col: '#ffb060', life: rnd(2, 5) }); break;
      }
      parts.push(p);
    }
  }

  // ------------------------------------------------------------------------------- frame
  function frame(dt) {
    if (!ctx) return;
    t += dt;
    const b = battle;
    if (b !== lastBattle) {
      lastBattle = b;
      texts = []; projs = []; effects = [];
      A.enemy.alpha = 0; A.enemy.sprite = b && b.enemy ? b.enemy.sprite : null;
      A.hero.dead = 0;
    }
    const bgName = b ? b.bg : 'bg_goldhain';
    if (bgName !== curBg) {
      curBg = bgName;
      parts = [];
      const z = ZONES.find((zz) => zz.bg === bgName);
      weather = z ? z.weather : /raid_glut|cathedral|mine|temple/.test(bgName) ? 'torch' : /abyss|thron/.test(bgName) ? 'void' : /ice|nebel/.test(bgName) ? 'snow' : null;
    }
    spawnWeather(dt);
    const sx = shake > 0 ? Math.round(rnd(-2, 2)) : 0, sy = shake > 0 ? Math.round(rnd(-1, 1)) : 0;
    shake = Math.max(0, shake - dt);
    ctx.setTransform(k, 0, 0, k, sx * k, sy * k);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    const bgi = bg(bgName);
    if (bgi.complete && bgi.naturalWidth) ctx.drawImage(bgi, 0, 0, W, H);
    else { ctx.fillStyle = '#101018'; ctx.fillRect(0, 0, W, H); }

    // actors (sorted by feet y)
    const draws = [];
    const hero = A.hero;
    hero.lunge = Math.max(0, hero.lunge - dt);
    hero.flash = Math.max(0, hero.flash - dt);
    const heroDead = b && b.h.dead > 0;
    if (S) {
      const bob = heroDead ? 0 : Math.sin(t * 2.4) * 1.1;
      const lx = hero.lunge > 0 ? Math.sin(Math.PI * (1 - hero.lunge / 0.2)) * 7 : 0;
      draws.push({ y: hero.y, fn: () => { shadow(hero.x, hero.y, 24); drawSprite(CLASSES[S.cls].sprite, hero.x + lx, hero.y + bob, { flash: hero.flash, rot: heroDead ? -Math.PI / 2 : 0, grey: heroDead }); } });
      if (S.cls === 'jaeger' && !(ATLAS.sprites.painted || []).includes('hero_jaeger')) {
        const pet = A.pet;
        pet.lunge = Math.max(0, pet.lunge - dt);
        const px2 = (S.comp.thorga ? 88 : 100) + (pet.lunge > 0 ? Math.sin(Math.PI * (1 - pet.lunge / 0.25)) * 18 : 0);
        draws.push({ y: pet.y, fn: () => { shadow(px2, pet.y, 22); drawSprite('waldwolf', px2, pet.y + Math.sin(t * 3) * 0.6, { flip: true, scale: 0.8 }); } });
      }
      for (const c of COMPANIONS) {
        if (!S.comp[c.id]) continue;
        const p = A.comps[c.id] || (A.comps[c.id] = { x: COMP_POS[c.id][0], y: COMP_POS[c.id][1], lunge: 0 });
        p.lunge = Math.max(0, p.lunge - dt);
        const lx2 = p.lunge > 0 ? Math.sin(Math.PI * (1 - p.lunge / 0.2)) * 6 : 0;
        const bob2 = Math.sin(t * 2.1 + p.x) * 1;
        draws.push({ y: p.y, fn: () => { shadow(p.x, p.y, 20); drawSprite(COMP_SPRITE[c.id], p.x + lx2, p.y + bob2, {}); } });
      }
    }
    const en = A.enemy;
    if (b && b.enemy && en.sprite) {
      en.lunge = Math.max(0, en.lunge - dt);
      en.flash = Math.max(0, en.flash - dt);
      if (en.spawn > 0) { en.spawn -= dt; en.alpha = 1 - Math.max(0, en.spawn) / 0.35; }
      else if (en.dying > 0) { en.dying -= dt; en.alpha = Math.max(0, en.dying / 0.6); }
      else if (!b.enemy.dead) en.alpha = 1;
      const big = spriteHeight(en.sprite) > 60;
      const bob = Math.sin(t * 2 + 1) * (big ? 1.6 : 1.1);
      const lx = en.lunge > 0 ? -Math.sin(Math.PI * (1 - en.lunge / 0.2)) * 7 : 0;
      const sink = en.dying > 0 ? (1 - en.dying / 0.6) * 6 : 0;
      const drop = en.spawn > 0 ? -en.spawn * 20 : 0;
      if (en.alpha > 0.01) {
        draws.push({ y: en.y, fn: () => {
          shadow(en.x, en.y, big ? 56 : 30);
          if (b.enemy.kind !== 'normal' && !b.enemy.dead) {
            ctx.save();
            ctx.globalAlpha = 0.25 + Math.sin(t * 4) * 0.08;
            ctx.fillStyle = b.enemy.kind === 'elite' ? '#ffd040' : '#ff5030';
            ctx.beginPath();
            ctx.ellipse(en.x, en.y - 1, big ? 34 : 22, 4, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
          }
          drawSprite(en.sprite, en.x + lx, en.y + bob + sink + drop, { flash: en.flash, alpha: en.alpha });
        } });
      }
    }
    draws.sort((a, c) => a.y - c.y);
    for (const d of draws) d.fn();

    // projectiles
    projs = projs.filter((p) => {
      p.t += dt;
      const q = Math.min(1, p.t / p.dur);
      const x = p.x0 + (p.x1 - p.x0) * q, y = p.y0 + (p.y1 - p.y0) * q - Math.sin(q * Math.PI) * p.arc;
      const r = spr(p.sprite);
      if (r) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(Math.atan2(p.y1 - p.y0, p.x1 - p.x0));
        ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], -r[2] / SC / 2, -r[3] / SC / 2, r[2] / SC, r[3] / SC);
        ctx.restore();
      }
      if (q >= 1) { if (p.onArrive) p.onArrive(); return false; }
      return true;
    });

    // effects
    effects = effects.filter((e) => {
      e.t += dt;
      const q = e.t / e.dur;
      if (q >= 1) return false;
      ctx.save();
      if (e.kind === 'slash') {
        const r = spr('fx_slash');
        const s = e.small ? 0.6 : 1;
        ctx.globalAlpha = 1 - q;
        ctx.translate(e.x, e.y);
        ctx.rotate(-0.6 + q * 0.8);
        ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], -16 * s, -16 * s, 32 * s, 32 * s);
      } else if (e.kind === 'whirl') {
        const r = spr('fx_whirl');
        ctx.globalAlpha = 1 - q * 0.6;
        ctx.translate(e.x, e.y);
        ctx.rotate(q * 12);
        ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], -20, -20, 40, 40);
      } else if (e.kind === 'ring') {
        const r = spr(e.sprite);
        const s = 0.4 + q * 0.9;
        ctx.globalAlpha = 1 - q;
        ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], e.x - 20 * s, e.y - 20 * s * 0.6, 40 * s, 40 * s * 0.6);
      } else if (e.kind === 'burst') {
        const col = { fx_fire: '#ff8030', fx_frost: '#a0e0ff', fx_arcane: '#d090ff', fx_holy: '#fff0a0', fx_shadow: '#a050e0', fx_arrow: '#ffffff' }[e.col] || '#fff';
        ctx.globalAlpha = 1 - q;
        ctx.fillStyle = col;
        for (let i = 0; i < 8; i++) {
          const a = i / 8 * Math.PI * 2;
          ctx.beginPath();
          ctx.arc(e.x + Math.cos(a) * q * 16, e.y + Math.sin(a) * q * 12, 1.3 * (1 - q * 0.5), 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (e.kind === 'pillar') {
        const r = spr('fx_pillar');
        ctx.globalAlpha = q < 0.2 ? q / 0.2 : 1 - (q - 0.2) / 0.8;
        ctx.drawImage(IMG.sprites, r[0], r[1], r[2], r[3], e.x - 18, e.y - 96, 36, 96);
      } else if (e.kind === 'loot') {
        const y = e.y - Math.min(1, q * 3) * 26;
        ctx.globalAlpha = q > 0.75 ? (1 - q) / 0.25 : 1;
        if (e.r >= 4) {
          ctx.fillStyle = e.col;
          ctx.globalAlpha *= 0.35;
          ctx.fillRect(e.x - 5, 0, 10, e.y);
          ctx.globalAlpha = q > 0.75 ? (1 - q) / 0.25 : 1;
        }
        ctx.shadowColor = e.col;
        ctx.shadowBlur = 8;
        ctx.fillStyle = e.col;
        ctx.fillRect(e.x - 10, y - 10, 20, 20);
        ctx.shadowBlur = 0;
        drawIcon(e.icon, e.x, y, 18);
      }
      ctx.restore();
      return true;
    });

    // particles
    parts = parts.filter((p) => {
      p.life -= dt;
      if (p.life <= 0 || p.y > H + 6 || p.x < -50 || p.x > W + 50) return false;
      p.x += (p.vx + (p.wob !== undefined ? Math.sin(t * 2 + p.wob) * 6 : 0)) * dt;
      p.y += p.vy * dt;
      if (p.blink !== undefined && Math.sin(t * 3 + p.blink) < 0) return true;
      ctx.fillStyle = p.col;
      if (p.size >= 20) {
        ctx.beginPath();
        ctx.ellipse(p.x, p.y, p.size, p.size * 0.3, 0, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 0.6, 0, Math.PI * 2);
        ctx.fill();
      }
      return true;
    });

    // floating text
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    texts = texts.filter((tx) => {
      if (tx.delay > 0) { tx.delay -= dt; return true; }
      tx.life -= dt;
      if (tx.life <= 0) return false;
      tx.y += tx.vy * dt;
      tx.vy *= 0.96;
      const age = tx.max - tx.life;
      const pop = age < 0.12 ? 1 + (0.12 - age) * 4 : 1;
      ctx.globalAlpha = Math.min(1, tx.life / 0.35);
      ctx.font = `${tx.bold ? '800' : '600'} ${Math.round(tx.size * pop)}px "Alegreya Sans", "Trebuchet MS", sans-serif`;
      ctx.lineWidth = Math.max(1.6, tx.size * 0.22);
      ctx.strokeStyle = 'rgba(10,6,4,0.95)';
      ctx.lineJoin = 'round';
      ctx.strokeText(tx.str, tx.x, tx.y);
      ctx.fillStyle = tx.color;
      ctx.fillText(tx.str, tx.x, tx.y);
      ctx.globalAlpha = 1;
      return true;
    });

    if (redFlash > 0) {
      redFlash -= dt;
      ctx.fillStyle = `rgba(200,20,10,${Math.max(0, redFlash) * 0.6})`;
      ctx.fillRect(-4, -4, W + 8, H + 8);
    }
    if (heroDead) {
      ctx.fillStyle = 'rgba(30,30,60,0.35)';
      ctx.fillRect(0, 0, W, H);
      bigText('Du bist gestorben', W / 2, 58, '#d0d8ff', 13);
      ctx.font = '600 8px "Alegreya Sans", sans-serif';
      ctx.fillStyle = '#e8e8f8';
      ctx.fillText(`Wiederbelebung in ${Math.ceil(b.h.dead)}…`, W / 2, 74);
    }
    if (warnText) {
      warnText.t -= dt;
      if (warnText.t <= 0) warnText = null;
      else {
        ctx.globalAlpha = Math.min(1, warnText.t / 0.3);
        bigText(warnText.str, W / 2, 30, '#ff8a2a', 10);
        ctx.globalAlpha = 1;
      }
    }
    if (banner) {
      banner.t -= dt;
      if (banner.t <= 0) banner = null;
      else {
        const age = 2.6 - banner.t;
        ctx.globalAlpha = Math.min(1, banner.t / 0.4, age / 0.15);
        const s = age < 0.2 ? 1.4 - age * 2 : 1;
        bigText(banner.str, W / 2, 52, banner.col, Math.round(18 * s));
        if (banner.sub) { ctx.font = '700 8px "Cinzel", Georgia, serif'; ctx.fillStyle = '#f0e6c8'; ctx.fillText(banner.sub, W / 2, 68); }
        ctx.globalAlpha = 1;
      }
    }
  }

  function bigText(str, x, y, col, size) {
    ctx.font = `700 ${size}px "Cinzel", Georgia, serif`;
    ctx.textAlign = 'center';
    ctx.lineWidth = 3;
    ctx.strokeStyle = 'rgba(12,6,2,0.95)';
    ctx.strokeText(str, x, y);
    ctx.fillStyle = col;
    ctx.fillText(str, x, y);
  }

  // Draws a sprite into a small canvas (portraits, previews). crop: fraction of height from top.
  function portrait(c, name, o = {}) {
    if (!IMG.sprites) return false;
    const r = spr(name);
    if (!r) return false;
    const x = c.getContext('2d');
    x.imageSmoothingEnabled = true;
    x.clearRect(0, 0, c.width, c.height);
    if (o.bg) { x.fillStyle = o.bg; x.fillRect(0, 0, c.width, c.height); }
    const crop = o.crop || 1;
    const sh = Math.round(r[3] * crop);
    const scale = o.scale || Math.min(c.width / r[2], c.height / sh);
    const w = r[2] * scale, h = sh * scale;
    x.drawImage(IMG.sprites, r[0], r[1] + (o.top || 0), r[2], sh, Math.round((c.width - w) / 2 + (o.dx || 0)), Math.round(c.height - h + (o.dy || 0)), w, h);
    return true;
  }

  return { init, frame, FX, portrait, resize, ready: () => !!IMG.sprites, W, H };
})();
