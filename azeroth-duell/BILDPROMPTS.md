# Azeroth Duell – Bildprompts für alle Grafiken

Die Prompts sind auf Englisch, weil Bildmodelle damit am zuverlässigsten arbeiten. Jeder Prompt besteht aus
**[STIL-BLOCK] + Motiv-Zeile**. Den Stil-Block immer vorne einfügen, damit alles aus einem Guss aussieht.

## Globale Stil-Blöcke

**STIL-ICON** (Fähigkeiten, Items, Klassenwappen)
> flat vector game icon, bold clean shapes, thick dark brown outline, limited warm palette with one strong accent color, subtle cel-shaded highlights, centered single subject, high contrast, fantasy MMO style inspired by classic World of Warcraft icons, no text, no watermark, transparent background, square 1:1, SVG-friendly, 512x512

**STIL-PORTRAIT** (Rassen, Monster)
> stylized vector character portrait, bust shot, front view, thick dark outline, flat colors with simple cel shading, exaggerated fantasy proportions like Warcraft cinematic art, expressive glowing eyes, shoulder armor visible, circular composition, transparent background, no text, SVG-friendly, 1024x1024

**STIL-UI** (Hintergründe, Buttons, Rahmen)
> vector game UI asset, hand-painted fantasy MMO interface style like classic World of Warcraft, worn aged materials, crisp edges, no text, no characters, SVG-friendly

---

## 1. UI-Grundelemente

### 1.1 Hintergrund (Pergament)
Hochformat, wird hinter allen Menüs verwendet.
> [STIL-UI] seamless-looking aged parchment paper background, portrait 9:19, warm beige and tan tones, subtle fibers and stains, darker burnt and torn edges with soft vignette, faint ink splatters in the corners, a very faint compass-rose watermark in the center, plenty of calm empty space for UI on top, 1080x2280

Varianten:
- **Pergament hell (Menüs):** wie oben, „light cream parchment".
- **Pergament dunkel (Kampfleiste):** „dark weathered parchment, brown leather-stained, candle-lit edges".
- **Pergamentrolle (Tooltip-Panel):** > [STIL-UI] small parchment scroll panel with curled top and bottom edges, flat empty center, wax-seal-red thin border, 4:3, transparent outside

### 1.2 Button – rot, eckig (Standard)
> [STIL-UI] rectangular game button, deep crimson red with a subtle vertical gradient, squared angular corners with small chamfered corners, thin gold-bronze metal frame with tiny rivets in the corners, inner dark red bevel, slight glossy top highlight, empty center for text, 3:1 ratio, 960x320

Zustände (jeweils derselbe Prompt plus):
- **Normal:** „default state".
- **Gedrückt:** „pressed state, darker red, inner shadow, frame slightly sunk".
- **Deaktiviert:** „disabled state, desaturated gray-red, dull frame".
- **Hover/Aktiv:** „highlighted state, brighter red, soft golden glow around the frame".

### 1.3 Button klein / quadratisch (Menü, Ton, Zurück)
> [STIL-UI] small square game button, crimson red face, chamfered corners, gold-bronze frame with rivets, empty center, 1:1, 256x256

### 1.4 Button golden (Hauptaktion „Kampf beginnen")
> [STIL-UI] wide rectangular call-to-action button, polished gold and amber metal plate, angular chamfered corners, engraved border line, red gem in each end, empty center, 3:1, 960x320

### 1.5 Symbol-Rahmen für Fähigkeiten
> [STIL-UI] square ability slot frame, thick bronze-gold border with beveled edges and four corner studs, dark empty inner field, slightly rounded corners, 1:1, 512x512

Varianten: **Völkerfähigkeit** (grüner Rahmen), **Gegenstand/Trank** (roter Rahmen), **gesperrt** (Rahmen grau mit Schloss darüber, Mitte leer).

### 1.6 Seltenheits-Rahmen (Items)
Gleicher Prompt wie 1.5, Farbe: **Gewöhnlich** silbrig-weiß, **Selten** grün, **Hervorragend** blau, **Episch** violett mit leichtem Leuchten.

### 1.7 Einheitenrahmen / Namensplakette
> [STIL-UI] horizontal unit nameplate, dark leather and bronze frame, empty health bar slot (long) and thinner resource bar slot beneath, small level badge at the right end, 4:1, 1200x300

### 1.8 Balken
- **Lebensbalken:** > [STIL-UI] horizontal health bar fill, glossy green gradient with small top highlight, 10:1, plus empty dark trough with metal rim
- **Mana:** blau, **Wut:** rot, **Energie:** gelb, **Fokus:** orange – gleicher Prompt, Farbe wechseln.

### 1.9 Titel-Logo
> [STIL-UI] game logo lettering "AZEROTH DUELL", chiseled gold metallic serif letters with dark bronze outline and warm glow, crossed sword and axe behind the text, small banner reading nothing, transparent background, 3:1, 1500x500

### 1.10 Siegbanner / Niederlage
- **SIEG:** > [STIL-UI] victory banner, golden laurel wreath and radiating sunburst behind an empty gold plaque, 3:2
- **NIEDERLAGE:** > [STIL-UI] defeat banner, cracked gray stone plaque, broken sword, dark smoke, 3:2

### 1.11 Hinweis- und Statussymbole (klein)
Gleicher STIL-ICON: Betäubung (kreisende Sterne), Blutung (Tropfen), Gift (grüne Giftwolke), Schild (blauer Schild), Verlangsamt (Eiskristall), Heilung über Zeit (grünes Kleeblatt-Plus), Wut-Buff (rote Aura).

---

## 2. Kampf-Hintergründe (5 Zonen, Hochformat)

Alle: > [STIL-UI] painterly vector battle arena background, portrait 9:16, flat ground plane in the lower third for two fighters, atmospheric depth layers (foreground, midground, far background), soft fog, no characters, no text, empty center

1. **Wald der Nebel:** „misty ancient forest, tall dark green pines and oaks, golden light rays through the fog, mossy stone path"
2. **Die Rote Wüste:** „red desert canyon, sandstone arches, cacti, orange-red sky with two suns low, dust haze"
3. **Düsterfenn:** „gloomy swamp graveyard, crooked tombstones, dead trees, purple-blue night, will-o-wisps, ruined chapel"
4. **Eiskronengletscher:** „frozen glacier plateau, jagged ice peaks, blowing snow, cold blue light, ancient frozen ruins"
5. **Brennende Steppe:** „volcanic wasteland, rivers of lava, black basalt spires, ember sky with floating sparks, demonic banners"

---

## 3. Rassen-Portraits (8)

Alle: [STIL-PORTRAIT] + Motiv. Allianz = blauer, Horde = roter Rand/Hintergrundton.

| Rasse | Motiv-Zeile |
|---|---|
| **Mensch** | „young human adventurer, short brown hair, warm friendly face, light skin, kingdom-blue background glow, steel pauldrons" |
| **Zwerg** | „stocky dwarf, huge braided copper-orange beard with gold rings, bushy eyebrows, round nose, sturdy plate shoulders, forge-glow background" |
| **Nachtelf** | „night elf, violet-blue skin, long pointed upturned ears, long teal-white hair, glowing silver eyes without pupils, subtle facial markings, moonlit blue background" |
| **Gnom** | „tiny gnome inventor, oversized head, wild bubblegum-pink hair puffs, brass goggles on forehead, cheeky grin, gear and cog details, workshop background" |
| **Orc** | „muscular orc warrior, green skin, strong jaw with two upward tusks, black topknot ponytail, heavy brow, yellow-red eyes, spiked iron pauldrons, ember-red background" |
| **Untoter** | „undead Forsaken, gray-green decaying skin, sunken cheeks, exposed teeth and jawbone, glowing yellow eyes, thin dark ragged hair, tattered cloth shoulders, sickly violet mist" |
| **Taure** | „tauren, brown bull face with wide snout and gold nose ring, curved ivory horns, black mane, large side ears, tribal totem shoulders, golden plains background" |
| **Troll** | „jungle troll, teal-blue skin, tall crimson mohawk, long curved tusks, long pointy ears, glowing yellow eyes, tribal bone shoulders, jungle green-red background" |

---

## 4. Klassen-Wappen (9) – Abzeichen am Portrait

Alle: [STIL-ICON] circular class emblem badge, + Motiv, Klassenfarbe als Hauptton.

| Klasse | Farbe | Motiv |
|---|---|---|
| Krieger | Braun/Sand `#C79C6E` | crossed sword and shield |
| Paladin | Rosa `#F58CBA` | glowing warhammer with holy wings |
| Jäger | Hellgrün `#ABD473` | bow with arrow and paw print |
| Schurke | Gelb `#FFF569` | two crossed daggers |
| Priester | Weiß `#F0F0F0` | radiant star burst with halo |
| Schamane | Blau `#2B7DF0` | lightning bolt over a totem |
| Magier | Hellblau `#69CCF0` | arcane orb with swirling runes |
| Hexenmeister | Violett `#9482C9` | purple flame skull with demon eye |
| Druide | Orange `#FF7D0A` | oak leaf with moon crescent and claw marks |

---

## 5. Klassenfähigkeiten (45 Symbole)

Alle: [STIL-ICON] + Motiv. Schulfarbe als Akzent: Physisch = Stahlgrau, Feuer = Orange, Frost = Eisblau, Arkan = Violett, Natur = Grün, Schatten = Dunkelviolett, Heilig = Gold.

**Krieger:** Heldenhafter Stoß – „sword slash arc with spark" · Zerschmettern – „heavy hammer smashing the ground, cracks" · Schildschlag – „shield with impact burst and stars" · Schlachtruf – „war horn with red sound waves" · Hinrichten – „executioner axe above a skull"

**Paladin:** Kreuzfahrerstoß – „glowing cross-shaped sword strike" · Richturteil – „golden scales of justice with light beam" · Heiliges Licht – „soft golden light cascading from above" · Segen der Macht – „praying hands with golden aura" · Göttlicher Schutz – „golden shield bubble with wings"

**Jäger:** Schuss – „single arrow in flight" · Zielschuss – „crosshair over a bullseye with arrow" · Schlangenbiss – „green viper with fangs and poison drops" · Mehrfachschuss – „three arrows raining down" · Frostfalle – „steel trap with ice crystals"

**Schurke:** Boshafter Stich – „dagger stabbing with blood spark" · Blutung – „red blood drop with dripping blade" · Nierenhieb – „clenched fist with impact lines" · Entrinnen – „swirling smoke cloud with fading silhouette" · Meucheln – „dagger and skull, deadly red glint"

**Priester:** Strafe – „bolt of holy light from a staff" · Schattenwort: Schmerz – „purple skull with dark tendrils" · Blitzheilung – „pink glowing heart with sparkles" · Machtwort: Schild – „translucent blue-gold shield with runes" · Heiliges Feuer – „white-gold flame descending"

**Schamane:** Blitzschlag – „crackling blue-green lightning bolt" · Flammenschock – „fire burst from a stone totem" · Erdschock – „erupting earth with cracked stone shards" · Welle der Heilung – „curling teal wave with green sparkles" · Kampfrausch – „swirling wind vortex with red streaks"

**Magier:** Frostblitz – „ice shard bolt with snow trail" · Feuerball – „blazing fireball comet" · Arkane Geschosse – „three purple magic missiles" · Frostnova – „expanding ring of ice spikes" · Manaschild – „violet-blue arcane shield bubble with runes"

**Hexenmeister:** Schattenblitz – „dark purple bolt with black smoke" · Verderbnis – „wilting rose with dark mist" · Lebensentzug – „red drops flowing from a victim into a hand" · Furcht – „terrified screaming ghost face" · Seelenfeuer – „green-orange fel fire explosion with skull"

**Druide:** Zorn – „green leaf bolt with wooden thorn" · Mondfeuer – „glowing moon crescent with falling silver sparks" · Verjüngung – „sprouting seedling with green glow" · Wurzeln – „thick tree roots coiling upward" · Sternenfall – „big falling star comet with arcane trail"

## 6. Völkerfähigkeiten (8)

Alle: [STIL-ICON] + Motiv, **grüner Akzent/Rand**.
Mensch – Wille der Menschheit: „raised determined fist with white aura" · Zwerg – Steingestalt: „body turned to gray granite skin, rock shards" · Nachtelf – Schattenhuschen: „translucent elf silhouette dissolving into purple mist" · Gnom – Entfesselungskünstler: „broken chain and glowing cogs" · Orc – Blutrausch: „red rage aura around roaring orc face" · Untoter – Kannibalismus: „bone and bitten ribs with green glow" · Taure – Kriegsdonner: „hoof stomping the ground with shockwave" · Troll – Berserker: „twin axes with red frenzy swirls"

## 7. Gegenstände

Alle: [STIL-ICON], pro Seltenheit Rand/Glühen in der Rarity-Farbe.
- **Waffen:** Schwert, Streitkolben, Bogen, Dolch, Stab (je „ornate [Waffe], slightly different design per rarity")
- **Rüstung:** Brustplatte, Lederwams, Robe
- **Schmuck:** Amulett, Ring, Talisman
- **Heiltrank:** „red health potion in a round glass flask with cork, glowing liquid, gold label rune"
- **Abwarten:** „hourglass with golden sand"

## 8. Monster (18) und Bosse (6)

Alle: [STIL-PORTRAIT] ohne Schultern, stattdessen „creature bust". Bosse zusätzlich: „elite boss, glowing silver-gold frame, menacing aura".

Wolf – „snarling gray wolf" · Wilder Eber – „tusked wild boar with bristly mane" · Murloc – „blue-teal murloc with wide mouth and bulging eyes" · Riesenspinne – „large purple-black spider with red eyes" · Skorpid – „armored desert scorpion" · Harpyie – „screeching harpy with feathered wings and talons" · Giftschlange – „coiled green cobra, hood flared" · Krokilisk – „armored swamp crocolisk jaw open" · Zombie – „rotting zombie, torn clothes, green skin" · Skelettkrieger – „skeleton with rusted sword and cracked shield" · Blutfledermaus – „giant red-eyed bat, fangs" · Rastloser Geist – „pale blue ghost with wailing face" · Gletscher-Yeti – „white-furred yeti roaring" · Eiselementar – „floating ice elemental with crystal body" · Frostwyrm-Welpe – „young blue frost drake" · Eisbär – „polar bear with scarred face" · Wichtel – „small magenta imp with flames" · Feuerelementar – „living fire elemental, molten core" · Lavagolem – „hulking lava golem with glowing cracks" · Schwarzer Drachkin – „dark dragonkin humanoid with horns and wings"

**Bosse:** Hogger – „huge muscular gnoll with brown fur and dog snout, brutal grin" · Edwin VanCleef – „masked human rogue in red bandana, twin daggers" · Onyxia – „giant black dragon with red eyes, spread wings" · Kel'Thuzad – „pale lich in purple robes with frost crown and glowing blue eyes" · Ragnaros – „fire lord of molten rock with flaming hair and hammer" · C'Thun – „giant green eldritch eye with tentacles"

## 9. Effekte (optional, transparent)

> [STIL-UI] flat vector battle effect sprite, [Beschreibung], transparent background, 512x512

Treffer-Funke (gelb-weiß), Kritischer Treffer (großer roter Stern mit Linien), Heil-Glitzer (grüne Funken), Schadenszahl-Rahmen (zerfranster Zackenstern), Betäubungssterne (kreisend), Level-Up-Strahlen (goldene Lichtstrahlen).

---

### Tipps für die Erzeugung
- **Einheitlich bleiben:** erst 3–4 Icons erzeugen, das beste als Referenzbild (Style-Reference) für alle weiteren verwenden.
- **Echtes Vektor-SVG** liefert z. B. Recraft oder Adobe Illustrator Generative Recolor; sonst PNG erzeugen und mit Vectorizer/Inkscape nachzeichnen.
- Für die Spielintegration: Icons 256×256, Portraits 512×512, Hintergründe 1080×1920. Buttons als 9-Slice-Rahmen anlegen (Ecken fix, Mitte dehnbar), damit sie sich jeder Größe anpassen.
