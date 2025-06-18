# Minecraft Skin zu Totem Generator

Ein Python-Programm mit Pillow, das Minecraft-Skin-Texturen in Totem-Texturen umwandelt.

## Features

- **GUI-basierte Anwendung** mit tkinter
- **PNG-Datei Upload** für Minecraft-Skins
- **Bildvorschau** mit Scroll-Funktionalität
- **Validierung** von Minecraft-Skin-Formaten
- **Vorbereitung** für Cropping und Resizing-Funktionen

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- pip (Python Package Manager)

### Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Alternative Installation

```bash
pip install Pillow
```

## Verwendung

### Programm starten

```bash
python totem_generator.py
```

### Bedienung

1. **Skin hochladen**: Klicken Sie auf "Skin-Datei auswählen" und wählen Sie eine PNG-Datei aus
2. **Vorschau**: Das hochgeladene Bild wird in der Vorschau angezeigt
3. **Validierung**: Das Programm überprüft automatisch das Format der Datei
4. **Nächste Schritte**: Der "Totem generieren" Button wird aktiviert (Funktionalität folgt)

## Unterstützte Formate

Das Programm erkennt und validiert folgende Minecraft-Skin-Größen:
- 64x32 (klassisches Format)
- 64x64 (HD-Format)
- 128x128 (2x HD)
- 256x256 (4x HD)
- 512x512 (8x HD)

## Projektstruktur

```
Totem Generator/
├── totem_generator.py    # Hauptprogramm
├── requirements.txt      # Python-Abhängigkeiten
└── README.md            # Diese Datei
```

## Nächste Schritte

Das Programm ist derzeit in der ersten Phase. Geplante Features:

- [ ] **Skin-Parts Cropping**: Automatisches Ausschneiden verschiedener Körperteile
- [ ] **Totem-Textur Generierung**: Zusammenfügen der Parts zu einer Totem-Textur
- [ ] **Einstellungen**: Anpassbare Cropping-Parameter
- [ ] **Export-Funktionen**: Speichern der generierten Totem-Texturen

## Technische Details

- **GUI**: tkinter mit ttk-Widgets
- **Bildverarbeitung**: Pillow (PIL)
- **Datei-Handling**: Standard Python os und pathlib
- **Layout**: Responsive Grid-System

## Lizenz

Dieses Projekt ist für Bildungszwecke erstellt.

## Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository.

## Web-Version (Flask)

Mit der Web-Version kannst du den Totem-Generator direkt im Browser nutzen.

### Installation

1. Repository klonen oder Dateien herunterladen.
2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```
3. Die Datei `outline.png` muss im Hauptverzeichnis liegen.

### Starten

```bash
python app.py
```

Danach öffne deinen Browser und gehe zu:

    http://localhost:5000

### Nutzung

- Skin-Datei (PNG) auswählen und hochladen.
- Totem wird generiert und als Vorschau angezeigt.
- Mit dem Download-Link kannst du das fertige Totem speichern. 