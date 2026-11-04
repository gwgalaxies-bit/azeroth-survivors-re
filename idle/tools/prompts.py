#!/usr/bin/env python3
"""Image prompts for the art Valdoran Idle still draws procedurally. Writes idle/art/PROMPTS.md.

Each prompt is complete and ready to paste. Save the generated image under the file name in its row
(idle/art/<name>.jpg or idle/art/icons/<name>.jpg) and run tools/gen_assets.py; custom_art.py picks it up.
"""
import os

MONSTER = (', full body, side view facing left, stylized hand-painted fantasy MMO creature, chunky exaggerated '
           'proportions, bold saturated colors, dramatic rim light, clean silhouette, isolated on transparent background, no text')
ALLY = (', full body, side view facing right, standing idle pose, stylized hand-painted fantasy MMO character, chunky heroic '
        'proportions, oversized shoulder armor, bold saturated colors, warm rim light, clean silhouette, isolated on transparent background, no text')
HALL = (', interior, wide 2D game battle backdrop, side view, flat open floor in the lower quarter, no characters, no text, '
        'stylized hand-painted fantasy MMO art, painterly brush strokes, saturated colors, dramatic lighting')
ICON = ('Square fantasy RPG icon: {}, centered, hand-painted, glossy highlights, dark vignette background, thin dark beveled '
        'border, bold saturated colors, no text')
MOUNT = ('Square fantasy RPG icon: head and shoulders portrait of {} wearing a riding bridle, centered, hand-painted, glossy '
         'highlights, dark vignette background, thin dark beveled border, bold saturated colors, no text')

# (section title, note, format, [(game name, file name, subject)])
SECTIONS = [
    ('Normale Monster', 'Die siehst du ständig. Querformat oder quadratisch, Blick nach links.', MONSTER, [
        ('Waldwolf (Goldhain)', 'waldwolf', 'Grey-brown forest wolf, lean and snarling'),
        ('Tunnelkobold (Goldhain)', 'kobold', 'Small rat-eared kobold miner with a candle on his helmet and a rusty pickaxe'),
        ('Waldspinne (Goldhain)', 'waldspinne', 'Giant brown forest spider with red markings'),
        ('Moorschleim (Nebelmoor)', 'moorschleim', 'Bubbling green swamp slime with two big eyes'),
        ('Sumpfkriecher (Nebelmoor)', 'sumpfkriecher', 'Hunched teal fish-man with orange fins and claws'),
        ('Moorkrokilisk (Nebelmoor)', 'krokilisk', 'Swamp crocodile-lizard with a spiny back, low crawling pose'),
        ('Steppenhyäne (Rotfels)', 'hyaene', 'Spotted sandy hyena with a dark mane'),
        ('Rotfels-Oger (Rotfels)', 'oger', 'Hulking tan-skinned ogre with tusks and a spiked wooden club'),
        ('Staubelementar (Rotfels)', 'staubelementar', 'Swirling dust elemental made of rocks and sand'),
        ('Glutskorpid (Sonnenglut)', 'skorpid', 'Giant golden desert scorpion with raised stinger'),
        ('Sandmumie (Sonnenglut)', 'mumie', 'Shambling mummy in torn linen wrappings with glowing green eyes'),
        ('Dünenwurm (Sonnenglut)', 'sandwurm', 'Giant sandworm bursting from the sand, round maw full of teeth'),
        ('Gipfelyeti (Frostgipfel)', 'yeti', 'Shaggy white yeti with blue horns and big claws'),
        ('Frostwolf (Frostgipfel)', 'frostwolf', 'White frost wolf with icy blue eyes and frosted fur'),
        ('Eiselementar (Frostgipfel)', 'eiselementar', 'Ice elemental of jagged blue crystals with a glowing core'),
        ('Hungriger Ghul (Schattenhain)', 'ghul', 'Gaunt hunched ghoul with grey-green skin and red eyes'),
        ('Skelettkrieger (Schattenhain)', 'skelett', 'Skeleton warrior with a rusty sword and dented shoulder plates'),
        ('Klagende Banshee (Schattenhain)', 'banshee', 'Pale ghostly banshee with flowing hair and a wispy tail'),
        ('Feuerelementar (Glutschlund)', 'feuerelementar', 'Fire elemental of living flames with a white-hot core'),
        ('Lavahund (Glutschlund)', 'lavahund', 'Black lava hound with glowing orange cracks and a spiked back'),
        ('Glutwichtel (Glutschlund)', 'wichtel', 'Small red imp with bat wings, horns and a pointed tail'),
        ('Leerwandler (Leerenriss)', 'leerwandler', 'Floating void wraith of purple smoke with a star-speckled body'),
        ('Tentakelgrauen (Leerenriss)', 'tentakelgrauen', 'Floating flesh orb with one huge eye and dangling tentacles'),
        ('Sternenbestie (Leerenriss)', 'sternenbestie', 'Purple star-speckled great cat with curved horns and glowing cyan eyes'),
    ]),
    ('Elitegegner', 'Erscheinen während der Zonenquests. Blick nach links.', MONSTER, [
        ('Graufang', 'graufang', 'Huge scarred grey alpha wolf with glowing red eyes'),
        ('Uralter Schlammbrocken', 'schlammbrocken', 'Huge ancient mud and moss slime with roots and stones inside'),
        ('Ogerschamane Brug', 'brug', 'Green-skinned ogre shaman with horns, a bone necklace and a staff with a pink glowing orb'),
        ('Grabwächter Ankhu', 'ankhu', 'Mummy tomb guardian in blue and gold armor with a golden scythe'),
        ('Eisklaue', 'eisklaue', 'Massive blue-white yeti with icy horns'),
        ('Knochenwächter', 'knochenwaechter', 'Big armored skeleton knight with a dark helmet, a huge axe and red glowing eyes'),
        ('Magmagolem', 'magmagolem', 'Basalt golem with glowing lava cracks and a molten core'),
        ('Augenlose Wache', 'augenlose_wache', 'Eyeless void stone golem with purple crystal shards'),
    ]),
    ('Dungeonbosse', 'Je drei pro Dungeon. Blick nach links.', MONSTER, [
        ('Vorarbeiter Schnarr (Kobaltminen)', 'schnarr', 'Blue-skinned kobold foreman with a candle helmet and a pickaxe'),
        ('Skarra die Höhlenmutter (Kobaltminen)', 'hoehlenspinne', 'Giant cave spider with glowing blue markings'),
        ('Der Erzkoloss (Kobaltminen)', 'erzkoloss', 'Rock golem studded with glowing blue crystal ore'),
        ('Die Sporenmutter (Moderhöhle)', 'sporenmutter', 'Huge purple fungal slime with pink glowing spores and a small crown'),
        ('Krokilisk-Alpha (Moderhöhle)', 'krokilisk_alpha', 'Huge armored swamp crocodile with golden spikes'),
        ('Sumpfhexer Ulgra (Moderhöhle)', 'ulgra', 'Old swamp witch with teal skin, a pointed hat and a purple-glowing staff'),
        ('Skarabäusfürst Zek (Tempel von Khet)', 'skarabaeus', 'Giant turquoise scarab-scorpion with a golden stinger'),
        ('Hohepriesterin Nefra (Tempel von Khet)', 'nefra', 'Mummified high priestess in gold and white robes with a magenta glowing staff'),
        ('Der Steinwächter (Tempel von Khet)', 'steinwaechter', 'Sandstone temple guardian golem with glowing teal runes'),
        ('Häuptling Eisklinge (Frostspitzbastion)', 'yeti_boss', 'Giant white yeti chieftain with an ice-covered club'),
        ('Frostrufer Halvar (Frostspitzbastion)', 'halvar', 'Bearded frost mage in blue hooded robes with an ice staff'),
        ('Der Kryomant (Frostspitzbastion)', 'kryoskelett', 'Ice skeleton with a frost scythe and glowing cyan eyes'),
        ('Banshee-Königin Velia (Aschenkathedrale)', 'velia', 'Red ghostly banshee queen with a pale crown'),
        ('Der Knochenkoloss (Aschenkathedrale)', 'knochenkoloss', 'Gigantic skeleton brute in dark armor with a bone club'),
        ('Inquisitor Malhar (Aschenkathedrale)', 'malhar', 'Skeletal inquisitor in red and gold robes with a golden scythe and a crown'),
        ('Die Leerenbrut (Abyssaler Schlund)', 'leerenbrut', 'Dark purple void spider with glowing violet markings'),
        ('Der Tentakelmeister (Abyssaler Schlund)', 'tentakelmeister', 'Green eye-orb monster with eyestalks and tentacles'),
        ('Wächter des Abgrunds (Abyssaler Schlund)', 'abgrundwaechter', 'Dark void golem with glowing cyan crystals and core'),
    ]),
    ('Raid- und Weltbosse', 'Die größten Gegner. Blick nach links.', MONSTER, [
        ('Magmaul (Glutkrone)', 'magmaul', 'Gigantic black lava hound with horns and glowing cracks'),
        ('Glutweberin Sythra (Glutkrone)', 'glutweberin', 'Huge black and orange lava spider'),
        ('Baron Aschenfaust (Glutkrone)', 'aschenfaust', 'Fiery demon lord with horns, bat wings and a burning axe'),
        ('Ignis, Herz der Flamme (Glutkrone)', 'ignis', 'Colossal fire elemental with a white-hot core'),
        ('Knochenfürst Varn (Nebelthron)', 'varn', 'Armored skeleton lord with a crown, a cape and a frost sword'),
        ('Die Bleiche Dame (Nebelthron)', 'bleiche_dame', 'Pale white ghost queen with flowing hair and a crown'),
        ('Frostdrache Nivara (Nebelthron)', 'nivara', 'Deep blue frost dragon with icy wings'),
        ('Der Nebelkönig (Nebelthron)', 'nebelkoenig', 'Undead king in blue armor and cape with a glowing frost runeblade and a crown'),
        ('Sternenfresser (Verschlinger)', 'sternenfresser', 'Huge cosmic beast with a star-filled purple hide and glowing horns'),
        ('Die Zwillingsaugen (Verschlinger)', 'zwillingsaugen', 'Crimson flesh orb with two huge eyes and many eyestalks'),
        ('Xaroth, Schwinge des Abgrunds (Verschlinger)', 'xaroth', 'Dark teal abyssal dragon with glowing cyan veins'),
        ("Nhal'zor der Erwachte (Verschlinger)", 'nhalzor', 'Colossal void god, a giant purple eye-orb with a crown of horns and writhing tentacles'),
        ('Azurschwinge (Weltboss)', 'azurschwinge', 'Majestic blue dragon with golden horns'),
        ('Grollhuf der Urberg (Weltboss)', 'grollhuf', 'Mossy mountain golem with yellow-green glowing crystals'),
        ('Die Verderbte Eiche (Weltboss)', 'verderbte_eiche', 'Corrupted tree giant with purple leaves and glowing pink eyes'),
        ('Hüter des Hains (Weltboss)', 'eiche', 'Ancient tree giant with green leaves and glowing eyes'),
    ]),
    ('Gefährten', 'Kämpfen an deiner Seite. Blick nach rechts.', ALLY, [
        ('Thorga Eisenschild', 'comp_tank', 'Stout shield maiden in blue and gold plate armor with a war hammer and a tower shield'),
        ('Schwester Elyra', 'comp_heiler', 'Healer priestess in green and white robes with a glowing nature staff'),
        ('Varrik Falkenauge', 'comp_schuetze', 'Ranger in dark red leather armor with a longbow and a hood'),
        ('Mirra Sturmruf', 'comp_zauberin', 'Fire sorceress in red and black robes with a flaming staff'),
    ]),
    ('Dungeon- und Raid-Hintergründe', 'Querformat 3:2 oder 16:9.', HALL, [
        ('Die Kobaltminen', 'bg_mine', 'Abandoned underground mine tunnel, wooden support beams, lanterns, glowing blue ore veins in the rock walls, rail tracks'),
        ('Die Moderhöhle', 'bg_cave', 'Damp fungal cave, giant glowing purple and green mushrooms, hanging roots, murky puddles'),
        ('Tempel von Khet', 'bg_temple', 'Golden sandstone temple hall, hieroglyph-carved pillars, blue banners, torches, sand on the floor'),
        ('Frostspitzbastion', 'bg_ice', 'Fortress hall made of blue ice, icicles, frozen banners, cold blue torchlight'),
        ('Aschenkathedrale', 'bg_cathedral', 'Desecrated gothic cathedral, broken stained glass windows, red banners, candles, ash and bones on the floor'),
        ('Abyssaler Schlund', 'bg_abyss', 'Stone platform floating in a void, giant glowing eye in the dark sky, purple crystals, stars'),
        ('Hallen der Glutkrone', 'bg_raid_glut', 'Volcanic throne hall, lava rivers between obsidian pillars, red banners, fiery glow'),
        ('Nebelthron-Zitadelle', 'bg_raid_nebel', 'Frozen citadel throne room, an ice throne, pale blue mist, dark blue banners'),
        ('Thron des Verschlingers', 'bg_raid_thron', 'Cosmic void throne at the bottom of a rift, tentacles rising from the floor, nebula sky, purple light'),
    ]),
    ('Fähigkeiten', 'Quadratisch, 1:1. Immer in der Aktionsleiste sichtbar.', ICON, [
        ('Schmetterhieb (Krieger)', 'icons/sk_schmetterhieb', 'a sword striking down with a white impact flash'),
        ('Klingensturm (Krieger)', 'icons/sk_klingensturm', 'a whirlwind of spinning blades'),
        ('Kampfschrei (Krieger)', 'icons/sk_kampfschrei', 'a war horn blasting golden sound waves'),
        ('Feuerkugel (Magier)', 'icons/sk_feuerkugel', 'a blazing fireball'),
        ('Eislanze (Magier)', 'icons/sk_eislanze', 'a jagged ice lance'),
        ('Arkanflut (Magier)', 'icons/sk_arkanflut', 'a swirling violet arcane vortex'),
        ('Präziser Schuss (Jäger)', 'icons/sk_praeziser_schuss', 'an arrow hitting the center of a target'),
        ('Pfeilhagel (Jäger)', 'icons/sk_pfeilhagel', 'a rain of arrows falling from the sky'),
        ('Wolfsbiss (Jäger)', 'icons/sk_wolfsbiss', 'a snarling grey wolf head'),
        ('Lichtstrahl (Priester)', 'icons/sk_lichtstrahl', 'a golden beam of holy light from above'),
        ('Schattenpein (Priester)', 'icons/sk_schattenpein', 'a purple shadow skull in dark smoke'),
        ('Segnung (Priester)', 'icons/sk_segnung', 'glowing green healing hands'),
    ]),
    ('Währungen und Menü', 'Quadratisch, 1:1.', ICON, [
        ('Gold', 'icons/gold', 'a pile of shining gold coins'),
        ('Heldenabzeichen', 'icons/badge', 'a blue and gold heraldic shield emblem with a sword'),
        ('Raidmarke', 'icons/raidmark', 'a purple and gold medal with a dragon head'),
        ('Ehre', 'icons/honor', 'a red and silver medal with crossed swords'),
        ('Tab Quests', 'icons/scroll', 'a rolled parchment scroll with a red wax seal'),
        ('Tab Instanzen', 'icons/portal', 'a glowing purple stone portal'),
        ('Tab Berufe', 'icons/tools', 'a crossed pickaxe and smithing hammer'),
        ('Tab Stadt', 'icons/castle', 'a castle with blue-roofed towers'),
    ]),
    ('Rohstoffe und Elixiere', 'Quadratisch, 1:1.', ICON, [
        ('Kupfererz', 'icons/erz_kupfer', 'a chunk of copper ore'),
        ('Eisenerz', 'icons/erz_eisen', 'a chunk of iron ore'),
        ('Silbererz', 'icons/erz_silber', 'a chunk of silver ore'),
        ('Mondstahlerz', 'icons/erz_mondstahl', 'a chunk of pale blue glowing moonsteel ore'),
        ('Sternenerz', 'icons/erz_sternen', 'a chunk of violet glowing star ore'),
        ('Wiesenklee', 'icons/kraut_wiesenklee', 'a bunch of white clover flowers'),
        ('Blutdorn', 'icons/kraut_blutdorn', 'a red-thorned herb'),
        ('Nebelmoos', 'icons/kraut_nebelmoos', 'a clump of pale blue moss'),
        ('Sonnenblüte', 'icons/kraut_sonnenbluete', 'a golden sun flower'),
        ('Sternenlotus', 'icons/kraut_sternenlotus', 'a glowing violet lotus'),
        ('Elixier der Macht', 'icons/elixir_atk', 'an orange elixir flask'),
        ('Elixier des Wissens', 'icons/elixir_xp', 'a blue elixir flask'),
        ('Glückselixier', 'icons/elixir_luck', 'a green elixir flask'),
        ('Fläschchen der Titanen', 'icons/flask_titan', 'a golden glowing titan flask'),
    ]),
    ('Reittiere', 'Quadratisch, 1:1.', MOUNT, [
        ('Brauner Hengst', 'icons/m_pferd', 'a brown stallion'),
        ('Grauer Reitwolf', 'icons/m_wolf', 'a grey riding wolf'),
        ('Bergwidder', 'icons/m_widder', 'a mountain ram with curled horns'),
        ('Goldmähnen-Säbelzahn', 'icons/m_saebelzahn', 'a golden-maned sabertooth cat'),
        ('Frostwolf des Gipfels', 'icons/m_frostwolf', 'a white frost wolf'),
        ('Glutross', 'icons/m_glutross', 'a black lava horse with a burning mane'),
        ('Leerendrache', 'icons/m_drache', 'a purple void dragon'),
    ]),
]


def prompt(fmt, subject):
    return fmt.format(subject) if '{}' in fmt else subject + fmt


def entries():
    for title, note, fmt, rows in SECTIONS:
        yield title, note, [(name, f, prompt(fmt, subject)) for name, f, subject in rows]


def markdown():
    out = ['# Bildprompts für Valdoran Idle', '',
           'Jeder Prompt ist vollständig. Speichere das Bild unter dem angegebenen Dateinamen in `idle/art/` '
           '(als `.jpg` oder `.png`) und führe `make idle-assets` aus.', '']
    for title, note, rows in entries():
        out += [f'## {title}', '', note, '']
        for name, f, p in rows:
            out += [f'**{name}** → `{f}.jpg`', '', '```', p, '```', '']
    return '\n'.join(out)


if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'art', 'PROMPTS.md')
    with open(path, 'w') as fh:
        fh.write(markdown())
    print(sum(len(r) for _, _, r in entries()), 'prompts →', path)
