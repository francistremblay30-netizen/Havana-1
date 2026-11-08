# Cabane à pêche blanche 8 × 10 pi — plans 2D

`Plans_cabane_peche_8x10.pdf` : 4 feuilles, lettre paysage (imprimer à 100 % pour garder l'échelle).

1. Vue en plan / aménagement (1:24) : 4 trappes, 2 bancs, chauffage, porte, fenêtres, ventilation
2. Élévations avant et latérale (1:32)
3. Ossature : plancher (1:24), mur latéral et mur avant (1:32)
4. Coupe A-A (1:24) + liste de matériaux estimée

Régénérer après une modification des paramètres en tête de `generer_plans.py` :
```
python3 generer_plans.py   # -> feuille-1..4.svg
node exporter.js           # -> PDF + PNG (Playwright)
```
Statut : préliminaire, à valider avant de construire.

## Cabane légère 5 × 10 pi — motoneige (`5x10/`)

`5x10/Plans_cabane_5x10_motoneige.pdf` : 6 feuilles — plan, élévation latérale, pignons, coupe A-A (1:16), ossature, matériaux et poids estimé (≈ 740 lb tel que dessiné, ≈ 600 lb version allégée).
Toit en pointe 8:12 à faîtière structurale 2×8, murs 2×2 @ 24 po, patins 2×6 à nez relevé + semelle UHMW, timon en A rigide.
```
cd 5x10 && python3 generer_5x10.py && node ../exporter.js . Plans_cabane_5x10_motoneige.pdf
```
