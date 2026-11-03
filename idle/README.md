# Valdoran Idle

Ein Idle-RPG im Hochformat im Stil klassischer Fantasy-MMOs: Dein Held kämpft von allein,
auch während du offline bist, und du kommst zurück, um Quests abzugeben, Beute anzulegen,
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
| **Kampf** | Automatischer Kampf mit drei Klassenfähigkeiten, Tippen für Extraschaden, Heiltränke, Zonenbosse mit Zeitlimit, Elitegegner |
| **Kampagne** | 8 Zonen (Stufe 1–60) mit je 6 Quests, Questgebern und Story; danach endlose Weltstufen |
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
| `tools/` | Python-Generator für alle Grafiken (`numpy`, `Pillow` mit WebP); `px.py` enthält den Pixel- und den gemalten Renderer |

Grafiken neu erzeugen (dauert gut eine Minute):

```bash
make idle-assets   # python3 idle/tools/gen_assets.py
```
