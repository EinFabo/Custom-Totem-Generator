#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Skin zu Totem Textur Generator
=======================================

Dieses Programm ermöglicht es, Minecraft-Skin-Texturen hochzuladen
und diese später in Totem-Texturen umzuwandeln.

Autor: Totem Generator
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
import winsound

class TotemGenerator:
    """
    Hauptklasse für den Totem Generator
    Verwaltet die GUI und die Bildverarbeitung
    """
    
    def __init__(self, root):
        """
        Initialisiert die Hauptanwendung
        
        Args:
            root: Das tkinter Root-Fenster
        """
        self.root = root
        self.root.title("Minecraft Skin zu Totem Generator")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')  # Dunkles Theme
        
        # Windows-Sounds deaktivieren
        self.disable_windows_sounds()
        
        # Variablen für die Bildverarbeitung
        self.uploaded_image = None
        self.image_path = None
        self.preview_image = None
        
        # Info-Label für Advancement-Style Hinweise
        self.info_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), fg="#fff", bg="#333", bd=2, relief=tk.RIDGE)
        self.info_label.place(relx=0.5, rely=0.02, anchor="n")
        self.info_label.lower()  # Anfangs versteckt
        
        # GUI erstellen
        self.setup_gui()
        
    def disable_windows_sounds(self):
        """
        Deaktiviert Windows-System-Sounds für messagebox-Dialoge
        """
        # Temporär Windows-Sounds deaktivieren
        try:
            # System-Sounds stumm schalten (nur für messagebox)
            winsound.PlaySound(None, winsound.SND_ASYNC)
        except:
            # Falls winsound nicht verfügbar ist, ignorieren
            pass
    
    def show_silent_message(self, title, message, message_type="info"):
        """
        Zeigt eine temporäre Nachricht im Stil eines Minecraft-Advancements oben im Fenster an.
        Die Nachricht verschwindet nach wenigen Sekunden automatisch.
        Für Ja/Nein-Fragen ('yesno') wird ein klassischer Dialog angezeigt.
        """
        if message_type == "yesno":
            # Für Ja/Nein-Fragen klassischen Dialog verwenden
            from tkinter import messagebox
            return messagebox.askyesno(title, message)
        color = "#4caf50"  # Standard: grün für Erfolg/info
        if message_type == "warning":
            color = "#ffb300"  # gelb
        elif message_type == "error":
            color = "#e53935"  # rot
        self.info_label.config(text=message, bg=color)
        self.info_label.lift()
        self.info_label.after(2500, lambda: self.info_label.lower())
    
    def setup_gui(self):
        """
        Erstellt die Benutzeroberfläche mit allen Widgets
        """
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(
            main_frame, 
            text="Minecraft Skin zu Totem Generator", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Upload-Bereich
        self.create_upload_section(main_frame)
        
        # Vorschau-Bereich
        self.create_preview_section(main_frame)
        
        # Button-Bereich
        self.create_button_section(main_frame)
        
        # Grid-Konfiguration für responsive Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def create_upload_section(self, parent):
        """
        Erstellt den Upload-Bereich der GUI
        
        Args:
            parent: Das übergeordnete Widget
        """
        # Upload Frame
        upload_frame = ttk.LabelFrame(parent, text="Skin hochladen", padding="10")
        upload_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Datei-Pfad Anzeige
        self.path_var = tk.StringVar(value="Keine Datei ausgewählt")
        path_label = ttk.Label(upload_frame, textvariable=self.path_var, wraplength=400)
        path_label.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Upload Button
        upload_btn = ttk.Button(
            upload_frame, 
            text="Skin-Datei auswählen", 
            command=self.upload_image
        )
        upload_btn.grid(row=1, column=0, padx=(0, 10))
        
        # Datei löschen Button
        clear_btn = ttk.Button(
            upload_frame, 
            text="Datei löschen", 
            command=self.clear_image
        )
        clear_btn.grid(row=1, column=1)

        # Checkbox für Kopf-Overlay
        self.overlay_var = tk.BooleanVar(value=True)
        overlay_check = ttk.Checkbutton(
            upload_frame,
            text="Kopf-Overlay anzeigen",
            variable=self.overlay_var
        )
        overlay_check.grid(row=1, column=2, padx=(10, 0))
        
        # Grid-Konfiguration
        upload_frame.columnconfigure(0, weight=1)
        
    def create_preview_section(self, parent):
        """
        Erstellt den Vorschau-Bereich der GUI
        
        Args:
            parent: Das übergeordnete Widget
        """
        # Preview Frame
        preview_frame = ttk.LabelFrame(parent, text="Vorschau", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Canvas für die Bildvorschau
        self.preview_canvas = tk.Canvas(
            preview_frame, 
            bg='white', 
            width=400, 
            height=400,
            relief=tk.SUNKEN,
            bd=1
        )
        self.preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar für die Vorschau
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.preview_canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Grid-Konfiguration
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
    def create_button_section(self, parent):
        """
        Erstellt den Button-Bereich der GUI
        
        Args:
            parent: Das übergeordnete Widget
        """
        # Button Frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Totem generieren Button (später aktiviert)
        self.generate_btn = ttk.Button(
            button_frame, 
            text="Totem generieren", 
            command=self.generate_totem,
            state=tk.DISABLED
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Totem speichern Button (256x256)
        self.save_btn = ttk.Button(
            button_frame,
            text="Totem speichern",
            command=self.save_totem,
            state=tk.DISABLED
        )
        self.save_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Totem (32x32) speichern Button
        self.save32_btn = ttk.Button(
            button_frame,
            text="Totem (32x32) speichern",
            command=self.save_totem_32,
            state=tk.DISABLED
        )
        self.save32_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Einstellungen Button
        settings_btn = ttk.Button(
            button_frame, 
            text="Einstellungen", 
            command=self.open_settings
        )
        settings_btn.grid(row=0, column=3)
        
    def upload_image(self):
        """
        Öffnet einen Datei-Dialog zum Hochladen einer PNG-Datei
        """
        # Datei-Dialog öffnen
        file_path = filedialog.askopenfilename(
            title="Minecraft Skin auswählen",
            filetypes=[
                ("PNG Dateien", "*.png"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Bild laden und validieren
                self.load_and_validate_image(file_path)
            except Exception as e:
                self.show_silent_message(
                    "Fehler", 
                    f"Fehler beim Laden der Datei:\n{str(e)}",
                    "error"
                )
                
    def load_and_validate_image(self, file_path):
        """
        Lädt und validiert das hochgeladene Bild
        
        Args:
            file_path: Pfad zur Bilddatei
        """
        # Bild mit Pillow laden
        image = Image.open(file_path)
        
        # Überprüfen ob es sich um ein gültiges Minecraft-Skin-Format handelt
        width, height = image.size
        
        # Typische Minecraft-Skin-Größen (64x32, 64x64, 128x128, etc.)
        valid_sizes = [(64, 32), (64, 64), (128, 128), (256, 256), (512, 512)]
        
        if (width, height) not in valid_sizes:
            # Warnung anzeigen, aber trotzdem fortfahren
            result = self.show_silent_message(
                "Warnung",
                f"Die ausgewählte Datei hat die Größe {width}x{height}.\n"
                f"Typische Minecraft-Skin-Größen sind: {', '.join([f'{w}x{h}' for w, h in valid_sizes])}\n\n"
                f"Möchten Sie trotzdem fortfahren?",
                "yesno"
            )
            if not result:
                return
        
        # Bild speichern und GUI aktualisieren
        self.uploaded_image = image
        self.image_path = file_path
        self.path_var.set(f"Ausgewählte Datei: {os.path.basename(file_path)}")
        
        # Vorschau aktualisieren
        self.update_preview()
        
        # Generate-Button aktivieren
        self.generate_btn.config(state=tk.NORMAL)
        
        self.show_silent_message(
            "Erfolg", 
            f"Skin erfolgreich geladen!\nGröße: {width}x{height}",
            "info"
        )
        
    def update_preview(self):
        """
        Aktualisiert die Bildvorschau im Canvas
        """
        if self.uploaded_image is None:
            return
            
        # Canvas leeren
        self.preview_canvas.delete("all")
        
        # Bild für Vorschau skalieren
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas noch nicht gerendert
            canvas_width, canvas_height = 400, 400
            
        # Bild proportional skalieren
        img_width, img_height = self.uploaded_image.size
        scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Bild skalieren
        preview_img = self.uploaded_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Für tkinter konvertieren
        self.preview_image = ImageTk.PhotoImage(preview_img)
        
        # Bild im Canvas anzeigen
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        
        # Canvas-Scrollregion setzen
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        
    def clear_image(self):
        """
        Löscht das aktuell geladene Bild
        """
        self.uploaded_image = None
        self.image_path = None
        self.preview_image = None
        self.path_var.set("Keine Datei ausgewählt")
        
        # Canvas leeren
        self.preview_canvas.delete("all")
        
        # Generate-Button deaktivieren
        self.generate_btn.config(state=tk.DISABLED)
        
    def generate_totem(self):
        """
        Generiert die Totem-Textur für Kopf und beide Arme mit flexiblem Mapping.
        Die Arme werden ohne Resizing direkt aus der Skin-Textur ausgeschnitten und ins Totem eingefügt.
        """
        if self.uploaded_image is None:
            self.show_silent_message(
                "Warnung", 
                "Bitte laden Sie zuerst eine Skin-Datei hoch!",
                "warning"
            )
            return

        # --- 1. Mapping-Parameter für Kopf und Arme definieren ---
        mapping = {
            "kopf": {
                "skin": [8, 8, 8, 8],  # Bereich im Skin: x, y, Breite, Höhe
                "totem": [8, 1, 16, 16],  # Zielbereich im Totem: x, y, Breite, Höhe (hier: ganzes Bild)
                "resize": "nearest",  # Vergrößern mit Nachbarpixel (Nearest-Neighbor)
                "crop": [
                    [0, 0, 15, 0],
                    [0, 1],
                    [1, 1],
                    [14, 1],
                    [15, 1],
                    [0, 2],
                    [15, 2],
                    [0, 15, 15, 15]  # oben die pixel weg
                ]
            },
            "arm_links": {
                "skin": [44, 20, 3, 9],
                "totem": [8, 17, 3, 9],
                "resize": None,
                "crop": []
            },
            "arm_rechts": {
                "skin": [36, 52, 3, 9],
                "totem": [21, 17, 3, 9],
                "resize": None,
                "crop": []
            },
            "koerper": {
                # Beispiel-Koordinaten für den Körper (Standard-Skin: [20, 20, 8, 12])
                "skin": [20, 20, 8, 12],
                # Zielposition und -größe im Totem (z.B. mittig unter dem Kopf)
                "totem": [12, 16, 8, 12],
                "resize": None,
                "crop": []
            }
        }

        # --- 2. Leeres Totem-Bild mit 32x32 Pixel erstellen ---
        totem_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))

        # --- 3. Kopf generieren (wie bisher) ---
        kopf = mapping["kopf"]
        sx, sy, sw, sh = kopf["skin"]
        kopf_img = self.uploaded_image.crop((sx, sy, sx+sw, sy+sh))
        if kopf["resize"] == "nearest":
            ziel_w, ziel_h = kopf["totem"][2], kopf["totem"][3]
            kopf_img = kopf_img.resize((ziel_w, ziel_h), Image.NEAREST)
        kopf_img = kopf_img.convert("RGBA")
        pixels = kopf_img.load()
        for crop in kopf["crop"]:
            if len(crop) == 4:
                x1, y1, x2, y2 = crop
                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if 0 <= x < kopf_img.width and 0 <= y < kopf_img.height:
                            pixels[x, y] = (0, 0, 0, 0)
            elif len(crop) == 2:
                x, y = crop
                if 0 <= x < kopf_img.width and 0 <= y < kopf_img.height:
                    pixels[x, y] = (0, 0, 0, 0)

        # --- Kopf-Overlay extrahieren, vergrößern und croppen (wie Kopf) ---
        if self.overlay_var.get():
            overlay_img = self.uploaded_image.crop((40, 8, 40+8, 8+8))
            if kopf["resize"] == "nearest":
                overlay_img = overlay_img.resize((ziel_w, ziel_h), Image.NEAREST)
            overlay_img = overlay_img.convert("RGBA")
            overlay_pixels = overlay_img.load()
            for crop in kopf["crop"]:
                if len(crop) == 4:
                    x1, y1, x2, y2 = crop
                    for x in range(x1, x2+1):
                        for y in range(y1, y2+1):
                            if 0 <= x < overlay_img.width and 0 <= y < overlay_img.height:
                                overlay_pixels[x, y] = (0, 0, 0, 0)
                elif len(crop) == 2:
                    x, y = crop
                    if 0 <= x < overlay_img.width and 0 <= y < overlay_img.height:
                        overlay_pixels[x, y] = (0, 0, 0, 0)
            # Overlay über den Kopf legen
            kopf_img = Image.alpha_composite(kopf_img, overlay_img)

        tx, ty = kopf["totem"][0], kopf["totem"][1]
        totem_img.paste(kopf_img, (tx, ty), kopf_img)

        # --- 4. Linken Arm generieren und einfügen ---
        arm_l = mapping["arm_links"]
        sx, sy, sw, sh = arm_l["skin"]
        arm_l_img = self.uploaded_image.crop((sx, sy, sx+sw, sy+sh))
        arm_l_img = arm_l_img.convert("RGBA")
        # Optionales Cropping für den Arm (wie beim Kopf)
        pixels = arm_l_img.load()
        for crop in arm_l["crop"]:
            if len(crop) == 4:
                x1, y1, x2, y2 = crop
                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if 0 <= x < arm_l_img.width and 0 <= y < arm_l_img.height:
                            pixels[x, y] = (0, 0, 0, 0)
            elif len(crop) == 2:
                x, y = crop
                if 0 <= x < arm_l_img.width and 0 <= y < arm_l_img.height:
                    pixels[x, y] = (0, 0, 0, 0)
        tx, ty = arm_l["totem"][0], arm_l["totem"][1]
        totem_img.paste(arm_l_img, (tx, ty), arm_l_img)

        # --- 5. Rechten Arm generieren und einfügen ---
        arm_r = mapping["arm_rechts"]
        sx, sy, sw, sh = arm_r["skin"]
        arm_r_img = self.uploaded_image.crop((sx, sy, sx+sw, sy+sh))
        arm_r_img = arm_r_img.convert("RGBA")
        # Optionales Cropping für den Arm (wie beim Kopf)
        pixels = arm_r_img.load()
        for crop in arm_r["crop"]:
            if len(crop) == 4:
                x1, y1, x2, y2 = crop
                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if 0 <= x < arm_r_img.width and 0 <= y < arm_r_img.height:
                            pixels[x, y] = (0, 0, 0, 0)
            elif len(crop) == 2:
                x, y = crop
                if 0 <= x < arm_r_img.width and 0 <= y < arm_r_img.height:
                    pixels[x, y] = (0, 0, 0, 0)
        tx, ty = arm_r["totem"][0], arm_r["totem"][1]
        totem_img.paste(arm_r_img, (tx, ty), arm_r_img)

        # --- 6. Körper generieren und einfügen ---
        koerper = mapping["koerper"]
        sx, sy, sw, sh = koerper["skin"]
        koerper_img = self.uploaded_image.crop((sx, sy, sx+sw, sy+sh))
        koerper_img = koerper_img.convert("RGBA")
        # Optionales Cropping für den Körper
        pixels = koerper_img.load()
        for crop in koerper["crop"]:
            if len(crop) == 4:
                x1, y1, x2, y2 = crop
                for x in range(x1, x2+1):
                    for y in range(y1, y2+1):
                        if 0 <= x < koerper_img.width and 0 <= y < koerper_img.height:
                            pixels[x, y] = (0, 0, 0, 0)
            elif len(crop) == 2:
                x, y = crop
                if 0 <= x < koerper_img.width and 0 <= y < koerper_img.height:
                    pixels[x, y] = (0, 0, 0, 0)
        tx, ty = koerper["totem"][0], koerper["totem"][1]
        totem_img.paste(koerper_img, (tx, ty), koerper_img)

        # --- 7. Spezielle Pixel-Kopieraktionen für den Körper (Feinschliff) ---
        # 1. Pixel von (10, 17) nach (10, 16) kopieren
        px = totem_img.getpixel((10, 17))
        totem_img.putpixel((10, 16), px)

        # 2. Vertikale Reihe von (12, 16)-(12, 26) nach (11, 16)-(11, 26) kopieren (links)
        for y in range(16, 27):
            px = totem_img.getpixel((12, y))
            totem_img.putpixel((11, y), px)

        # 3. Vertikale Reihe von (19, 16)-(19, 26) nach (20, 16)-(20, 26) kopieren (rechts)
        for y in range(16, 27):
            px = totem_img.getpixel((19, y))
            totem_img.putpixel((20, y), px)

        # 4. Pixel von (21, 17) nach (21, 16) kopieren (rechte Seite)
        px = totem_img.getpixel((21, 17))
        totem_img.putpixel((21, 16), px)

        # --- 8. Outline laden und drüberlegen, falls vorhanden ---
        outline_path = Path("outline.png")
        if outline_path.exists():
            try:
                outline_img = Image.open(outline_path).convert("RGBA")
                if outline_img.size != (32, 32):
                    outline_img = outline_img.resize((32, 32), Image.NEAREST)
                totem_img = Image.alpha_composite(totem_img, outline_img)
            except Exception as e:
                self.show_silent_message(
                    "Warnung", f"Outline konnte nicht geladen werden: {e}", "warning"
                )

        # --- 9. Großes Totem-Bild (256x256) für Export erzeugen ---
        self.large_totem_img = totem_img.resize((256, 256), Image.NEAREST)
        self.small_totem_img = totem_img.copy()

        # --- 10. Vorschau aktualisieren ---
        self.show_totem_preview(totem_img)

        # --- 11. Erfolgsmeldung und Save-Buttons aktivieren ---
        self.save_btn.config(state=tk.NORMAL)
        self.save32_btn.config(state=tk.NORMAL)
        self.show_silent_message(
            "Erfolg", 
            "Totem-Kopf und Arme wurden generiert!\nPasse die Mapping-Koordinaten nach Bedarf an.",
            "info"
        )

    def show_totem_preview(self, totem_img):
        """
        Zeigt das generierte Totem-Bild in der Vorschau an.
        Das Bild wird für die Vorschau um den Faktor 5 (auf 160x160) mit Nearest-Neighbor vergrößert,
        damit die Pixel klar erkennbar bleiben. Die Vorschau bleibt zentriert im Canvas.
        """
        # Canvas leeren
        self.preview_canvas.delete("all")
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Bild für die Vorschau um den Faktor 5 vergrößern (Nearest-Neighbor)
        scale = 5
        preview_img = totem_img.resize((32 * scale, 32 * scale), Image.NEAREST)
        
        # Bild zentriert im Canvas anzeigen
        x = (canvas_width - 32 * scale) // 2
        y = (canvas_height - 32 * scale) // 2
        self.preview_image = ImageTk.PhotoImage(preview_img)
        self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_image)
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def open_settings(self):
        """
        Öffnet die Einstellungen (Platzhalter für später)
        """
        self.show_silent_message(
            "Einstellungen", 
            "Einstellungen werden in einer späteren Version verfügbar sein.\n"
            "Hier können Sie später die Cropping-Parameter anpassen.",
            "info"
        )

    def save_totem(self):
        """
        Öffnet einen Dialog zum Speichern des großen Totem-Bildes (256x256) als PNG.
        """
        if not hasattr(self, 'large_totem_img') or self.large_totem_img is None:
            self.show_silent_message(
                "Fehler", "Bitte generieren Sie zuerst ein Totem!", "error"
            )
            return
        # Dateidialog zum Speichern öffnen
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG-Bild", "*.png")],
            title="Totem speichern"
        )
        if file_path:
            try:
                self.large_totem_img.save(file_path, "PNG")
                self.show_silent_message(
                    "Erfolg", f"Totem erfolgreich gespeichert unter:\n{file_path}", "info"
                )
            except Exception as e:
                self.show_silent_message(
                    "Fehler", f"Fehler beim Speichern: {e}", "error"
                )

    def save_totem_32(self):
        """
        Öffnet einen Dialog zum Speichern des kleinen Totem-Bildes (32x32) als PNG.
        """
        if not hasattr(self, 'small_totem_img') or self.small_totem_img is None:
            self.show_silent_message(
                "Fehler", "Bitte generieren Sie zuerst ein Totem!", "error"
            )
            return
        # Dateidialog zum Speichern öffnen
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG-Bild", "*.png")],
            title="Totem (32x32) speichern"
        )
        if file_path:
            try:
                self.small_totem_img.save(file_path, "PNG")
                self.show_silent_message(
                    "Erfolg", f"Totem (32x32) erfolgreich gespeichert unter:\n{file_path}", "info"
                )
            except Exception as e:
                self.show_silent_message(
                    "Fehler", f"Fehler beim Speichern: {e}", "error"
                )

def main():
    """
    Hauptfunktion zum Starten der Anwendung
    """
    # Root-Fenster erstellen
    root = tk.Tk()
    
    # Anwendung starten
    app = TotemGenerator(root)
    
    # Event-Loop starten
    root.mainloop()

if __name__ == "__main__":
    main() 