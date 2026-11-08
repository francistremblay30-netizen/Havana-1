#!/usr/bin/env python3
"""Cabane à pêche légère 5 x 10 pi, toit en pointe, tirée à la motoneige.

6 feuilles SVG (lettre paysage) dans ce dossier, puis :
  node ../exporter.js . Plans_cabane_5x10_motoneige.pdf
Cotes en pouces réels. Réutilise les outils de dessin de ../generer_plans.py.
"""
import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent))
import generer_plans as g  # noqa: E402
from generer_plans import Feuille, Vue, titre_vue, notes, callout  # noqa: E402

_fi = g.fi


def fi(po):
    """Comme g.fi, mais 9 3/4" au lieu de 0'-9 3/4"."""
    t = _fi(po)
    return t[3:] if t.startswith("0'-") else t


g.fi = fi

g.PROJET = "Cabane à pêche légère 5 × 10 pi — motoneige"
g.NB_FEUILLES = 6
g.DATE = "2026-11-08"

# --- Paramètres (pouces) ----------------------------------------------------
L, B = 120, 60            # longueur (X, avant = timon) et largeur (Y, 0 = côté banc)
T = 2.0                   # mur : CP 1/4 + 2x2 + panneau int. 1/4
UHMW = 0.25               # semelle de glisse
PAT = 5.5                 # patin 2x6 sur chant
CAD = 3.5                 # cadre de plancher 2x4 sur chant
CP = 0.5                  # plancher CP 1/2
Z_P = UHMW + PAT          # dessous du cadre = 5.75
Z_PL = Z_P + CAD + CP     # dessus du plancher = 9.75
H_MUR = 60                # murs latéraux (plancher -> dessus sablière)
PENTE = 8 / 12
DEB_E, DEB_P = 4, 3       # débords : égout (côtés) et pignons (bouts)
CHEV = 3.0                # chevron 2x3 mesuré à la verticale
TOIT = 4.2                # chevron + fourrure + tôle, à la verticale
FAITE = 7.25              # faîtière 2x8
PATIN_Y = [(0, 1.5), (B - 1.5, B)]
NEZ = 12                  # avancée du nez relevé des patins devant la cabane
ATT = -57                 # anneau d'attelage (X)
TRAPPES = [(18, 20), (50, 20), (82, 20)]   # coin (X, Y), 12 x 12
PORTE_Y = (18, 42)        # porte 24 po au pignon arrière
H_PORTE = 60
FEN_COTE = (44, 68)       # fenêtre côté allée (X), 24 x 12
FEN_AV = (14, 30)         # fenêtre pignon avant (Y), 16 x 12
FEN_Z = (30, 42)          # allège et tête des fenêtres (au-dessus du plancher)
BANC = 14                 # profondeur du banc
H_BANC = 16
BLEU, ROUGE, BOIS = "#1f5f8b", "#c0392b", "#7a5a2a"
bois = dict(fill="#f3ead8", stroke=BOIS, sw=0.6)


def zr(y):
    """Dessous des chevrons (Z depuis la glace) selon Y, débords compris."""
    return Z_PL + H_MUR + (B / 2 - abs(y - B / 2)) * PENTE


Z_FAITE = zr(B / 2) + CHEV            # dessus de la faîtière
Z_TOP = zr(B / 2) + TOIT              # hors-tout
LIBRE_FAITE = Z_FAITE - FAITE - Z_PL  # dégagement sous la faîtière


def glace(v, x1, x2, prof=8):
    v.rect(x1, -prof, x2 - x1, prof, fill="url(#glace)", stroke="none")
    v.line(x1, 0, x2, 0, stroke=BLEU, sw=1)


def nez_patin():
    """Profil latéral d'un patin (X, Z) avec nez relevé."""
    return [(L, 0), (L, Z_P), (2, Z_P), (-5, Z_P + 2.5), (-10, Z_P + 6.5), (-NEZ, Z_P + 7.5),
            (-NEZ - 1.5, Z_P + 5.5), (-9, Z_P + 1), (-3, 1.2), (6, 0)]


# =============================================================================
def f_plan():
    f = Feuille(1, "Vue en plan — aménagement")
    titre_vue(f, 40, 40, "VUE EN PLAN — AMÉNAGEMENT", "Échelle 1:24 (1/2 po = 1 pi) · avant (timon) à gauche")
    v = Vue(f, 240, 128, 24)
    # patins et timon (sous la cabane, pointillés)
    for y0, y1 in PATIN_Y:
        v.rect(-NEZ, y0, L + NEZ, y1 - y0, stroke=BLEU, sw=0.6, dash="5,2.5")
    ya, yb = 0.75, B - 0.75
    v.poly([(-NEZ, ya), (ATT + 3, B / 2), (-NEZ, yb)], close=False, stroke="#333", sw=1.4)
    v.line(-22, ya + (B / 2 - ya) * (10 / (ATT + 3 + NEZ) * -1), -22, yb - (yb - B / 2) * (10 / (ATT + 3 + NEZ) * -1), stroke="#333", sw=1)
    v.circle(ATT, B / 2, 3, stroke="#333", sw=1.2)
    v.text(-34, B / 2 - 3, "TIMON EN A", size=6.5, anchor="middle", weight="bold")
    v.text(-34, B / 2 + 5.5, "tube acier 1 1/2 po", size=5.5, anchor="middle")
    v.text(ATT, B / 2 + 9, "anneau", size=5.5, anchor="middle")
    v.text(ATT, B / 2 + 14, "d'attelage", size=5.5, anchor="middle")
    # murs
    o = [(0, 0), (L, 0), (L, B), (0, B)]
    i = [(T, T), (L - T, T), (L - T, B - T), (T, B - T)]
    pts = lambda P: " ".join(f"{a:.2f},{b:.2f}" for a, b in (v.P(*p) for p in P))
    f.add(f'<path d="M{pts(o)}Z M{pts(i[::-1])}Z" fill="#bbb" stroke="#111" stroke-width="1" fill-rule="evenodd"/>')
    # porte arrière, ouvre vers l'extérieur (penture côté allée)
    p0, p1 = PORTE_Y
    v.rect(L - T - 0.2, p0, T + 0.4, p1 - p0, fill="#fff", stroke="none")
    v.line(L - T, p0, L, p0, sw=1)
    v.line(L - T, p1, L, p1, sw=1)
    w = p1 - p0
    v.rect(L, p1 - 1.2, w, 1.2, fill="#fff", stroke="#111", sw=0.8)
    v.arc(L, p1, w, L, p0, L + w, p1)
    v.text(L + 4, p0 - 2, "PORTE 24 × 60 po", size=6, weight="bold")
    v.text(L + 4, p0 + 3.5, "ouvre vers l'ext.", size=5.5, italic=True)
    # fenêtres
    v.rect(FEN_COTE[0], B - T, FEN_COTE[1] - FEN_COTE[0], T, fill="#fff", stroke="#111", sw=0.6)
    v.line(FEN_COTE[0], B - T / 2, FEN_COTE[1], B - T / 2, sw=0.5)
    v.text((FEN_COTE[0] + FEN_COTE[1]) / 2, B + 5, "FENÊTRE 24 × 12", size=5.8, anchor="middle")
    v.rect(0, FEN_AV[0], T, FEN_AV[1] - FEN_AV[0], fill="#fff", stroke="#111", sw=0.6)
    v.line(T / 2, FEN_AV[0], T / 2, FEN_AV[1], sw=0.5)
    # banc
    v.rect(T, T, L - 2 * T, BANC, fill="#f3ead8", stroke=BOIS, sw=0.7)
    for x in range(26, int(L - T), 24):
        v.line(x, T, x, T + BANC, stroke=BOIS, sw=0.3, dash="2,2")
    v.text(L / 2 + 6, T + BANC / 2 + 1.5, "BANC prof. 14 po · haut. 16 po · rangement dessous", size=6.3, anchor="middle")
    # trappes
    for n, (tx, ty) in enumerate(TRAPPES, 1):
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke=BLEU, sw=1)
        v.circle(tx + 6, ty + 6, 4, stroke=BLEU, dash="2,1.5")
        v.text(tx + 6, ty + 7.6, f"T{n}", size=6.5, anchor="middle", weight="bold", fill=BLEU)
    v.text(75, 47, "ALLÉE 26 po", size=7, anchor="middle", fill="#777")
    # chauffage
    v.rect(T, 34, 20, B - T - 34, stroke=ROUGE, sw=0.5, dash="3,2")
    v.rect(4, 40, 12, 16, fill="#fde2df", stroke=ROUGE, sw=0.9)
    v.text(10, 48.5, "CHAUF.", size=5.2, anchor="middle", weight="bold", fill=ROUGE)
    # coupe A-A
    xa = 24
    v.line(xa, -7, xa, B + 7, stroke=ROUGE, sw=0.7, dash="10,3,2,3")
    for ya_ in (-7, B + 7):
        a, b = v.P(xa, ya_)
        f.add(f'<polygon points="{a:.1f},{b-4:.1f} {a:.1f},{b+4:.1f} {a+9:.1f},{b:.1f}" fill="{ROUGE}"/>')
        f.text(a - 7, b + 3, "A", size=9, anchor="middle", weight="bold", fill=ROUGE)
    v.text(L / 2, -17, "CÔTÉ BANC", size=6.3, anchor="middle", fill="#555")
    v.text(L / 2, B + 11, "CÔTÉ ALLÉE", size=6.3, anchor="middle", fill="#555")
    v.text(-2, -4, "AVANT", size=6.5, weight="bold", fill="#555", anchor="end")
    v.text(L + 2, -4, "ARRIÈRE", size=6.5, weight="bold", fill="#555")
    # cotes
    v.dim(0, 0, L, 0, -60, f"{fi(L)}  (3,05 m)")
    for a, b_ in [(0, 18), (18, 30), (30, 50), (50, 62), (62, 82), (82, 94), (94, L)]:
        v.dim(a, 0, b_, 0, -38, size=5.8)
    v.dim(L, 0, L, B, 92, f"{fi(B)}  (1,52 m)")
    for a, b_ in [(0, 20), (20, 32), (32, B)]:
        v.dim(0, a, 0, b_, -12, size=5.8)
    v.dim(ATT - 3, B, L, B, 62, f"{fi(L - ATT + 3)} hors-tout avec timon")

    col = [
        f"Cabane 5'-0\" × 10'-0\" (1,52 × 3,05 m). Longueur avec timon {fi(L - ATT + 3)}. Étroite et basse : elle suit la trace de la motoneige et passe dans les sentiers.",
        "Ossature légère : murs 2×2 @ 24 po c/c, revêtement CP 1/4, toit en pointe (2 versants) pente 8:12 en tôle.",
        "3 trappes de 12 × 12 po devant le banc, entre les traverses du plancher : on pêche assis, le trou entre les pieds.",
        "Banc de 14 po sur toute la longueur, couvercles à charnières : cannes, tarière courte et sac dessous.",
    ]
    col2 = [
        "Allée de 26 po. Porte 24 × 60 po au pignon arrière, ouvre vers l'extérieur.",
        "Chauffage propane portatif homologué pour l'intérieur, dans le coin avant, sur plaque incombustible.",
        "Ventilation : grille basse dans la porte, grille haute au pignon avant. Détecteur de CO et extincteur obligatoires.",
        "Afficher nom, adresse et téléphone ; vérifier le règlement municipal (dates de pose et de retrait).",
    ]
    notes(f, 40, 420, "NOTES", col, larg=62, inter=9.5)
    y = 434
    for i, l in enumerate(col2, 5):
        mots, cur, out = l.split(), "", []
        for m in mots:
            if len(cur) + len(m) + 1 > 62:
                out.append(cur); cur = m
            else:
                cur = (cur + " " + m).strip()
        out.append(cur)
        f.text(410, y, f"{i}.", size=7.2, weight="bold")
        for o_ in out:
            f.text(422, y, o_, size=7.2); y += 9.5
        y += 2.5
    return f


# =============================================================================
def f_cote():
    f = Feuille(2, "Élévation latérale")
    titre_vue(f, 40, 40, "ÉLÉVATION LATÉRALE (côté allée)", "Échelle 1:24 (1/2 po = 1 pi)")
    v = Vue(f, 250, 420, 24, flip=True)
    glace(v, ATT - 8, L + 14)
    # patin
    v.poly(nez_patin(), fill="url(#bois)", stroke="#111", sw=0.8)
    v.rect(6, 0, L - 6, UHMW, fill="#222", stroke="none")
    # timon
    v.poly([(-NEZ + 1, Z_P + 6.5), (ATT + 3, 13), (ATT + 3, 11.5), (-NEZ + 1, Z_P + 4.5)], fill="#666", stroke="#111", sw=0.6)
    v.circle(ATT, 12.2, 2.6, stroke="#111", sw=1.2)
    # cadre + plancher
    v.rect(0, Z_P, L, CAD, fill="#e9dcc3", stroke="#111", sw=0.6)
    v.rect(0, Z_P + CAD, L, CP, fill="#d8c39a", stroke="#111", sw=0.4)
    # mur
    v.rect(0, Z_PL, L, H_MUR, fill="#f7f4ee", stroke="#111", sw=1)
    for x in (48, 96):
        v.line(x, Z_PL, x, Z_PL + H_MUR, stroke="#aaa", sw=0.5)
    for x in (0.75, L - 0.75):
        v.rect(x - 0.75, Z_PL, 1.5, H_MUR, fill="#e3dccd", stroke="#999", sw=0.3)
    v.rect(FEN_COTE[0], Z_PL + FEN_Z[0], 24, 12, fill="#dbeaf5", stroke="#111", sw=1)
    v.line(FEN_COTE[0], Z_PL + FEN_Z[0], FEN_COTE[1], Z_PL + FEN_Z[1], stroke="#9cc", sw=0.4)
    # toit (vu de côté : bande d'égout + versant)
    ze = zr(-DEB_E)
    v.rect(-DEB_P, ze + 1.2, L + 2 * DEB_P, Z_TOP - ze - 1.2, fill="#7d858a", stroke="#111", sw=0.8)
    for x in range(-DEB_P + 9, L + DEB_P, 9):
        v.line(x, ze + 1.2, x, Z_TOP, stroke="#5d6468", sw=0.5)
    v.rect(-DEB_P, ze - 0.3, L + 2 * DEB_P, 1.5, fill="#444", stroke="#111", sw=0.5)
    v.line(-DEB_P, Z_TOP, L + DEB_P, Z_TOP, stroke="#111", sw=2)
    # textes
    v.text(4, Z_PL + H_MUR - 6, "AVANT", size=6.5, weight="bold", fill="#555")
    v.text(L - 4, Z_PL + H_MUR - 6, "ARRIÈRE", size=6.5, weight="bold", fill="#555", anchor="end")
    v.text(56, Z_PL + FEN_Z[1] + 4, "fenêtre 24 × 12", size=5.8, anchor="middle")
    v.text(60, 2.4, "patin 2×6 traité + semelle UHMW", size=5.5, anchor="middle")
    v.text(-30, 21, "timon rigide", size=5.8, anchor="middle")
    v.text(ATT, 18, "attelage", size=5.5, anchor="middle")
    v.text(L / 2, Z_TOP + 3, "faîte", size=5.5, anchor="middle", fill="#555")
    # cotes
    v.dim(0, 0, L, 0, 22)
    v.dim(ATT - 3, 0, L, 0, 42, f"{fi(L - ATT + 3)} avec timon")
    v.dim(L + DEB_P, 0, L + DEB_P, Z_TOP, 44, f"{fi(Z_TOP)} hors-tout")
    v.dim(L, 0, L, Z_PL, 14, size=6)
    v.dim(L, Z_PL, L, Z_PL + H_MUR, 14, size=6)
    v.dim(FEN_COTE[0], Z_PL, FEN_COTE[0], Z_PL + FEN_Z[0], -10, size=6)
    v.dim(-NEZ - 1.5, 0, 0, 0, 22, size=5.5)
    notes(f, 40, 478, "PATINS ET REMORQUAGE", [
        "Patins 2×6 traité sur chant, sous les rives (voie 4'-10 1/2\"). Nez relevé de 12 po découpé à la scie sauteuse ; semelle UHMW 1/4 po vissée dessous : glisse mieux et ne colle pas sur la glace.",
        "Timon en A rigide, tube acier carré 1 1/2 po boulonné aux patins : la cabane ne peut pas rattraper la motoneige au freinage. Anneau pour la goupille d'attelage + chaîne de sécurité.",
    ], larg=150, inter=9)
    return f


# =============================================================================
def pignon(v, avant=True):
    """Pignon vu de face. u = Y (avant) ou B - Y (arrière)."""
    glace(v, -14, B + 14)
    # patins
    for y0, y1 in PATIN_Y:
        if avant:
            v.rect(y0, 0, 1.5, Z_P + 7.5, fill="url(#bois)", stroke="#111", sw=0.7)
        else:
            v.rect(y0, 0, 1.5, Z_P, fill="url(#bois)", stroke="#111", sw=0.7)
    v.rect(0, Z_P, B, CAD, fill="#e9dcc3", stroke="#111", sw=0.6)
    v.rect(0, Z_P + CAD, B, CP, fill="#d8c39a", stroke="#111", sw=0.4)
    pent = [(0, Z_PL), (B, Z_PL), (B, Z_PL + H_MUR), (B / 2, zr(B / 2)), (0, Z_PL + H_MUR)]
    v.poly(pent, fill="#f7f4ee", stroke="#111", sw=1)
    v.poly([(-DEB_E, zr(-DEB_E)), (B / 2, zr(B / 2)), (B + DEB_E, zr(B + DEB_E)), (B + DEB_E, zr(B + DEB_E) + TOIT),
            (B / 2, Z_TOP), (-DEB_E, zr(-DEB_E) + TOIT)], fill="#7d858a", stroke="#111", sw=0.8)
    if avant:
        v.rect(FEN_AV[0], Z_PL + FEN_Z[0], 16, 12, fill="#dbeaf5", stroke="#111", sw=1)
        v.line(FEN_AV[0], Z_PL + FEN_Z[0], FEN_AV[1], Z_PL + FEN_Z[1], stroke="#9cc", sw=0.4)
        gz = Z_PL + 66
        v.rect(B / 2 - 5, gz, 10, 5, fill="#444", stroke="#111", sw=0.5)
        for k in range(1, 4):
            v.line(B / 2 - 4, gz + k * 1.25, B / 2 + 4, gz + k * 1.25, stroke="#bbb", sw=0.4)
        # timon au premier plan
        v.poly([(0.75, Z_P + 6.5), (B / 2, 13), (B - 0.75, Z_P + 6.5)], close=False, stroke="#333", sw=2)
        v.circle(B / 2, 12.2, 2.4, stroke="#111", sw=1.2, fill="#fff")
        v.text((FEN_AV[0] + FEN_AV[1]) / 2, Z_PL + FEN_Z[1] + 3.5, "fenêtre 16 × 12", size=5.6, anchor="middle")
        v.text(B / 2, gz + 8.5, "ventilation haute", size=5.4, anchor="middle")
        v.text(3, -5, "côté banc", size=5.6, fill="#555")
    else:
        u0, u1 = B - PORTE_Y[1], B - PORTE_Y[0]
        v.rect(u0, Z_PL, u1 - u0, H_PORTE, fill="#fff", stroke="#111", sw=1)
        v.rect(u0 + 3, Z_PL + 3, u1 - u0 - 6, H_PORTE - 6, stroke="#999", sw=0.4)
        v.rect(u0 + 7, Z_PL + 4, 10, 4, fill="#444", stroke="#111", sw=0.4)
        v.circle(u1 - 3, Z_PL + 32, 0.9, fill="#111")
        for zz in (6, 30, 54):
            v.rect(u0, Z_PL + zz - 2, 1.2, 4, fill="#111", stroke="none")
        v.text(B / 2, Z_PL + 11, "grille basse", size=5.2, anchor="middle")
        v.text(B - 3, -5, "côté banc", size=5.6, fill="#555", anchor="end")


def f_pignons():
    f = Feuille(3, "Pignons avant et arrière")
    titre_vue(f, 40, 40, "PIGNON AVANT (timon)", "Échelle 1:24 (1/2 po = 1 pi)")
    titre_vue(f, 420, 40, "PIGNON ARRIÈRE (porte)", "Échelle 1:24 (1/2 po = 1 pi)")
    for x0, av in ((120, True), (500, False)):
        v = Vue(f, x0, 430, 24, flip=True)
        pignon(v, av)
        v.dim(0, 0, B, 0, 24)
        v.dim(-DEB_E, Z_TOP, B + DEB_E, Z_TOP, -14, f"{fi(B + 2 * DEB_E)} toit")
        v.dim(0, 0, 0, Z_PL, -14, size=6)
        v.dim(0, Z_PL, 0, Z_PL + H_MUR, -14, size=6)
        v.dim(B + DEB_E, 0, B + DEB_E, Z_TOP, 18, f"{fi(Z_TOP)} hors-tout", size=6.5)
        if not av:
            v.dim(B - PORTE_Y[1], Z_PL, B - PORTE_Y[0], Z_PL, 34, "24 po", size=6)
            v.dim(B - PORTE_Y[0], Z_PL, B - PORTE_Y[0], Z_PL + H_PORTE, 8, size=6)
    notes(f, 40, 488, "TOIT EN POINTE", [
        f"Pente 8:12, faîtière structurale 2×8 portée par les deux pignons : pas d'entraits, le centre reste dégagé ({fi(LIBRE_FAITE)} sous la faîtière, {fi(zr(B / 2) - Z_PL)} sous les chevrons).",
        "La neige glisse toute seule ; la tôle foncée chauffe au soleil. Débord de 4 po aux égouts et de 3 po aux pignons.",
    ], larg=150, inter=9)
    return f


# =============================================================================
def f_coupe():
    f = Feuille(4, "Coupe A-A")
    titre_vue(f, 40, 40, "COUPE A-A (vers l'arrière)", "Échelle 1:16 (3/4 po = 1 pi)")
    v = Vue(f, 110, 500, 16, flip=True)
    v.rect(-10, -8, B + 20, 8, fill="url(#glace)", stroke="none")
    v.line(-10, 0, B + 10, 0, stroke=BLEU, sw=1.1)
    tx, ty = TRAPPES[0]
    v.rect(ty + 1, -8, 10, 8, fill="#fff", stroke=BLEU, sw=0.6, dash="3,1.5")
    # patins coupés + semelles
    for y0, _ in PATIN_Y:
        v.rect(y0, UHMW, 1.5, PAT, fill="url(#hach)", stroke="#111", sw=0.8)
        v.rect(y0, 0, 1.5, UHMW, fill="#222", stroke="none")
    # traverse au-delà + rives coupées
    v.rect(1.5, Z_P, B - 3, CAD, fill="#f3ead8", stroke=BOIS, sw=0.6)
    for y0 in (0, B - 1.5):
        v.rect(y0, Z_P, 1.5, CAD, fill="url(#hach)", stroke="#111", sw=0.7)
    # plancher coupé (ouverture T1)
    for a, b in [(0, ty), (ty + 12, B)]:
        v.rect(a, Z_P + CAD, b - a, CP, fill="url(#hach)", stroke="#111", sw=0.7)
    v.poly([(ty, Z_PL), (ty - 0.3, Z_PL + 12), (ty + 0.4, Z_PL + 12), (ty + 0.75, Z_PL)], fill="#d8c39a", stroke="#111", sw=0.5)
    # murs coupés : CP ext 1/4 | 2x2 + XPS 1 po | panneau int. 1/4
    for x_ext, sg in ((0, 1), (B, -1)):
        lay = [(0.25, "#d8c39a"), (1.5, "url(#isol)"), (0.25, "#efe3c8")]
        x = x_ext
        for ep, fill in lay:
            v.rect(min(x, x + sg * ep), Z_PL, ep, H_MUR, fill=fill, stroke="#111", sw=0.5)
            x += sg * ep
        v.rect(min(x_ext + sg * 0.25, x_ext + sg * 1.75), Z_PL + H_MUR - 1.5, 1.5, 1.5, fill="url(#hach)", stroke="#111", sw=0.5)
    # chevrons (dans le plan de coupe), faîtière coupée, fourrures et tôle
    for sgn in (1, -1):
        y_e = -DEB_E if sgn == 1 else B + DEB_E
        ys = [y_e, B / 2]
        bas = [(y, zr(y)) for y in ys]
        haut = [(y, zr(y) + CHEV) for y in ys[::-1]]
        v.poly(bas + haut, fill="#f3ead8", stroke=BOIS, sw=0.7)
        v.poly([(y_e, zr(y_e) + CHEV), (B / 2, zr(B / 2) + CHEV), (B / 2, zr(B / 2) + CHEV + 0.75), (y_e, zr(y_e) + CHEV + 0.75)],
               fill="#c9b48a", stroke="#111", sw=0.4)
        v.poly([(y_e - 0.5, zr(y_e - 0.5) + TOIT - 0.3), (B / 2, Z_TOP - 0.3), (B / 2, Z_TOP), (y_e - 0.5, zr(y_e - 0.5) + TOIT)],
               fill="#555", stroke="#111", sw=0.4)
        yi = T if sgn == 1 else B - T
        v.poly([(yi, zr(yi) - 1.0), (B / 2 - sgn * 0.75, zr(B / 2) - 1.0), (B / 2 - sgn * 0.75, zr(B / 2)), (yi, zr(yi))],
               fill="url(#isol)", stroke="#111", sw=0.3)
    v.rect(B / 2 - 0.75, Z_FAITE - FAITE, 1.5, FAITE, fill="url(#hach)", stroke="#111", sw=0.7)
    # banc
    v.rect(T, Z_PL + H_BANC - 0.5, BANC, 0.5, fill="#d8c39a", stroke="#111", sw=0.6)
    v.rect(T + BANC - 0.5, Z_PL, 0.5, H_BANC - 0.5, fill="#d8c39a", stroke="#111", sw=0.6)
    # porte au-delà
    v.rect(PORTE_Y[0], Z_PL, 24, H_PORTE, stroke="#999", sw=0.6, dash="4,2")
    v.text(B / 2, Z_PL + H_PORTE / 2, "porte (au-delà)", size=6, anchor="middle", fill="#888")
    pastilles = [
        (B / 2 - 10, zr(B / 2 - 10) + TOIT - 0.15, 1, -6, -22),
        (B / 2 + 12, zr(B / 2 + 12) + CHEV + 0.4, 2, 10, -26),
        (12, zr(12) + 1.5, 3, -30, -10),
        (40, zr(40) - 0.5, 4, 18, 26),
        (B / 2, Z_FAITE - FAITE / 2, 5, 34, 6),
        (0.1, Z_PL + 40, 6, -26, 0),
        (1, Z_PL + 25, 7, -26, 0),
        (T + 7, Z_PL + H_BANC, 8, 0, -22),
        (44, Z_PL - 0.25, 9, -26, 22),
        (40, Z_P + 1.75, 10, 18, 24),
        (B - 0.75, 3, 11, 26, 0),
        (B - 0.75, 0.1, 12, 26, 16),
        (ty + 0.4, Z_PL + 8, 13, 26, -6),
        (ty + 6, -5, 14, 30, 4),
    ]
    for x, y, n, dx, dy in pastilles:
        callout(v, x, y, n, dx, dy)
    v.dim(0, 0, 0, Z_PL, -40, size=6)
    v.dim(0, Z_PL, 0, Z_PL + H_MUR, -40, size=6)
    v.dim(-DEB_E, 0, -DEB_E, Z_TOP, -62, f"{fi(Z_TOP)} hors-tout", size=6.5)
    v.dim(B / 2 + 6, Z_PL, B / 2 + 6, Z_FAITE - FAITE, 0, f"{fi(LIBRE_FAITE)} libre", size=6)
    v.dim(T, Z_PL + H_BANC, T + BANC, Z_PL + H_BANC, -10, "14 po", size=5.8)
    leg = [
        "Tôle prépeinte cal. 29 (ou aluminium, plus légère)",
        "Fourrures 1×3 @ 16 po",
        "Chevrons 2×3 @ 24 po c/c, débord 4 po",
        "Isolant XPS 1 po entre chevrons",
        "Faîtière structurale 2×8, portée par les pignons",
        "Revêtement CP 1/4 extérieur, peint",
        "Montants 2×2 @ 24 po + XPS 1 po + panneau 1/4",
        "Banc : dessus CP 1/2, devant CP 1/2",
        "Plancher CP 1/2 traité, collé-vissé",
        "Traverses 2×4 @ 16 po c/c (cadre sur chant)",
        "Patin 2×6 traité sur chant (coupé)",
        "Semelle de glisse UHMW 1/4 po",
        "Trappe 12 × 12 ouverte",
        "Trou dans la glace, tarière 8 à 10 po",
    ]
    x0, y0 = 470, 110
    f.text(x0, y0 - 16, "LÉGENDE", size=9, weight="bold")
    for i, t in enumerate(leg):
        y = y0 + i * 15
        f.add(f'<circle cx="{x0+6}" cy="{y-2.6}" r="6" fill="#fff" stroke="{ROUGE}" stroke-width="0.8"/>')
        f.text(x0 + 6, y, str(i + 1), size=6.5, anchor="middle", weight="bold", fill=ROUGE)
        f.text(x0 + 17, y, t, size=7.2)
    notes(f, 470, y0 + 14 * 15 + 16, "HAUTEURS", [
        f"Plancher à {fi(Z_PL)} de la glace : assez pour la neige, assez bas pour la stabilité.",
        f"Assis sur le banc, la tête passe sous le versant ({fi(zr(T) - Z_PL)} au mur). Debout au centre : {fi(LIBRE_FAITE)}.",
    ], larg=52, inter=9.5)
    return f


# =============================================================================
def f_ossature():
    f = Feuille(5, "Ossature")
    titre_vue(f, 40, 40, "CADRE DE PLANCHER, PATINS ET TIMON (vue de dessus)", "Échelle 1:24 — contreplaqué retiré")
    v = Vue(f, 236, 112, 24)
    for y0, y1 in PATIN_Y:
        v.rect(-NEZ, y0, NEZ, y1 - y0, fill="url(#bois)", stroke="#111", sw=0.6)
    v.rect(0, 0, L, 1.5, **bois)
    v.rect(0, B - 1.5, L, 1.5, **bois)
    xs = [0] + [16 * n - 0.75 for n in range(1, 8)] + [L - 1.5]
    for x in xs:
        v.rect(x, 1.5, 1.5, B - 3, **bois)
    for tx, ty in TRAPPES:
        x0 = 16 * (tx // 16) + 0.75
        x1 = 16 * (tx // 16 + 1) - 0.75
        v.rect(x0, ty - 1.5, x1 - x0, 1.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
        v.rect(x0, ty + 12, x1 - x0, 1.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke=BLEU, sw=0.8)
    ya, yb = 0.75, B - 0.75
    v.poly([(-NEZ, ya), (ATT + 3, B / 2), (-NEZ, yb)], close=False, stroke="#333", sw=2.2)
    k = (-24 + NEZ) / (ATT + 3 + NEZ)
    v.line(-24, ya + (B / 2 - ya) * k, -24, yb - (yb - B / 2) * k, stroke="#333", sw=1.6)
    v.circle(ATT, B / 2, 3, stroke="#333", sw=1.2)
    v.dim(0, 0, L, 0, -16)
    v.dim(L, 0, L, B, 16)
    for n in range(0, 2):
        v.dim(16 * n, B, 16 * (n + 1), B, 14, "16 po c/c" if n == 1 else fi(16), size=5.6)
    v.dim(ATT + 3, B, 0, B, 14, size=5.6)
    notes(f, 628, 112, "CADRE", [
        "2×4 traité sur chant, rives de 10 pi, traverses @ 16 po.",
        "Chevêtres 2×4 autour des 3 trappes.",
        "Patins vissés sous les rives : tire-fonds 3/8 × 5 @ 16 po.",
        "Timon boulonné dans le nez des patins (2 boulons 3/8 par côté) + traverse de raidissement.",
     ], larg=27, size=6.4, inter=8.3)

    # --- mur latéral côté allée ----------------------------------------------
    titre_vue(f, 40, 322, "MUR LATÉRAL (côté allée, vu de l'extérieur)", "Échelle 1:32 — 2×2 @ 24 po c/c")
    v = Vue(f, 70, 530, 32, flip=True)
    v.rect(0, 0, L, 1.5, **bois)
    v.rect(0, H_MUR - 1.5, L, 1.5, **bois)
    w0, w1 = FEN_COTE
    top = lambda x: H_MUR - 1.5

    def mt(x, z0, z1):
        v.rect(x, z0, 1.5, z1 - z0, **bois)
    for x in [0] + [24 * n - 0.75 for n in range(1, 5)] + [L - 1.5]:
        if w0 - 1.5 < x < w1:
            continue
        mt(x, 1.5, H_MUR - 1.5)
    mt(w0 - 1.5, 1.5, H_MUR - 1.5)
    mt(w1, 1.5, H_MUR - 1.5)
    v.rect(w0, FEN_Z[0] - 1.5, w1 - w0, 1.5, **bois)
    v.rect(w0, FEN_Z[1], w1 - w0, 3.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    mt(47.25, 1.5, FEN_Z[0] - 1.5)
    mt(47.25, FEN_Z[1] + 3.5, H_MUR - 1.5)
    v.dim(0, 0, L, 0, 12)
    v.dim(0, 0, 0, H_MUR, -10, size=6)
    v.dim(w0, FEN_Z[0], w1, FEN_Z[0], -10, "ouv. brute 24 × 12", size=5.4)
    v.text(4, -9, "AVANT", size=6, weight="bold", fill="#555")
    v.text(L - 4, -9, "ARRIÈRE", size=6, weight="bold", fill="#555", anchor="end")

    # --- pignon arrière --------------------------------------------------------
    titre_vue(f, 470, 322, "PIGNON ARRIÈRE (vu de l'intérieur)", "Échelle 1:32 — porte et poteau de faîte")
    v = Vue(f, 540, 530, 32, flip=True)
    yl, yrr = 1.75, B - 1.75
    ztop = lambda y: zr(y) - Z_PL
    p0, p1 = PORTE_Y[0] - 1, PORTE_Y[1] + 1      # ouverture brute 26 po
    v.rect(yl, 0, p0 - 1.5 - 1.5 - yl, 1.5, **bois)
    v.rect(p1 + 3, 0, yrr - p1 - 3, 1.5, **bois)
    v.poly([(yl, ztop(yl) - 1.5), (B / 2, ztop(B / 2) - 1.5), (B / 2, ztop(B / 2)), (yl, ztop(yl))], **bois)
    v.poly([(B / 2, ztop(B / 2) - 1.5), (yrr, ztop(yrr) - 1.5), (yrr, ztop(yrr)), (B / 2, ztop(B / 2))], **bois)

    def mtp(y, z0, z1f, w=1.5):
        v.poly([(y, z0), (y + w, z0), (y + w, z1f(y + w)), (y, z1f(y))], **bois)
    hautp = lambda y: ztop(y) - 1.5
    for y in (yl, 8, yrr - 1.5, B - 9.5):
        mtp(y, 1.5 if y in (yl, yrr - 1.5) or True else 0, hautp)
    mtp(p0 - 3, 0, hautp)
    mtp(p1 + 1.5, 0, hautp)
    mtp(p0 - 1.5, 0, lambda y: H_PORTE + 1)
    mtp(p1, 0, lambda y: H_PORTE + 1)
    v.rect(p0 - 1.5, H_PORTE + 1, p1 - p0 + 3, 3.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    z_f = Z_FAITE - FAITE - Z_PL
    v.rect(B / 2 - 1.75, H_PORTE + 4.5, 3.5, z_f - H_PORTE - 4.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    v.rect(B / 2 - 0.75, z_f, 1.5, FAITE, fill="url(#hach)", stroke="#111", sw=0.6)
    v.dim(p0, 0, p1, 0, 12, "26 po ouv. brute", size=5.4)
    v.dim(p1, 0, p1, H_PORTE + 1, 20, "61 po", size=5.4)
    v.text(B / 2 + 4, z_f + 5, "faîtière 2×8", size=5.2)
    v.text(B / 2 + 3, H_PORTE + 12, "poteau 2×4", size=5.2)
    v.text(B / 2, H_PORTE + 2.4, "linteau 2×4 doublé", size=4.8, anchor="middle")
    return f


# =============================================================================
MATERIAUX = [
    ("BASE, PATINS, TIMON", None),
    ("Patins", "2 × 2×6 × 12 pi traité"),
    ("Semelles de glisse", "2 × UHMW 1/4 × 1 1/2 po × 11 pi"),
    ("Cadre de plancher + chevêtres", "8 × 2×4 × 10 pi traité"),
    ("Plancher", "2 × CP 1/2 po 4×8 traité"),
    ("Timon en A", "12 pi tube acier 1 1/2 po + anneau + chaîne"),
    ("MURS ET PIGNONS", None),
    ("Montants, lisses, sablières", "≈ 24 × 2×2 × 8 pi"),
    ("Poteau de faîte, linteau, rives", "3 × 2×4 × 8 pi"),
    ("Revêtement extérieur", "6 × CP 1/4 po 4×8"),
    ("Panneau intérieur (option)", "5 × CP 1/4 po ou panneau 1/8"),
    ("TOIT", None),
    ("Faîtière structurale", "1 × 2×8 × 12 pi"),
    ("Chevrons @ 24 po", "6 × 2×3 × 8 pi"),
    ("Fourrures", "6 × 1×3 × 12 pi"),
    ("Tôle", "8 × 3 pi × 3'-6\" + faîtière + rives"),
    ("ISOLATION, INTÉRIEUR", None),
    ("Isolant XPS 1 po", "≈ 14 panneaux 2×8 pi"),
    ("Banc + 3 couvercles de trappes", "1 × CP 1/2 4×8 + 3 × 2×2 × 8"),
    ("Plaque incombustible", "panneau ciment 1/2 po 2×3 pi"),
    ("OUVERTURES", None),
    ("Porte 24 × 60 maison", "3 pentures, loquet, moraillon"),
    ("Fenêtres polycarbonate 1/4", "24 × 12 et 16 × 12"),
    ("Grilles de ventilation", "2 × 4 × 10 po réglables"),
    ("QUINCAILLERIE, SÉCURITÉ", None),
    ("Vis ext. 2 1/2 et 1 1/4 po", "≈ 5 lb + 2 lb"),
    ("Tire-fonds 3/8 × 5 + boulons timon", "16 + 4"),
    ("Vis à tôle à rondelle", "≈ 150"),
    ("Détecteur CO, extincteur ABC", "1 + 1"),
]

# (poste, livres) — masses volumiques courantes du bois d'œuvre et des panneaux
POIDS = [
    ("Patins + semelles", 48),
    ("Cadre de plancher 2×4 traité", 112),
    ("Plancher CP 1/2 traité", 75),
    ("Ossature murs 2×2 + poteau, linteau", 107),
    ("Revêtement CP 1/4", 108),
    ("Isolant XPS", 28),
    ("Faîtière, chevrons, fourrures", 79),
    ("Tôle et moulures", 55),
    ("Banc et couvercles", 54),
    ("Porte, fenêtres, grilles", 25),
    ("Timon acier + attelage", 25),
    ("Quincaillerie, peinture", 25),
]


def f_materiaux():
    f = Feuille(6, "Matériaux et poids")
    x, y = 40, 44
    f.text(x, y, "LISTE DE MATÉRIAUX (estimation)", size=11, weight="bold")
    f.text(x, y + 11, "Ajouter 10 % de perte. Bois traité pour tout ce qui touche la neige.", size=6.5, fill="#555")
    y += 26
    for nom, qte in MATERIAUX:
        if qte is None:
            f.add(f'<rect x="{x-2}" y="{y-8}" width="364" height="11" fill="#eef3f7"/>')
            f.text(x, y, nom, size=7, weight="bold", fill=BLEU)
        else:
            f.text(x + 4, y, nom, size=6.8)
            f.text(x + 360, y, qte, size=6.8, anchor="end")
            f.add(f'<line x1="{x}" y1="{y+2.5}" x2="{x+360}" y2="{y+2.5}" stroke="#e3e3e3" stroke-width="0.4"/>')
        y += 15.2

    x, y = 440, 44
    total = sum(p for _, p in POIDS)
    f.text(x, y, "POIDS ESTIMÉ", size=11, weight="bold")
    f.text(x, y + 11, "Calcul approximatif, à confirmer à la pesée.", size=6.5, fill="#555")
    y += 28
    mx = max(p for _, p in POIDS)
    for nom, p in POIDS:
        f.text(x, y, nom, size=6.8)
        f.add(f'<rect x="{x+150}" y="{y-7}" width="{p / mx * 120:.1f}" height="8" fill="{BLEU}" opacity="0.75"/>')
        f.text(x + 310, y, f"{p} lb", size=6.8, anchor="end")
        y += 13
    f.add(f'<line x1="{x}" y1="{y-6}" x2="{x+310}" y2="{y-6}" stroke="#111" stroke-width="0.8"/>')
    f.text(x, y + 6, "TOTAL TEL QUE DESSINÉ", size=8, weight="bold")
    f.text(x + 310, y + 6, f"≈ {total} lb ({round(total * 0.4536 / 5) * 5} kg)", size=8, weight="bold", anchor="end")
    y += 30
    y = notes(f, x, y, "POUR ALLÉGER (≈ 600 lb / 270 kg)", [
        "Tôle d'aluminium au toit au lieu de l'acier : environ 30 lb de moins.",
        "Cadre de plancher en 2×3 non traité, peint : environ 35 lb de moins.",
        "Pas de panneau intérieur ; bancs en CP 3/8 : environ 25 lb de moins.",
        "Revêtement en panneau d'aluminium ou CP 3/16 : environ 30 lb de moins.",
    ], larg=60, size=6.8, inter=9)
    notes(f, x, y + 6, "VERSION 5 × 12 PI", [
        "Même coupe, 2 pi de plus : 4 trappes au lieu de 3, environ 130 lb de plus. Toujours sous 8'-0\" de haut.",
    ], larg=60, size=6.8, inter=9)
    return f


if __name__ == "__main__":
    for fe in (f_plan(), f_cote(), f_pignons(), f_coupe(), f_ossature(), f_materiaux()):
        (ICI / f"feuille-{fe.num}.svg").write_text(fe.svg(), encoding="utf-8")
    print("hors-tout", fi(Z_TOP), "| libre faîtière", fi(LIBRE_FAITE), "| total", sum(p for _, p in POIDS), "lb")
