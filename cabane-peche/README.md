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
