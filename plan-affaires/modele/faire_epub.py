#!/usr/bin/env python3
"""Texte → EPUB, pour la lecture à voix haute des applications de livres.

Google Play Livres, Moon+ Reader et les autres lisent un EPUB à voix haute en
arrière-plan, écran éteint, et retiennent la position — ce que « Sélectionner
pour prononcer » d'Android ne fait pas. Les fichiers .txt ne sont pas acceptés
par Play Livres ; l'EPUB l'est.

Chaque ligne en MAJUSCULES devient un chapitre, ce qui donne une table des
matières navigable et des points de reprise.

Usage : python3 faire_epub.py <texte.txt> "<Titre>" [sortie.epub]
"""
import html
import re
import sys
import uuid
import zipfile
from pathlib import Path

GABARIT = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
<head><title>{titre}</title><meta charset="utf-8"/></head>
<body>{corps}</body>
</html>
"""


MARQUEUR = re.compile(r"(?=\bChapitre \d+\.)")


def chapitres(texte):
    """Découpe sur les lignes de titre (en majuscules), garde l'ordre du texte.

    À défaut de titres en majuscules, on retombe sur les « Chapitre N. » que le
    convertisseur audio insère en tête de chapitre.
    """
    blocs, courant = [], {"titre": "Début", "paragraphes": []}
    for para in [p.strip() for p in texte.split("\n\n") if p.strip()]:
        ligne = para.split("\n")[0].strip()
        lettres = [c for c in ligne if c.isalpha()]
        est_titre = (
            len(ligne) < 120
            and len(lettres) > 3
            and all(c.isupper() for c in lettres)
        )
        if est_titre:
            if courant["paragraphes"]:
                blocs.append(courant)
            reste = para.split("\n")[1:]
            courant = {"titre": ligne.rstrip("."), "paragraphes": [r.strip() for r in reste if r.strip()]}
        else:
            courant["paragraphes"].append(para.replace("\n", " "))
    if courant["paragraphes"] or not blocs:
        blocs.append(courant)
    if len(blocs) > 1:
        return blocs
    return chapitres_par_marqueur(texte)


def titre_de_chapitre(part):
    """« Chapitre 4. Analyse du marché Le camping… » → « Chapitre 4. Analyse du marché ».

    Rien ne sépare le titre de la phrase d'accroche qui le suit. On s'arrête donc
    au deuxième mot capitalisé : c'est là que l'accroche commence.
    """
    entete = re.match(r"(Chapitre \d+\.)\s*(.*)", part, re.S)
    if not entete:
        return "Début"
    mots = entete.group(2).split()[:7]
    garde = mots[:1]
    for mot in mots[1:]:
        if mot[:1].isupper():
            break
        garde.append(mot)
    return (entete.group(1) + " " + " ".join(garde)).strip()


def chapitres_par_marqueur(texte):
    """Repli : découpe sur « Chapitre N. » en tête de paragraphe."""
    blocs = []
    for part in MARQUEUR.split(texte):
        part = part.strip()
        if not part:
            continue
        paragraphes = [p.strip().replace("\n", " ") for p in part.split("\n\n") if p.strip()]
        blocs.append({"titre": titre_de_chapitre(part), "paragraphes": paragraphes})
    return blocs or [{"titre": "Début", "paragraphes": [texte]}]


def ecrire(source, titre, destination):
    texte = Path(source).read_text(encoding="utf-8")
    blocs = chapitres(texte)
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, titre))

    fichiers = []
    for i, bloc in enumerate(blocs, 1):
        corps = f"<h1>{html.escape(bloc['titre'])}</h1>\n" + "\n".join(
            f"<p>{html.escape(p)}</p>" for p in bloc["paragraphes"]
        )
        fichiers.append((f"ch{i:02d}.xhtml", bloc["titre"],
                         GABARIT.format(titre=html.escape(bloc["titre"]), corps=corps)))

    manifeste = "\n".join(
        f'<item id="ch{i}" href="{nom}" media-type="application/xhtml+xml"/>'
        for i, (nom, _, _) in enumerate(fichiers, 1))
    colonne = "\n".join(f'<itemref idref="ch{i}"/>' for i in range(1, len(fichiers) + 1))
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">{uid}</dc:identifier>
<dc:title>{html.escape(titre)}</dc:title>
<dc:language>fr</dc:language>
<dc:creator>Complexe Havana</dc:creator>
<meta property="dcterms:modified">2026-09-16T00:00:00Z</meta>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
{manifeste}
</manifest>
<spine>
{colonne}
</spine>
</package>
"""
    liens = "\n".join(f'<li><a href="{nom}">{html.escape(t)}</a></li>' for nom, t, _ in fichiers)
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="fr" lang="fr">
<head><title>Table des matières</title><meta charset="utf-8"/></head>
<body><nav epub:type="toc"><h1>Table des matières</h1><ol>
{liens}
</ol></nav></body>
</html>
"""
    with zipfile.ZipFile(destination, "w") as z:
        # « mimetype » doit être le premier fichier et non compressé.
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0" encoding="utf-8"?>\n'
                   '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/content.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>',
                   zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        for nom, _, contenu in fichiers:
            z.writestr(f"OEBPS/{nom}", contenu, zipfile.ZIP_DEFLATED)
    print(f"Écrit : {destination} ({len(fichiers)} chapitres, {len(texte.split())} mots)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    titre = sys.argv[2]
    dst = Path(sys.argv[3]) if len(sys.argv) > 3 else src.with_suffix(".epub")
    ecrire(src, titre, dst)
