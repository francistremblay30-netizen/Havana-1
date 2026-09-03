#!/usr/bin/env python3
"""Prépare les photos pour le document Word (mise en page magazine).

Lit photos/photos.json. Chaque emplacement a un type de recadrage :
  cover   : pleine page (8,5 x 11 po), dégradé marine dans le bas
  banner  : bandeau pleine largeur (8,5 x 4,2 po), dégradé marine dans le bas
  wide    : 16:9 pleine largeur du texte
  pair    : 3:2 pour les photos côte à côte
  natural : aucun recadrage (plans, cartes)
  portrait: aucun recadrage, hauteur fixe
Écrit photos/photos_meta.json (chemins et dimensions) pour generer_plan.js.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PHOTOS = ROOT / "photos"
PREP = PHOTOS / "prepare"
PREP.mkdir(exist_ok=True)

NAVY = (11, 42, 74)
DPI = 200
SIZES = {
    "cover": (int(8.5 * DPI), int(11 * DPI)),
    "banner": (int(8.5 * DPI), int(4.2 * DPI)),
    "wide": (int(6.7 * DPI), int(6.7 * DPI * 9 / 16)),
    "pair": (int(3.3 * DPI), int(3.3 * DPI * 2 / 3)),
}
GRADIENT = {"cover": (0.38, 0.96), "banner": (0.30, 0.95)}  # (début en fraction de hauteur, opacité max)


def load(name):
    src = PHOTOS / name
    if not src.exists():
        raise SystemExit(f"Photo introuvable : {src}")
    return ImageOps.exif_transpose(Image.open(src)).convert("RGB")


def crop_to(im, size, anchor="center"):
    """Recadre en conservant le ratio cible, puis redimensionne (agrandit au besoin)."""
    tw, th = size
    ratio = tw / th
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        left = (w - nw) // 2
        box = (left, 0, left + nw, h)
    else:
        nh = int(w / ratio)
        top = 0 if anchor == "top" else (h - nh) // 2 if anchor == "center" else h - nh
        box = (0, top, w, top + nh)
    im = im.crop(box)
    return im.resize((tw, th), Image.LANCZOS)


def gradient(im, start, max_alpha):
    """Fond en dégradé vers le marine dans la partie basse pour le texte en surimpression."""
    w, h = im.size
    overlay = Image.new("RGB", (w, h), NAVY)
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    y0 = int(h * start)
    for y in range(y0, h):
        a = int(255 * max_alpha * ((y - y0) / max(1, h - y0)) ** 0.9)
        for x in range(w):
            px[x, y] = a
    return Image.composite(overlay, im, mask)


def prepare(name, kind, anchor="center"):
    im = load(name)
    if kind in SIZES:
        im = crop_to(im, SIZES[kind], anchor)
    elif im.width > 1800:
        im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
    if kind in GRADIENT:
        im = gradient(im, *GRADIENT[kind])
    out = PREP / f"{Path(name).stem}-{kind}.jpg"
    im.save(out, "JPEG", quality=88, optimize=True)
    return {"file": str(out.relative_to(ROOT)), "width": im.width, "height": im.height, "kind": kind}


def solid(kind):
    """Page unie marine pour la quatrième de couverture."""
    im = Image.new("RGB", SIZES["cover"], NAVY)
    out = PREP / f"navy-{kind}.jpg"
    im.save(out, "JPEG", quality=70)
    return {"file": str(out.relative_to(ROOT)), "width": im.width, "height": im.height, "kind": kind}


mapping = json.loads((PHOTOS / "photos.json").read_text(encoding="utf-8"))
meta = {}
for slot, value in mapping.items():
    if slot.startswith("_") or value is None:
        continue
    if isinstance(value, list):
        meta[slot] = [dict(prepare(v["file"], v.get("kind", "pair"), v.get("anchor", "center")), caption=v.get("caption", "")) for v in value]
    elif value.get("file") == "__navy__":
        meta[slot] = dict(solid(value.get("kind", "cover")), caption="")
    else:
        meta[slot] = dict(prepare(value["file"], value.get("kind", "pair"), value.get("anchor", "center")), caption=value.get("caption", ""))

(PHOTOS / "photos_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
print("Emplacements préparés :", ", ".join(meta.keys()))
