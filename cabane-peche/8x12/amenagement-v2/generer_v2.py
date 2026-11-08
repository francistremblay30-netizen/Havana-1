#!/usr/bin/env python3
"""Aménagement v2 de la cabane 8 x 12, style « cabane de luxe » (photo de référence).

Dînette au fond qui se transforme en lit double 54 x 90 (2 adultes), lit rabattable
sur chaînes pour l'ado, comptoirs latéraux avec réchaud, trous ronds à couvercle,
finition lambris. Porte au mur avant, timon amovible.
  python3 generer_v2.py && node ../../exporter.js . Amenagement_v2_cabane_8x12.pdf
"""
import sys
from pathlib import Path

ICI = Path(__file__).parent
sys.path.insert(0, str(ICI.parent))
sys.path.insert(0, str(ICI.parent.parent))
import generer_8x12 as c  # noqa: E402
import generer_plans as g  # noqa: E402
from generer_plans import Feuille, Vue, titre_vue, notes  # noqa: E402

fi = c.fi
g.PROJET = "Cabane 8 × 12 — aménagement style chalet"
g.NB_FEUILLES = 3
g.DATE = "2026-11-08"

L, B, T = c.L, c.B, c.T
BLEU, ROUGE, BOIS = c.BLEU, c.ROUGE, c.BOIS
PIN, PIN_F = "#f1e2c4", "#b9925a"     # lambris
COUSSIN = "#3b3f45"                  # coussins foncés comme sur la photo
MATELAS = "#e6edf3"

# Mobilier (X, Y, longueur en X, profondeur en Y) — X = 0 avant, Y = 0 côté haut (mur 7')
BANC = (12, 3, 75, 20)          # banc-coffre côté haut, assise 16 po
SUPERP = (12, 3, 75, 28)        # lit rabattable de l'ado, au-dessus du banc (charnières à 50 po)
DIN_H = (87, 3, 54, 20)         # banquette dînette côté haut, assise 18 po
DIN_B = (87, 73, 54, 20)        # banquette dînette côté bas
TABLE = (96, 33, 36, 30)        # table sur pied, 36 x 30
CUISINE = (30, 73, 42, 20)      # comptoir cuisine 42 x 20, h. 34 (côté bas)
GARDE = (72, 73, 15, 20)        # garde-manger / glacière
CHAUF = (3, 77, 12, 16)         # chauffage propane à ventouse
VESTIAIRE = (3, 3, 9, 20)
TROUS = [(40, 31, "T1"), (72, 31, "T2"), (56, 64, "T3"), (104, 41, "T4"), (120, 55, "T5")]   # centres, Ø 10 po
PORTE = (34, 62)
FEN_HAUT, FEN_BAS, FEN_AR = (40, 64), (39, 63), (36, 60)
H_BANC, H_DIN, H_TABLE, H_COMPTOIR, H_SUPERP = 16, 18, 28, 34, 50


def rect(v, r, **k):
    x, y, w, h = r
    v.rect(x, y, w, h, **k)


def murs(v, f, porte=True):
    o = [(0, 0), (L, 0), (L, B), (0, B)]
    i = [(T, T), (L - T, T), (L - T, B - T), (T, B - T)]
    pts = lambda P: " ".join(f"{a:.2f},{b:.2f}" for a, b in (v.P(*p) for p in P))
    f.add(f'<path d="M{pts(o)}Z M{pts(i[::-1])}Z" fill="#9aa1a5" stroke="#111" stroke-width="1" fill-rule="evenodd"/>')
    # lambris : liseré bois sur la face intérieure
    v.poly(i, fill="none", stroke=PIN_F, sw=2.2)
    for (a, b), y0 in ((FEN_HAUT, 0), (FEN_BAS, B - T)):
        v.rect(a, y0, b - a, T, fill="#fff", stroke="#111", sw=0.5)
        v.line(a, y0 + T / 2, b, y0 + T / 2, sw=0.4)
    v.rect(L - T, FEN_AR[0], T, FEN_AR[1] - FEN_AR[0], fill="#fff", stroke="#111", sw=0.5)
    v.line(L - T / 2, FEN_AR[0], L - T / 2, FEN_AR[1], sw=0.4)
    p0, p1 = PORTE
    v.rect(-0.2, p0, T + 0.4, p1 - p0, fill="#fff", stroke="none")
    if porte:
        v.line(0, p0, T, p0, sw=1); v.line(0, p1, T, p1, sw=1)
        w = p1 - p0
        v.rect(-w, p1 - 1.2, w, 1.2, fill="#fff", stroke="#111", sw=0.7)
        v.arc(0, p1, w, -w, p1, 0, p0)


def planches(v, r, pas=6, sens="x"):
    """Lignes de lambris / planches sur un meuble."""
    x, y, w, h = r
    if sens == "x":
        k = y + pas
        while k < y + h - 0.5:
            v.line(x, k, x + w, k, stroke=PIN_F, sw=0.3); k += pas
    else:
        k = x + pas
        while k < x + w - 0.5:
            v.line(k, y, k, y + h, stroke=PIN_F, sw=0.3); k += pas


def trous(v, size=6.2, nuit=False):
    for cx, cy, nom in TROUS:
        if nuit and cx > DIN_H[0]:
            continue
        v.circle(cx, cy, 5, fill="#222", stroke="#000", sw=0.6)
        v.circle(cx, cy, 3.6, stroke="#555", sw=0.5)
        v.text(cx, cy + 1.6 if size > 5.5 else cy + 1.3, nom, size=size, anchor="middle", weight="bold", fill="#fff")


def cuisine(v, detail=True):
    rect(v, CUISINE, fill=PIN, stroke=PIN_F, sw=0.8)
    x, y, w, h = CUISINE
    v.rect(x + 1.5, y + 1.5, w - 3, h - 3, fill="#d8d2c4", stroke="#9b9384", sw=0.5)   # dessus imitation pierre
    v.rect(x + 3, y + 3.5, 20, 13, fill="#cfd5d9", stroke="#555", sw=0.6)
    for cx in (x + 8, x + 18):
        v.circle(cx, y + 10, 3.2, stroke="#333", sw=0.8)
        v.circle(cx, y + 10, 1.4, stroke="#333", sw=0.5)
    v.rect(x + 27, y + 4.5, 11, 11, fill="#fff", stroke="#555", sw=0.6)
    v.circle(x + 32.5, y + 10, 0.8, fill="#555", stroke="none")
    if detail:
        v.text(x + 13, y + 2.6, "réchaud 2 feux", size=5, anchor="middle")
        v.text(x + 32.5, y + 2.6, "bassine", size=5, anchor="middle")


def mobilier(v, mode="plan", detail=True):
    """mode : 'plan', 'jour' ou 'nuit'."""
    rect(v, VESTIAIRE, fill=PIN, stroke=PIN_F, sw=0.6)
    # banc-coffre côté haut + lit rabattable
    rect(v, BANC, fill=PIN, stroke=PIN_F, sw=0.8)
    planches(v, BANC, pas=5)
    if mode == "nuit":
        rect(v, SUPERP, fill=MATELAS, stroke="#7f95a8", sw=0.8)
        v.rect(SUPERP[0] + 2, SUPERP[1] + 2, 9, SUPERP[3] - 4, fill="#fff", stroke="#7f95a8", sw=0.5)
    else:
        rect(v, SUPERP, stroke="#7f95a8", sw=0.7, dash="5,3")
    for xc in (SUPERP[0] + 4, SUPERP[0] + SUPERP[2] - 4):     # chaînes
        v.line(xc, SUPERP[1], xc, SUPERP[1] + SUPERP[3], stroke="#888", sw=0.6, dash="1,1.5")
    # dînette
    for r in (DIN_H, DIN_B):
        rect(v, r, fill=PIN, stroke=PIN_F, sw=0.8)
        x, y, w, h = r
        dos = (x, y, w, 4) if r is DIN_H else (x, y + h - 4, w, 4)
        assise = (x + 1, y + 4, w - 2, h - 5) if r is DIN_H else (x + 1, y + 1, w - 2, h - 5)
        rect(v, dos, fill="#6b4e2e", stroke="none")
        rect(v, assise, fill=COUSSIN, stroke="#111", sw=0.5)
    if mode == "nuit":
        v.rect(DIN_H[0] + 1, DIN_H[1] + 4, DIN_H[2] - 2, (DIN_B[1] + DIN_B[3] - 4) - (DIN_H[1] + 4), fill=MATELAS, stroke="#7f95a8", sw=0.8)
        for k in range(2):
            v.rect(L - T - 11, DIN_H[1] + 6 + k * 22, 9, 20, fill="#fff", stroke="#7f95a8", sw=0.5)
    else:
        rect(v, TABLE, fill="#f4ecdc", stroke="#8a7a5c", sw=0.9)
        v.circle(TABLE[0] + TABLE[2] / 2, TABLE[1] + TABLE[3] / 2, 1.6, fill="#555", stroke="none")
    # cuisine, garde-manger, chauffage
    cuisine(v, detail)
    rect(v, GARDE, fill=PIN, stroke=PIN_F, sw=0.7)
    planches(v, GARDE, pas=5)
    rect(v, CHAUF, fill="#fde2df", stroke=ROUGE, sw=0.9)
    v.rect(T, 65, 24, B - T - 65, stroke=ROUGE, sw=0.5, dash="3,2")
    trous(v, 6.2 if detail else 4.6, nuit=(mode == "nuit"))


# =============================================================================
def f_plan():
    f = Feuille(1, "Plan d'aménagement")
    titre_vue(f, 40, 40, "PLAN D'AMÉNAGEMENT — STYLE CHALET", "Échelle 5/8 po = 1 pi (1:19,2) · avant à gauche · 2 adultes + 1 ado")
    v = Vue(f, 178, 104, 19.2)
    v.poly([(-c.NEZ, 0.75), (-30, B / 2), (-c.NEZ, B - 0.75)], close=False, stroke="#999", sw=1, dash="5,3")
    v.text(-20, B / 2 + 24, "timon", size=6, anchor="middle", fill="#777")
    v.text(-20, B / 2 + 28.5, "amovible", size=6, anchor="middle", fill="#777")
    murs(v, f)
    mobilier(v, "plan")
    lab = lambda x, y, t, **k: v.text(x, y, t, size=k.pop("size", 7), anchor=k.pop("anchor", "middle"), **k)
    lab(49.5, 9, "BANC-COFFRE (assise 16 po)", weight="bold", size=6.5)
    lab(49.5, 26.5, "lit rabattable de l'ado au-dessus, 28 × 75, sur chaînes", size=5.6, fill="#55687a")
    lab(114, 30, "TABLE 36 × 30", size=6, weight="bold", fill="#6b5a3e")
    lab(114, 50.5, "pied amovible", size=5.4, fill="#6b5a3e")
    lab(114, 12.5, "BANQUETTE", size=6, weight="bold", fill="#fff")
    lab(114, 81, "BANQUETTE", size=6, weight="bold", fill="#fff")
    lab(114, 70, "DÎNETTE 4 PLACES → LIT DOUBLE 54 × 90", size=6, weight="bold")
    lab(51, 92, "COMPTOIR CUISINE 42 × 20 · h. 34 po", size=5.6, weight="bold")
    lab(79.5, 84, "garde-", size=5.2)
    lab(79.5, 88, "manger", size=5.2)
    lab(9, 84.5, "CHAUF.", size=5.2, weight="bold", fill=ROUGE)
    lab(9, 88.5, "ventouse", size=5, fill=ROUGE)
    lab(7.5, 13, "manteaux", size=4.8, rot=-90)
    lab(22, 48.5, "ENTRÉE", size=6.5, weight="bold", fill="#777")
    lab(16, 69, "dégagement", size=4.8, fill=ROUGE)
    v.text(-14, PORTE[0] - 3, "PORTE 28 × 70", size=6.2, weight="bold", anchor="middle")
    v.text(-14, PORTE[0] + 1.5, "ouvre vers l'ext.", size=5.4, italic=True, anchor="middle")
    lab(80, 47, "trous ronds Ø 10 po à couvercle", size=5.6, fill="#333")
    v.dim(0, 0, L, 0, -24, f"{fi(L)} hors-tout")
    v.dim(T, 0, BANC[0], 0, -10, size=5.4)
    v.dim(BANC[0], 0, DIN_H[0], 0, -10, size=5.6)
    v.dim(DIN_H[0], 0, L - T, 0, -10, size=5.6)
    v.dim(L, 0, L, B, 24, f"{fi(B)} hors-tout")
    v.dim(L, T, L, B - T, 12, "lit " + fi(B - 2 * T), size=5.6)
    v.dim(CUISINE[0], B, CUISINE[0] + CUISINE[2], B, 20, size=5.6)
    v.dim(T, BANC[1] + BANC[3], T, CUISINE[1], -40, "allée " + fi(CUISINE[1] - BANC[1] - BANC[3]), size=5.6)
    return f


# =============================================================================
def f_jour_nuit():
    f = Feuille(2, "Mode jour / mode nuit")
    titre_vue(f, 40, 40, "MODE JOUR : ON PÊCHE, ON MANGE", "Échelle 1:32 · lit de l'ado relevé, dînette montée")
    titre_vue(f, 420, 40, "MODE NUIT : 3 PLACES POUR DORMIR", "Échelle 1:32 · dînette en lit double, lit de l'ado baissé")
    for x0, mode in ((60, "jour"), (430, "nuit")):
        v = Vue(f, x0, 96, 32)
        murs(v, f, porte=False)
        v.text(-3, (PORTE[0] + PORTE[1]) / 2, "porte", size=5.4, anchor="middle", rot=-90)
        mobilier(v, mode, detail=False)
        if mode == "jour":
            for (x, y) in [(40, 14), (72, 14), (104, 16), (124, 80)]:
                v.circle(x, y, 3.2, fill="#ffd27a", stroke="#a87b1d", sw=0.6)
        else:
            for (x, y) in [(20, 17), (128, 30), (128, 62)]:
                v.circle(x, y, 3.2, fill="#ffd27a", stroke="#a87b1d", sw=0.6)
            v.text(49.5, 17, "ado (en hauteur)", size=5.6, anchor="middle", weight="bold")
            v.text(110, 48, "2 adultes", size=6, anchor="middle", weight="bold")
    f.add('<circle cx="70" cy="336" r="4" fill="#ffd27a" stroke="#a87b1d" stroke-width="0.6"/>')
    f.text(80, 339, "= une personne", size=6.5)
    notes(f, 40, 372, "COMMENT ÇA MARCHE", [
        "Jour : la dînette reçoit 4 personnes. On pêche à table (T4, T5 sous la table) et sur le banc-coffre (T1, T2). Le lit de l'ado est relevé à plat contre le mur, retenu par ses chaînes.",
        "Soir : on retire le pied de la table, la table se pose sur des tasseaux au niveau des banquettes, 2 planches d'appoint (rangées sous les banquettes) complètent : plateforme de 54 × 90 po. Les coussins des banquettes + 2 coussins d'appoint font le matelas des adultes.",
        "L'ado baisse son lit rabattable : 2 chaînes le tiennent à plat à 50 po du plancher, au-dessus du banc. 30 po de dégagement au-dessus du matelas.",
        "Couvercles des trous fermés la nuit (froid et sécurité). Tout est vissé : rien ne bouge en remorquage.",
    ], larg=130, size=7, inter=10)
    return f


# =============================================================================
def f_coupe_details():
    f = Feuille(3, "Coupe, finition et sécurité")
    titre_vue(f, 40, 40, "COUPE VERS L'ARRIÈRE (à X = 5 pi), MODE NUIT", "Échelle 1:24 (1/2 po = 1 pi)")
    v = Vue(f, 100, 412, 24, flip=True)
    zp = c.Z_PL
    v.rect(-8, -6, B + 16, 6, fill="url(#glace)", stroke="none")
    v.line(-8, 0, B + 8, 0, stroke=BLEU, sw=0.8)
    v.rect(0, c.Z_P, B, c.CAD + c.CP, fill="#e9dcc3", stroke="#111", sw=0.5)
    for y0, _ in c.PATIN_Y:
        v.rect(y0, 0, 1.5, c.Z_P, fill="url(#hach)", stroke="#111", sw=0.5)
    # murs coupés + lambris
    v.rect(0, zp, T - 0.6, c.H_HAUT, fill="#cfcfcf", stroke="#111", sw=0.5)
    v.rect(T - 0.6, zp, 0.6, c.H_HAUT, fill=PIN, stroke=PIN_F, sw=0.4)
    v.rect(B - T + 0.6, zp, T - 0.6, c.H_BAS, fill="#cfcfcf", stroke="#111", sw=0.5)
    v.rect(B - T, zp, 0.6, c.H_BAS, fill=PIN, stroke=PIN_F, sw=0.4)
    v.poly([(-c.DEB_E, c.zr(-c.DEB_E)), (B + c.DEB_E, c.zr(B + c.DEB_E)), (B + c.DEB_E, c.zr(B + c.DEB_E) + c.TOIT), (-c.DEB_E, c.zr(-c.DEB_E) + c.TOIT)],
           fill="#7d858a", stroke="#111", sw=0.6)
    v.poly([(T, c.zr(T) - 0.6), (B - T, c.zr(B - T) - 0.6), (B - T, c.zr(B - T)), (T, c.zr(T))], fill=PIN, stroke=PIN_F, sw=0.4)
    v.circle(B / 2, c.zr(B / 2) - 1.2, 1.2, fill="#ffe9a8", stroke="#a87b1d", sw=0.4)
    # dînette au fond (en élévation), en lit
    for y0 in (DIN_H[1], DIN_B[1]):
        v.rect(y0, zp, 20, H_DIN - 4, fill=PIN, stroke=PIN_F, sw=0.6)
    v.rect(T, zp + H_DIN - 4, B - 2 * T, 4, fill=COUSSIN, stroke="#111", sw=0.5)
    v.rect(T, zp + H_DIN, B - 2 * T, 2, fill=MATELAS, stroke="#7f95a8", sw=0.4)
    v.rect(DIN_H[1] + 20, zp + H_DIN - 5.5, B - 2 * T - 40, 1.5, fill="#c9b48a", stroke="#111", sw=0.4)
    v.text(B / 2, zp + H_DIN - 9, "table abaissée + planches", size=5, anchor="middle")
    v.text(B / 2, zp + H_DIN + 5, "lit double des adultes (au fond) 54 × 90", size=5.4, anchor="middle")
    for y0, h in ((T, c.H_HAUT), (B - T - 4, c.H_BAS)):
        v.rect(y0, zp + H_DIN, 4, 16, fill="#6b4e2e", stroke="none")
    v.rect(FEN_AR[0], zp + 40, 24, 12, fill="#dbeaf5", stroke="#999", sw=0.5)
    # banc-coffre + lit rabattable (coupés)
    v.rect(T, zp, BANC[3], H_BANC, fill="#fff", stroke="none")
    v.rect(T, zp, BANC[3], H_BANC, fill="url(#hach)", stroke="#111", sw=0.6)
    v.rect(T, zp + H_SUPERP, SUPERP[3], 1.5, fill="#c9b48a", stroke="#111", sw=0.5)
    v.rect(T, zp + H_SUPERP + 1.5, SUPERP[3], 4, fill=MATELAS, stroke="#7f95a8", sw=0.5)
    v.line(T + SUPERP[3], zp + H_SUPERP + 1.5, T + 0.5, zp + H_SUPERP + 26, stroke="#666", sw=0.7, dash="1.2,1.2")
    v.rect(T, zp + H_SUPERP, 1.5, SUPERP[3], stroke="#7f95a8", sw=0.5, dash="3,2")
    v.text(T + 14, zp + H_SUPERP + 9.5, "lit ado", size=5.2, anchor="middle")
    v.text(T + 3, zp + H_SUPERP + 27, "relevé le jour", size=4.6, fill="#55687a")
    v.text(T + 19, zp + H_SUPERP + 14, "chaîne", size=4.6, fill="#666")
    # comptoir cuisine (coupé)
    v.rect(CUISINE[1], zp, CUISINE[3], H_COMPTOIR, fill="#fff", stroke="none")
    v.rect(CUISINE[1], zp, CUISINE[3], H_COMPTOIR, fill="url(#hach)", stroke="#111", sw=0.6)
    v.rect(CUISINE[1] + 3, zp + H_COMPTOIR, 9, 4, fill="#cfd5d9", stroke="#555", sw=0.5)
    v.text(CUISINE[1] + 7.5, zp + H_COMPTOIR + 6.5, "réchaud", size=4.8, anchor="middle")
    v.dim(T, zp, T, zp + H_BANC, -18, size=5)
    v.dim(T, zp, T, zp + H_SUPERP, -32, size=5)
    v.dim(T + SUPERP[3] + 2, zp + H_SUPERP + 5.5, T + SUPERP[3] + 2, c.zr(T + SUPERP[3] + 2) - 0.6, 0, fi(c.zr(T + SUPERP[3] + 2) - 0.6 - zp - H_SUPERP - 5.5) + " libre", size=5)
    v.dim(B - T, zp, B - T, zp + H_COMPTOIR, 14, size=5)
    v.dim(26, zp, 26, zp + H_DIN, 0, size=5)

    y = notes(f, 450, 70, "FINITION « CHALET »", [
        "Lambris de pin aux murs et au plafond, comme la photo. Pour le poids, prendre du lambris mince 5/16 po (environ 0,9 lb/pi²) plutôt que du 1×6 de 3/4 po.",
        "Lambris mince sur murs et plafond : environ 290 lb, contre environ 100 lb pour le panneau 1/4 prévu. En 1×6 plein, on dépasserait 400 lb.",
        "Coussins de banquette en vinyle marin foncé, dessus de comptoir stratifié imitation pierre, plafonnier DEL 12 V au centre.",
        "Plancher en vinyle ou en caoutchouc (pas de tapis : l'eau des trous et la neige des bottes).",
    ], larg=52, size=6.6, inter=8.6)
    y = notes(f, 450, y + 4, "DORMIR EN SÉCURITÉ", [
        "Chauffage à ventouse (chambre de combustion scellée) obligatoire pour dormir, pas de chaufferette portative ouverte.",
        "Détecteur de CO et détecteur de fumée près des lits. Réchaud jamais allumé pour chauffer ni pendant le sommeil.",
        "Bonbonnes à l'extérieur. Grilles de ventilation ouvertes. Extincteur ABC près de la porte.",
    ], larg=52, size=6.6, inter=8.6)
    notes(f, 450, y + 4, "POIDS", [
        "Dînette, lit rabattable, cuisine et coussins : environ 150 lb. Avec le lambris mince : environ 340 lb de plus que la version pêche seule.",
    ], larg=52, size=6.6, inter=8.6)
    return f


if __name__ == "__main__":
    for fe in (f_plan(), f_jour_nuit(), f_coupe_details()):
        (ICI / f"feuille-{fe.num}.svg").write_text(fe.svg(), encoding="utf-8")
    print("ok")
