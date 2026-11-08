#!/usr/bin/env python3
"""Aménagement intérieur « couchette » de la cabane 8 x 12 monopente.

Couche 2 adultes (lit double) + 1 ado (banc-lit), kitchenette avec réchaud,
5 trappes dont 2 sous le lit relevable. Porte déplacée au mur avant.
  python3 generer_amenagement.py && node ../../exporter.js . Amenagement_cabane_8x12.pdf
"""
import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent))
sys.path.insert(0, str(ICI.parent.parent))
import generer_8x12 as c  # noqa: E402  (paramètres de la cabane + fi en pieds-pouces)
import generer_plans as g  # noqa: E402
from generer_plans import Feuille, Vue, titre_vue, notes  # noqa: E402

fi = c.fi
g.PROJET = "Cabane 8 × 12 — aménagement couchette"
g.NB_FEUILLES = 3
g.DATE = "2026-11-08"

L, B, T = c.L, c.B, c.T
BLEU, ROUGE, BOIS = c.BLEU, c.ROUGE, c.BOIS
MATELAS = "#e6edf3"
VERT = "#2e7d5b"

# Mobilier (X, Y, largeur en X, profondeur en Y) — X = 0 à l'avant, Y = 0 côté haut
ADO = (12, 3, 75, 30)          # banc-lit ado, assise 16 po
LIT = (87, 3, 54, 75)          # lit double 54 x 75, plateforme 20 po relevable
CHEVET = (87, 78, 54, 15)      # chevet / rangement au pied latéral du lit
CUISINE = (30, 73, 42, 20)     # comptoir 42 x 20, hauteur 34
GLACIERE = (73, 71, 14, 22)    # glacière 28 pintes qui sert de siège
CHAUF = (3, 77, 12, 16)        # chaufferette propane à ventouse
VESTIAIRE = (3, 3, 9, 30)      # crochets + bac à bottes
TABLE = (48, 37, 36, 24)       # table amovible sur pied de VR
TRAPPES = [(34, 37, "T1"), (66, 37, "T2"), (66, 57, "T3"), (98, 40, "T4"), (114, 40, "T5")]
PORTE = (34, 62)               # mur avant, porte 28 x 70
H_PORTE = 70
FEN_HAUT, FEN_BAS, FEN_AR = (40, 64), (39, 63), (36, 60)
H_BANC, H_LIT, H_COMPTOIR = 16, 20, 34


def rect(v, r, **k):
    x, y, w, h = r
    v.rect(x, y, w, h, **k)


def murs(v, f, porte=True):
    o = [(0, 0), (L, 0), (L, B), (0, B)]
    i = [(T, T), (L - T, T), (L - T, B - T), (T, B - T)]
    pts = lambda P: " ".join(f"{a:.2f},{b:.2f}" for a, b in (v.P(*p) for p in P))
    f.add(f'<path d="M{pts(o)}Z M{pts(i[::-1])}Z" fill="#9aa1a5" stroke="#111" stroke-width="1" fill-rule="evenodd"/>')
    for (a, b), y0 in ((FEN_HAUT, 0), (FEN_BAS, B - T)):
        v.rect(a, y0, b - a, T, fill="#fff", stroke="#111", sw=0.5)
        v.line(a, y0 + T / 2, b, y0 + T / 2, sw=0.4)
    v.rect(L - T, FEN_AR[0], T, FEN_AR[1] - FEN_AR[0], fill="#fff", stroke="#111", sw=0.5)
    v.line(L - T / 2, FEN_AR[0], L - T / 2, FEN_AR[1], sw=0.4)
    if porte:
        p0, p1 = PORTE
        v.rect(-0.2, p0, T + 0.4, p1 - p0, fill="#fff", stroke="none")
        v.line(0, p0, T, p0, sw=1); v.line(0, p1, T, p1, sw=1)
        w = p1 - p0
        v.rect(-w, p1 - 1.2, w, 1.2, fill="#fff", stroke="#111", sw=0.7)
        v.arc(0, p1, w, -w, p1, 0, p0)


def matelas(v, r, oreiller="droite", n=1):
    x, y, w, h = r
    v.rect(x + 0.5, y + 0.5, w - 1, h - 1, fill=MATELAS, stroke="#7f95a8", sw=0.6)
    if oreiller == "droite":       # oreillers contre le mur côté X max
        for k in range(n):
            hh = (h - 4) / n
            v.rect(x + w - 11, y + 2 + k * hh, 9, hh - 1.5, fill="#fff", stroke="#7f95a8", sw=0.5)
    elif oreiller == "haut":       # oreillers côté Y min
        for k in range(n):
            ww = (w - 4) / n
            v.rect(x + 2 + k * ww, y + 2, ww - 1.5, 9, fill="#fff", stroke="#7f95a8", sw=0.5)
    else:                          # côté X min
        v.rect(x + 2, y + 2, 9, h - 4, fill="#fff", stroke="#7f95a8", sw=0.5)


def trappes(v, lit_releve=True, size=6.5):
    for tx, ty, nom in TRAPPES:
        sous_lit = tx >= LIT[0]
        st = dict(fill="#e8f2fa", stroke=BLEU, sw=0.9)
        if sous_lit and not lit_releve:
            st = dict(fill="none", stroke=BLEU, sw=0.6, dash="3,2")
        v.rect(tx, ty, 12, 12, **st)
        v.circle(tx + 6, ty + 6, 4, stroke=BLEU, dash="2,1.5")
        v.text(tx + 6, ty + 7.4, nom, size=size, anchor="middle", weight="bold", fill=BLEU)


def cuisine(v, detail=True):
    rect(v, CUISINE, fill="#ece6da", stroke="#6b5a3e", sw=0.8)
    x, y, w, h = CUISINE
    v.rect(x + 2, y + 3, 20, 13, fill="#cfd5d9", stroke="#555", sw=0.6)      # plaque inox
    for cx in (x + 7, x + 17):
        v.circle(cx, y + 9.5, 3.2, stroke="#333", sw=0.8)
        v.circle(cx, y + 9.5, 1.4, stroke="#333", sw=0.5)
    v.rect(x + 26, y + 4, 12, 11, fill="#fff", stroke="#555", sw=0.6)        # bassine
    v.circle(x + 32, y + 9.5, 0.8, fill="#555", stroke="none")
    if detail:
        v.text(x + 12, y + 1.8, "réchaud 2 feux", size=5.4, anchor="middle")
        v.text(x + 32, y + 1.8, "bassine", size=5.4, anchor="middle")


def mobilier(v, mode="nuit", detail=True):
    """mode : 'nuit' (lits faits), 'jour' (lit relevé, table en place), 'plan' (vue complète)."""
    # vestiaire
    rect(v, VESTIAIRE, fill="#efeae0", stroke="#8a7a5c", sw=0.6)
    # banc-lit ado
    rect(v, ADO, fill="#f3ead8", stroke=BOIS, sw=0.8)
    if mode != "jour":
        matelas(v, ADO, oreiller="gauche")
    else:
        for k in range(1, 3):
            v.line(ADO[0] + k * 25, ADO[1], ADO[0] + k * 25, ADO[1] + ADO[3], stroke=BOIS, sw=0.4, dash="2,2")
    # lit double
    if mode == "jour":
        rect(v, LIT, fill="#fff", stroke=BOIS, sw=0.8, dash="5,3")
    else:
        rect(v, LIT, fill="#f3ead8", stroke=BOIS, sw=0.8)
        matelas(v, LIT, oreiller="droite", n=2)
    rect(v, CHEVET, fill="#efeae0", stroke="#8a7a5c", sw=0.6)
    trappes(v, lit_releve=(mode == "jour"), size=6.5 if detail else 5)
    cuisine(v, detail)
    rect(v, GLACIERE, fill="#d9ecf5", stroke=BLEU, sw=0.7)
    rect(v, CHAUF, fill="#fde2df", stroke=ROUGE, sw=0.9)
    v.rect(T, 65, 24, B - T - 65, stroke=ROUGE, sw=0.5, dash="3,2")
    if mode == "jour":
        rect(v, TABLE, fill="#f6efe2", stroke="#6b5a3e", sw=0.9)
        v.circle(TABLE[0] + TABLE[2] / 2, TABLE[1] + TABLE[3] / 2, 1.5, fill="#6b5a3e", stroke="none")
    elif mode == "plan":
        rect(v, TABLE, stroke="#6b5a3e", sw=0.7, dash="4,2")


# =============================================================================
def f_plan():
    f = Feuille(1, "Plan d'aménagement")
    titre_vue(f, 40, 40, "PLAN D'AMÉNAGEMENT — 2 ADULTES + 1 ADO", "Échelle 5/8 po = 1 pi (1:19,2) · avant à gauche")
    v = Vue(f, 178, 104, 19.2)
    # timon amovible (pointillés)
    v.poly([(-c.NEZ, 0.75), (-30, B / 2), (-c.NEZ, B - 0.75)], close=False, stroke="#999", sw=1, dash="5,3")
    v.text(-20, B / 2 + 22, "timon", size=6, anchor="middle", fill="#777")
    v.text(-20, B / 2 + 26.5, "amovible", size=6, anchor="middle", fill="#777")
    murs(v, f)
    mobilier(v, "plan")
    lab = lambda x, y, t, **k: v.text(x, y, t, size=k.pop("size", 7), anchor=k.pop("anchor", "middle"), **k)
    lab(49.5, 11, "BANC-LIT ADO", weight="bold")
    lab(49.5, 15.5, "30 × 75 po · assise 16 po", size=6)
    lab(49.5, 20, "coffres dessous, étagère au-dessus", size=5.6, fill="#555")
    lab(108, 26, "LIT DOUBLE", weight="bold")
    lab(108, 30.5, "54 × 75 po · plateforme 20 po", size=6)
    lab(108, 61, "sommier relevable sur vérins :", size=5.8, fill="#555")
    lab(108, 65, "de jour, il monte et libère T4 et T5", size=5.8, fill="#555")
    lab(114, 87, "CHEVET · liseuses USB · tiroirs", size=5.8)
    lab(51, 92.2, "KITCHENETTE 42 × 20 · comptoir 34 po", size=5.6, weight="bold")
    lab(80, 79, "GLACIÈRE", size=5.2, weight="bold", fill=BLEU)
    lab(80, 83, "= siège", size=5.2, fill=BLEU)
    lab(9, 84.5, "CHAUF.", size=5.2, weight="bold", fill=ROUGE)
    lab(9, 88.5, "ventouse", size=5, fill=ROUGE)
    lab(7.5, 16, "manteaux", size=4.8, rot=-90)
    lab(66, 47.5, "table amovible 24 × 36 (repas)", size=5.6, fill="#6b5a3e")
    lab(18, 48.5, "ENTRÉE", size=6.5, weight="bold", fill="#777")
    v.text(-14, PORTE[0] - 3, "PORTE 28 × 70", size=6.2, weight="bold", anchor="middle")
    v.text(-14, PORTE[0] + 1.5, "ouvre vers l'ext.", size=5.4, italic=True, anchor="middle")
    # zones de dégagement chauffage
    lab(16, 69, "dégagement", size=4.8, fill=ROUGE)
    # cotes
    v.dim(0, 0, L, 0, -24, f"{fi(L)} hors-tout")
    v.dim(T, 0, ADO[0], 0, -10, size=5.4)
    v.dim(ADO[0], 0, LIT[0], 0, -10, size=5.6)
    v.dim(LIT[0], 0, L - T, 0, -10, size=5.6)
    v.dim(L, 0, L, B, 24, f"{fi(B)} hors-tout")
    v.dim(L, T, L, LIT[1] + LIT[3], 12, size=5.6)
    v.dim(L, LIT[1] + LIT[3], L, B - T, 12, size=5.4)
    v.dim(CUISINE[0], B, CUISINE[0] + CUISINE[2], B, 20, size=5.6)
    v.dim(T, ADO[1] + ADO[3], T, CUISINE[1], -40, "allée " + fi(CUISINE[1] - ADO[1] - ADO[3]), size=5.6)
    return f


# =============================================================================
def f_jour_nuit():
    f = Feuille(2, "Mode jour / mode nuit")
    titre_vue(f, 40, 40, "MODE JOUR : ON PÊCHE, ON MANGE", "Échelle 1:32 · lit relevé, 5 trappes ouvertes, table en place")
    titre_vue(f, 420, 40, "MODE NUIT : 3 PLACES POUR DORMIR", "Échelle 1:32 · table rangée, lit baissé")
    for x0, mode in ((60, "jour"), (430, "nuit")):
        v = Vue(f, x0, 96, 32)
        murs(v, f, porte=False)
        v.rect(-0.2, PORTE[0], T + 0.4, PORTE[1] - PORTE[0], fill="#fff", stroke="none")
        v.text(-3, (PORTE[0] + PORTE[1]) / 2, "porte", size=5.4, anchor="middle", rot=-90)
        mobilier(v, mode, detail=False)
        if mode == "jour":
            for n, (x, y) in enumerate([(50, 30), (60, 66), (79, 67), (40, 30)]):
                pass
            for (x, y) in [(40, 26), (72, 26), (58, 64), (78, 64)]:
                v.circle(x, y, 3.2, fill="#ffd27a", stroke="#a87b1d", sw=0.6)
            v.text(L / 2 + 30, 64, "lit monté au plafond", size=5.6, anchor="middle", fill="#555")
        else:
            for (x, y) in [(22, 18), (128, 22), (128, 52)]:
                v.circle(x, y, 3.2, fill="#ffd27a", stroke="#a87b1d", sw=0.6)
            v.text(49.5, 8.5, "ado", size=6, anchor="middle", weight="bold")
            v.text(108, 40, "2 adultes", size=6, anchor="middle", weight="bold")
    f.add('<circle cx="70" cy="336" r="4" fill="#ffd27a" stroke="#a87b1d" stroke-width="0.6"/>')
    f.text(80, 339, "= une personne", size=6.5)

    notes(f, 40, 372, "COMMENT ÇA MARCHE", [
        "Le soir, on range la table, on baisse le lit double et on étend le matelas de l'ado sur son banc.",
        "Le matin, le sommier du lit monte sur 2 vérins à gaz (comme un lit coffre) et se bloque en haut : T4 et T5 sont libres, on pêche assis sur le bord de la plateforme.",
        "Matelas en mousse de 4 po (ado) et 6 po (lit double), housses lavables. Rideau occultant devant le lit double.",
        "Tout est vissé au plancher et aux murs : rien ne bouge pendant le remorquage.",
    ], larg=130, size=7, inter=10)
    return f


# =============================================================================
def f_cuisine_securite():
    f = Feuille(3, "Cuisine et sécurité")
    titre_vue(f, 40, 40, "MUR CÔTÉ BAS, VU DE L'INTÉRIEUR", "Échelle 1:32 (3/8 po = 1 pi) · arrière à gauche, avant à droite")
    v = Vue(f, 60, 300, 32, flip=True)
    U = lambda x: L - x
    H = c.H_BAS
    v.rect(0, 0, L, H, fill="#f7f4ee", stroke="#111", sw=0.8)
    v.line(0, 0, L, 0, stroke="#111", sw=1.2)
    # lit double (pied latéral) et chevet
    v.rect(U(L - T), 0, LIT[2], H_LIT, fill="#f3ead8", stroke=BOIS, sw=0.6)
    v.rect(U(L - T), H_LIT, LIT[2], 6, fill=MATELAS, stroke="#7f95a8", sw=0.6)
    v.text(U(L - T) + LIT[2] / 2, 9, "chevet / tiroirs", size=5.6, anchor="middle")
    # glacière
    a = U(GLACIERE[0] + GLACIERE[2])
    v.rect(a, 0, GLACIERE[2], 16, fill="#d9ecf5", stroke=BLEU, sw=0.7)
    v.text(a + GLACIERE[2] / 2, 7, "glacière", size=5, anchor="middle", fill=BLEU)
    # comptoir
    a = U(CUISINE[0] + CUISINE[2])
    w = CUISINE[2]
    v.rect(a, 0, w, H_COMPTOIR - 1.5, fill="#ece6da", stroke="#6b5a3e", sw=0.7)
    v.rect(a, H_COMPTOIR - 1.5, w, 1.5, fill="#c9b48a", stroke="#111", sw=0.5)
    v.line(a + w / 2, 2, a + w / 2, H_COMPTOIR - 3, stroke="#6b5a3e", sw=0.5)
    v.rect(a + 3, 3, 16, 22, fill="#4a7fa8", stroke="#111", sw=0.5)
    v.text(a + 11, 14, "eau 10 L", size=5, anchor="middle", fill="#fff")
    v.text(a + w * 0.75, 14, "rangement", size=5.2, anchor="middle")
    xr = a + w - 22                       # réchaud côté avant (droite)
    v.rect(xr, H_COMPTOIR, 20, 4, fill="#cfd5d9", stroke="#555", sw=0.6)
    v.text(xr + 10, H_COMPTOIR + 5.5, "réchaud", size=5, anchor="middle")
    v.rect(a + 2, H_COMPTOIR + 4.5 - 4.5, 12, 0.01, stroke="none")
    v.rect(a + 4, H_COMPTOIR, 12, 3, fill="#fff", stroke="#555", sw=0.5)
    v.rect(a, H_COMPTOIR + 25, w, 0.75, fill="#c9b48a", stroke="#111", sw=0.5)
    v.text(a + w / 2, H_COMPTOIR + 27.5, "étagère + crochets", size=5, anchor="middle")
    fa, fb = U(FEN_BAS[1]), U(FEN_BAS[0])
    v.rect(fa, 30, fb - fa, 12, fill="#dbeaf5", stroke="#111", sw=0.8) if False else None
    v.rect(fa, H_COMPTOIR + 10, fb - fa, 12, fill="#dbeaf5", stroke="#111", sw=0.8)
    v.rect(xr + 4, H - 6, 12, 4, fill="#444", stroke="#111", sw=0.4)
    v.text(xr - 2, H - 4.5, "ventil. 12 V", size=4.8, anchor="end")
    # chauffage à ventouse
    a = U(CHAUF[0] + CHAUF[2])
    v.rect(a, 6, CHAUF[2], 22, fill="#fde2df", stroke=ROUGE, sw=0.8)
    v.text(a + 6, 17, "chauf.", size=5, anchor="middle", fill=ROUGE)
    v.rect(a - 1, 0, CHAUF[2] + 2, 0.75, fill="#999", stroke="none")
    v.dim(U(CUISINE[0] + CUISINE[2]), 0, U(CUISINE[0] + CUISINE[2]), H_COMPTOIR, -10, size=5.6)
    v.dim(U(CUISINE[0] + CUISINE[2]), 0, U(CUISINE[0]), 0, 12, size=5.6)
    v.dim(L, 0, L, H, 12, size=5.6)
    v.text(4, H - 5, "ARRIÈRE", size=6, weight="bold", fill="#555")
    v.text(L - 4, H - 5, "AVANT", size=6, weight="bold", fill="#555", anchor="end")

    # coupe vers l'arrière
    titre_vue(f, 450, 40, "COUPE VERS L'ARRIÈRE (à X = 5 pi)", "Échelle 1:32 · banc-lit, table, comptoir, lit double au fond")
    v = Vue(f, 500, 312, 32, flip=True)
    zp = c.Z_PL
    v.rect(-6, -4, B + 12, 4, fill="url(#glace)", stroke="none")
    v.line(-6, 0, B + 6, 0, stroke=BLEU, sw=0.8)
    v.rect(0, c.Z_P, B, c.CAD + c.CP, fill="#e9dcc3", stroke="#111", sw=0.5)
    for y0, _ in c.PATIN_Y:
        v.rect(y0, 0, 1.5, c.Z_P, fill="url(#hach)", stroke="#111", sw=0.5)
    v.poly([(0, zp), (T, zp), (T, zp + c.H_HAUT), (0, zp + c.H_HAUT)], fill="#cfcfcf", stroke="#111", sw=0.6)
    v.poly([(B - T, zp), (B, zp), (B, zp + c.H_BAS), (B - T, zp + c.H_BAS)], fill="#cfcfcf", stroke="#111", sw=0.6)
    v.poly([(-c.DEB_E, c.zr(-c.DEB_E)), (B + c.DEB_E, c.zr(B + c.DEB_E)), (B + c.DEB_E, c.zr(B + c.DEB_E) + c.TOIT), (-c.DEB_E, c.zr(-c.DEB_E) + c.TOIT)],
           fill="#7d858a", stroke="#111", sw=0.6)
    # lit double au fond (élévation)
    v.rect(T, zp, LIT[3], H_LIT, fill="#f3ead8", stroke=BOIS, sw=0.6)
    v.rect(T, zp + H_LIT, LIT[3], 6, fill=MATELAS, stroke="#7f95a8", sw=0.6)
    v.rect(T + 2, zp + 54, LIT[3] - 4, 6, fill="none", stroke="#8a7a5c", sw=0.5, dash="3,2")
    v.text(T + LIT[3] / 2, zp + 58.5, "lit relevé (jour)", size=5, anchor="middle", fill="#8a7a5c")
    v.rect(FEN_AR[0], zp + 40, 24, 12, fill="#dbeaf5", stroke="#999", sw=0.5)
    # banc-lit ado (coupé)
    v.rect(T, zp, ADO[3], H_BANC, fill="url(#hach)", stroke="#111", sw=0.6)
    v.rect(T, zp + H_BANC, ADO[3], 4, fill=MATELAS, stroke="#7f95a8", sw=0.6)
    v.rect(T, zp + 60, 12, 0.75, fill="#d8c39a", stroke="#111", sw=0.5)
    v.text(T + 6, zp + 62, "étagère", size=4.8, anchor="middle")
    # table + comptoir (coupés)
    v.rect(TABLE[1], zp + 28, TABLE[3], 1.25, fill="#6b5a3e", stroke="#111", sw=0.4)
    v.rect(TABLE[1] + TABLE[3] / 2 - 0.75, zp, 1.5, 28, fill="#6b5a3e", stroke="none")
    v.rect(CUISINE[1], zp, CUISINE[3], H_COMPTOIR, fill="url(#hach)", stroke="#111", sw=0.6)
    v.rect(CUISINE[1] + 3, zp + H_COMPTOIR, 9, 4, fill="#cfd5d9", stroke="#555", sw=0.5)
    v.rect(CUISINE[1] + 2, zp + 54, CUISINE[3] - 2, 0.75, fill="#d8c39a", stroke="#111", sw=0.5)
    v.text(CUISINE[1] + 8, zp + H_COMPTOIR + 6, "réchaud", size=4.8, anchor="middle")
    v.dim(T, zp, T, zp + H_BANC, -14, size=5)
    v.dim(B - T, zp, B - T, zp + H_COMPTOIR, 14, size=5)
    v.dim(TABLE[1] + TABLE[3], zp, TABLE[1] + TABLE[3], zp + 28, 8, size=5)

    notes(f, 40, 352, "LE COIN CUISINE", [
        "Comptoir de 42 × 20 po à 34 po de haut, dessus stratifié ou contreplaqué verni. Rebord de 1 po pour que rien ne glisse en sentier.",
        "Le réchaud 2 feux (propane, bonbonne de 1 lb) reste à demeure sur une plaque inox vissée, contre la fenêtre et sous le ventilateur 12 V.",
        "Bidon d'eau de 10 L avec robinet + bassine amovible ; rangement dessous ; étagère et crochets au-dessus.",
        "La glacière de 28 pintes sert de siège pour pêcher à T3 et de 4e place à table.",
    ], larg=60, size=6.6, inter=8.8)
    y = notes(f, 420, 352, "DORMIR EN SÉCURITÉ (À RESPECTER)", [
        "Pour dormir, un chauffage à ventouse (prise d'air et évacuation par le mur, chambre de combustion scellée) au lieu d'une chaufferette portative ouverte.",
        "Détecteur de monoxyde de carbone (CO) à piles près des lits, et détecteur de fumée. Les tester à chaque sortie.",
        "Ne jamais laisser le réchaud allumé pour chauffer ni pendant le sommeil. Bonbonnes dehors ou dans un coffre ventilé vers l'extérieur.",
        "Garder les deux grilles de ventilation ouvertes. Extincteur ABC près de la porte.",
    ], larg=56, size=6.6, inter=8.8)
    notes(f, 420, y + 2, "POIDS AJOUTÉ", [
        "Lit, banc-lit, cuisine, matelas et glacière : environ 150 à 200 lb de plus que la version pêche seule.",
    ], larg=56, size=6.6, inter=8.8)
    return f


if __name__ == "__main__":
    for fe in (f_plan(), f_jour_nuit(), f_cuisine_securite()):
        (ICI / f"feuille-{fe.num}.svg").write_text(fe.svg(), encoding="utf-8")
    print("ok")
