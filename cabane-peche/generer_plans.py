#!/usr/bin/env python3
"""Plans 2D d'une cabane à pêche blanche 8 x 10 pi sur patins.

Produit 4 feuilles SVG (format lettre paysage) dans ce dossier :
  1. Vue en plan / aménagement (1:24)
  2. Élévations avant et latérale (1:32)
  3. Ossature : plancher (1:24) et murs (1:32)
  4. Coupe A-A (1:24) et liste de matériaux
Puis : node exporter.js  -> PDF + PNG.

Toutes les cotes du dessin sont en pouces réels.
"""
from pathlib import Path

ICI = Path(__file__).parent
W, H = 792, 612  # lettre paysage en points
DATE = "2026-11-07"
NB_FEUILLES = 4

# --- Paramètres de la cabane (pouces) --------------------------------------
L = 120          # longueur hors-tout (10 pi)
B = 96           # largeur hors-tout (8 pi)
T = 3.5          # épaisseur des murs (2x3 + OSB + finition)
H_BAS = 72       # mur côté bas (côté gauche), plancher -> dessus sablière
H_HAUT = 84      # mur côté haut (côté droit)
PATIN_H = 7.25   # 2x8 sur chant
SOL_H = 5.5      # solives 2x6
CP = 0.75        # contreplaqué de plancher
Z_PL = PATIN_H + SOL_H + CP   # dessus du plancher au-dessus de la glace = 13.5
TOIT = 5.0       # chevron 2x4 + OSB + tôle sur fourrures
DEBORD = 6
PORTE = (50, 80)                 # ouverture finie de la porte (x)
TRAPPES = [(18, 34), (18, 82), (66, 34), (66, 82)]  # coin sup. gauche, 12x12
FEN_Y = (40, 64)                 # fenêtres des murs latéraux (plan)
FEN_Z = (32, 44)                 # hauteur des fenêtres au-dessus du plancher


def wtop(x):
    """Dessus de sablière au-dessus du plancher, selon x (pente 1,5:12)."""
    return H_BAS + (H_HAUT - H_BAS) * x / B


def fi(po):
    """Pouces -> pieds-pouces, au 1/4 près : 8'-0", 2'-10 1/2"."""
    q = round(po * 4)
    pi, r = divmod(q, 48)
    ent, frac = divmod(r, 4)
    fr = {0: "", 1: " 1/4", 2: " 1/2", 3: " 3/4"}[frac]
    return f"{pi}'-{ent}{fr}\""


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Feuille:
    def __init__(self, num, titre):
        self.num, self.titre = num, titre
        self.el = []

    def add(self, s):
        self.el.append(s)

    # primitives en points papier
    def text(self, x, y, s, size=8, anchor="start", weight="normal", rot=0, fill="#111", italic=False):
        tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
        st = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}"{st}{tr}>{esc(s)}</text>')

    def svg(self):
        cadre = [
            f'<rect x="18" y="18" width="{W-36}" height="{H-36}" fill="none" stroke="#111" stroke-width="1.2"/>',
            f'<line x1="18" y1="{H-58}" x2="{W-18}" y2="{H-58}" stroke="#111" stroke-width="1"/>',
        ]
        cols = [18, 300, 470, 560, 660, W - 18]
        for c in cols[1:-1]:
            cadre.append(f'<line x1="{c}" y1="{H-58}" x2="{c}" y2="{H-18}" stroke="#111" stroke-width="0.6"/>')
        champs = [
            ("PROJET", "Cabane à pêche blanche 8 × 10 pi sur patins"),
            ("FEUILLE", self.titre),
            ("DATE", DATE),
            ("STATUT", "Préliminaire"),
            ("NO", f"{self.num} / {NB_FEUILLES}"),
        ]
        for (lab, val), x0 in zip(champs, cols):
            cadre.append(f'<text x="{x0+6}" y="{H-46}" font-size="6" fill="#555">{lab}</text>')
            cadre.append(f'<text x="{x0+6}" y="{H-29}" font-size="9.5" font-weight="bold" fill="#111">{esc(val)}</text>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'font-family="DejaVu Sans, Arial, sans-serif">'
                f'<rect width="{W}" height="{H}" fill="#fff"/>'
                + DEFS + "".join(cadre) + "".join(self.el) + "</svg>")


DEFS = """<defs>
<pattern id="hach" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <line x1="0" y1="0" x2="0" y2="5" stroke="#555" stroke-width="0.6"/></pattern>
<pattern id="bois" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <line x1="0" y1="0" x2="0" y2="4" stroke="#7a5a2a" stroke-width="0.5"/>
  <line x1="0" y1="0" x2="4" y2="0" stroke="#7a5a2a" stroke-width="0.5"/></pattern>
<pattern id="glace" width="8" height="8" patternUnits="userSpaceOnUse">
  <line x1="0" y1="8" x2="8" y2="0" stroke="#7fb3d5" stroke-width="0.6"/></pattern>
<pattern id="isol" width="6" height="6" patternUnits="userSpaceOnUse">
  <circle cx="3" cy="3" r="1.1" fill="none" stroke="#c0392b" stroke-width="0.4"/></pattern>
</defs>"""


class Vue:
    """Vue à l'échelle. flip=True : z vers le haut (élévations, coupes)."""

    def __init__(self, f, ox, oy, echelle, flip=False):
        self.f, self.ox, self.oy, self.s, self.flip = f, ox, oy, 72 / echelle, flip

    def P(self, x, y):
        return (self.ox + x * self.s, self.oy - y * self.s if self.flip else self.oy + y * self.s)

    def poly(self, pts, fill="none", stroke="#111", sw=0.8, dash=None, close=True):
        d = " ".join(f"{a:.2f},{b:.2f}" for a, b in (self.P(*p) for p in pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        tag = "polygon" if close else "polyline"
        self.f.add(f'<{tag} points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def rect(self, x, y, w, h, **k):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], **k)

    def line(self, x1, y1, x2, y2, stroke="#111", sw=0.8, dash=None):
        (a, b), (c, d) = self.P(x1, y1), self.P(x2, y2)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.f.add(f'<line x1="{a:.2f}" y1="{b:.2f}" x2="{c:.2f}" y2="{d:.2f}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def circle(self, x, y, r, fill="none", stroke="#111", sw=0.6, dash=None):
        a, b = self.P(x, y)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.f.add(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="{r*self.s:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def arc(self, cx, cy, r, x1, y1, x2, y2, sw=0.5, dash="3,2"):
        (a, b), (c, d) = self.P(x1, y1), self.P(x2, y2)
        rr = r * self.s
        self.f.add(f'<path d="M{a:.2f},{b:.2f} A{rr:.2f},{rr:.2f} 0 0 1 {c:.2f},{d:.2f}" fill="none" '
                   f'stroke="#111" stroke-width="{sw}" stroke-dasharray="{dash}"/>')

    def text(self, x, y, s, **k):
        a, b = self.P(x, y)
        self.f.text(a, b, s, **k)

    def dim(self, x1, y1, x2, y2, off, label=None, size=7):
        """Cote horizontale (y1==y2) ou verticale (x1==x2). off en points."""
        label = label or fi(abs((x2 - x1) if y1 == y2 else (y2 - y1)))
        (a, b), (c, d) = self.P(x1, y1), self.P(x2, y2)
        g = 'stroke="#333" stroke-width="0.45"'
        if abs(b - d) < 0.01:  # horizontale
            yy = b + off
            sg = 1 if off > 0 else -1
            self.f.add(f'<line x1="{a:.2f}" y1="{b+2*sg:.2f}" x2="{a:.2f}" y2="{yy+3*sg:.2f}" {g}/>')
            self.f.add(f'<line x1="{c:.2f}" y1="{d+2*sg:.2f}" x2="{c:.2f}" y2="{yy+3*sg:.2f}" {g}/>')
            self.f.add(f'<line x1="{min(a,c)-3:.2f}" y1="{yy:.2f}" x2="{max(a,c)+3:.2f}" y2="{yy:.2f}" {g}/>')
            for x in (a, c):
                self.f.add(f'<line x1="{x-2.5:.2f}" y1="{yy+2.5:.2f}" x2="{x+2.5:.2f}" y2="{yy-2.5:.2f}" stroke="#111" stroke-width="0.9"/>')
            self.f.text((a + c) / 2, yy - 2.5, label, size=size, anchor="middle")
        else:  # verticale
            xx = a + off
            sg = 1 if off > 0 else -1
            self.f.add(f'<line x1="{a+2*sg:.2f}" y1="{b:.2f}" x2="{xx+3*sg:.2f}" y2="{b:.2f}" {g}/>')
            self.f.add(f'<line x1="{c+2*sg:.2f}" y1="{d:.2f}" x2="{xx+3*sg:.2f}" y2="{d:.2f}" {g}/>')
            self.f.add(f'<line x1="{xx:.2f}" y1="{min(b,d)-3:.2f}" x2="{xx:.2f}" y2="{max(b,d)+3:.2f}" {g}/>')
            for y in (b, d):
                self.f.add(f'<line x1="{xx-2.5:.2f}" y1="{y+2.5:.2f}" x2="{xx+2.5:.2f}" y2="{y-2.5:.2f}" stroke="#111" stroke-width="0.9"/>')
            self.f.text(xx - 2.5, (b + d) / 2, label, size=size, anchor="middle", rot=-90)


def titre_vue(f, x, y, titre, echelle):
    f.text(x, y, titre, size=11, weight="bold")
    f.text(x, y + 11, echelle, size=7, fill="#555")


def callout(v, x, y, n, dx=0, dy=0):
    """Pastille numérotée (dx, dy en points depuis le point visé, avec ligne de rappel)."""
    a, b = v.P(x, y)
    cx, cy = a + dx, b + dy
    if dx or dy:
        v.f.add(f'<line x1="{a:.2f}" y1="{b:.2f}" x2="{cx:.2f}" y2="{cy:.2f}" stroke="#c0392b" stroke-width="0.5"/>')
        v.f.add(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="1.2" fill="#c0392b"/>')
    v.f.add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="6" fill="#fff" stroke="#c0392b" stroke-width="0.8"/>')
    v.f.text(cx, cy + 2.6, str(n), size=7, anchor="middle", weight="bold", fill="#c0392b")


def notes(f, x, y, titre, lignes, larg=60, size=7.2, inter=10):
    f.text(x, y, titre, size=9, weight="bold")
    y += 14
    for i, l in enumerate(lignes, 1):
        mots, cur, out = l.split(), "", []
        for m in mots:
            if len(cur) + len(m) + 1 > larg:
                out.append(cur)
                cur = m
            else:
                cur = (cur + " " + m).strip()
        out.append(cur)
        f.text(x, y, f"{i}.", size=size, weight="bold")
        for o in out:
            f.text(x + 12, y, o, size=size)
            y += inter
        y += 2.5
    return y


# =============================================================================
# FEUILLE 1 — VUE EN PLAN
# =============================================================================
def feuille_plan():
    f = Feuille(1, "Vue en plan — aménagement")
    titre_vue(f, 40, 38, "VUE EN PLAN — AMÉNAGEMENT", "Échelle 1:24 (1/2 po = 1 pi) si imprimé à 100 %, format lettre")
    v = Vue(f, 120, 100, 24)
    # murs (poché)
    o = [(0, 0), (B, 0), (B, L), (0, L)]
    i = [(T, T), (B - T, T), (B - T, L - T), (T, L - T)]
    pts = lambda P: " ".join(f"{a:.2f},{b:.2f}" for a, b in (v.P(*p) for p in P))
    f.add(f'<path d="M{pts(o)}Z M{pts(i[::-1])}Z" fill="#bbb" stroke="#111" stroke-width="1" fill-rule="evenodd"/>')
    # porte : ouverture + battant ouvrant vers l'extérieur (penture côté droit)
    v.rect(PORTE[0], L - T - 0.2, PORTE[1] - PORTE[0], T + 0.4, fill="#fff", stroke="none")
    v.line(PORTE[0], L - T, PORTE[0], L, sw=1)
    v.line(PORTE[1], L - T, PORTE[1], L, sw=1)
    w = PORTE[1] - PORTE[0]
    v.rect(PORTE[1] - 1.5, L, 1.5, w, fill="#fff", stroke="#111", sw=0.8)
    v.arc(PORTE[1], L, w, PORTE[1], L + w, PORTE[0], L)
    v.text(PORTE[0] + 4, L + 16, "PORTE 30 × 72 po", size=6.5)
    v.text(PORTE[0] + 4, L + 21, "ouvre vers l'ext.", size=6.5, italic=True)
    # fenêtres
    for x0 in (0, B - T):
        v.rect(x0, FEN_Y[0], T, FEN_Y[1] - FEN_Y[0], fill="#fff", stroke="#111", sw=0.6)
        v.line(x0 + T / 2, FEN_Y[0], x0 + T / 2, FEN_Y[1], sw=0.5)
    v.text(-3, (FEN_Y[0] + FEN_Y[1]) / 2, "FENÊTRE 24 × 12", size=6, anchor="middle", rot=-90)
    v.text(B + 4, (FEN_Y[0] + FEN_Y[1]) / 2, "FENÊTRE 24 × 12", size=6, anchor="middle", rot=90)
    # bancs
    for x0 in (T, B - T - 12):
        v.rect(x0, T, 12, L - 2 * T, fill="#f3ead8", stroke="#7a5a2a", sw=0.7)
        for yy in range(int(T) + 24, int(L - T), 24):
            v.line(x0, yy, x0 + 12, yy, stroke="#7a5a2a", sw=0.3, dash="2,2")
    v.text(T + 6, 100, "BANC prof. 12 po · haut. 17 po", size=6.3, anchor="middle", rot=-90)
    v.text(B - T - 6, 100, "BANC prof. 12 po · haut. 17 po", size=6.3, anchor="middle", rot=-90)
    # chauffage + plaque incombustible
    v.rect(34, T, 28, 22, stroke="#c0392b", sw=0.5, dash="3,2")
    v.rect(40, 6, 16, 12, fill="#fde2df", stroke="#c0392b", sw=0.9)
    v.text(48, 13.2, "CHAUFFAGE", size=5.6, anchor="middle", weight="bold", fill="#c0392b")
    v.text(48, 23.5, "plaque incombustible", size=5, anchor="middle", fill="#c0392b")
    # trappes
    for n, (tx, ty) in enumerate(TRAPPES, 1):
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke="#1f5f8b", sw=1)
        v.circle(tx + 6, ty + 6, 4, stroke="#1f5f8b", dash="2,1.5")
        v.text(tx + 6, ty + 7.6, f"T{n}", size=6.5, anchor="middle", weight="bold", fill="#1f5f8b")
    v.text(48, 60, "ALLÉE", size=7, anchor="middle", fill="#777")
    v.text(48, 65, "36 po entre trappes", size=5.6, anchor="middle", fill="#777")
    # ventilation
    v.rect(20, L - T, 8, T, fill="#444", stroke="#111", sw=0.5)
    v.text(24, L + 11, "VENT. BASSE", size=5.5, anchor="middle")
    v.rect(70, 0, 8, T, fill="#444", stroke="#111", sw=0.5)
    v.text(74, -2, "VENT. HAUTE", size=5.5, anchor="middle")
    # coupe A-A
    yA = 40
    v.line(-14, yA, B + 14, yA, stroke="#c0392b", sw=0.7, dash="10,3,2,3")
    for xa in (-14, B + 14):
        a, b = v.P(xa, yA)
        f.add(f'<polygon points="{a-4:.1f},{b:.1f} {a+4:.1f},{b:.1f} {a:.1f},{b-9:.1f}" fill="#c0392b"/>')
        f.text(a, b + 10, "A", size=9, anchor="middle", weight="bold", fill="#c0392b")
    # côté bas / côté haut
    v.text(-6, 100, "CÔTÉ BAS (mur 6'-0\")", size=6.3, anchor="middle", rot=-90, fill="#555")
    v.text(B + 4, 100, "CÔTÉ HAUT (mur 7'-0\")", size=6.3, anchor="middle", rot=90, fill="#555")
    # cotes
    v.dim(0, 0, B, 0, -30, f"{fi(B)}  (2,44 m)")
    for a, b_ in [(0, 18), (18, 30), (30, 66), (66, 78), (78, B)]:
        v.dim(a, 0, b_, 0, -15, size=6)
    v.dim(0, 0, 0, L, -52, f"{fi(L)}  (3,05 m)")
    for a, b_ in [(0, 34), (34, 46), (46, 82), (82, 94), (94, L)]:
        v.dim(B, a, B, b_, 40, size=6)
    for a, b_ in [(0, PORTE[0]), PORTE, (PORTE[1], B)]:
        v.dim(a, L, b_, L, 14, size=6)

    y = notes(f, 482, 96, "NOTES", [
        "Dimensions hors-tout 8'-0\" × 10'-0\" (2,44 × 3,05 m). Largeur sous 8'-6\" : transportable sur remorque sans permis spécial.",
        "Plancher à 13 1/2 po au-dessus de la glace (patins 2×8 + solives 2×6 + CP 3/4).",
        "4 trappes T1 à T4 de 12 × 12 po, logées entre les solives. Couvercles affleurants en CP 3/4 avec poignée encastrée. Trou à la tarière de 8 à 10 po sous chaque trappe.",
        "Bancs de 12 po de profondeur et 17 po de hauteur sur toute la longueur, couvercles à charnières pour le rangement.",
        "Porte 30 × 72 po qui ouvre vers l'extérieur (libère l'intérieur). Loquet intérieur et cadenas extérieur.",
        "Toit à une pente : mur gauche 6'-0\", mur droit 7'-0\" (pente 1 1/2 : 12).",
        "Chauffage au propane homologué pour l'intérieur, posé sur une plaque incombustible. Respecter les dégagements du fabricant.",
        "Ventilation basse (porte) et haute (arrière) toujours ouvertes, détecteur de monoxyde de carbone (CO) à piles et extincteur ABC obligatoires.",
        "Afficher nom, adresse et téléphone du propriétaire à l'extérieur ; vérifier le règlement municipal (dates de pose et de retrait sur le lac).",
    ], larg=52)
    f.text(482, y + 8, "Cotes en pieds-pouces. Vérifier toutes les cotes au chantier.", size=6.5, italic=True, fill="#555")
    return f


# =============================================================================
# FEUILLE 2 — ÉLÉVATIONS
# =============================================================================
def glace(v, x1, x2, prof=6):
    v.rect(x1, -prof, x2 - x1, prof, fill="url(#glace)", stroke="none")
    v.line(x1, 0, x2, 0, stroke="#1f5f8b", sw=1)


def feuille_elevations():
    f = Feuille(2, "Élévations avant et latérale")
    titre_vue(f, 40, 44, "ÉLÉVATION AVANT (porte)", "Échelle 1:32 (3/8 po = 1 pi)")
    titre_vue(f, 420, 44, "ÉLÉVATION LATÉRALE DROITE (côté haut)", "Échelle 1:32 (3/8 po = 1 pi)")

    # --- avant -------------------------------------------------------------
    v = Vue(f, 95, 430, 32, flip=True)
    glace(v, -20, B + 20)
    for x0 in (6, 87):
        v.rect(x0, 0, 3, PATIN_H, fill="url(#bois)", stroke="#111", sw=0.7)
        v.circle(x0 + 1.5, 3.6, 0.9, stroke="#111", sw=0.6)
    v.rect(0, PATIN_H, B, SOL_H, fill="#e9dcc3", stroke="#111", sw=0.7)
    v.rect(0, PATIN_H + SOL_H, B, CP, fill="#d8c39a", stroke="#111", sw=0.5)
    v.poly([(0, Z_PL), (B, Z_PL), (B, Z_PL + wtop(B)), (0, Z_PL + wtop(0))], fill="#f7f4ee", stroke="#111", sw=1)
    # revêtement : lignes de tôle verticales
    for x in range(8, B, 8):
        v.line(x, Z_PL, x, Z_PL + wtop(x), stroke="#bbb", sw=0.35)
    # toit
    zr = lambda x: Z_PL + wtop(x)
    v.poly([(-DEBORD, zr(-DEBORD)), (B + DEBORD, zr(B + DEBORD)), (B + DEBORD, zr(B + DEBORD) + TOIT),
            (-DEBORD, zr(-DEBORD) + TOIT)], fill="#666", stroke="#111", sw=0.8)
    # porte
    v.rect(PORTE[0], Z_PL, 30, 72, fill="#fff", stroke="#111", sw=1)
    v.rect(PORTE[0] + 4, Z_PL + 4, 22, 64, stroke="#888", sw=0.4)
    v.circle(PORTE[0] + 4.5, Z_PL + 36, 0.9, fill="#111")
    for zz in (8, 36, 64):
        v.rect(PORTE[1] - 1.2, Z_PL + zz - 2, 1.2, 4, fill="#111", stroke="none")
    # ventilation basse
    v.rect(20, Z_PL + 4, 8, 4, fill="#444", stroke="#111", sw=0.5)
    # marche
    v.rect(PORTE[0] + 3, 0, 24, 6.75, fill="#e9dcc3", stroke="#111", sw=0.6, dash="3,1.5")
    v.text(PORTE[0] + 15, 2.3, "marche amovible", size=5.5, anchor="middle")
    v.text(24, Z_PL + 11, "vent. basse", size=5.5, anchor="middle")
    v.text(7.5, -10, "œillets de remorquage", size=5.5)
    # cotes
    v.dim(0, 0, B, 0, 30)
    v.dim(-DEBORD, zr(B + DEBORD) + TOIT, B + DEBORD, zr(B + DEBORD) + TOIT, -16, f"{fi(B + 2*DEBORD)} toit")
    v.dim(0, 0, 0, Z_PL, -16, size=6)
    v.dim(0, Z_PL, 0, Z_PL + wtop(0), -16, size=6)
    v.dim(B + DEBORD, 0, B + DEBORD, zr(B + DEBORD) + TOIT, 22, f"{fi(zr(B + DEBORD) + TOIT)} hors-tout")
    v.dim(B, Z_PL, B, Z_PL + wtop(B), 8, size=6)
    v.dim(PORTE[0], Z_PL, PORTE[0], Z_PL + 72, -8, size=6)

    # --- latérale droite --------------------------------------------------
    v = Vue(f, 455, 430, 32, flip=True)
    glace(v, -20, L + 20)
    v.poly([(0, 4), (6, 0), (L - 6, 0), (L, 4), (L, PATIN_H), (0, PATIN_H)], fill="url(#bois)", stroke="#111", sw=0.8)
    for u in (3, L - 3):
        v.circle(u, 3.8, 0.9, stroke="#111", sw=0.6)
    v.rect(0, PATIN_H, L, SOL_H, fill="#e9dcc3", stroke="#111", sw=0.7)
    v.rect(0, PATIN_H + SOL_H, L, CP, fill="#d8c39a", stroke="#111", sw=0.5)
    v.rect(0, Z_PL, L, H_HAUT, fill="#f7f4ee", stroke="#111", sw=1)
    for u in range(8, L, 8):
        v.line(u, Z_PL, u, Z_PL + H_HAUT, stroke="#bbb", sw=0.35)
    zt = Z_PL + H_HAUT + (H_HAUT - H_BAS) * DEBORD / B
    v.rect(-DEBORD, zt, L + 2 * DEBORD, TOIT, fill="#666", stroke="#111", sw=0.8)
    u0, u1 = L - FEN_Y[1], L - FEN_Y[0]
    v.rect(u0, Z_PL + FEN_Z[0], u1 - u0, FEN_Z[1] - FEN_Z[0], fill="#dbeaf5", stroke="#111", sw=1)
    v.line(u0, Z_PL + FEN_Z[0], u1, Z_PL + FEN_Z[1], stroke="#9cc", sw=0.4)
    v.text(3, Z_PL + H_HAUT - 6, "AVANT", size=6.5, weight="bold", fill="#555")
    v.text(L - 3, Z_PL + H_HAUT - 6, "ARRIÈRE", size=6.5, weight="bold", fill="#555", anchor="end")
    v.text((u0 + u1) / 2, Z_PL + FEN_Z[1] + 4, "fenêtre 24 × 12", size=5.8, anchor="middle")
    v.text(L / 2, 2.6, "patin 2×8 doublé, bouts biseautés", size=5.5, anchor="middle")
    v.dim(0, 0, L, 0, 30)
    v.dim(-DEBORD, zt + TOIT, L + DEBORD, zt + TOIT, -16, f"{fi(L + 2*DEBORD)} toit")
    v.dim(L, Z_PL, L, Z_PL + H_HAUT, 10, size=6)
    v.dim(L, 0, L, Z_PL, 10, size=6)
    v.dim(0, Z_PL, 0, Z_PL + FEN_Z[0], -10, size=6)
    v.dim(u0, Z_PL + FEN_Z[0], u1, Z_PL + FEN_Z[0], 10, size=6)

    notes(f, 40, 505, "FINITION", [
        "Revêtement extérieur : tôle d'acier prépeinte calibre 29 posée à la verticale sur OSB 7/16 (ou contreplaqué peint). Couleur foncée = gain solaire.",
        "Côté gauche : identique en miroir, mur de 6'-0\". Arrière : sans ouverture, ventilation haute sous le toit.",
    ], larg=150, inter=9)
    return f


# =============================================================================
# FEUILLE 3 — OSSATURE
# =============================================================================
def montant(v, x, z0, z1f, w=1.5, **k):
    """Montant vertical de x à x+w, du bas z0 jusqu'à une fonction de dessus."""
    v.poly([(x, z0), (x + w, z0), (x + w, z1f(x + w)), (x, z1f(x))], fill="#f3ead8", stroke="#7a5a2a", sw=0.6, **k)


def feuille_ossature():
    f = Feuille(3, "Ossature plancher et murs")
    titre_vue(f, 40, 44, "OSSATURE DU PLANCHER (vue de dessus)", "Échelle 1:24 — contreplaqué retiré")
    v = Vue(f, 110, 96, 24)
    bois = dict(fill="#f3ead8", stroke="#7a5a2a", sw=0.7)
    # patins (cachés)
    for x0 in (6, 87):
        v.rect(x0, -2, 3, L + 4, stroke="#1f5f8b", sw=0.7, dash="5,2.5")
    # rives
    v.rect(0, 0, 1.5, L, **bois)
    v.rect(B - 1.5, 0, 1.5, L, **bois)
    # solives
    ys = [0] + [16 * n - 0.75 for n in range(1, 8)] + [L - 1.5]
    for y in ys:
        v.rect(1.5, y, B - 3, 1.5, **bois)
    # chevêtres des trappes
    for tx, ty in TRAPPES:
        y0 = 16 * (ty // 16) + 0.75
        y1 = 16 * (ty // 16 + 1) - 0.75
        v.rect(tx - 1.5, y0, 1.5, y1 - y0, fill="#e7c9a0", stroke="#7a5a2a", sw=0.7)
        v.rect(tx + 12, y0, 1.5, y1 - y0, fill="#e7c9a0", stroke="#7a5a2a", sw=0.7)
        v.rect(tx, ty, 12, 12, fill="#e8f2fa", stroke="#1f5f8b", sw=0.8)
        v.text(tx + 6, ty + 7.5, "trappe", size=5.2, anchor="middle", fill="#1f5f8b")
    v.dim(0, 0, B, 0, -18)
    v.dim(0, 0, 0, L, -20)
    for n in range(0, 3):
        v.dim(B, 16 * n, B, 16 * (n + 1), 18, "16 po c/c" if n == 1 else fi(16), size=5.8)
    v.text(-2, L + 10, "Patins (pointillés bleus) : 2×8 traité doublé, 10'-0\", à 6 po des rives.", size=6)
    v.text(-2, L + 15.5, "Chevêtres 2×6 de chaque côté des trappes. Attaches anti-soulèvement solive/patin.", size=6)
    v.text(-2, L + 21, "Plancher : CP 3/4 traité, collé et vissé ; découper les 4 trappes après la pose.", size=6)

    # --- mur latéral droit (côté haut) ------------------------------------
    titre_vue(f, 420, 44, "OSSATURE MUR LATÉRAL DROIT (côté haut)", "Échelle 1:32 — 2×3 @ 16 po c/c, vue de l'intérieur")
    v = Vue(f, 455, 258, 32, flip=True)
    top = lambda x: H_HAUT - 1.5
    v.rect(0, 0, L, 1.5, **bois)
    v.rect(0, H_HAUT - 1.5, L, 1.5, **bois)
    w0, w1 = FEN_Y          # en vue intérieure, l'avant est à gauche : u = y
    for u in [0] + [16 * n - 0.75 for n in range(1, 8)] + [L - 1.5]:
        if w0 - 1.5 < u < w1:
            continue
        montant(v, u, 1.5, top)
    for u in (w0 - 1.5, w1):   # montants de rive de la fenêtre
        montant(v, u, 1.5, top)
    v.rect(w0, FEN_Z[0] - 1.5, w1 - w0, 1.5, **bois)                 # appui
    v.rect(w0, FEN_Z[1], w1 - w0, 3.5, fill="#e7c9a0", stroke="#7a5a2a", sw=0.6)  # linteau
    montant(v, 47.25 + 0, 1.5, lambda x: FEN_Z[0] - 1.5)
    montant(v, 47.25, FEN_Z[1] + 3.5, top)
    v.dim(0, 0, L, 0, 10)
    v.dim(0, 0, 0, H_HAUT, -12, size=6)
    v.dim(w0, FEN_Z[0], w1, FEN_Z[0], -12, "ouv. brute 24 × 12", size=5.5)
    v.dim(L, 0, L, FEN_Z[0], 10, size=6)
    v.text(4, -9, "ARRIÈRE", size=6, weight="bold", fill="#555")
    v.text(L - 4, -9, "AVANT", size=6, weight="bold", fill="#555", anchor="end")

    # --- mur avant -----------------------------------------------------------
    titre_vue(f, 420, 298, "OSSATURE MUR AVANT (porte)", "Échelle 1:32 — posé entre les murs latéraux, vue de l'extérieur")
    v = Vue(f, 475, 515, 32, flip=True)
    x0, x1 = 2.5, B - 2.5
    top = lambda x: wtop(x) - 1.5
    v.rect(x0, 0, PORTE[0] - 1 - x0 - 3, 1.5, **bois)
    v.rect(PORTE[1] + 1 + 3, 0, x1 - PORTE[1] - 4, 1.5, **bois)
    v.poly([(x0, wtop(x0) - 1.5), (x1, wtop(x1) - 1.5), (x1, wtop(x1)), (x0, wtop(x0))], **bois)
    ro0, ro1 = PORTE[0] - 1, PORTE[1] + 1   # ouverture brute 32 po
    for x in [x0, 16 - 0.75, 32 - 0.75, x1 - 1.5]:
        montant(v, x, 1.5, top)
    montant(v, ro0 - 3, 0, top)       # montant de rive
    montant(v, ro1 + 1.5, 0, top)
    montant(v, ro0 - 1.5, 0, lambda x: 74)   # montant nain (trimmer)
    montant(v, ro1, 0, lambda x: 74)
    v.rect(ro0 - 1.5, 74, ro1 - ro0 + 3, 1.5, fill="#e7c9a0", stroke="#7a5a2a", sw=0.6)  # linteau
    montant(v, 64 - 0.75, 75.5, top)
    v.rect(20, 4, 8, 4, fill="#444", stroke="#111", sw=0.5)
    v.dim(ro0, 0, ro1, 0, 14, "32 po ouv. brute", size=5.8)
    v.dim(ro0 + 8, 0, ro0 + 8, 74, 0, "74 po ouv. brute", size=5.5)
    v.dim(x0, 0, x0, wtop(x0), -12, size=6)
    v.dim(x1, 0, x1, wtop(x1), 12, size=6)
    v.text(PORTE[0] + 17, 70, "linteau 2×4 à plat", size=5, anchor="middle")
    v.text(PORTE[0] + 17, 66, "(mur non porteur)", size=5, anchor="middle")
    v.text(24, 10, "vent.", size=5.2, anchor="middle")
    v.text(x0, -11, "Mur arrière : même gabarit, sans porte, ventilation haute. Chevrons 2×4 vis-à-vis des montants.", size=6)
    return f


# =============================================================================
# FEUILLE 4 — COUPE A-A + MATÉRIAUX
# =============================================================================
MATERIAUX = [
    ("BASE", None),
    ("Patins", "4 × 2×8 × 10 pi traité"),
    ("Solives de rive", "2 × 2×6 × 10 pi traité"),
    ("Solives + chevêtres", "11 × 2×6 × 8 pi traité"),
    ("Plancher", "3 × CP 3/4 po 4×8 traité"),
    ("MURS", None),
    ("Montants, lisses, sablières", "≈ 48 × 2×3 × 8 pi"),
    ("Linteaux", "2 × 2×4 × 8 pi"),
    ("Revêtement", "8 × OSB 7/16 po 4×8"),
    ("Tôle murs", "≈ 230 pi² (cal. 29)"),
    ("TOIT", None),
    ("Chevrons @ 24 po", "6 × 2×4 × 10 pi"),
    ("Fourrures", "8 × 1×3 × 12 pi"),
    ("Pontage", "4 × OSB 7/16 po 4×8"),
    ("Tôle toit", "4 × 3 pi × 9 pi + moulures"),
    ("ISOLATION / INTÉRIEUR", None),
    ("Isolant XPS 1 1/2 po", "≈ 19 panneaux 2×8 pi"),
    ("Finition intérieure (murs + plafond)", "9 × CP 1/4 po 4×8"),
    ("Bancs + couvercles trappes", "3 × CP 3/4 po 4×8 + 6 × 2×3"),
    ("OUVERTURES", None),
    ("Porte 30 × 72 maison", "3 pentures, loquet, moraillon"),
    ("Fenêtres", "2 × polycarbonate 1/4 po 24×12"),
    ("Ventilation", "2 grilles réglables 4×10 po"),
    ("QUINCAILLERIE", None),
    ("Vis 3 po ext., vis 1 5/8 po", "≈ 5 lb + 3 lb"),
    ("Vis à tôle à rondelle", "≈ 300"),
    ("Attaches anti-soulèvement", "18 (solive/patin, chevron/mur)"),
    ("Œillets de remorquage", "2 × tire-fond à œil 1/2 po"),
    ("SÉCURITÉ", None),
    ("Détecteur CO, extincteur ABC", "1 + 1"),
    ("Plaque incombustible", "1 × panneau ciment 1/2 po"),
]


def feuille_coupe():
    f = Feuille(4, "Coupe A-A et matériaux")
    titre_vue(f, 40, 44, "COUPE A-A (vers l'arrière)", "Échelle 1:24 (1/2 po = 1 pi)")
    v = Vue(f, 85, 420, 24, flip=True)
    # glace et trous
    v.rect(-14, -14, B + 28, 14, fill="url(#glace)", stroke="none")
    v.line(-14, 0, B + 14, 0, stroke="#1f5f8b", sw=1.1)
    for tx in (18, 66):
        v.rect(tx + 2, -14, 8, 14, fill="#fff", stroke="#1f5f8b", sw=0.6, dash="3,1.5")
    # patins coupés
    for x0 in (6, 87):
        v.rect(x0, 0, 3, PATIN_H, fill="url(#hach)", stroke="#111", sw=0.8)
    # solive au-delà
    v.rect(1.5, PATIN_H, B - 3, SOL_H, fill="#f3ead8", stroke="#7a5a2a", sw=0.6)
    for x0 in (0, B - 1.5):
        v.rect(x0, PATIN_H, 1.5, SOL_H, fill="url(#hach)", stroke="#111", sw=0.7)
    # plancher coupé avec ouvertures de trappes
    segs = [(0, 18), (30, 66), (78, B)]
    for a, b in segs:
        v.rect(a, PATIN_H + SOL_H, b - a, CP, fill="url(#hach)", stroke="#111", sw=0.7)
    for tx in (18, 66):   # couvercle ouvert, appuyé
        v.poly([(tx, Z_PL), (tx - 0.2, Z_PL + 12), (tx + 0.55, Z_PL + 12), (tx + 0.75, Z_PL)], fill="#d8c39a", stroke="#111", sw=0.5)
    # murs coupés
    def mur(x_ext, x_int, h):
        sgn = 1 if x_int > x_ext else -1
        a = x_ext
        v.rect(min(a, a + sgn * 0.5), Z_PL, 0.5, h, fill="#d8c39a", stroke="#111", sw=0.5)          # OSB
        b = a + sgn * 0.5
        v.rect(min(b, b + sgn * 2.5), Z_PL, 2.5, h, fill="url(#isol)", stroke="#111", sw=0.5)       # 2x3 + XPS
        c = b + sgn * 2.5
        v.rect(min(c, c + sgn * 0.5), Z_PL, 0.5, h, fill="#efe3c8", stroke="#111", sw=0.5)          # finition
    mur(0, T, H_BAS)
    mur(B, B - T, H_HAUT)
    # mur arrière au-delà
    v.poly([(T, Z_PL), (B - T, Z_PL), (B - T, Z_PL + wtop(B - T)), (T, Z_PL + wtop(T))], fill="none", stroke="#999", sw=0.5)
    v.rect(70, Z_PL + wtop(70) - 9, 8, 4, fill="#444", stroke="none")
    # toit
    zr = lambda x: Z_PL + wtop(x)
    v.poly([(-DEBORD, zr(-DEBORD)), (B + DEBORD, zr(B + DEBORD)), (B + DEBORD, zr(B + DEBORD) + 3.5),
            (-DEBORD, zr(-DEBORD) + 3.5)], fill="#f3ead8", stroke="#7a5a2a", sw=0.7)
    v.poly([(T, zr(T) - 1.5), (B - T, zr(B - T) - 1.5), (B - T, zr(B - T)), (T, zr(T))], fill="url(#isol)", stroke="#111", sw=0.4)
    v.poly([(-DEBORD, zr(-DEBORD) + 3.5), (B + DEBORD, zr(B + DEBORD) + 3.5), (B + DEBORD, zr(B + DEBORD) + 3.95),
            (-DEBORD, zr(-DEBORD) + 3.95)], fill="#d8c39a", stroke="#111", sw=0.5)
    v.poly([(-DEBORD - 1, zr(-DEBORD - 1) + 4.7), (B + DEBORD + 1, zr(B + DEBORD + 1) + 4.7),
            (B + DEBORD + 1, zr(B + DEBORD + 1) + 5.0), (-DEBORD - 1, zr(-DEBORD - 1) + 5.0)], fill="#555", stroke="#111", sw=0.5)
    # bancs
    for x0 in (T, B - T - 12):
        v.rect(x0, Z_PL + 16.25, 12, 0.75, fill="#d8c39a", stroke="#111", sw=0.6)
        xf = x0 + 11.25 if x0 == T else x0
        v.rect(xf, Z_PL, 0.75, 16.25, fill="#d8c39a", stroke="#111", sw=0.6)
    # chauffage au-delà
    v.rect(40, Z_PL, 16, 15, fill="#fde2df", stroke="#c0392b", sw=0.7)
    v.text(48, Z_PL + 6.5, "chauffage", size=5.2, anchor="middle", fill="#c0392b")
    v.text(74, Z_PL + wtop(70) - 12, "vent. haute (au-delà)", size=5.2, anchor="middle")

    # pastilles
    pastilles = [
        (B / 2, zr(B / 2) + 4.85, 1, 0, -22),
        (B / 2 + 20, zr(B / 2 + 20) + 3.7, 2, 0, -38),
        (30, zr(30) + 1.8, 3, -10, -48),
        (60, zr(60) - 0.75, 4, 0, 30),
        (0.25, 60, 5, -24, 0),
        (1.75, 40, 6, -24, 0),
        (B - 9, Z_PL + 16.6, 7, 0, -24),
        (50, Z_PL - 0.4, 8, 0, 22),
        (40, PATIN_H + 3, 9, 0, 26),
        (7.5, 3.5, 10, -26, 0),
        (24, Z_PL, 11, 0, -26),
        (24, -8, 12, 22, 10),
    ]
    for x, y, n, dx, dy in pastilles:
        callout(v, x, y, n, dx, dy)
    # cotes
    v.dim(0, 0, 0, Z_PL, -46, size=6)
    v.dim(0, Z_PL, 0, Z_PL + H_BAS, -46, f"{fi(H_BAS)} libre", size=6)
    v.dim(B, Z_PL, B, Z_PL + H_HAUT, 16, f"{fi(H_HAUT)} libre", size=6)
    v.dim(B + DEBORD, 0, B + DEBORD, zr(B + DEBORD) + 5, 34, f"{fi(zr(B + DEBORD) + 5)} hors-tout", size=6)
    v.dim(T, Z_PL + 17, T + 12, Z_PL + 17, -8, "12 po", size=5.5)
    v.dim(B - T, Z_PL, B - T, Z_PL + 17, -10, "17 po", size=5.5)

    leg = [
        "Tôle prépeinte cal. 29 sur fourrures 1×3",
        "Pontage OSB 7/16 po",
        "Chevrons 2×4 @ 24 po c/c, débord 6 po",
        "Isolant XPS 1 1/2 po entre chevrons",
        "Tôle + OSB 7/16 po (revêtement)",
        "Montants 2×3 @ 16 po + XPS + CP 1/4",
        "Banc : dessus CP 3/4, couvercle à charnières",
        "Plancher CP 3/4 po traité, collé-vissé",
        "Solives 2×6 traité @ 16 po c/c",
        "Patin 2×8 traité doublé (coupé)",
        "Trappe 12 × 12 ouverte",
        "Trou dans la glace, tarière 8 à 10 po",
    ]
    y0 = 470
    for i, t in enumerate(leg):
        col, row = divmod(i, 6)
        x = 40 + col * 200
        y = y0 + row * 12
        f.add(f'<circle cx="{x+5}" cy="{y-2.6}" r="5" fill="#fff" stroke="#c0392b" stroke-width="0.7"/>')
        f.text(x + 5, y, str(i + 1), size=6, anchor="middle", weight="bold", fill="#c0392b")
        f.text(x + 14, y, t, size=6.6)

    # matériaux
    x, y = 470, 44
    f.text(x, y, "LISTE DE MATÉRIAUX (estimation)", size=11, weight="bold")
    f.text(x, y + 11, "Ajouter 10 % de perte. Bois traité pour tout ce qui touche la glace.", size=6.5, fill="#555")
    y += 26
    for nom, qte in MATERIAUX:
        if qte is None:
            f.add(f'<rect x="{x-2}" y="{y-8}" width="304" height="11" fill="#eef3f7"/>')
            f.text(x, y, nom, size=7, weight="bold", fill="#1f5f8b")
        else:
            f.text(x + 4, y, nom, size=6.8)
            f.text(x + 300, y, qte, size=6.8, anchor="end")
            f.add(f'<line x1="{x}" y1="{y+2.5}" x2="{x+300}" y2="{y+2.5}" stroke="#e3e3e3" stroke-width="0.4"/>')
        y += 13.6
    return f


if __name__ == "__main__":
    feuilles = [feuille_plan(), feuille_elevations(), feuille_ossature(), feuille_coupe()]
    for fe in feuilles:
        (ICI / f"feuille-{fe.num}.svg").write_text(fe.svg(), encoding="utf-8")
    print("SVG écrits :", ", ".join(f"feuille-{fe.num}.svg" for fe in feuilles))
