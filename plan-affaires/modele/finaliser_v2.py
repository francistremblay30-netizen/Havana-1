#!/usr/bin/env python3
"""Finalise le plan v2 : docx → PDF (Word), réinjection des images HD que Word a réduites,
planche-contact de contrôle. Usage : python finaliser_v2.py"""
import os, re, io, shutil, subprocess, zipfile, tempfile
import fitz, numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PA = os.path.abspath(os.path.join(HERE, ".."))
DOCX = os.path.join(PA, "Plan_affaires_Complexe_Havana_v2.docx")
PDF = os.path.join(PA, "Plan_affaires_Complexe_Havana_v2.pdf")
tmp = tempfile.mkdtemp(prefix="havana_v2_")
src = os.path.join(tmp, "docx")
with zipfile.ZipFile(DOCX) as z:
    z.extractall(src)
# ne pas compresser les images à l'enregistrement / export
p = os.path.join(src, "word", "settings.xml")
s = open(p, encoding="utf8").read()
if "doNotAutoCompressPictures" not in s:
    s = s.replace("<w:compat>", "<w:doNotAutoCompressPictures/><w:compat>", 1) if "<w:compat>" in s else s.replace("</w:settings>", "<w:doNotAutoCompressPictures/></w:settings>")
    open(p, "w", encoding="utf8").write(s)
print_docx = os.path.join(tmp, "print.docx")
with zipfile.ZipFile(print_docx, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(src, "[Content_Types].xml"), "[Content_Types].xml")
    for root, d, files in os.walk(src):
        for f in files:
            full = os.path.join(root, f); rel = os.path.relpath(full, src).replace(os.sep, "/")
            if rel != "[Content_Types].xml":
                z.write(full, rel)
word_pdf = os.path.join(tmp, "word.pdf")
ps = f'$w=New-Object -ComObject Word.Application;$w.Visible=$false;$d=$w.Documents.Open("{print_docx}",$false,$true);$d.Fields.Update() | Out-Null;$d.ExportAsFixedFormat("{word_pdf}",17,$false,0,0,0,0,0,$true,$true,0,$true,$true,$false);$d.Close($false);$w.Quit()'
subprocess.check_call(["powershell", "-NoProfile", "-Command", ps])
print("export Word ok")

# réinjection des images HD réduites par Word
media = os.path.join(src, "word", "media")
def fp(im): return np.asarray(im.convert("RGB").resize((24, 24), Image.BILINEAR), dtype=float)
orig = {f: Image.open(os.path.join(media, f)) for f in os.listdir(media)}
ofp = {f: fp(im) for f, im in orig.items()}
d = fitz.open(word_pdf); done = 0
for pg in d:
    for info in pg.get_images(full=True):
        x = info[0]
        pix = fitz.Pixmap(d, x)
        if pix.n - pix.alpha >= 4: pix = fitz.Pixmap(fitz.csRGB, pix)
        im = Image.frombytes("RGBA" if pix.alpha else "RGB", (pix.width, pix.height), pix.samples); ar = pix.width / pix.height
        cands = [(np.abs(ofp[f] - fp(im)).mean(), f) for f in orig if abs(orig[f].width / orig[f].height - ar) < 0.03]
        if not cands: continue
        diff, f = min(cands)
        if diff < 15 and pix.width < 0.95 * orig[f].width and orig[f].mode == "RGB":
            buf = io.BytesIO(); orig[f].save(buf, "JPEG", quality=90)
            d.update_stream(x, buf.getvalue(), new=True, compress=False)
            for k, v in [("Width", str(orig[f].width)), ("Height", str(orig[f].height)), ("Filter", "/DCTDecode"), ("ColorSpace", "/DeviceRGB"), ("BitsPerComponent", "8"), ("SMask", "null"), ("Decode", "null"), ("DecodeParms", "null")]:
                d.xref_set_key(x, k, v)
            done += 1
d.save(PDF, garbage=4, deflate=True)
d = fitz.open(PDF); n = len(d)
print("images HD réinjectées :", done, "| pages :", n, "| taille :", os.path.getsize(PDF) // 1024, "ko")
# planche-contact
thumbs = []
for i in range(n):
    pix = d[i].get_pixmap(dpi=28); thumbs.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
tw, th = thumbs[0].size; cols = 8; rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 6), rows * (th + 6)), "grey")
for k, t in enumerate(thumbs): sheet.paste(t, ((k % cols) * (tw + 6), (k // cols) * (th + 6)))
sheet.save(os.path.join(HERE, "planche_v2.png")); print("planche :", sheet.size)
shutil.rmtree(tmp, ignore_errors=True)
