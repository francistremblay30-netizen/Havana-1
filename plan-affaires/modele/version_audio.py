#!/usr/bin/env python3
"""Version écoutable d'un plan d'affaires : PDF → texte conçu pour la synthèse vocale.

Retire ce qui n'a aucun sens à l'oreille (en-têtes répétés à chaque page, table des
matières avec ses points de conduite, légendes de figures, champs à compléter), et
transforme les tableaux en phrases qui se lisent à voix haute au lieu d'une suite de
nombres. Développe aussi les abréviations que les moteurs de synthèse écorchent
(M$, k$, DSCR, pi², %).

Usage : python3 version_audio.py <plan.pdf> [sortie.txt]
"""
import re
import sys
from pathlib import Path

import pymupdf

# En-tête répété en haut de chaque page (4 lignes) : à retirer.
ENTETE = re.compile(r"^(Complexe Havana|Plan d'affaires \d{4} – \d{4}|Confidentiel|Page \d+)\s*$")
# Ligne de table des matières : « Titre ..................... 12 »
LIGNE_TDM = re.compile(r"\.{4,}\s*\d+\s*$")
LEGENDE = re.compile(r"^(Figure|Tableau)\s+\d+\s*[–-]")
# Champs laissés à compléter dans le document.
A_COMPLETER = re.compile(r"\[[^\]]{2,300}\]")

# Remplacements pour la synthèse vocale, appliqués dans l'ordre.
ORAL = [
    (r"(\d) (\d)", r"\1 \2"),            # espace fine insécable dans les nombres
    (r"(\d) (\d)", r"\1 \2"),            # espace insécable dans les nombres
    (r" ", " "),
    (r"\bM\$", " millions de dollars"),
    (r"\bk\$", " mille dollars"),
    (r"\$", " dollars"),
    (r"\s*%", " pour cent"),
    (r"\bDSCR\b", "ratio de couverture de la dette"),
    (r"\bBAIIA\b", "bénéfice avant intérêts, impôts et amortissement"),
    (r"\bDPA\b", "déduction pour amortissement"),
    (r"\bRBQ\b", "Régie du bâtiment du Québec"),
    (r"\bCPTAQ\b", "Commission de protection du territoire agricole"),
    (r"\bRACJ\b", "Régie des alcools, des courses et des jeux"),
    (r"\bMRC\b", "municipalité régionale de comté"),
    (r"\bRMR\b", "région métropolitaine"),
    (r"\bETP\b", "employés à temps plein"),
    (r"\bFLI / FLS\b", "fonds locaux d'investissement"),
    (r"\bDEC\b", "Développement économique Canada"),
    (r"\bpi²", " pieds carrés"),
    (r"\bTI\b", "informatique"),
    (r"\b4 saisons\b", "quatre saisons"),
    (r"\b12×24\b", "12 pieds par 24"),
    (r"≈", "environ "),
    (r"−", "moins "),
    (r"(\d)\s*x\b", r"\1 fois"),
    (r"\bn°\s*", "numéro "),
    (r"(\d)\s*h\b", r"\1 heures"),
    (r"\((\d[\d  ]*)\)\s*dollars", r"moins \1 dollars"),   # négatif comptable entre parenthèses
    (r"\s*[•·]\s*", ". "),                                 # une puce devient une pause
    (r"\.\s*(?=\.)", ""),
    (r"([:;])\s*\.\s*", r"\1 "),                           # « 18 mois :. Phase 1 »
    (r"^0(\d)\s+", r"Chapitre \1. "),                      # « 02 L'entreprise » → « Chapitre 2 »
    (r"\s+([;:,.])", r"\1"),
    (r"\s{2,}", " "),
]


def oraliser(texte):
    for motif, remplacement in ORAL:
        texte = re.sub(motif, remplacement, texte)
    return texte.strip()


VALEUR = re.compile(r"^[\d(−+-]")   # une cellule qui commence par un chiffre ou un signe


def grille(table):
    """Tableau en grille rectangulaire, colonnes vides retirées, lignes de continuation fusionnées.

    Les colonnes doivent rester alignées : on ne retire une colonne que si elle est
    vide sur TOUTES les lignes, sinon les valeurs se décalent d'un en-tête.
    """
    lignes = table.extract()
    if not lignes:
        return []
    largeur = max(len(l) for l in lignes)
    g = [[(c or "").strip() for c in l] + [""] * (largeur - len(l)) for l in lignes]
    g = [l for l in g if any(l)]
    garder = [i for i in range(largeur) if any(l[i] for l in g)]
    g = [[l[i] for i in garder] for l in g]
    fusionnees = []
    for ligne in g:
        suite_du_libelle = fusionnees and ligne[0] and not any(ligne[1:]) and any(fusionnees[-1][1:])
        suite_des_valeurs = fusionnees and not ligne[0] and any(ligne[1:])
        if suite_du_libelle:
            fusionnees[-1][0] += " " + ligne[0]
        elif suite_des_valeurs:
            # Cellule dont le texte déborde sur la ligne suivante : recoller colonne par colonne.
            for i, cellule in enumerate(ligne):
                if cellule:
                    fusionnees[-1][i] = (fusionnees[-1][i] + " " + cellule).strip()
        else:
            fusionnees.append(ligne)
    return fusionnees


def tableau_en_phrases(table):
    """Un tableau devient une phrase par ligne, chaque valeur annoncée par son en-tête."""
    g = grille(table)
    if len(g) < 2:
        return ""
    # Tuiles de chiffres clés : une ligne de valeurs, une ligne de libellés.
    if len(g) == 2:
        valeurs, libelles = g
        if not all(VALEUR.match(c) for c in valeurs if c):
            valeurs, libelles = libelles, valeurs
        paires = [f"{lib} : {val}" for val, lib in zip(valeurs, libelles) if val and lib]
        return ". ".join(paires) + "." if paires else ""
    entetes, out = g[0], []
    for ligne in g[1:]:
        libelle = ligne[0]
        paires = [f"{entetes[i]} : {v}" if i < len(entetes) and entetes[i] else v
                  for i, v in enumerate(ligne) if i > 0 and v]
        if not libelle and not paires:
            continue
        if paires:
            out.append((f"{libelle} — " if libelle else "") + " ; ".join(paires) + ".")
        else:
            out.append(f"{libelle}.")
    if not out:
        return ""
    titre = ", ".join(e for e in entetes if e)
    return (f"Tableau : {titre}.\n" if titre else "") + "\n".join(out)


def page_en_texte(page, sauter_tdm):
    tables = page.find_tables().tables
    zones = [t.bbox for t in tables]
    morceaux = []
    for bloc in page.get_text("blocks"):
        x0, y0, x1, y1, texte = bloc[0], bloc[1], bloc[2], bloc[3], bloc[4]
        # Un bloc dont le centre tombe dans un tableau est traité avec le tableau.
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if any(bx0 <= cx <= bx1 and by0 <= cy <= by1 for bx0, by0, bx1, by1 in zones):
            continue
        lignes = []
        for ligne in texte.splitlines():
            ligne = ligne.strip()
            if not ligne or ENTETE.match(ligne) or LEGENDE.match(ligne):
                continue
            if sauter_tdm and LIGNE_TDM.search(ligne):
                continue
            lignes.append(ligne)
        if lignes:
            # Un mot coupé garde son trait d'union : le retirer casserait les noms
            # composés (« Cantons- / de-l'Est » deviendrait « Cantonsde-l'Est »).
            bloc_texte = lignes[0]
            for suite in lignes[1:]:
                bloc_texte += suite if bloc_texte.endswith("-") else " " + suite
            morceaux.append((y0, bloc_texte))
    for t in tables:
        phrases = tableau_en_phrases(t)
        if phrases:
            morceaux.append((t.bbox[1], phrases))
    morceaux.sort(key=lambda m: m[0])
    return "\n\n".join(m[1] for m in morceaux)


def convertir(source, destination):
    doc = pymupdf.open(source)
    pages = []
    for i, page in enumerate(doc):
        texte = page_en_texte(page, sauter_tdm=i < 4)
        texte = A_COMPLETER.sub("", texte)
        texte = oraliser(texte)
        if texte:
            pages.append(texte)
    corps = "\n\n".join(pages)
    corps = re.sub(r"\n{3,}", "\n\n", corps)
    Path(destination).write_text(corps + "\n", encoding="utf-8")
    mots = len(corps.split())
    print(f"Écrit : {destination}")
    print(f"{mots} mots — environ {mots / 150:.0f} minutes d'écoute à 150 mots/minute.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "-AUDIO.txt")
    convertir(src, dst)
