import io
from flask import Flask, request, send_file, render_template
from PIL import Image
from pathlib import Path
import zipfile
import json
import uuid
import requests

app = Flask(__name__)

@app.route('/')
def index():
    # Gibt die HTML-Seite zurück
    return render_template('index.html')

@app.route('/generate_totem', methods=['POST'])
def generate_totem():
    # Prüfe, ob ein Username übergeben wurde
    username = request.form.get('username', '').strip()
    if username:
        # Schritt 1: UUID von Mojang API abfragen
        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_response = requests.get(mojang_url)
        if mojang_response.status_code == 200:
            # UUID erfolgreich erhalten
            uuid = mojang_response.json()['id']
            # Schritt 2: Skin von Crafatar mit UUID laden
            skin_url = f"https://crafatar.com/skins/{uuid}"
            response = requests.get(skin_url)
            if response.status_code == 200:
                # Skin erfolgreich geladen, öffne das Bild
                uploaded_image = Image.open(io.BytesIO(response.content))
            else:
                # Fehler: Skin konnte nicht von Crafatar geladen werden
                return "Skin konnte nicht von Crafatar geladen werden.", 400
        else:
            # Fehler: Username existiert nicht laut Mojang API
            return "Username existiert nicht (laut Mojang API).", 400
    else:
        # Wenn kein Username angegeben wurde, verwende das hochgeladene Bild
        file = request.files['skin']
        uploaded_image = Image.open(file.stream)

    # --- Bildverarbeitung: Totem generieren (aus deiner bisherigen Logik) ---
    # Mapping-Parameter für Kopf, Arme und Körper
    mapping = {
        "kopf": {
            "skin": [8, 8, 8, 8],
            "totem": [8, 1, 16, 16],
            "resize": "nearest",
            "crop": [
                [0, 0, 15, 0], [0, 1], [1, 1], [14, 1], [15, 1], [0, 2], [15, 2], [0, 15, 15, 15]
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
            "skin": [20, 20, 8, 12],
            "totem": [12, 16, 8, 12],
            "resize": None,
            "crop": []
        }
    }

    # Leeres Totem-Bild (32x32 Pixel, transparent)
    totem_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))

    # Kopf generieren
    kopf = mapping["kopf"]
    sx, sy, sw, sh = kopf["skin"]
    kopf_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh))
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

    # Overlay-Option aus dem Formular auslesen (Checkbox)
    overlay = request.form.get('overlay', 'off') == 'on'

    # Kopf-Overlay extrahieren und drüberlegen (nur wenn overlay aktiviert ist)
    if overlay:
        overlay_img = uploaded_image.crop((40, 8, 40+8, 8+8))
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
        kopf_img = Image.alpha_composite(kopf_img, overlay_img)

    tx, ty = kopf["totem"][0], kopf["totem"][1]
    totem_img.paste(kopf_img, (tx, ty), kopf_img)

    # Linken Arm generieren
    arm_l = mapping["arm_links"]
    sx, sy, sw, sh = arm_l["skin"]
    arm_l_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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

    # Rechten Arm generieren
    arm_r = mapping["arm_rechts"]
    sx, sy, sw, sh = arm_r["skin"]
    arm_r_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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

    # Körper generieren
    koerper = mapping["koerper"]
    sx, sy, sw, sh = koerper["skin"]
    koerper_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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

    # Spezielle Pixel-Kopieraktionen für den Körper (Feinschliff)
    px = totem_img.getpixel((10, 17))
    totem_img.putpixel((10, 16), px)
    for y in range(16, 27):
        px = totem_img.getpixel((12, y))
        totem_img.putpixel((11, y), px)
    for y in range(16, 27):
        px = totem_img.getpixel((19, y))
        totem_img.putpixel((20, y), px)
    px = totem_img.getpixel((21, 17))
    totem_img.putpixel((21, 16), px)

    # Outline laden und drüberlegen, falls vorhanden
    outline_path = Path("outline.png")
    if outline_path.exists():
        try:
            outline_img = Image.open(outline_path).convert("RGBA")
            if outline_img.size != (32, 32):
                outline_img = outline_img.resize((32, 32), Image.NEAREST)
            totem_img = Image.alpha_composite(totem_img, outline_img)
        except Exception as e:
            pass  # Fehler ignorieren, Outline ist optional

    # Bild als PNG zurückgeben
    img_io = io.BytesIO()
    totem_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/generate_java_zip', methods=['POST'])
def generate_java_zip():
    file = request.files['skin']
    uploaded_image = Image.open(file.stream)
    overlay = request.form.get('overlay', 'off') == 'on'

    # Totem-Bild generieren (wie in generate_totem)
    mapping = {
        "kopf": {"skin": [8, 8, 8, 8], "totem": [8, 1, 16, 16], "resize": "nearest", "crop": [[0, 0, 15, 0], [0, 1], [1, 1], [14, 1], [15, 1], [0, 2], [15, 2], [0, 15, 15, 15]]},
        "arm_links": {"skin": [44, 20, 3, 9], "totem": [8, 17, 3, 9], "resize": None, "crop": []},
        "arm_rechts": {"skin": [36, 52, 3, 9], "totem": [21, 17, 3, 9], "resize": None, "crop": []},
        "koerper": {"skin": [20, 20, 8, 12], "totem": [12, 16, 8, 12], "resize": None, "crop": []}
    }
    totem_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    kopf = mapping["kopf"]
    sx, sy, sw, sh = kopf["skin"]
    kopf_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh))
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
    if overlay:
        overlay_img = uploaded_image.crop((40, 8, 40+8, 8+8))
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
        kopf_img = Image.alpha_composite(kopf_img, overlay_img)
    tx, ty = kopf["totem"][0], kopf["totem"][1]
    totem_img.paste(kopf_img, (tx, ty), kopf_img)
    arm_l = mapping["arm_links"]
    sx, sy, sw, sh = arm_l["skin"]
    arm_l_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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
    arm_r = mapping["arm_rechts"]
    sx, sy, sw, sh = arm_r["skin"]
    arm_r_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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
    koerper = mapping["koerper"]
    sx, sy, sw, sh = koerper["skin"]
    koerper_img = uploaded_image.crop((sx, sy, sx+sw, sy+sh)).convert("RGBA")
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
    px = totem_img.getpixel((10, 17))
    totem_img.putpixel((10, 16), px)
    for y in range(16, 27):
        px = totem_img.getpixel((12, y))
        totem_img.putpixel((11, y), px)
    for y in range(16, 27):
        px = totem_img.getpixel((19, y))
        totem_img.putpixel((20, y), px)
    px = totem_img.getpixel((21, 17))
    totem_img.putpixel((21, 16), px)
    outline_path = Path("outline.png")
    if outline_path.exists():
        try:
            outline_img = Image.open(outline_path).convert("RGBA")
            if outline_img.size != (32, 32):
                outline_img = outline_img.resize((32, 32), Image.NEAREST)
            totem_img = Image.alpha_composite(totem_img, outline_img)
        except Exception as e:
            pass
    # ZIP bauen
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        # pack.png (Icon)
        icon_bytes = io.BytesIO()
        totem_img.save(icon_bytes, 'PNG')
        icon_bytes.seek(0)
        zf.writestr('pack.png', icon_bytes.read())
        # pack.mcmeta
        mcmeta = {
            "pack": {
                "description": "§6Have fun with youre custom §bTotem§6. §4Made by §5EinFabo",
                "pack_format": 15,
                "supported_formats": {
                    "min_inclusive": 15,
                    "max_inclusive": 99
                }
            }
        }
        zf.writestr('pack.mcmeta', json.dumps(mcmeta, indent=2, ensure_ascii=False))
        # assets/minecraft/textures/item/totem_of_undying.png
        tex_bytes = io.BytesIO()
        totem_img.save(tex_bytes, 'PNG')
        tex_bytes.seek(0)
        zf.writestr('assets/minecraft/textures/item/totem_of_undying.png', tex_bytes.read())
    mem_zip.seek(0)
    return send_file(mem_zip, mimetype='application/zip', as_attachment=True, download_name='Custom_Totem.zip')

if __name__ == '__main__':
    app.run(debug=True) 