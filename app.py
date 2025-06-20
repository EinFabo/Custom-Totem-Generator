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

def generate_totem_image(uploaded_image, overlay):
    """
    Erzeugt aus einem Minecraft-Skin-Bild (uploaded_image) und Overlay-Flag ein Totem-Bild (32x32).
    Gibt ein PIL.Image-Objekt zurück.
    """
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

    # --- Kopf generieren ---
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

    # --- Kopf-Overlay extrahieren und drüberlegen (nur wenn overlay aktiviert ist) ---
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

    # --- Linken Arm generieren ---
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

    # --- Rechten Arm generieren ---
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

    # --- Körper generieren ---
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

    # --- Spezielle Pixel-Kopieraktionen für den Körper (Feinschliff) ---
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

    # --- Outline laden und drüberlegen, falls vorhanden ---
    outline_path = Path("outline.png")
    if outline_path.exists():
        try:
            outline_img = Image.open(outline_path).convert("RGBA")
            if outline_img.size != (32, 32):
                outline_img = outline_img.resize((32, 32), Image.NEAREST)
            totem_img = Image.alpha_composite(totem_img, outline_img)
        except Exception as e:
            pass  # Fehler ignorieren, Outline ist optional

    return totem_img

@app.route('/generate_totem', methods=['POST'])
def generate_totem():
    # Prüfe, ob ein Username übergeben wurde
    username = request.form.get('username', '').strip()
    if username:
        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_response = requests.get(mojang_url)
        if mojang_response.status_code == 200:
            uuid = mojang_response.json()['id']
            skin_url = f"https://crafatar.com/skins/{uuid}"
            response = requests.get(skin_url)
            if response.status_code == 200:
                try:
                    uploaded_image = Image.open(io.BytesIO(response.content))
                    print("[DEBUG] Username: Bild geladen, Typ:", type(uploaded_image), "Größe:", getattr(uploaded_image, 'size', 'NO SIZE'))
                except Exception as e:
                    print("[DEBUG] Fehler beim Laden des Bildes (Username):", e)
                    raise
            else:
                print("[DEBUG] Fehler: Skin konnte nicht von Crafatar geladen werden.")
                return "Skin konnte nicht von Crafatar geladen werden.", 400
        else:
            print("[DEBUG] Fehler: Username existiert nicht laut Mojang API.")
            return "Username existiert nicht (laut Mojang API).", 400
    else:
        try:
            file = request.files['skin']
            uploaded_image = Image.open(file.stream)
            print("[DEBUG] Datei-Upload: Bild geladen, Typ:", type(uploaded_image), "Größe:", getattr(uploaded_image, 'size', 'NO SIZE'))
        except Exception as e:
            print("[DEBUG] Fehler beim Laden des Bildes (Datei):", e)
            raise
    overlay = request.form.get('overlay', 'off') == 'on'

    # --- NEU: Bildverarbeitung ausgelagert ---
    totem_img = generate_totem_image(uploaded_image, overlay)

    # Bild als PNG zurückgeben
    img_io = io.BytesIO()
    totem_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

# Inhalt der pack.mcmeta als String-Konstante direkt im Code
PACK_MCMETA = """{
    "pack": {
        "description": "§6Have fun with youre custom §bTotem§6. §4Made with §5mc-totem.com",
        "pack_format": 15,
        "supported_formats": {
          "min_inclusive": 15,
          "max_inclusive": 99
        }
    }
}"""

@app.route('/generate_java_zip', methods=['POST'])
def generate_java_zip():
    username = request.form.get('username', '').strip()
    if username:
        mojang_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        mojang_response = requests.get(mojang_url)
        if mojang_response.status_code == 200:
            uuid = mojang_response.json()['id']
            skin_url = f"https://crafatar.com/skins/{uuid}"
            response = requests.get(skin_url)
            if response.status_code == 200:
                try:
                    uploaded_image = Image.open(io.BytesIO(response.content))
                    print("[DEBUG] Username (ZIP): Bild geladen, Typ:", type(uploaded_image), "Größe:", getattr(uploaded_image, 'size', 'NO SIZE'))
                except Exception as e:
                    print("[DEBUG] Fehler beim Laden des Bildes (Username, ZIP):", e)
                    raise
            else:
                print("[DEBUG] Fehler: Skin konnte nicht von Crafatar geladen werden (ZIP).")
                return "Skin konnte nicht von Crafatar geladen werden.", 400
        else:
            print("[DEBUG] Fehler: Username existiert nicht laut Mojang API (ZIP).")
            return "Username existiert nicht (laut Mojang API).", 400
    else:
        try:
            file = request.files['skin']
            uploaded_image = Image.open(file.stream)
            print("[DEBUG] Datei-Upload (ZIP): Bild geladen, Typ:", type(uploaded_image), "Größe:", getattr(uploaded_image, 'size', 'NO SIZE'))
        except Exception as e:
            print("[DEBUG] Fehler beim Laden des Bildes (Datei, ZIP):", e)
            raise
    overlay = request.form.get('overlay', 'off') == 'on'

    # --- NEU: Bildverarbeitung ausgelagert ---
    totem_img = generate_totem_image(uploaded_image, overlay)

    # Bild als PNG in BytesIO speichern
    img_io = io.BytesIO()
    totem_img.save(img_io, 'PNG')
    img_io.seek(0)

    # --- pack.png dynamisch aus Totem-Textur erzeugen (256x256) ---
    pack_img = totem_img.resize((256, 256), Image.NEAREST)
    pack_io = io.BytesIO()
    pack_img.save(pack_io, 'PNG')
    pack_io.seek(0)

    # --- ZIP-Archiv erstellen ---
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Totem-Bild ins ZIP schreiben
        zipf.writestr('assets/minecraft/textures/item/totem_of_undying.png', img_io.read())
        # pack.mcmeta direkt aus String-Konstante hinzufügen
        zipf.writestr('pack.mcmeta', PACK_MCMETA)
        # pack.png aus Totem-Textur erzeugen und hinzufügen
        zipf.writestr('pack.png', pack_io.read())
    zip_io.seek(0)
    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='Custom_Totem.zip')

if __name__ == '__main__':
    app.run(debug=True) 