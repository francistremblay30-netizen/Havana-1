#!/usr/bin/env python3
"""Prépare les photos pour le document Word.

Lit photos/photos.json, convertit chaque photo en JPEG, la réduit à 1800 px
de large au maximum (pour garder un document léger) et écrit
photos/photos_meta.json avec les dimensions, utilisé par generer_plan.js.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
PHOTOS = HERE.parent / "photos"
PREP = PHOTOS / "prepare"
PREP.mkdir(exist_ok=True)
MAX_W = 1800

mapping = json.loads((PHOTOS / "photos.json").read_text(encoding="utf-8"))
meta = {}


def prepare(name):
    src = PHOTOS / name
    if not src.exists():
        raise SystemExit(f"Photo introuvable : {src}")
    out = PREP / (src.stem + ".jpg")
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(out, "JPEG", quality=86, optimize=True)
    return {"file": str(out.relative_to(PHOTOS.parent)), "width": im.width, "height": im.height}


for slot, value in mapping.items():
    if slot.startswith("_") or value is None:
        continue
    if isinstance(value, list):
        meta[slot] = [dict(prepare(v["file"]), caption=v.get("caption", "")) for v in value]
    else:
        meta[slot] = dict(prepare(value["file"]), caption=value.get("caption", ""))

(PHOTOS / "photos_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print("Emplacements remplis :", ", ".join(meta.keys()) or "aucun")
