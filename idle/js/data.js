// Valdoran — static game content: classes, zones, quests, instances, items, professions.
'use strict';

const RARITY = [
  { name: 'Schlecht', color: '#9d9d9d', q: 0.55, adj: ['Rostig', 'Abgenutzt', 'Brüchig', 'Zerkratzt'] },
  { name: 'Verbreitet', color: '#ffffff', q: 0.8, adj: ['Schlicht', 'Robust', 'Solide', 'Einfach'] },
  { name: 'Selten', color: '#1eff00', q: 1.0, adj: ['Gehärtet', 'Verstärkt', 'Feingearbeitet', 'Geschmiedet'] },
  { name: 'Rar', color: '#2f8cff', q: 1.3, adj: ['Verzaubert', 'Runenverziert', 'Meisterhaft', 'Gesegnet'] },
  { name: 'Episch', color: '#b648ff', q: 1.7, adj: ['Uralt', 'Heldenhaft', 'Sagenhaft', 'Glorreich'] },
  { name: 'Legendär', color: '#ff8000', q: 2.4, adj: [] },
];

const SLOTS = ['weapon', 'head', 'shoulder', 'chest', 'hands', 'legs', 'feet', 'trinket'];
const SLOT_NAME = { weapon: 'Waffe', head: 'Kopf', shoulder: 'Schultern', chest: 'Brust', hands: 'Hände', legs: 'Beine', feet: 'Füße', trinket: 'Schmuck' };

// [name, gender] per tier; gender: m f n p(lural) for adjective endings
const BASES = {
  krieger: [['Kurzschwert', 'n'], ['Breitschwert', 'n'], ['Langschwert', 'n'], ['Runenklinge', 'f'], ['Sternenklinge', 'f']],
  magier: [['Eichenstab', 'm'], ['Zauberstab', 'm'], ['Kristallstab', 'm'], ['Runenstab', 'm'], ['Sternenstab', 'm']],
  jaeger: [['Kurzbogen', 'm'], ['Langbogen', 'm'], ['Kompositbogen', 'm'], ['Runenbogen', 'm'], ['Sternenbogen', 'm']],
  priester: [['Knüppel', 'm'], ['Streitkolben', 'm'], ['Morgenstern', 'm'], ['Runenhammer', 'm'], ['Sternenhammer', 'm']],
  head: [['Lederkappe', 'f'], ['Kettenhaube', 'f'], ['Stahlhelm', 'm'], ['Goldhelm', 'm'], ['Leerenkrone', 'f']],
  shoulder: [['Lederpolster', 'p'], ['Kettenschultern', 'p'], ['Stahlschiftungen', 'p'], ['Goldschulterstücke', 'p'], ['Leerenschultern', 'p']],
  chest: [['Lederwams', 'n'], ['Kettenhemd', 'n'], ['Stahlbrustplatte', 'f'], ['Goldharnisch', 'm'], ['Leerenharnisch', 'm']],
  hands: [['Lederhandschuhe', 'p'], ['Kettenhandschuhe', 'p'], ['Stahlstulpen', 'p'], ['Goldstulpen', 'p'], ['Leerengriffe', 'p']],
  legs: [['Lederhose', 'f'], ['Kettengamaschen', 'p'], ['Stahlbeinschienen', 'p'], ['Goldbeinschienen', 'p'], ['Leerengamaschen', 'p']],
  feet: [['Lederstiefel', 'p'], ['Kettenstiefel', 'p'], ['Stahlsabatons', 'p'], ['Goldsabatons', 'p'], ['Leerenschreiter', 'p']],
  trinket: [['Holzamulett', 'n'], ['Silberanhänger', 'm'], ['Saphiramulett', 'n'], ['Rubinmedaillon', 'n'], ['Leerenauge', 'n']],
};

const LEGENDARY = {
  krieger: 'Sonnenbrecher, Klinge der Morgenröte', magier: 'Stab der Sternenweberin', jaeger: 'Windflüsterer, Bogen des Nordens',
  priester: 'Lichtbringer, Hammer der Ersten', head: 'Krone des Ewigen Königs', shoulder: 'Schwingen des Drachenfürsten',
  chest: 'Herz des Berges', hands: 'Griffe des Titanen', legs: 'Beinschienen der Unendlichkeit', feet: 'Pfadfinder der Leere',
  trinket: 'Auge des Verschlingers',
};

const SECONDARY = {
  crit: { name: 'Kritische Trefferchance', suffix: 'der Präzision', unit: '%' },
  haste: { name: 'Tempo', suffix: 'des Sturms', unit: '%' },
  critDmg: { name: 'Kritischer Schaden', suffix: 'der Klinge', unit: '%' },
  goldP: { name: 'Goldfund', suffix: 'des Glücks', unit: '%' },
  xpP: { name: 'Erfahrung', suffix: 'des Gelehrten', unit: '%' },
  atkP: { name: 'Angriff', suffix: 'der Macht', unit: '%' },
  hpP: { name: 'Leben', suffix: 'des Bollwerks', unit: '%' },
};

const CLASSES = {
  krieger: {
    name: 'Krieger', res: 'Wut', resBar: 'red', sprite: 'hero_krieger', color: '#c79c6e',
    desc: 'Ein Bollwerk in schwerer Platte. Viel Leben und Rüstung, baut im Kampf Wut auf.',
    mods: { atk: 1.0, hp: 1.3, def: 1.35, crit: 5, haste: 0 },
    skills: ['schmetterhieb', 'klingensturm', 'kampfschrei'],
  },
  magier: {
    name: 'Magier', res: 'Mana', resBar: 'blue', sprite: 'hero_magier', color: '#69ccf0',
    desc: 'Meister der Elemente. Enormer Schaden, aber zerbrechlich wie Glas.',
    mods: { atk: 1.35, hp: 0.85, def: 0.8, crit: 8, haste: 0 },
    skills: ['feuerkugel', 'eislanze', 'arkanflut'],
  },
  jaeger: {
    name: 'Jäger', res: 'Fokus', resBar: 'orange', sprite: 'hero_jaeger', color: '#abd473',
    desc: 'Schneller Fernkämpfer mit treuem Wolfsgefährten. Hohe Kritchance und Tempo.',
    mods: { atk: 1.12, hp: 1.0, def: 1.0, crit: 10, haste: 8 },
    skills: ['praeziser_schuss', 'pfeilhagel', 'wolfsbiss'],
  },
  priester: {
    name: 'Priester', res: 'Mana', resBar: 'blue', sprite: 'hero_priester', color: '#f0ebe0',
    desc: 'Diener des Lichts. Heilt sich selbst, verflucht Feinde mit Schatten und ist schwer zu bezwingen.',
    mods: { atk: 1.08, hp: 1.1, def: 1.0, crit: 5, haste: 0 },
    skills: ['lichtstrahl', 'schattenpein', 'segnung'],
  },
};

// Peoples of Valdoran. pro/con use the stat keys of STAT_NAME (percent points); h scales the hero's height.
const RACES = {
  mensch: { name: 'Mensch', plural: 'Menschen', h: 1, desc: 'Anpassungsfähige Bewohner der Hohenmark. Sie lernen schnell und handeln geschickt.',
    pro: { xpP: 10, goldP: 5 }, con: {} },
  zwerg: { name: 'Zwerg', plural: 'Zwerge', h: 0.84, desc: 'Zähes Bergvolk aus den Frostgipfeln, geboren an Esse und Amboss. Kaum zu Fall zu bringen, aber nicht die Schnellsten.',
    pro: { hpP: 10, defP: 15 }, con: { haste: -5 } },
  elf: { name: 'Elf', plural: 'Elfen', h: 1.03, desc: 'Uraltes Volk der Sternenwälder. Flink und treffsicher, aber von zierlicher Gestalt.',
    pro: { crit: 4, haste: 6 }, con: { hpP: -8 } },
  ork: { name: 'Ork', plural: 'Orks', h: 1.08, desc: 'Stolze Krieger der Rotfelssteppe. Rohe Kraft und dicke Haut, doch wenig Geduld für Bücher.',
    pro: { atkP: 10, hpP: 5 }, con: { xpP: -5 } },
  halbling: { name: 'Halbling', plural: 'Halblinge', h: 0.72, desc: 'Kleines, findiges Volk aus den Hügeln. Sie finden immer etwas Glänzendes, schlagen aber nicht hart zu.',
    pro: { goldP: 15, lootP: 15 }, con: { atkP: -6 } },
  untot: { name: 'Untoter', plural: 'Untote', h: 1, desc: 'Von einem Fluch zurückgeholt. Ihr Fleisch heilt von selbst, doch Heiltränke wirken bei ihnen schwächer.',
    pro: { regen: 0.6, bossP: 6 }, con: { potion: -30 } },
};

// kind: dmg | dot | heal | buff ; mult on ATK ; fx: projectile sprite
const SKILLS = {
  schmetterhieb: { name: 'Schmetterhieb', icon: 'sk_schmetterhieb', lvl: 1, cd: 6, cost: 20, kind: 'dmg', mult: 1.44, fx: 'slash', desc: 'Ein wuchtiger Hieb: 144% Angriffsschaden.' },
  klingensturm: { name: 'Klingensturm', icon: 'sk_klingensturm', lvl: 6, cd: 14, cost: 35, kind: 'dmg', mult: 2.52, fx: 'whirl', desc: 'Wirbelt durch den Gegner: 252% Angriffsschaden.' },
  kampfschrei: { name: 'Kampfschrei', icon: 'sk_kampfschrei', lvl: 14, cd: 30, cost: 10, kind: 'buff', mult: 0.35, dur: 10, fx: 'ring', desc: '+35% Angriff für 10 Sek.' },
  feuerkugel: { name: 'Feuerkugel', icon: 'sk_feuerkugel', lvl: 1, cd: 5, cost: 25, kind: 'dmg', mult: 1.44, fx: 'fx_fire', desc: 'Schleudert eine Feuerkugel: 144% Angriffsschaden.' },
  eislanze: { name: 'Eislanze', icon: 'sk_eislanze', lvl: 6, cd: 10, cost: 30, kind: 'dmg', mult: 1.32, slow: 6, fx: 'fx_frost', desc: '132% Schaden und verlangsamt die Angriffe des Ziels 6 Sek. lang um 40%.' },
  arkanflut: { name: 'Arkanflut', icon: 'sk_arkanflut', lvl: 14, cd: 20, cost: 50, kind: 'dmg', mult: 3.9, fx: 'fx_arcane', desc: 'Entfesselt arkane Energie: 390% Angriffsschaden.' },
  praeziser_schuss: { name: 'Präziser Schuss', icon: 'sk_praeziser_schuss', lvl: 1, cd: 6, cost: 25, kind: 'dmg', mult: 1.5, fx: 'fx_arrow', desc: 'Ein genau gezielter Schuss: 150% Angriffsschaden.' },
  pfeilhagel: { name: 'Pfeilhagel', icon: 'sk_pfeilhagel', lvl: 6, cd: 15, cost: 40, kind: 'dmg', mult: 2.64, fx: 'fx_arrow', desc: 'Lässt Pfeile regnen: 264% Angriffsschaden.' },
  wolfsbiss: { name: 'Wolfsbiss', icon: 'sk_wolfsbiss', lvl: 14, cd: 12, cost: 20, kind: 'dot', mult: 2.4, dur: 8, fx: 'slash', desc: 'Dein Wolf reißt eine Wunde: 240% Schaden über 8 Sek.' },
  lichtstrahl: { name: 'Lichtstrahl', icon: 'sk_lichtstrahl', lvl: 1, cd: 6, cost: 20, kind: 'dmg', mult: 1.38, fx: 'fx_holy', desc: 'Ein Strahl heiligen Lichts: 138% Angriffsschaden.' },
  schattenpein: { name: 'Schattenpein', icon: 'sk_schattenpein', lvl: 6, cd: 12, cost: 25, kind: 'dot', mult: 3.0, dur: 10, fx: 'fx_shadow', desc: 'Schattenmagie zehrt am Ziel: 300% Schaden über 10 Sek.' },
  segnung: { name: 'Segnung', icon: 'sk_segnung', lvl: 14, cd: 16, cost: 35, kind: 'heal', mult: 0.4, fx: 'ring_green', desc: 'Heilt dich um 40% deines maximalen Lebens.' },
};

const MOBS = {
  waldwolf: 'Waldwolf', kobold: 'Tunnelkobold', waldspinne: 'Waldspinne', graufang: 'Graufang', kragg: 'Grubenmeister Kragg',
  moorschleim: 'Moorschleim', sumpfkriecher: 'Sumpfkriecher', krokilisk: 'Moorkrokilisk', schlammbrocken: 'Uralter Schlammbrocken', morva: 'Moorhexe Morva',
  hyaene: 'Steppenhyäne', oger: 'Rotfels-Oger', staubelementar: 'Staubelementar', brug: 'Ogerschamane Brug', gromm: 'Häuptling Gromm',
  skorpid: 'Glutskorpid', mumie: 'Sandmumie', sandwurm: 'Dünenwurm', ankhu: 'Grabwächter Ankhu', khet: 'Pharao Khet-Amun',
  yeti: 'Gipfelyeti', frostwolf: 'Frostwolf', eiselementar: 'Eiselementar', eisklaue: 'Eisklaue', glaciara: 'Glaciara die Frostwyrm',
  ghul: 'Hungriger Ghul', skelett: 'Skelettkrieger', banshee: 'Klagende Banshee', knochenwaechter: 'Knochenwächter', mordrek: 'Lich Mordrek',
  feuerelementar: 'Feuerelementar', lavahund: 'Lavahund', wichtel: 'Glutwichtel', magmagolem: 'Magmagolem', ignaroth: 'Ignaroth der Flammenfürst',
  leerwandler: 'Leerwandler', tentakelgrauen: 'Tentakelgrauen', sternenbestie: 'Sternenbestie', augenlose_wache: 'Augenlose Wache', umbrax: 'Umbrax der Sternenschlinger',
};

function Q(t, txt, kind, n, target, item) { return { t, txt, kind, n, target, item }; }

const ZONES = [
  {
    id: 'goldhain', name: 'Goldhain', lvl: [1, 8], bg: 'bg_goldhain', weather: 'leaves', giver: 'Hauptmann Aldric',
    desc: 'Sanfte Hügel und dichte Wälder vor den Toren der Hauptstadt Hohenmark.',
    mobs: ['waldwolf', 'kobold', 'waldspinne'], elite: 'graufang', boss: 'kragg',
    quests: [
      Q('Wölfe vor den Toren', 'Die Waldwölfe werden immer dreister und reißen das Vieh der Bauern. Dünne ihre Rudel aus, Rekrut.', 'kill', 14, 'waldwolf'),
      Q('Gestohlene Kerzen', 'Tunnelkobolde haben die Kerzen der Kapelle gestohlen. Hol sie zurück, bevor sie damit die Minen anzünden.', 'collect', 10, 'kobold', 'Gestohlene Kerze'),
      Q('Netze im Unterholz', 'Riesige Spinnen weben ihre Netze über die Handelswege. Räum sie aus dem Weg.', 'kill', 16, 'waldspinne'),
      Q('Graufang', 'Ein alter Leitwolf namens Graufang führt die Rudel an. Ohne ihn zerfallen sie.', 'elite', 1, 'graufang'),
      Q('Ruhe in Goldhain', 'Die Wälder sind noch nicht sicher. Zeig den Kreaturen, dass Hohenmark sich wehrt.', 'any', 25),
      Q('Der Grubenmeister', 'Hinter allem steckt Grubenmeister Kragg, der Anführer der Kobolde. Stell ihn in seiner Mine!', 'boss', 1, 'kragg'),
    ],
  },
  {
    id: 'nebelmoor', name: 'Nebelmoor', lvl: [8, 16], bg: 'bg_nebelmoor', weather: 'fireflies', giver: 'Kräuterkundige Wilma',
    desc: 'Ein dampfendes Sumpfland, in dem Irrlichter Wanderer in die Tiefe locken.',
    mobs: ['moorschleim', 'sumpfkriecher', 'krokilisk'], elite: 'schlammbrocken', boss: 'morva',
    quests: [
      Q('Schleim im Brunnen', 'Moorschleime verstopfen die Brunnen des Dorfes. Ohne sauberes Wasser werden alle krank.', 'kill', 14, 'moorschleim'),
      Q('Flossen als Beweis', 'Der Dorfrat glaubt nicht an die Sumpfkriecher. Bring mir ihre Flossen, dann muss er handeln.', 'collect', 10, 'sumpfkriecher', 'Kriecherflosse'),
      Q('Zähne im Schilf', 'Moorkrokilisken lauern im Schilf und schnappen nach jedem, der zu nah kommt.', 'kill', 16, 'krokilisk'),
      Q('Der Uralte', 'Ein uralter Schlammbrocken ist aus dem Moor erwacht. Er verschlingt alles auf seinem Weg.', 'elite', 1, 'schlammbrocken'),
      Q('Lichter im Nebel', 'Der Nebel wird dichter. Halte die Kreaturen des Moors in Schach.', 'any', 25),
      Q('Die Moorhexe', 'Moorhexe Morva hat den Sumpf verflucht. Brich ihren Bann!', 'boss', 1, 'morva'),
    ],
  },
  {
    id: 'rotfels', name: 'Rotfelsschlucht', lvl: [16, 24], bg: 'bg_rotfels', weather: 'dust', giver: 'Späherin Kaya',
    desc: 'Rote Tafelberge, heiße Winde und die Lager der Ogerstämme.',
    mobs: ['hyaene', 'oger', 'staubelementar'], elite: 'brug', boss: 'gromm',
    quests: [
      Q('Hungrige Hyänen', 'Steppenhyänen folgen unseren Karawanen. Halte sie uns vom Leib.', 'kill', 14, 'hyaene'),
      Q('Ogerkeulen', 'Ohne ihre Keulen sind Oger nur halb so gefährlich. Bring mir einige davon.', 'collect', 10, 'oger', 'Ogerkeule'),
      Q('Wirbelnder Staub', 'Staubelementare reißen unsere Zelte nieder. Bring sie zur Ruhe.', 'kill', 16, 'staubelementar'),
      Q('Der Schamane', 'Ogerschamane Brug beschwört die Stürme. Schalte ihn aus.', 'elite', 1, 'brug'),
      Q('Die Schlucht halten', 'Die Ogerstämme sammeln sich. Zeig ihnen, wer die Schlucht beherrscht.', 'any', 25),
      Q('Gromms Fall', 'Häuptling Gromm will gegen Hohenmark marschieren. Er darf die Schlucht nie verlassen.', 'boss', 1, 'gromm'),
    ],
  },
  {
    id: 'sonnenglut', name: 'Sonnenglutwüste', lvl: [24, 32], bg: 'bg_sonnenglut', weather: 'heat', giver: 'Archäologe Bertram',
    desc: 'Glühender Sand über den Gräbern eines vergessenen Königreichs.',
    mobs: ['skorpid', 'mumie', 'sandwurm'], elite: 'ankhu', boss: 'khet',
    quests: [
      Q('Stachel und Panzer', 'Glutskorpide nisten rund um die Ausgrabung. Keiner meiner Helfer traut sich mehr hinaus.', 'kill', 14, 'skorpid'),
      Q('Grabbeigaben', 'Die Mumien tragen goldene Skarabäen bei sich. Für die Wissenschaft!', 'collect', 10, 'mumie', 'Goldener Skarabäus'),
      Q('Beben unter dem Sand', 'Dünenwürmer untergraben das Lager. Treib sie zurück in die Tiefe.', 'kill', 16, 'sandwurm'),
      Q('Der Grabwächter', 'Grabwächter Ankhu bewacht den Eingang zur Pharaonengruft.', 'elite', 1, 'ankhu'),
      Q('Die Ausgrabung sichern', 'Die Toten erheben sich überall. Sichere die Ausgrabung.', 'any', 25),
      Q('Der erwachte Pharao', 'Pharao Khet-Amun ist erwacht und will sein Reich zurück. Leg ihn wieder schlafen.', 'boss', 1, 'khet'),
    ],
  },
  {
    id: 'frostgipfel', name: 'Frostgipfel', lvl: [32, 40], bg: 'bg_frostgipfel', weather: 'snow', giver: 'Bergführer Halvdan',
    desc: 'Eisige Pässe unter ewigem Schnee, wo eine Frostwyrm ihre Kreise zieht.',
    mobs: ['yeti', 'frostwolf', 'eiselementar'], elite: 'eisklaue', boss: 'glaciara',
    quests: [
      Q('Spuren im Schnee', 'Gipfelyetis überfallen die Holzfäller. Folge ihren Spuren.', 'kill', 14, 'yeti'),
      Q('Warme Pelze', 'Der Winter wird hart. Frostwolfpelze halten die Kinder im Dorf warm.', 'collect', 10, 'frostwolf', 'Frostwolfpelz'),
      Q('Lebendiges Eis', 'Eiselementare frieren den Pass zu. Brich sie in Stücke.', 'kill', 16, 'eiselementar'),
      Q('Eisklaue', 'Ein riesiger Yeti namens Eisklaue regiert die Höhlen. Fordere ihn heraus.', 'elite', 1, 'eisklaue'),
      Q('Der Pass muss frei sein', 'Die Versorgung über den Pass muss wieder fließen.', 'any', 25),
      Q('Schwingen aus Eis', 'Glaciara die Frostwyrm hüllt das Land in ewigen Winter. Hol sie vom Himmel!', 'boss', 1, 'glaciara'),
    ],
  },
  {
    id: 'schattenhain', name: 'Schattenhain', lvl: [40, 48], bg: 'bg_schattenhain', weather: 'mist', giver: 'Priesterin Elinor',
    desc: 'Ein verfluchter Wald, in dem die Toten keine Ruhe finden.',
    mobs: ['ghul', 'skelett', 'banshee'], elite: 'knochenwaechter', boss: 'mordrek',
    quests: [
      Q('Hunger der Toten', 'Ghule plündern die Gräber unserer Ahnen. Gib ihnen ewige Ruhe.', 'kill', 14, 'ghul'),
      Q('Verfluchte Knochen', 'Die Skelette sind von einem Fluch durchdrungen. Bring mir Splitter, damit ich ihn erforschen kann.', 'collect', 10, 'skelett', 'Verfluchter Knochensplitter'),
      Q('Das Klagen verstummen lassen', 'Das Klagen der Banshees treibt die Menschen in den Wahnsinn.', 'kill', 16, 'banshee'),
      Q('Der Knochenwächter', 'Ein Knochenwächter bewacht die Krypta des Lichs.', 'elite', 1, 'knochenwaechter'),
      Q('Licht in der Finsternis', 'Trag das Licht tiefer in den Schattenhain.', 'any', 25),
      Q('Der Lich', 'Lich Mordrek ist die Quelle des Fluchs. Zerstöre ihn!', 'boss', 1, 'mordrek'),
    ],
  },
  {
    id: 'glutschlund', name: 'Glutschlund', lvl: [48, 55], bg: 'bg_glutschlund', weather: 'embers', giver: 'Feuerwächter Brandt',
    desc: 'Ein brodelnder Vulkan, dessen Herz von einem Flammenfürsten beherrscht wird.',
    mobs: ['feuerelementar', 'lavahund', 'wichtel'], elite: 'magmagolem', boss: 'ignaroth',
    quests: [
      Q('Lodernde Gefahr', 'Feuerelementare strömen aus den Spalten. Lösche sie, bevor die Wälder brennen.', 'kill', 14, 'feuerelementar'),
      Q('Glühende Herzen', 'Lavahunde tragen glühende Herzen in sich. Unsere Schmiede brauchen sie.', 'collect', 10, 'lavahund', 'Lavaherz'),
      Q('Wichtelplage', 'Glutwichtel zünden alles an, was nicht wegläuft.', 'kill', 16, 'wichtel'),
      Q('Der Magmagolem', 'Ein Magmagolem blockiert den Weg zum Krater.', 'elite', 1, 'magmagolem'),
      Q('Durch die Flammen', 'Kämpf dich bis zum Kraterrand vor.', 'any', 25),
      Q('Der Flammenfürst', 'Ignaroth der Flammenfürst will die Welt in Brand setzen. Stoß ihn zurück in den Vulkan!', 'boss', 1, 'ignaroth'),
    ],
  },
  {
    id: 'leerenriss', name: 'Der Leerenriss', lvl: [55, 60], bg: 'bg_leerenriss', weather: 'void', giver: 'Erzmagierin Selwyn',
    desc: 'Ein klaffender Riss im Himmel, aus dem Wesen zwischen den Sternen strömen.',
    mobs: ['leerwandler', 'tentakelgrauen', 'sternenbestie'], elite: 'augenlose_wache', boss: 'umbrax',
    quests: [
      Q('Risse in der Welt', 'Leerwandler treten aus dem Riss. Jeder einzelne macht ihn größer.', 'kill', 14, 'leerwandler'),
      Q('Splitter der Leere', 'Mit Leerensplittern kann ich den Riss vermessen. Die Tentakelgrauen tragen welche.', 'collect', 10, 'tentakelgrauen', 'Leerensplitter'),
      Q('Sternenjagd', 'Sternenbestien jagen in Rudeln über die schwebenden Inseln.', 'kill', 16, 'sternenbestie'),
      Q('Die Augenlose Wache', 'Die Augenlose Wache hütet den Kern des Risses.', 'elite', 1, 'augenlose_wache'),
      Q('Den Riss eindämmen', 'Halte die Leere zurück, während ich den Riss versiegle.', 'any', 25),
      Q('Der Sternenschlinger', 'Umbrax der Sternenschlinger frisst die Sterne selbst. Er muss fallen!', 'boss', 1, 'umbrax'),
    ],
  },
];

const DUNGEONS = [
  { id: 'kobaltminen', name: 'Die Kobaltminen', lvl: 10, bg: 'bg_mine', desc: 'Verlassene Stollen voller Kobolde und lebender Erzbrocken.',
    bosses: [['schnarr', 'Vorarbeiter Schnarr'], ['hoehlenspinne', 'Skarra die Höhlenmutter'], ['erzkoloss', 'Der Erzkoloss']] },
  { id: 'moderhoehle', name: 'Die Moderhöhle', lvl: 18, bg: 'bg_cave', desc: 'Ein Pilzgeflecht unter dem Moor, in dem etwas Uraltes wuchert.',
    bosses: [['sporenmutter', 'Die Sporenmutter'], ['krokilisk_alpha', 'Krokilisk-Alpha'], ['ulgra', 'Sumpfhexer Ulgra']] },
  { id: 'tempel', name: 'Tempel von Khet', lvl: 28, bg: 'bg_temple', desc: 'Goldene Hallen unter dem Sand, bewacht von Priestern und Konstrukten.',
    bosses: [['skarabaeus', 'Skarabäusfürst Zek'], ['nefra', 'Hohepriesterin Nefra'], ['steinwaechter', 'Der Steinwächter']] },
  { id: 'frostspitze', name: 'Frostspitzbastion', lvl: 38, bg: 'bg_ice', desc: 'Eine Festung aus Eis, in der ein Kryomant seine Armee schmiedet.',
    bosses: [['yeti_boss', 'Häuptling Eisklinge'], ['halvar', 'Frostrufer Halvar'], ['kryoskelett', 'Der Kryomant']] },
  { id: 'aschenkathedrale', name: 'Aschenkathedrale', lvl: 46, bg: 'bg_cathedral', desc: 'Eine entweihte Kathedrale, in der ein Inquisitor die Toten befehligt.',
    bosses: [['velia', 'Banshee-Königin Velia'], ['knochenkoloss', 'Der Knochenkoloss'], ['malhar', 'Inquisitor Malhar']] },
  { id: 'schlund', name: 'Abyssaler Schlund', lvl: 56, bg: 'bg_abyss', desc: 'Der Abgrund unter dem Leerenriss. Hier beginnt das Nichts.',
    bosses: [['leerenbrut', 'Die Leerenbrut'], ['tentakelmeister', 'Der Tentakelmeister'], ['abgrundwaechter', 'Wächter des Abgrunds']] },
];

// special: periodic heavy attack {name, every (s), mult of max HP}
const RAIDS = [
  { id: 'glutkrone', name: 'Hallen der Glutkrone', lvl: 50, ilvl: 44, bg: 'bg_raid_glut', desc: 'Der Thronsaal tief im Glutschlund, Sitz der Feuerlords.',
    bosses: [
      { sprite: 'magmaul', name: 'Magmaul', special: 'Lavawelle' },
      { sprite: 'glutweberin', name: 'Glutweberin Sythra', special: 'Brennendes Netz' },
      { sprite: 'aschenfaust', name: 'Baron Aschenfaust', special: 'Höllenfeuer' },
      { sprite: 'ignis', name: 'Ignis, Herz der Flamme', special: 'Supernova', mount: 'glutross' },
    ] },
  { id: 'nebelthron', name: 'Nebelthron-Zitadelle', lvl: 58, ilvl: 54, bg: 'bg_raid_nebel', desc: 'Eine Zitadelle aus Eis und Nebel, regiert von einem untoten König.',
    bosses: [
      { sprite: 'varn', name: 'Knochenfürst Varn', special: 'Knochensturm' },
      { sprite: 'bleiche_dame', name: 'Die Bleiche Dame', special: 'Todesschrei' },
      { sprite: 'nivara', name: 'Frostdrache Nivara', special: 'Frostatem' },
      { sprite: 'nebelkoenig', name: 'Der Nebelkönig', special: 'Seelenernte' },
    ] },
  { id: 'verschlinger', name: 'Thron des Verschlingers', lvl: 60, ilvl: 62, bg: 'bg_raid_thron', desc: 'Am Grund des Leerenrisses erwacht ein Gott, der Welten frisst.',
    bosses: [
      { sprite: 'sternenfresser', name: 'Sternenfresser', special: 'Gravitationskollaps' },
      { sprite: 'zwillingsaugen', name: 'Die Zwillingsaugen', special: 'Doppelblick' },
      { sprite: 'xaroth', name: 'Xaroth, Schwinge des Abgrunds', special: 'Leerenatem' },
      { sprite: 'nhalzor', name: 'Nhal\'zor der Erwachte', special: 'Weltenende', mount: 'drache' },
    ] },
];

const WORLD_BOSSES = [
  { sprite: 'azurschwinge', name: 'Azurschwinge', bg: 'bg_goldhain', special: 'Arkansturm' },
  { sprite: 'grollhuf', name: 'Grollhuf der Urberg', bg: 'bg_rotfels', special: 'Erdbeben' },
  { sprite: 'verderbte_eiche', name: 'Die Verderbte Eiche', bg: 'bg_schattenhain', special: 'Dornenfluch' },
  { sprite: 'eiche', name: 'Hüter des Hains', bg: 'bg_nebelmoor', special: 'Wurzelgriff' },
];

const COMPANIONS = [
  { id: 'thorga', name: 'Thorga Eisenschild', role: 'Beschützerin', sprite: 'comp_tank', type: 'tank', unlock: 10,
    desc: 'Fängt 18% des Schadens ab, den du erleidest, und schlägt mit ihrem Hammer zu.' },
  { id: 'elyra', name: 'Schwester Elyra', role: 'Heilerin', sprite: 'comp_heiler', type: 'heal', unlock: 18,
    desc: 'Heilt dich im Kampf fortlaufend und erhöht deine Erholung.' },
  { id: 'varrik', name: 'Varrik Falkenauge', role: 'Schütze', sprite: 'comp_schuetze', type: 'dps', unlock: 26,
    desc: 'Ein Meisterschütze, der jedes Ziel trifft.' },
  { id: 'mirra', name: 'Mirra Sturmruf', role: 'Zauberin', sprite: 'comp_zauberin', type: 'dps', unlock: 34,
    desc: 'Schleudert Feuer auf alles, was dich bedroht.' },
];

const MOUNTS = [
  { id: 'pferd', name: 'Brauner Hengst', icon: 'm_pferd', bonus: 5, lvl: 10, price: 40 },
  { id: 'wolf', name: 'Grauer Reitwolf', icon: 'm_wolf', bonus: 10, lvl: 20, price: 60 },
  { id: 'widder', name: 'Bergwidder', icon: 'm_widder', bonus: 15, lvl: 30, price: 90 },
  { id: 'saebelzahn', name: 'Goldmähnen-Säbelzahn', icon: 'm_saebelzahn', bonus: 20, lvl: 40, price: 130 },
  { id: 'frostwolf', name: 'Frostwolf des Gipfels', icon: 'm_frostwolf', bonus: 25, source: 'Erfolg „Treue Seele“: 14 Tage in Folge einloggen' },
  { id: 'glutross', name: 'Glutross', icon: 'm_glutross', bonus: 32, source: 'Beute von Ignis, Herz der Flamme (6%)' },
  { id: 'drache', name: 'Leerendrache', icon: 'm_drache', bonus: 40, source: 'Beute von Nhal\'zor dem Erwachten (4%)' },
];

const TALENTS = {
  krieger: [
    ['Waffenmeister', 'atkP', 2, 5, 'st_atk'], ['Zähigkeit', 'hpP', 3, 5, 'st_hp'], ['Schwere Rüstung', 'defP', 5, 5, 'st_def'],
    ['Tiefe Wunden', 'critDmg', 6, 5, 'sk_schmetterhieb'], ['Schlachtrufer', 'cdr', 3, 5, 'sk_kampfschrei'], ['Blutdurst', 'regen', 0.12, 5, 'sk_segnung'],
    ['Brutalität', 'skillP', 6, 5, 'sk_klingensturm'], ['Unerschütterlich', 'hpP', 4, 5, 'st_def'], ['Kriegsbeute', 'goldP', 5, 5, 'gold'],
    ['Zorn', 'crit', 1.5, 5, 'st_crit'], ['Titanengriff', 'bossP', 6, 5, 'skull'], ['Kommandant', 'compP', 8, 5, 'flag'],
    ['Berserker', 'haste', 4, 3, 'st_haste'], ['Schildmauer', 'defP', 12, 3, 'st_def'], ['Avatar des Krieges', 'atkP', 12, 1, 'swords'],
  ],
  magier: [
    ['Arkane Intelligenz', 'atkP', 2, 5, 'book_blue'], ['Eisbarriere', 'hpP', 3, 5, 'sk_eislanze'], ['Konzentration', 'cdr', 3, 5, 'clock'],
    ['Feuerkraft', 'skillP', 5, 5, 'sk_feuerkugel'], ['Arkane Brillanz', 'crit', 1.2, 5, 'st_crit'], ['Frostrüstung', 'defP', 5, 5, 'st_def'],
    ['Zündung', 'critDmg', 8, 5, 'sk_feuerkugel'], ['Manaschild', 'hpP', 4, 5, 'st_hp'], ['Studien', 'xpP', 4, 5, 'book'],
    ['Pyromanie', 'bossP', 6, 5, 'skull'], ['Zeitkrümmung', 'haste', 3, 5, 'st_haste'], ['Beschwörer', 'compP', 8, 5, 'portal'],
    ['Erzmagier', 'skillP', 10, 3, 'sk_arkanflut'], ['Kälteeinbruch', 'cdr', 5, 3, 'sk_eislanze'], ['Meister der Elemente', 'atkP', 14, 1, 'star'],
  ],
  jaeger: [
    ['Scharfschütze', 'crit', 1, 5, 'sk_praeziser_schuss'], ['Wildnisleben', 'hpP', 3, 5, 'st_hp'], ['Schnellfeuer', 'haste', 2, 5, 'st_haste'],
    ['Tödliche Schüsse', 'critDmg', 6, 5, 'st_crit'], ['Tierbändiger', 'compP', 6, 5, 'sk_wolfsbiss'], ['Spurenleser', 'goldP', 5, 5, 'map'],
    ['Gezielte Schläge', 'skillP', 5, 5, 'sk_pfeilhagel'], ['Ausweichen', 'defP', 6, 5, 'st_def'], ['Jagdbeute', 'lootP', 6, 5, 'bag'],
    ['Jagdinstinkt', 'bossP', 6, 5, 'skull'], ['Erste Hilfe', 'regen', 0.12, 5, 'sk_segnung'], ['Fernkampfmeister', 'atkP', 3, 5, 'st_atk'],
    ['Rudelführer', 'compP', 15, 3, 'sk_wolfsbiss'], ['Bestienzorn', 'haste', 5, 3, 'st_haste'], ['Meisterschütze', 'crit', 6, 1, 'star'],
  ],
  priester: [
    ['Göttliche Stärke', 'atkP', 2, 5, 'sk_lichtstrahl'], ['Seelenstärke', 'hpP', 3, 5, 'st_hp'], ['Heilige Rüstung', 'defP', 5, 5, 'st_def'],
    ['Lichtbrunnen', 'regen', 0.14, 5, 'sk_segnung'], ['Inspiration', 'compP', 8, 5, 'flag'], ['Göttliche Gunst', 'crit', 1.2, 5, 'st_crit'],
    ['Heiliges Feuer', 'skillP', 6, 5, 'sk_lichtstrahl'], ['Gnade', 'potion', 12, 5, 'potion_heal'], ['Weisheit', 'xpP', 5, 5, 'book'],
    ['Schattenform', 'bossP', 6, 5, 'sk_schattenpein'], ['Machtwort', 'cdr', 4, 5, 'clock'], ['Segen des Glücks', 'goldP', 6, 5, 'gold'],
    ['Erleuchtung', 'atkP', 6, 3, 'star'], ['Schutzgeist', 'hpP', 8, 3, 'st_hp'], ['Avatar des Lichts', 'skillP', 30, 1, 'sk_lichtstrahl'],
  ],
};

const STAT_NAME = {
  atkP: 'Angriff', hpP: 'Leben', defP: 'Rüstung', crit: 'Kritische Trefferchance', critDmg: 'Kritischer Schaden', haste: 'Tempo',
  skillP: 'Fähigkeitsschaden', bossP: 'Schaden gegen Bosse und Elite', goldP: 'Goldfund', xpP: 'Erfahrung', tapP: 'Tippschaden',
  regen: 'Lebensregeneration pro Sek.', offline: 'Offline-Effizienz', compP: 'Stärke der Gefährten', cdr: 'Abklingzeitverringerung',
  potion: 'Trankheilung', lootP: 'Beutechance',
};

const TRAINING = [
  { id: 'atk', name: 'Waffentraining', icon: 'st_atk', key: 'atkP', per: 3, base: 15, growth: 1.19, teacher: 'Waffenmeisterin Brunhild' },
  { id: 'hp', name: 'Abhärtung', icon: 'st_hp', key: 'hpP', per: 3, base: 15, growth: 1.19, teacher: 'Feldscher Gorm' },
  { id: 'def', name: 'Rüstungskunde', icon: 'st_def', key: 'defP', per: 3, base: 20, growth: 1.19, teacher: 'Schmied Harald' },
  { id: 'crit', name: 'Präzision', icon: 'st_crit', key: 'crit', per: 0.5, max: 40, base: 120, growth: 1.3, teacher: 'Klingentänzerin Ysra' },
  { id: 'haste', name: 'Kampftempo', icon: 'st_haste', key: 'haste', per: 1, max: 40, base: 150, growth: 1.3, teacher: 'Klingentänzerin Ysra' },
  { id: 'tap', name: 'Kampfeslust', icon: 'swords', key: 'tapP', per: 10, base: 10, growth: 1.18, teacher: 'Waffenmeisterin Brunhild' },
  { id: 'gold', name: 'Feilschen', icon: 'gold', key: 'goldP', per: 4, base: 60, growth: 1.25, teacher: 'Händler Fenwick' },
  { id: 'xp', name: 'Gelehrsamkeit', icon: 'book', key: 'xpP', per: 3, base: 80, growth: 1.26, teacher: 'Bibliothekar Aurelius' },
  { id: 'offline', name: 'Lagerfeuerkunde', icon: 'clock', key: 'offline', per: 4, max: 12, base: 400, growth: 1.75, teacher: 'Wildhüterin Maren',
    extra: '+20 Min. maximale Offline-Zeit pro Rang' },
];

const LOGIN_REWARDS = [
  { label: 'Goldbeutel', icon: 'gold', give: { goldKills: 120 } },
  { label: '2 Dungeonschlüssel', icon: 'key', give: { keys: 2 } },
  { label: '2 Elixiere der Macht', icon: 'elixir_atk', give: { cons: { elixir_atk: 2 } } },
  { label: '25 Heldenabzeichen', icon: 'badge', give: { badges: 25 } },
  { label: 'Epische Truhe', icon: 'chest_epic', give: { chest: 4 } },
  { label: 'Goldschatz + 3 Schlüssel', icon: 'gold', give: { goldKills: 400, keys: 3 } },
  { label: 'Truhe des Champions', icon: 'chest_gold', give: { chest: 5, raidmarks: 3 } },
];

// Professions --------------------------------------------------------------------------------
const ORES = ['erz_kupfer', 'erz_eisen', 'erz_silber', 'erz_mondstahl', 'erz_sternen'];
const HERBS = ['kraut_wiesenklee', 'kraut_blutdorn', 'kraut_nebelmoos', 'kraut_sonnenbluete', 'kraut_sternenlotus'];
const MAT_NAME = {
  erz_kupfer: 'Kupfererz', erz_eisen: 'Eisenerz', erz_silber: 'Silbererz', erz_mondstahl: 'Mondstahlerz', erz_sternen: 'Sternenerz',
  kraut_wiesenklee: 'Wiesenklee', kraut_blutdorn: 'Blutdorn', kraut_nebelmoos: 'Nebelmoos', kraut_sonnenbluete: 'Sonnenblüte', kraut_sternenlotus: 'Sternenlotus',
  dust: 'Arkanstaub',
};
const TIER_ILVL = [10, 22, 34, 46, 58];

const FISH = [
  { id: 'fisch_barsch', name: 'Goldhain-Barsch', tier: 0, rar: 0 }, { id: 'fisch_forelle', name: 'Regenbogenforelle', tier: 0, rar: 1 },
  { id: 'fisch_karpfen', name: 'Schlammkarpfen', tier: 1, rar: 0 }, { id: 'fisch_sumpfaal', name: 'Sumpfaal', tier: 1, rar: 1 },
  { id: 'fisch_hecht', name: 'Rotfelshecht', tier: 2, rar: 0 }, { id: 'fisch_wuestenkoi', name: 'Wüstenkoi', tier: 2, rar: 1 },
  { id: 'fisch_eisflosser', name: 'Eisflosser', tier: 3, rar: 0 }, { id: 'fisch_geisterfisch', name: 'Geisterfisch', tier: 3, rar: 1 },
  { id: 'fisch_lavaflosser', name: 'Lavaflosser', tier: 4, rar: 0 }, { id: 'fisch_leerenkrake', name: 'Leerenkrake', tier: 4, rar: 1 },
  { id: 'fisch_goldschuppe', name: 'Goldschuppe', tier: -1, rar: 2 }, { id: 'fisch_sternenwal', name: 'Kleiner Sternenwal', tier: -1, rar: 3 },
];

const CONSUMABLES = {
  potion_heal: { name: 'Heiltrank', desc: 'Wird im Kampf automatisch getrunken, wenn dein Leben unter 35% fällt. Heilt 35%, danach 30 Sek. Abklingzeit. Du trägst höchstens 20 bei dir.', auto: true },
  elixir_atk: { name: 'Elixier der Macht', desc: '+25% Angriff für 30 Min.', buff: 'atk', dur: 1800 },
  elixir_xp: { name: 'Elixier des Wissens', desc: '+50% Erfahrung für 30 Min.', buff: 'xp', dur: 1800 },
  elixir_luck: { name: 'Glückselixier', desc: '+40% Gold und +30% Beutechance für 30 Min.', buff: 'luck', dur: 1800 },
  flask_titan: { name: 'Fläschchen der Titanen', desc: '+20% Angriff, Leben und Rüstung für 2 Std.', buff: 'titan', dur: 7200 },
  food_fish: { name: 'Gebratener Fisch', desc: '+12% Leben für 30 Min.', buff: 'food', food: { hpP: 12 }, dur: 1800 },
  food_stew: { name: 'Fischeintopf', desc: '+12% Angriff für 30 Min.', buff: 'food', food: { atkP: 12 }, dur: 1800 },
  food_meat: { name: 'Anglerfestmahl', desc: '+20% Erfahrung und Gold für 1 Std.', buff: 'food', food: { xpP: 20, goldP: 20 }, dur: 3600 },
};

const ALCHEMY = [
  { id: 'potion_heal', skill: 0, out: 1, cost: { kraut_wiesenklee: 5 }, gold: 14 },
  { id: 'elixir_atk', skill: 50, out: 1, cost: { kraut_blutdorn: 3 } },
  { id: 'elixir_xp', skill: 110, out: 1, cost: { kraut_nebelmoos: 3, kraut_wiesenklee: 2 } },
  { id: 'elixir_luck', skill: 170, out: 1, cost: { kraut_sonnenbluete: 3, kraut_blutdorn: 2 } },
  { id: 'flask_titan', skill: 240, out: 1, cost: { kraut_sternenlotus: 4, kraut_sonnenbluete: 3 } },
];

const COOKING = [
  { id: 'food_fish', skill: 0, out: 1, cost: { fishCommon: 2 } },
  { id: 'food_stew', skill: 60, out: 1, cost: { fishCommon: 3 } },
  { id: 'food_meat', skill: 140, out: 1, cost: { fishRare: 1, fishCommon: 2 } },
];

const DAILY_POOL = [
  { id: 'kills', name: 'Monsterjagd', desc: 'Besiege {n} Monster', n: 60, stat: 'kills', icon: 'swords' },
  { id: 'bosses', name: 'Bosshatz', desc: 'Besiege {n} Bosse', n: 2, stat: 'bosses', icon: 'skull' },
  { id: 'dungeon', name: 'In die Tiefe', desc: 'Schließe {n} Dungeon ab', n: 1, stat: 'dungeons', icon: 'portal' },
  { id: 'fish', name: 'Angelausflug', desc: 'Fange {n} Fische', n: 5, stat: 'fish', icon: 'rod' },
  { id: 'craft', name: 'Handwerkskunst', desc: 'Stelle {n} Dinge her', n: 3, stat: 'crafts', icon: 'anvil' },
  { id: 'gather', name: 'Sammelleidenschaft', desc: 'Sammle {n} Rohstoffe', n: 12, stat: 'gathers', icon: 'sickle' },
  { id: 'arena', name: 'Arenaruhm', desc: 'Bestreite {n} Arenakämpfe', n: 2, stat: 'arena', icon: 'honor' },
  { id: 'exped', name: 'Kartentisch', desc: 'Schicke {n} Expeditionen los', n: 2, stat: 'expeds', icon: 'flag' },
  { id: 'taps', name: 'Kampfeifer', desc: 'Tippe {n}-mal auf Gegner', n: 150, stat: 'taps', icon: 'st_atk' },
  { id: 'loot', name: 'Plünderer', desc: 'Erbeute {n} Gegenstände', n: 8, stat: 'loot', icon: 'bag' },
];

const WEEKLY = [
  { id: 'w_kills', name: 'Feldzug der Woche', desc: 'Besiege {n} Monster', n: 1500, stat: 'kills', icon: 'swords' },
  { id: 'w_dungeon', name: 'Dungeonmeister', desc: 'Schließe {n} Dungeons ab', n: 7, stat: 'dungeons', icon: 'portal' },
  { id: 'w_raid', name: 'Schlachtzug', desc: 'Besiege {n} Raid- oder Weltbosse', n: 4, stat: 'raidKills', icon: 'raid' },
];

const EXPEDITIONS = [
  'Die verlorene Karawane', 'Schmugglerbucht', 'Ruinen von Altheim', 'Der Eulenturm', 'Goblinlager am Fluss', 'Die Silbermine',
  'Hügelgräber der Riesen', 'Verwunschene Mühle', 'Das Nebeltor', 'Banditenpass', 'Sternwarte von Kael', 'Die gesunkene Galeere',
  'Hexenkessel im Moor', 'Pilgerweg der Mönche', 'Drachenhort am Gipfel', 'Der Smaragdsee', 'Festung Rabenstein', 'Das Bernsteinkloster',
];
const EXP_DURATIONS = [15, 30, 60, 120, 240, 480];

const ACHIEVEMENTS = [
  { id: 'k100', name: 'Erstes Blut', desc: 'Besiege 100 Monster', stat: 'kills', n: 100, reward: { badges: 10 } },
  { id: 'k1000', name: 'Schlächter', desc: 'Besiege 1.000 Monster', stat: 'kills', n: 1000, reward: { badges: 25 }, title: 'der Schlächter' },
  { id: 'k10000', name: 'Geißel der Wildnis', desc: 'Besiege 10.000 Monster', stat: 'kills', n: 10000, reward: { badges: 60 }, title: 'Geißel der Wildnis' },
  { id: 'k100000', name: 'Unaufhaltsam', desc: 'Besiege 100.000 Monster', stat: 'kills', n: 100000, reward: { raidmarks: 10 }, title: 'der Unaufhaltsame' },
  { id: 'l10', name: 'Abenteurer', desc: 'Erreiche Stufe 10', stat: 'level', n: 10, reward: { keys: 2 } },
  { id: 'l20', name: 'Veteran', desc: 'Erreiche Stufe 20', stat: 'level', n: 20, reward: { keys: 3 } },
  { id: 'l40', name: 'Held', desc: 'Erreiche Stufe 40', stat: 'level', n: 40, reward: { badges: 40 }, title: 'der Held' },
  { id: 'l60', name: 'Champion von Valdoran', desc: 'Erreiche Stufe 60', stat: 'level', n: 60, reward: { raidmarks: 5 }, title: 'Champion von Valdoran' },
  { id: 'z4', name: 'Weitgereist', desc: 'Schließe die Kampagne in 4 Zonen ab', stat: 'zones', n: 4, reward: { badges: 30 } },
  { id: 'z8', name: 'Retter der Welt', desc: 'Schließe die gesamte Kampagne ab', stat: 'zones', n: 8, reward: { raidmarks: 5 }, title: 'Retter von Valdoran' },
  { id: 'd1', name: 'Dungeonkriecher', desc: 'Schließe einen Dungeon ab', stat: 'dungeons', n: 1, reward: { keys: 2 } },
  { id: 'd25', name: 'Dungeonveteran', desc: 'Schließe 25 Dungeons ab', stat: 'dungeons', n: 25, reward: { badges: 40 } },
  { id: 'd100', name: 'Herr der Tiefen', desc: 'Schließe 100 Dungeons ab', stat: 'dungeons', n: 100, reward: { raidmarks: 5 }, title: 'Herr der Tiefen' },
  { id: 'm10', name: 'Mythischer Pionier', desc: 'Schließe einen Dungeon auf Mythisch +10 ab', stat: 'mythic', n: 10, reward: { raidmarks: 5 }, title: 'der Mythische' },
  { id: 'r1', name: 'Raidneuling', desc: 'Besiege einen Raidboss', stat: 'raidBoss', n: 1, reward: { raidmarks: 2 } },
  { id: 'r12', name: 'Bezwinger der Throne', desc: 'Besiege alle 12 Raidbosse', stat: 'raidUnique', n: 12, reward: { raidmarks: 15 }, title: 'Bezwinger der Throne' },
  { id: 'wb5', name: 'Weltbossjäger', desc: 'Besiege 5 Weltbosse', stat: 'worldBoss', n: 5, reward: { raidmarks: 4 } },
  { id: 'epic1', name: 'Lila Glanz', desc: 'Erbeute einen epischen Gegenstand', stat: 'epics', n: 1, reward: { badges: 15 } },
  { id: 'leg1', name: 'Legende', desc: 'Erbeute einen legendären Gegenstand', stat: 'legendaries', n: 1, reward: { raidmarks: 5 }, title: 'der Legendäre' },
  { id: 'gold1m', name: 'Goldrausch', desc: 'Verdiene insgesamt 1 Mio. Gold', stat: 'goldEarned', n: 1e6, reward: { badges: 30 } },
  { id: 'gold1b', name: 'Drachenhort', desc: 'Verdiene insgesamt 1 Mrd. Gold', stat: 'goldEarned', n: 1e9, reward: { raidmarks: 8 }, title: 'der Drachenreiche' },
  { id: 'fish25', name: 'Petri Heil', desc: 'Fange 25 Fische', stat: 'fish', n: 25, reward: { cons: { food_meat: 2 } } },
  { id: 'fishall', name: 'Meisterangler', desc: 'Fange jede Fischart', stat: 'fishSpecies', n: 12, reward: { raidmarks: 4 }, title: 'Meisterangler' },
  { id: 'craft50', name: 'Meisterhandwerk', desc: 'Stelle 50 Dinge her', stat: 'crafts', n: 50, reward: { badges: 30 } },
  { id: 'arena1600', name: 'Herausforderer', desc: 'Erreiche eine Arenawertung von 1600', stat: 'rating', n: 1600, reward: { honor: 300 } },
  { id: 'arena2000', name: 'Gladiator', desc: 'Erreiche eine Arenawertung von 2000', stat: 'rating', n: 2000, reward: { raidmarks: 6 }, title: 'Gladiator' },
  { id: 'streak7', name: 'Stammgast', desc: 'Logge dich 7 Tage in Folge ein', stat: 'streak', n: 7, reward: { chest: 4 } },
  { id: 'streak14', name: 'Treue Seele', desc: 'Logge dich 14 Tage in Folge ein', stat: 'streak', n: 14, reward: { mount: 'frostwolf' }, title: 'die Treue Seele' },
  { id: 'comp4', name: 'Gemeinschaft', desc: 'Rekrutiere alle 4 Gefährten', stat: 'companions', n: 4, reward: { badges: 40 } },
  { id: 'mount4', name: 'Stallmeister', desc: 'Besitze 4 Reittiere', stat: 'mounts', n: 4, reward: { badges: 30 } },
  { id: 'wt3', name: 'Jenseits der Welt', desc: 'Erreiche Weltstufe 3', stat: 'worldTier', n: 3, reward: { raidmarks: 6 }, title: 'Weltenwanderer' },
];

const ARENA_RANKS = [
  [0, 'Rekrut'], [1200, 'Kämpfer'], [1400, 'Rivale'], [1600, 'Herausforderer'], [1800, 'Duellant'], [2000, 'Gladiator'], [2400, 'Elite-Gladiator'],
];
const ARENA_NAMES = ['Thrandor', 'Kaelith', 'Mirabel', 'Gorrim', 'Sylvara', 'Brannok', 'Velka', 'Durgan', 'Elowen', 'Rhaskar', 'Isolde', 'Torvin',
  'Asmira', 'Kragnar', 'Lunett', 'Orvald', 'Sefira', 'Yorin', 'Zhalia', 'Bertolf'];

const NAME_PARTS = [['Ael', 'Bran', 'Cael', 'Dor', 'Eld', 'Fen', 'Gar', 'Hal', 'Isen', 'Jor', 'Kael', 'Lor', 'Mor', 'Nym', 'Os', 'Ryn', 'Syl', 'Thal', 'Val', 'Wyn'],
  ['dric', 'wen', 'ion', 'gar', 'ara', 'ith', 'mund', 'ric', 'ora', 'eth', 'wyn', 'dor', 'iel', 'as', 'rin']];

// Places and quest givers per zone. A walks to and from these: the first giver waits in the village,
// the second at an outpost nearer the danger. Positions are along the zone's path and set walking times.
const WORLD = {
  goldhain: {
    hub: 'Hohenmark, Stadttor', post: 'Försterhütte',
    givers: [{ id: 'aldric', name: 'Hauptmann Aldric', role: 'Stadtwache' }, { id: 'jorik', name: 'Förster Jorik', role: 'Förster' }],
    hunts: { waldwolf: 'Wolfslichtung', kobold: 'Koboldstollen', waldspinne: 'Spinnenhain' }, elite: 'Graufangs Bau', boss: 'Kraggs Grube',
  },
  nebelmoor: {
    hub: 'Dorf Moorbrück', post: 'Pfahlbau-Wacht',
    givers: [{ id: 'wilma', name: 'Kräuterkundige Wilma', role: 'Heilerin' }, { id: 'edgar', name: 'Sumpfläufer Edgar', role: 'Kundschafter' }],
    hunts: { moorschleim: 'Schleimtümpel', sumpfkriecher: 'Kriecherufer', krokilisk: 'Schilfgürtel' }, elite: 'Schlammgrube', boss: 'Morvas Hütte',
  },
  rotfels: {
    hub: 'Karawanenlager', post: 'Fort Rotfels',
    givers: [{ id: 'kaya', name: 'Späherin Kaya', role: 'Späherin' }, { id: 'rothmann', name: 'Oberst Rothmann', role: 'Festungskommandant' }],
    hunts: { hyaene: 'Hyänenkuhle', oger: 'Ogerlager', staubelementar: 'Staubsenke' }, elite: 'Schamanenfelsen', boss: 'Gromms Thronhügel',
  },
  sonnenglut: {
    hub: 'Ausgrabungslager', post: 'Oase Al-Mirah',
    givers: [{ id: 'bertram', name: 'Archäologe Bertram', role: 'Gelehrter' }, { id: 'samira', name: 'Wüstenführerin Samira', role: 'Führerin' }],
    hunts: { skorpid: 'Skorpidnest', mumie: 'Grabfeld', sandwurm: 'Wurmdünen' }, elite: 'Grabeingang', boss: 'Pyramide von Khet',
  },
  frostgipfel: {
    hub: 'Holzfällerdorf Kaltbach', post: 'Passwacht',
    givers: [{ id: 'halvdan', name: 'Bergführer Halvdan', role: 'Bergführer' }, { id: 'sigrun', name: 'Jägerin Sigrun', role: 'Jägerin' }],
    hunts: { yeti: 'Yetihöhlen', frostwolf: 'Frostwolfpass', eiselementar: 'Eisfeld' }, elite: 'Eisklauenhöhle', boss: 'Glaciaras Horst',
  },
  schattenhain: {
    hub: 'Kapelle des Lichts', post: 'Friedhofswacht',
    givers: [{ id: 'elinor', name: 'Priesterin Elinor', role: 'Priesterin' }, { id: 'morten', name: 'Totengräber Morten', role: 'Totengräber' }],
    hunts: { ghul: 'Leichenacker', skelett: 'Knochengrund', banshee: 'Klagende Ruinen' }, elite: 'Vergessene Krypta', boss: 'Mordreks Gruft',
  },
  glutschlund: {
    hub: 'Feste Aschwall', post: 'Schmiede am Krater',
    givers: [{ id: 'brandt', name: 'Feuerwächter Brandt', role: 'Feuerwächter' }, { id: 'thorvald', name: 'Schmied Thorvald', role: 'Waffenschmied' }],
    hunts: { feuerelementar: 'Flammenspalten', lavahund: 'Lavabett', wichtel: 'Wichtelkessel' }, elite: 'Magmakammer', boss: 'Krater des Flammenfürsten',
  },
  leerenriss: {
    hub: 'Sternwacht', post: 'Vorposten am Riss',
    givers: [{ id: 'selwyn', name: 'Erzmagierin Selwyn', role: 'Erzmagierin' }, { id: 'varos', name: 'Leerenjäger Varos', role: 'Leerenjäger' }],
    hunts: { leerwandler: 'Leerenrand', tentakelgrauen: 'Tentakelsenke', sternenbestie: 'Sternenklippe' }, elite: 'Kern des Risses', boss: 'Thron der Sterne',
  },
};
// quest index -> giver index and the quests that must be turned in first
const QUEST_FLOW = [{ g: 0, req: [] }, { g: 0, req: [] }, { g: 0, req: [0, 1] }, { g: 1, req: [2] }, { g: 1, req: [2] }, { g: 1, req: [3, 4] }];
// painted stand-ins for quest givers until art/npc_<id>.jpg exists
const NPC_SPRITES = ['comp_tank', 'comp_heiler', 'comp_schuetze', 'comp_zauberin', 'rival_krieger', 'rival_priester', 'rival_jaeger', 'rival_magier'];
const TURNIN_LINES = [
  'Ausgezeichnete Arbeit. Valdoran steht in deiner Schuld.', 'Ich wusste, dass ich mich auf dich verlassen kann.',
  'Schneller als gedacht! Hier ist deine Belohnung.', 'Das wird die Leute hier ruhiger schlafen lassen. Danke dir.',
];
