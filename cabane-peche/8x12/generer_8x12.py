#!/usr/bin/env python3
"""Cabane à pêche 8 x 12 pi, toit monopente 1 1/2:12, tirée à la motoneige.

6 feuilles SVG (lettre paysage) dans ce dossier, puis :
  node ../exporter.js . Plans_cabane_8x12_monopente.pdf
Cotes en pouces réels. Réutilise les outils de ../generer_plans.py.
"""
import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent))
import generer_plans as g  # noqa: E402
from generer_plans import Feuille, Vue, titre_vue, notes, callout  # noqa: E402

_fi = g.fi


def fi(po):
    t = _fi(po)
    return t[3:] if t.startswith("0'-") else t


g.fi = fi
g.PROJET = "Cabane à pêche 8 × 12 pi monopente — motoneige"
g.NB_FEUILLES = 6
g.DATE = "2026-11-08"

# --- Paramètres (pouces) ----------------------------------------------------
L, B = 144, 96            # longueur (X, 0 = avant/timon) et largeur (Y, 0 = côté haut)
T = 3.0                   # mur : CP 1/4 + 2x3 + panneau 1/4
UHMW, PAT, CAD, CP = 0.25, 5.5, 3.5, 0.5
Z_P = UHMW + PAT
Z_PL = Z_P + CAD + CP     # 9.75
H_HAUT, H_BAS = 84, 72    # murs : côté haut (Y=0) et côté bas (Y=B)
PENTE = (H_HAUT - H_BAS) / B          # 1 1/2:12
DEB_E, DEB_P = 6, 4       # débords : égouts (côtés) et bouts
CHEV = 3.6                # chevron 2x4 mesuré à la verticale
TOIT = 4.7                # chevron + fourrure + tôle
PATIN_Y = [(0, 1.5), (47.25, 48.75), (94.5, 96)]
NEZ = 12
ATT = -60                 # anneau d'attelage
TR_X = [34, 66, 98]       # trappes : X de départ (entre traverses @ 16 po)
TR_Y = [21, 63]           # rangée côté haut, rangée côté bas
PORTE_X = (112, 140)      # porte 28 po dans le mur côté haut
H_PORTE = 72
FEN_HAUT = (40, 64)       # fenêtre mur côté haut (X)
FEN_BAS = (56, 80)        # fenêtre mur côté bas (X)
FEN_AR = (36, 60)         # fenêtre mur arrière (Y)
FEN_AV = (60, 76)         # fenêtre mur avant (Y), 16 po
BANC, H_BANC = 14, 16
BLEU, ROUGE, BOIS = "#1f5f8b", "#c0392b", "#7a5a2a"
bois = dict(fill="#f3ead8", stroke=BOIS, sw=0.6)


def wtop(y):
    """Dessus de sablière (au-dessus du plancher) selon Y."""
    return H_HAUT - PENTE * y


def zr(y):
    return Z_PL + wtop(y)


Z_TOP = zr(-DEB_E) + TOIT


def glace(v, x1, x2, prof=8):
    v.rect(x1, -prof, x2 - x1, prof, fill="url(#glace)", stroke="none")
    v.line(x1, 0, x2, 0, stroke=BLEU, sw=1)


def nez_patin():
    return [(L, 0), (L, Z_P), (2, Z_P), (-5, Z_P + 2.5), (-10, Z_P + 6.5), (-NEZ, Z_P + 7.5),
            (-NEZ - 1.5, Z_P + 5.5), (-9, Z_P + 1), (-3, 1.2), (6, 0)]


def trappes():
    n = 0
    for ty in TR_Y:
        for tx in TR_X:
            n += 1
            yield n, tx, ty


def wrap(txt, larg):
    mots, cur, out = txt.split(), "", []
    for m in mots:
        if len(cur) + len(m) + 1 > larg:
            out.append(cur); cur = m
        else:
            cur = (cur + " " + m).strip()
    out.append(cur)
    return out


# =============================================================================
def f_plan():
    f = Feuille(1, "Vue en plan — aménagement")
    titre_vue(f, 40, 40, "VUE EN PLAN — AMÉNAGEMENT", "Échelle 1:24 (1/2 po = 1 pi) · avant (timon) à gauche")
    v = Vue(f, 230, 168, 24)
    for y0, y1 in PATIN_Y:
        v.rect(-NEZ, y0, L + NEZ, y1 - y0, stroke=BLEU, sw=0.6, dash="5,2.5")
    ya, yb = 0.75, B - 0.75
    v.poly([(-NEZ, ya), (ATT + 3, B / 2), (-NEZ, yb)], close=False, stroke="#333", sw=1.4)
    k = (-24 + NEZ) / (ATT + 3 + NEZ)
    v.line(-24, ya + (B / 2 - ya) * k, -24, yb - (yb - B / 2) * k, stroke="#333", sw=1)
    v.line(-NEZ, B / 2, ATT + 3, B / 2, stroke="#333", sw=1)
    v.circle(ATT, B / 2, 3, stroke="#333", sw=1.2)
    v.text(-38, B / 2 - 4, "TIMON EN A", size=6.5, anchor="middle", weight="bold")
    v.text(-38, B / 2 + 7, "tube acier 1 1/2 po", size=5.5, anchor="middle")
    v.text(ATT, B / 2 + 9, "anneau", size=5.5, anchor="middle")
    # murs
    o = [(0, 0), (L, 0), (L, B), (0, B)]
    i = [(T, T), (L - T, T), (L - T, B - T), (T, B - T)]
    pts = lambda P: " ".join(f"{a:.2f},{b:.2f}" for a, b in (v.P(*p) for p in P))
    f.add(f'<path d="M{pts(o)}Z M{pts(i[::-1])}Z" fill="#bbb" stroke="#111" stroke-width="1" fill-rule="evenodd"/>')
    # porte (mur côté haut), ouvre vers l'extérieur
    p0, p1 = PORTE_X
    v.rect(p0, -0.2, p1 - p0, T + 0.4, fill="#fff", stroke="none")
    v.line(p0, 0, p0, T, sw=1); v.line(p1, 0, p1, T, sw=1)
    w = p1 - p0
    v.rect(p1 - 1.2, -w, 1.2, w, fill="#fff", stroke="#111", sw=0.8)
    v.arc(p1, 0, w, p0, 0, p1, -w)
    v.text(p0 - 3, -14, "PORTE 28 × 72 po", size=6, weight="bold", anchor="end")
    v.text(p0 - 3, -9, "ouvre vers l'ext.", size=5.5, italic=True, anchor="end")
    # fenêtres
    for (a, b_), y0 in ((FEN_HAUT, 0), (FEN_BAS, B - T)):
        v.rect(a, y0, b_ - a, T, fill="#fff", stroke="#111", sw=0.6)
        v.line(a, y0 + T / 2, b_, y0 + T / 2, sw=0.5)
    for (a, b_), x0 in ((FEN_AR, L - T), (FEN_AV, 0)):
        v.rect(x0, a, T, b_ - a, fill="#fff", stroke="#111", sw=0.6)
        v.line(x0 + T / 2, a, x0 + T / 2, b_, sw=0.5)
    # bancs
    v.rect(T, T, p0 - 4 - T, BANC, fill="#f3ead8", stroke=BOIS, sw=0.7)
    v.rect(T, B - T - BANC, L - 2 * T, BANC, fill="#f3ead8", stroke=BOIS, sw=0.7)
    v.text(56, T + BANC / 2 + 1.5, "BANC prof. 14 po · haut. 16 po", size=6.2, anchor="middle")
    v.text(72, B - T - BANC / 2 + 1.5, "BANC prof. 14 po · haut. 16 po · rangement dessous", size=6.2, anchor="middle")
    for n, tx, ty in trappes():
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke=BLEU, sw=1)
        v.circle(tx + 6, ty + 6, 4, stroke=BLEU, dash="2,1.5")
        v.text(tx + 6, ty + 7.6, f"T{n}", size=6.5, anchor="middle", weight="bold", fill=BLEU)
    v.text(88, B / 2 - 4, "ALLÉE 30 po", size=7, anchor="middle", fill="#777")
    # chauffage
    v.rect(T, 35, 22, 26, stroke=ROUGE, sw=0.5, dash="3,2")
    v.rect(T + 1, 40, 12, 16, fill="#fde2df", stroke=ROUGE, sw=0.9)
    v.text(T + 7, 48.5, "CHAUF.", size=5.2, anchor="middle", weight="bold", fill=ROUGE)
    # ventilation haute (mur avant, côté haut)
    v.rect(0, 8, T, 10, fill="#444", stroke="#111", sw=0.5)
    # coupe A-A
    xa = 40
    v.line(xa, -7, xa, B + 7, stroke=ROUGE, sw=0.7, dash="10,3,2,3")
    for y_ in (-7, B + 7):
        a, b = v.P(xa, y_)
        f.add(f'<polygon points="{a:.1f},{b-4:.1f} {a:.1f},{b+4:.1f} {a+9:.1f},{b:.1f}" fill="{ROUGE}"/>')
        f.text(a - 7, b + 3, "A", size=9, anchor="middle", weight="bold", fill=ROUGE)
    v.text(56, T + BANC + 2.6, "CÔTÉ HAUT (mur 7'-0\")", size=5.2, anchor="middle", fill="#555")
    v.text(L / 2, B - T - BANC - 2, "CÔTÉ BAS (mur 6'-0\")", size=6.3, anchor="middle", fill="#555")
    v.text(-2, B + 9, "AVANT", size=6.5, weight="bold", fill="#555", anchor="end")
    v.text(L + 2, B + 9, "ARRIÈRE", size=6.5, weight="bold", fill="#555")
    # cotes
    for a, b_ in [(0, 34), (34, 46), (46, 66), (66, 78), (78, 98), (98, 110), (110, L)]:
        v.dim(a, B, b_, B, 34, size=5.8)
    v.dim(0, B, L, B, 50, f"{fi(L)}  (3,66 m)")
    v.dim(ATT - 3, B, L, B, 66, f"{fi(L - ATT + 3)} hors-tout avec timon")
    v.dim(L, 0, L, B, 52, f"{fi(B)}  (2,44 m)")
    for a, b_ in [(0, 21), (21, 33), (33, 63), (63, 75), (75, B)]:
        v.dim(L, a, L, b_, 26, size=5.8)
    return f


# =============================================================================
def f_cote():
    f = Feuille(2, "Élévation côté haut")
    titre_vue(f, 40, 40, "ÉLÉVATION CÔTÉ HAUT (porte)", "Échelle 1:24 (1/2 po = 1 pi) · vue de l'extérieur, avant à droite")
    v = Vue(f, 70, 420, 24, flip=True)
    U = lambda x: L - x                    # vue depuis le côté haut : l'avant est à droite
    glace(v, -14, L - ATT + 8)
    v.poly([(U(x), z) for x, z in nez_patin()], fill="url(#bois)", stroke="#111", sw=0.8)
    v.rect(0, 0, L - 6, UHMW, fill="#222", stroke="none")
    v.poly([(U(-NEZ + 1), Z_P + 6.5), (U(ATT + 3), 13), (U(ATT + 3), 11.5), (U(-NEZ + 1), Z_P + 4.5)], fill="#666", stroke="#111", sw=0.6)
    v.circle(U(ATT), 12.2, 2.6, stroke="#111", sw=1.2)
    v.rect(0, Z_P, L, CAD, fill="#e9dcc3", stroke="#111", sw=0.6)
    v.rect(0, Z_P + CAD, L, CP, fill="#d8c39a", stroke="#111", sw=0.4)
    v.rect(0, Z_PL, L, H_HAUT, fill="#f7f4ee", stroke="#111", sw=1)
    for u in (48, 96):
        v.line(u, Z_PL, u, Z_PL + H_HAUT, stroke="#aaa", sw=0.5)
    # porte
    u0, u1 = U(PORTE_X[1]), U(PORTE_X[0])
    v.rect(u0, Z_PL, u1 - u0, H_PORTE, fill="#fff", stroke="#111", sw=1)
    v.rect(u0 + 3, Z_PL + 3, u1 - u0 - 6, H_PORTE - 6, stroke="#999", sw=0.4)
    v.rect(u0 + 9, Z_PL + 4, 10, 4, fill="#444", stroke="#111", sw=0.4)
    v.circle(u1 - 3, Z_PL + 36, 0.9, fill="#111")
    for zz in (8, 36, 64):
        v.rect(u0, Z_PL + zz - 2, 1.2, 4, fill="#111", stroke="none")
    # fenêtre
    a, b = U(FEN_HAUT[1]), U(FEN_HAUT[0])
    v.rect(a, Z_PL + 36, b - a, 12, fill="#dbeaf5", stroke="#111", sw=1)
    v.line(a, Z_PL + 36, b, Z_PL + 48, stroke="#9cc", sw=0.4)
    # bord du toit (égout côté haut)
    ze = zr(-DEB_E)
    v.rect(-DEB_P, ze, L + 2 * DEB_P, TOIT, fill="#7d858a", stroke="#111", sw=0.8)
    v.text(U(4), Z_PL + H_HAUT - 6, "AVANT", size=6.5, weight="bold", fill="#555", anchor="end")
    v.text(U(L - 4), Z_PL + H_HAUT - 6, "ARRIÈRE", size=6.5, weight="bold", fill="#555")
    v.text((a + b) / 2, Z_PL + 51, "fenêtre 24 × 12", size=5.8, anchor="middle")
    v.text((u0 + u1) / 2, Z_PL + 11, "grille basse", size=5.2, anchor="middle")
    v.text(72, 2.4, "patin 2×6 traité + semelle UHMW", size=5.5, anchor="middle")
    v.text(U(-34), 21, "timon rigide", size=5.8, anchor="middle")
    v.dim(0, 0, L, 0, 22)
    v.dim(0, 0, U(ATT - 3), 0, 42, f"{fi(L - ATT + 3)} avec timon")
    v.dim(-DEB_P, 0, -DEB_P, Z_TOP, -30, f"{fi(Z_TOP)} hors-tout")
    v.dim(0, 0, 0, Z_PL, -12, size=6)
    v.dim(L, Z_PL, L, Z_PL + H_HAUT, 12, size=6)
    v.dim(u0, Z_PL + H_PORTE, u1, Z_PL + H_PORTE, -10, "28 po", size=6)
    v.dim(u1, Z_PL, u1, Z_PL + H_PORTE, 10, size=6)
    v.dim(b, Z_PL, b, Z_PL + 36, 10, size=6)
    notes(f, 40, 488, "TOIT MONOPENTE 1 1/2:12", [
        f"Le toit descend du côté haut ({fi(H_HAUT)}) vers le côté bas ({fi(H_BAS)}) : 1 1/2 po par pied sur 8 pi, soit 12 po d'écart. La neige et l'eau partent du côté bas, loin de la porte. Pente faible : poser la tôle avec ruban scellant aux recouvrements et vérifier la pente minimale du fabricant.",
        "Chevrons 2×4 @ 24 po qui portent d'un mur à l'autre (pas de faîte), débord de 6 po aux deux égouts et de 4 po aux bouts.",
    ], larg=150, inter=9)
    return f


# =============================================================================
def bout(v, avant=True):
    """Mur d'about vu de l'extérieur. Avant : u = Y. Arrière : u = B - Y."""
    U = (lambda y: y) if avant else (lambda y: B - y)
    glace(v, -16, B + 16)
    for y0, y1 in PATIN_Y:
        a, b = sorted((U(y0), U(y1)))
        v.rect(a, 0, 1.5, (Z_P + 7.5) if avant else Z_P, fill="url(#bois)", stroke="#111", sw=0.7)
    v.rect(0, Z_P, B, CAD, fill="#e9dcc3", stroke="#111", sw=0.6)
    v.rect(0, Z_P + CAD, B, CP, fill="#d8c39a", stroke="#111", sw=0.4)
    v.poly([(U(0), Z_PL), (U(B), Z_PL), (U(B), zr(B)), (U(0), zr(0))], fill="#f7f4ee", stroke="#111", sw=1)
    v.poly([(U(-DEB_E), zr(-DEB_E)), (U(B + DEB_E), zr(B + DEB_E)), (U(B + DEB_E), zr(B + DEB_E) + TOIT), (U(-DEB_E), zr(-DEB_E) + TOIT)],
           fill="#7d858a", stroke="#111", sw=0.8)
    if avant:
        a, b = FEN_AV
        v.rect(a, Z_PL + 36, b - a, 12, fill="#dbeaf5", stroke="#111", sw=1)
        v.line(a, Z_PL + 36, b, Z_PL + 48, stroke="#9cc", sw=0.4)
        v.rect(8, Z_PL + 72, 10, 4, fill="#444", stroke="#111", sw=0.5)
        v.text(13, Z_PL + 68, "vent. haute", size=5.4, anchor="middle")
        v.poly([(0.75, Z_P + 6.5), (B / 2, 13), (B - 0.75, Z_P + 6.5)], close=False, stroke="#333", sw=2)
        v.circle(B / 2, 12.2, 2.4, stroke="#111", sw=1.2, fill="#fff")
        v.text((a + b) / 2, Z_PL + 51, "fenêtre 16 × 12", size=5.6, anchor="middle")
        v.text(2, -5.5, "côté haut", size=5.6, fill="#555")
        v.text(B - 2, -5.5, "côté bas", size=5.6, fill="#555", anchor="end")
    else:
        a, b = U(FEN_AR[1]), U(FEN_AR[0])
        v.rect(a, Z_PL + 40, b - a, 12, fill="#dbeaf5", stroke="#111", sw=1)
        v.line(a, Z_PL + 40, b, Z_PL + 52, stroke="#9cc", sw=0.4)
        v.text((a + b) / 2, Z_PL + 55, "fenêtre 24 × 12", size=5.6, anchor="middle")
        v.text(2, -5.5, "côté bas", size=5.6, fill="#555")
        v.text(B - 2, -5.5, "côté haut", size=5.6, fill="#555", anchor="end")


def f_bouts():
    f = Feuille(3, "Élévations avant et arrière")
    titre_vue(f, 40, 40, "ÉLÉVATION AVANT (timon)", "Échelle 1:24 (1/2 po = 1 pi)")
    titre_vue(f, 420, 40, "ÉLÉVATION ARRIÈRE", "Échelle 1:24 (1/2 po = 1 pi)")
    for x0, av in ((70, True), (432, False)):
        v = Vue(f, x0, 430, 24, flip=True)
        bout(v, av)
        v.dim(0, 0, B, 0, 24)
        v.dim(-DEB_E, Z_TOP + 1, B + DEB_E, Z_TOP + 1, -14, f"{fi(B + 2 * DEB_E)} toit")
        hi, lo = (0, B) if av else (B, 0)
        v.dim(hi, Z_PL, hi, Z_PL + H_HAUT, -12 if av else 12, size=6)
        v.dim(lo, Z_PL, lo, Z_PL + H_BAS, 12 if av else -12, size=6)
        v.dim(hi, 0, hi, Z_PL, -12 if av else 12, size=6)
    notes(f, 40, 488, "ABOUTS", [
        f"Les murs avant et arrière suivent la pente du toit : {fi(H_HAUT)} du côté haut, {fi(H_BAS)} du côté bas. Hauteur hors-tout {fi(Z_TOP)}.",
        "Avant : fenêtre 16 × 12 du côté bas, ventilation haute du côté haut, timon en A. Arrière : fenêtre 24 × 12 centrée.",
    ], larg=150, inter=9)
    return f


# =============================================================================
def f_coupe():
    f = Feuille(4, "Coupe A-A")
    titre_vue(f, 40, 40, "COUPE A-A (vers l'arrière)", "Échelle 1:24 (1/2 po = 1 pi)")
    v = Vue(f, 85, 490, 24, flip=True)
    v.rect(-12, -8, B + 24, 8, fill="url(#glace)", stroke="none")
    v.line(-12, 0, B + 12, 0, stroke=BLEU, sw=1.1)
    for ty in TR_Y:
        v.rect(ty + 1, -8, 10, 8, fill="#fff", stroke=BLEU, sw=0.6, dash="3,1.5")
    for y0, _ in PATIN_Y:
        v.rect(y0, UHMW, 1.5, PAT, fill="url(#hach)", stroke="#111", sw=0.8)
        v.rect(y0, 0, 1.5, UHMW, fill="#222", stroke="none")
    v.rect(1.5, Z_P, B - 3, CAD, fill="#f3ead8", stroke=BOIS, sw=0.6)
    for y0 in (0, B - 1.5):
        v.rect(y0, Z_P, 1.5, CAD, fill="url(#hach)", stroke="#111", sw=0.7)
    segs = [(0, TR_Y[0]), (TR_Y[0] + 12, TR_Y[1]), (TR_Y[1] + 12, B)]
    for a, b in segs:
        v.rect(a, Z_P + CAD, b - a, CP, fill="url(#hach)", stroke="#111", sw=0.7)
    # murs coupés
    for y_ext, sg, h in ((0, 1, H_HAUT), (B, -1, H_BAS)):
        y = y_ext
        for ep, fill in ((0.25, "#d8c39a"), (2.5, "url(#isol)"), (0.25, "#efe3c8")):
            v.rect(min(y, y + sg * ep), Z_PL, ep, h, fill=fill, stroke="#111", sw=0.5)
            y += sg * ep
    # mur arrière au-delà (fenêtre)
    v.poly([(T, Z_PL), (B - T, Z_PL), (B - T, zr(B - T)), (T, zr(T))], stroke="#aaa", sw=0.5)
    v.rect(FEN_AR[0], Z_PL + 40, 24, 12, stroke="#999", sw=0.6, dash="4,2")
    v.text(48, Z_PL + 46.5, "fenêtre (au-delà)", size=5.2, anchor="middle", fill="#888")
    # chevron au-delà, isolant, fourrures coupées, tôle
    y1, y2 = -DEB_E, B + DEB_E
    v.poly([(y1, zr(y1)), (y2, zr(y2)), (y2, zr(y2) + CHEV), (y1, zr(y1) + CHEV)], fill="#f3ead8", stroke=BOIS, sw=0.7)
    v.poly([(T, zr(T)), (B - T, zr(B - T)), (B - T, zr(B - T) + 1.5), (T, zr(T) + 1.5)], fill="url(#isol)", stroke="#111", sw=0.3)
    for k in range(6):
        yy = y1 + 2 + k * 21.5
        v.rect(yy, zr(yy) + CHEV, 2.5, 0.75, fill="url(#hach)", stroke="#111", sw=0.4)
    v.poly([(y1 - 0.5, zr(y1 - 0.5) + TOIT - 0.3), (y2 + 0.5, zr(y2 + 0.5) + TOIT - 0.3), (y2 + 0.5, zr(y2 + 0.5) + TOIT), (y1 - 0.5, zr(y1 - 0.5) + TOIT)],
           fill="#555", stroke="#111", sw=0.4)
    # bancs
    for y0, front in ((T, T + BANC - 0.5), (B - T - BANC, B - T - BANC)):
        v.rect(y0, Z_PL + H_BANC - 0.5, BANC, 0.5, fill="#d8c39a", stroke="#111", sw=0.6)
        v.rect(front, Z_PL, 0.5, H_BANC - 0.5, fill="#d8c39a", stroke="#111", sw=0.6)
    for ty in TR_Y:
        v.poly([(ty, Z_PL), (ty - 0.3, Z_PL + 12), (ty + 0.4, Z_PL + 12), (ty + 0.75, Z_PL)], fill="#d8c39a", stroke="#111", sw=0.5)
    pastilles = [
        (70, zr(70) + TOIT - 0.15, 1, 0, -22),
        (y1 + 2 + 3 * 21.5 + 1, zr(y1 + 2 + 3 * 21.5) + CHEV + 0.4, 2, 6, -30),
        (30, zr(30) + 2.5, 3, -12, -34),
        (60, zr(60) + 0.7, 4, 0, 26),
        (0.1, Z_PL + 50, 5, -24, 0),
        (1.5, Z_PL + 30, 6, -24, 0),
        (T + 7, Z_PL + H_BANC, 7, 0, -22),
        (40, Z_PL - 0.25, 8, -30, 28),
        (30, Z_P + 1.75, 9, -14, 34),
        (48, 3, 10, 26, 6),
        (48, 0.1, 11, 40, 22),
        (TR_Y[1] + 0.4, Z_PL + 8, 12, 24, 4),
        (TR_Y[0] + 6, -5, 13, -26, 2),
    ]
    for x, y, n, dx, dy in pastilles:
        callout(v, x, y, n, dx, dy)
    v.dim(0, Z_PL, 0, Z_PL + H_HAUT, -36, f"{fi(H_HAUT)} libre", size=6)
    v.dim(0, 0, 0, Z_PL, -36, size=6)
    v.dim(B, Z_PL, B, Z_PL + H_BAS, 14, f"{fi(H_BAS)} libre", size=6)
    v.dim(-DEB_E, 0, -DEB_E, Z_TOP, -58, f"{fi(Z_TOP)} hors-tout", size=6.5)
    v.dim(T, Z_PL + H_BANC, T + BANC, Z_PL + H_BANC, -8, "14 po", size=5.6)
    v.dim(TR_Y[0] + 12, Z_PL + 4, TR_Y[1], Z_PL + 4, 0, "allée 30 po", size=5.8)
    leg = [
        "Tôle prépeinte cal. 29 (ou aluminium)",
        "Fourrures 1×3 @ 24 po",
        "Chevrons 2×4 @ 24 po c/c, pente 1 1/2:12",
        "Isolant XPS 1 1/2 po entre chevrons",
        "Revêtement CP 1/4 extérieur, peint",
        "Montants 2×3 @ 24 po + XPS + panneau 1/4",
        "Bancs : dessus et devant CP 1/2",
        "Plancher CP 1/2 traité, collé-vissé",
        "Traverses 2×4 @ 16 po (portée 4 pi)",
        "3 patins 2×6 traité sur chant (coupés)",
        "Semelles de glisse UHMW 1/4 po",
        "Trappe 12 × 12 ouverte (6 en tout)",
        "Trou dans la glace, tarière 8 à 10 po",
    ]
    x0, y0 = 492, 96
    f.text(x0, y0 - 16, "LÉGENDE", size=9, weight="bold")
    for i, t in enumerate(leg):
        y = y0 + i * 15
        f.add(f'<circle cx="{x0+6}" cy="{y-2.6}" r="6" fill="#fff" stroke="{ROUGE}" stroke-width="0.8"/>')
        f.text(x0 + 6, y, str(i + 1), size=6.5, anchor="middle", weight="bold", fill=ROUGE)
        f.text(x0 + 17, y, t, size=7.2)
    notes(f, x0, y0 + 13 * 15 + 16, "POURQUOI 3 PATINS", [
        "À 8 pi de large, un patin central coupe la portée des traverses en deux (4 pi) : des 2×4 suffisent au lieu de 2×8, et le plancher ne fléchit pas en sentier.",
    ], larg=48, inter=9.5)
    return f


# =============================================================================
def f_ossature():
    f = Feuille(5, "Ossature")
    titre_vue(f, 40, 40, "CADRE DE PLANCHER, PATINS ET TIMON (vue de dessus)", "Échelle 1:32 — contreplaqué retiré")
    v = Vue(f, 200, 78, 32)
    for y0, y1 in PATIN_Y:
        v.rect(-NEZ, y0, L + NEZ, y1 - y0, stroke=BLEU, sw=0.6, dash="4,2")
        v.rect(-NEZ, y0, NEZ, y1 - y0, fill="url(#bois)", stroke="#111", sw=0.5)
    v.rect(0, 0, L, 1.5, **bois)
    v.rect(0, B - 1.5, L, 1.5, **bois)
    for x in [0] + [16 * n - 0.75 for n in range(1, 9)] + [L - 1.5]:
        v.rect(x, 1.5, 1.5, B - 3, **bois)
    for n, tx, ty in trappes():
        x0 = 16 * (tx // 16) + 0.75
        x1 = 16 * (tx // 16 + 1) - 0.75
        v.rect(x0, ty - 1.5, x1 - x0, 1.5, fill="#e7c9a0", stroke=BOIS, sw=0.5)
        v.rect(x0, ty + 12, x1 - x0, 1.5, fill="#e7c9a0", stroke=BOIS, sw=0.5)
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke=BLEU, sw=0.7)
    ya, yb = 0.75, B - 0.75
    v.poly([(-NEZ, ya), (ATT + 3, B / 2), (-NEZ, yb)], close=False, stroke="#333", sw=2)
    v.line(-NEZ, B / 2, ATT + 3, B / 2, stroke="#333", sw=1.6)
    k = (-26 + NEZ) / (ATT + 3 + NEZ)
    v.line(-26, ya + (B / 2 - ya) * k, -26, yb - (yb - B / 2) * k, stroke="#333", sw=1.4)
    v.circle(ATT, B / 2, 3, stroke="#333", sw=1.2)
    v.dim(0, 0, L, 0, -12)
    v.dim(L, 0, L, B, 12)
    v.dim(16, B, 32, B, 12, "16 po c/c", size=5.4)
    notes(f, 560, 92, "CADRE", [
        "2×4 traité sur chant : rives de 12 pi, traverses @ 16 po.",
        "Chevêtres 2×4 autour des 6 trappes.",
        "3 patins : sous chaque rive et au centre. Tire-fonds 3/8 × 5 à chaque traverse.",
        "Timon : 2 bras + bras central vers l'anneau, traverse de raidissement, boulonné dans le nez des 3 patins.",
    ], larg=34, size=6.5, inter=8.4)

    # --- mur côté haut ------------------------------------------------------
    titre_vue(f, 40, 318, "MUR CÔTÉ HAUT (vu de l'extérieur)", "Échelle 1:32 — 2×3 @ 24 po c/c, avant à droite")
    v = Vue(f, 60, 524, 32, flip=True)
    U = lambda x: L - x
    v.rect(0, 0, U(PORTE_X[1]) - 0, 1.5, **bois) if False else None
    ro0, ro1 = U(PORTE_X[1]) - 1, U(PORTE_X[0]) + 1     # ouv. brute 30 po
    v.rect(ro1 + 3, 0, L - ro1 - 3, 1.5, **bois)
    v.rect(0, H_HAUT - 1.5, L, 1.5, **bois)
    mt = lambda u, z0, z1: v.rect(u, z0, 1.5, z1 - z0, **bois)
    f0, f1 = U(FEN_HAUT[1]), U(FEN_HAUT[0])
    for u in [0] + [24 * n - 0.75 for n in range(1, 6)] + [L - 1.5]:
        if ro0 - 1.5 < u < ro1 + 3 or f0 - 1.5 < u < f1:
            continue
        mt(u, 0 if u < ro1 else 1.5, H_HAUT - 1.5)
    mt(ro1 + 1.5, 0, H_HAUT - 1.5)                  # montant de rive
    mt(ro1, 0, H_PORTE + 1)                        # montant nain
    mt(ro0 - 1.5, 0, H_HAUT - 1.5) if ro0 - 1.5 > 0 else None
    v.rect(max(0, ro0 - 1.5), H_PORTE + 1, ro1 - max(0, ro0 - 1.5) + 1.5, 3.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    mt(f0 - 1.5, 1.5, H_HAUT - 1.5)
    mt(f1, 1.5, H_HAUT - 1.5)
    v.rect(f0, 34.5, f1 - f0, 1.5, **bois)
    v.rect(f0, 48, f1 - f0, 3.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    mt(95.25, 1.5, 34.5)
    mt(95.25, 51.5, H_HAUT - 1.5)
    v.dim(0, 0, L, 0, 12)
    v.dim(0, 0, 0, H_HAUT, -10, size=6)
    v.dim(ro0, 0, ro1, 0, 22, "30 po ouv. brute", size=5.4)
    v.dim(f0, 36, f1, 36, -10, "ouv. brute 24 × 12", size=5.4)

    # --- mur avant ---------------------------------------------------------
    titre_vue(f, 470, 318, "MUR AVANT (vu de l'extérieur)", "Échelle 1:32 — entre les murs côtés")
    v = Vue(f, 500, 524, 32, flip=True)
    a0, a1 = T, B - T
    top = lambda y: wtop(y)
    v.rect(a0, 0, a1 - a0, 1.5, **bois)
    v.poly([(a0, top(a0) - 1.5), (a1, top(a1) - 1.5), (a1, top(a1)), (a0, top(a0))], **bois)

    def mtp(y, z0, z1f):
        v.poly([(y, z0), (y + 1.5, z0), (y + 1.5, z1f(y + 1.5)), (y, z1f(y))], **bois)
    hautp = lambda y: top(y) - 1.5
    w0, w1 = FEN_AV
    for y in (a0, 24 - 0.75, 48 - 0.75, a1 - 1.5, w0 - 1.5, w1):
        mtp(y, 1.5, hautp)
    v.rect(w0, 34.5, w1 - w0, 1.5, **bois)
    v.rect(w0, 48, w1 - w0, 3.5, fill="#e7c9a0", stroke=BOIS, sw=0.6)
    v.rect(8, 72, 10, 4, fill="#444", stroke="#111", sw=0.4)
    v.dim(a0, 0, a1, 0, 12, fi(a1 - a0) + " entre murs", size=5.6)
    v.dim(a0, 0, a0, top(a0), -10, size=5.6)
    v.dim(a1, 0, a1, top(a1), 10, size=5.6)
    v.text(13, 69, "vent.", size=5, anchor="middle")
    return f


# =============================================================================
MATERIAUX = [
    ("BASE, PATINS, TIMON", None),
    ("Patins (3)", "3 × 2×6 × 14 pi traité"),
    ("Semelles de glisse", "3 × UHMW 1/4 × 1 1/2 po × 13 pi"),
    ("Cadre : rives", "2 × 2×4 × 12 pi traité"),
    ("Cadre : traverses + chevêtres", "12 × 2×4 × 8 pi traité"),
    ("Plancher", "3 × CP 1/2 po 4×8 traité"),
    ("Timon en A", "16 pi tube acier 1 1/2 po + anneau + chaîne"),
    ("MURS", None),
    ("Montants, lisses, sablières", "≈ 37 × 2×3 × 8 pi"),
    ("Linteaux (porte, fenêtres)", "3 × 2×4 × 8 pi"),
    ("Revêtement extérieur", "9 × CP 1/4 po 4×8"),
    ("Panneau intérieur (option)", "7 × CP 1/4 ou panneau 1/8"),
    ("TOIT", None),
    ("Chevrons @ 24 po", "7 × 2×4 × 10 pi"),
    ("Fourrures", "6 × 1×3 × 14 pi"),
    ("Tôle", "5 × 3 pi × 9'-6\" + moulures + ruban scellant"),
    ("ISOLATION, INTÉRIEUR", None),
    ("Isolant XPS 1 1/2 po", "≈ 22 panneaux 2×8 pi"),
    ("2 bancs + 6 couvercles", "2 × CP 1/2 4×8 + 6 × 2×2 × 8"),
    ("Plaque incombustible", "panneau ciment 1/2 po 2×3 pi"),
    ("OUVERTURES", None),
    ("Porte 28 × 72 maison", "3 pentures, loquet, moraillon"),
    ("Fenêtres polycarbonate 1/4", "3 × 24×12 + 1 × 16×12"),
    ("Grilles de ventilation", "2 × 4 × 10 po réglables"),
    ("QUINCAILLERIE, SÉCURITÉ", None),
    ("Vis ext. 3 et 1 1/4 po", "≈ 6 lb + 3 lb"),
    ("Tire-fonds 3/8 × 5 + boulons timon", "30 + 6"),
    ("Vis à tôle à rondelle", "≈ 200"),
    ("Détecteur CO, extincteur ABC", "1 + 1"),
]

POIDS = [
    ("3 patins + semelles", 84),
    ("Cadre de plancher 2×4 traité", 185),
    ("Plancher CP 1/2 traité", 145),
    ("Ossature murs 2×3 + linteaux", 225),
    ("Revêtement CP 1/4", 196),
    ("Isolant XPS 1 1/2", 68),
    ("Chevrons et fourrures", 102),
    ("Tôle et moulures", 90),
    ("Bancs et couvercles", 106),
    ("Porte, fenêtres, grilles", 35),
    ("Timon acier + attelage", 30),
    ("Quincaillerie, peinture", 35),
]


def f_materiaux():
    f = Feuille(6, "Matériaux, poids et notes")
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
        y += 14.6

    x, y = 440, 44
    total = sum(p for _, p in POIDS)
    f.text(x, y, "POIDS ESTIMÉ", size=11, weight="bold")
    f.text(x, y + 11, "Calcul approximatif, à confirmer à la pesée.", size=6.5, fill="#555")
    y += 26
    mx = max(p for _, p in POIDS)
    for nom, p in POIDS:
        f.text(x, y, nom, size=6.8)
        f.add(f'<rect x="{x+150}" y="{y-7}" width="{p / mx * 120:.1f}" height="8" fill="{BLEU}" opacity="0.75"/>')
        f.text(x + 310, y, f"{p} lb", size=6.8, anchor="end")
        y += 12.5
    f.add(f'<line x1="{x}" y1="{y-6}" x2="{x+310}" y2="{y-6}" stroke="#111" stroke-width="0.8"/>')
    f.text(x, y + 6, "TOTAL TEL QUE DESSINÉ", size=8, weight="bold")
    f.text(x + 310, y + 6, f"≈ {total} lb ({round(total * 0.4536 / 5) * 5} kg)", size=8, weight="bold", anchor="end")
    y += 26
    y = notes(f, x, y, "POUR ALLÉGER (≈ 1 100 lb / 500 kg)", [
        "Tôle d'aluminium au toit : environ 50 lb de moins.",
        "Cadre de plancher non traité, peint : environ 40 lb de moins.",
        "Pas de panneau intérieur ; bancs en CP 3/8 : environ 35 lb de moins.",
        "Revêtement en panneau d'aluminium : environ 60 lb de moins.",
    ], larg=60, size=6.6, inter=8.8)
    notes(f, x, y + 4, "À SAVOIR", [
        "À ce poids, prévoir une motoneige utilitaire ou rouler lentement sur une trace tapée. Vérifier la capacité de remorquage de ta motoneige.",
        "Chauffage propane homologué intérieur, ventilation haute et basse, détecteur de CO et extincteur obligatoires.",
        "Afficher nom, adresse et téléphone ; vérifier le règlement municipal.",
    ], larg=60, size=6.6, inter=8.8)
    return f


if __name__ == "__main__":
    for fe in (f_plan(), f_cote(), f_bouts(), f_coupe(), f_ossature(), f_materiaux()):
        (ICI / f"feuille-{fe.num}.svg").write_text(fe.svg(), encoding="utf-8")
    print("hors-tout", fi(Z_TOP), "| avec timon", fi(L - ATT + 3), "| total", sum(p for _, p in POIDS), "lb")
