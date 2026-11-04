# Valdoran Idle

Ein Idle-RPG im Hochformat im Stil klassischer Fantasy-MMOs: Dein Held führt seine Waffenangriffe von allein,
auch während du offline bist; seine Fähigkeiten setzt du selbst ein, und du kommst zurück, um Quests abzugeben, Beute anzulegen,
Dungeons und Raids zu bestreiten und deine Berufe zu leveln.

Alles läuft im Browser, ohne Server und ohne Build-Schritt. Alle Grafiken sind Rastergrafiken
(WebP und PNG), die `tools/gen_assets.py` prozedural malt: rund 100 Figuren in dreifacher Auflösung,
150 Icons à 64 px, 19 Hintergründe in 960×640 und die UI-Texturen (Goldrahmen mit Medaillons,
Knöpfe, Portrait- und Minimap-Ringe). Es gibt keine Vektorgrafiken und keine fremden Spieldateien.

## Spielen

```bash
make idle          # → http://127.0.0.1:8091/
```

Oder ohne `make`: `cd idle && python3 -m http.server 8091`. Die Datei `index.html` lässt sich
auch direkt im Browser öffnen. Der Spielstand liegt im `localStorage` des Browsers; unter
*Stadt → Einstellungen* kannst du ihn exportieren und wieder importieren.

## Was es zu tun gibt

| Bereich | Inhalt |
|---|---|
| **Kampf** | Der Waffenangriff läuft von allein (auch offline); die drei Klassenfähigkeiten wirkst du selbst über die Aktionsleiste (Taste 1–3, gedrückt halten zeigt die Beschreibung). Tippen für Extraschaden, Heiltränke, Zonenbosse mit Zeitlimit, Elitegegner. Buffs (Elixiere, Essen, Kampfschrei, Erholt, Rast) stehen oben links in der Kampfszene, Debuffs des Gegners (Schattenpein, Unterkühlt, nahender Spezialangriff, Raserei) unter seinem Lebensbalken, jeweils mit Restzeit; antippen zeigt die Wirkung. Heiltränke: höchstens 20, 30 Sek. Abklingzeit |
| **Aufträge** | 8 Gebiete (Stufe 1–60) mit je 6 Aufträgen von zwei Auftraggebern. Du läufst zum Auftraggeber (gelbes **!**), nimmst an, läufst zu Jagdgebiet, Elite-Versteck oder Boss-Hort, kämpfst und läufst zum Abgeben zurück (**?**). Jedes Gebiet hat Dorf, Außenposten, drei Jagdgebiete, ein Elite-Versteck und einen Boss-Hort; Reittiere verkürzen die Wege, in Dörfern sammelt der Held Erholungsbonus. Danach endlose Weltstufen |
| **Held** | 8 Ausrüstungsplätze, 6 Seltenheitsstufen bis Legendär, Aufwerten bis +10, Entzaubern, 15 Talente pro Klasse |
| **Instanzen** | 6 Dungeons mit je 3 Bossen und Mythisch+ ohne Obergrenze, 3 Raids mit 4 Bossen und wöchentlicher Sperre (Reset Mittwoch 5 Uhr), Weltboss alle 3 Stunden, Arena mit Wertung und Rängen |
| **Berufe** | Bergbau und Kräuterkunde (laufen offline weiter), Schmiedekunst, Alchemie, Kochkunst, ein Angel-Minispiel mit 12 Fischarten, Expeditionen mit 15 Min bis 8 Std Dauer |
| **Stadt** | Tägliche Anmeldebelohnung mit Serienbonus, Versorgungskiste alle 4 Std, Lehrer, 4 Gefährten, 7 Reittiere, 3 Händler |
| **Ziele** | Tages- und Wochenquests, 31 Erfolge mit Titeln, Ruhmstufen nach Stufe 60 |

Gründe, regelmäßig vorbeizuschauen: Offline-Fortschritt (bis 8 Std, mit Training mehr) und
Erholungsbonus, Schlüssel, die alle 20 Minuten nachwachsen, zurückkehrende Expeditionen, die
Versorgungskiste, Weltboss-Fenster, Tagesquests und die tägliche Anmeldeserie.

## Aufbau

| Datei | Inhalt |
|---|---|
| `index.html`, `css/style.css` | Layout im Hochformat (max. 480 px breit): Einheitenrahmen, Minimap, Aktionsleiste, Steinpaneele, Goldrahmen, Pergament |
| `js/data.js` | Inhalte: Klassen, Zonen, Quests, Dungeons, Raids, Talente, Berufe, Erfolge |
| `js/game.js` | Zustand, Formeln, Kampfsimulation, Beute, Quests, Offline-Fortschritt; kein DOM |
| `js/scene.js` | Kampfszene: 240×160-Koordinaten, in voller Bildschirmauflösung geglättet gezeichnet |
| `js/ui.js` | Tabs, Ansichten, Modale, Toasts, Angel-Minispiel |
| `js/main.js` | Start, Hauptschleife, Speichern, synthetisierte Soundeffekte |
| `js/atlas.js` | Generierter Index der Sprite- und Icon-Atlanten |
| `tools/faces.py` | Kopfposition und -größe jeder Figur für die runden Portraits (Kopf im oberen Drittel, darunter Schultern und Brust); `tools/faces_sheet.py` zeigt alle Portraits zur Kontrolle |
| `tools/` | Python-Generator für alle Grafiken (`numpy`, `Pillow` mit WebP); `px.py` enthält den Pixel- und den gemalten Renderer |

### Eigene gemalte Bilder

Liegt in `art/` ein Bild mit passendem Namen, ersetzt es die erzeugte Grafik:

| Datei | Wird zu |
|---|---|
| `art/bg_<zone>.jpg` | Hintergrund der Zone (wird auf 3:2 zugeschnitten, 960×640) |
| `art/hero_<klasse>.jpg`, `art/<monster>.jpg` | Figur; Schachbrett- oder einfarbiger Hintergrund wird freigestellt, auch eingemalte Schatten; Leuchteffekte bleiben weich |
| `art/icons/<slot>.jpg` | Item-Icon; daraus entstehen sechs Stufen (Bronze, Eisen, Original, Gold, Leere, Legendär) |

Für jede Grafik, die noch fehlt, steht ein fertiger Prompt in `art/PROMPTS.md` (erzeugt von `tools/prompts.py`).
Auch dort gelistete Monster, Gefährten und Icons werden automatisch übernommen, sobald die Datei in `art/` liegt.
Gefährten ohne eigenes Bild und Arena-Gegner entstehen als umgefärbte Heldenbilder. Welche Figur wie groß gezeichnet wird
und in welche Richtung sie schaut, steht in `tools/custom_art.py`.

Grafiken neu erzeugen. Beim ersten Mal dauert das Freistellen der gemalten Figuren einige Minuten;
die Ergebnisse landen in `.art-cache/` (nicht im Repo), danach geht es deutlich schneller:

```bash
make idle-assets   # python3 idle/tools/gen_assets.py
```
