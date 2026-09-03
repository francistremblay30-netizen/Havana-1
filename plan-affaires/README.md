# Plan d'affaires — Havana-1

Ce dossier contient le plan d'affaires du projet Havana-1, découpé en sections.
Chaque section est un fichier Markdown séparé pour faciliter la relecture et
le suivi des modifications avec Git.

## Sections

1. [Résumé exécutif](01-resume-executif.md)
2. [Description de l'entreprise](02-description-entreprise.md)
3. [Analyse du marché](03-analyse-marche.md)
4. [Produits et services](04-produits-services.md)
5. [Stratégie marketing et ventes](05-marketing-ventes.md)
6. [Organisation et équipe](06-organisation-equipe.md)
7. [Plan financier](07-plan-financier.md)

## Documents sources

Le dossier `sources/` contient les documents d'origine :

- `Plan_affaire.docx` : texte du plan (mission, vision, histoire, projets et
  coûts).
- `Tableau_depenses_revenus_actuel.xls` : budget mensuel actuel.
- `Tableau_depenses_revenus_projetes.xls` : budget mensuel une fois les
  projets réalisés.
- `rapport-revenus-2025.jpg` et `rapport-revenus-2026.jpg` : rapports de
  revenus du système de réservation, annotés à la main.

## Comment travailler

- Remplir une section à la fois, en remplaçant le texte entre crochets.
- Garder les chiffres dans le plan financier et y renvoyer depuis les autres
  sections plutôt que de les dupliquer.
- Committer après chaque section terminée avec un message clair, par exemple
  `Rédiger le résumé exécutif`.

## Plan d'affaires bancaire (version présentable)

- `Plan_affaires_Complexe_Havana.docx` : document complet destiné à une
  institution financière (27 pages), avec emplacements réservés pour les
  images et champs `[à compléter]`.
- `Plan_affaires_Complexe_Havana.pdf` : même document, rendu PDF.
- `modele/modele_financier.py` : modèle financier sur cinq ans (hypothèses
  explicites, échéancier de la dette, ratios, sensibilité). Produit
  `modele.json` et les graphiques dans `modele/graphiques/`.
- `modele/generer_plan.js` : générateur du document Word à partir du modèle.

Pour régénérer après avoir modifié une hypothèse :

```bash
cd plan-affaires/modele
python3 modele_financier.py
node generer_plan.js      # nécessite le paquet npm « docx »
```

À l'ouverture du Word, accepter la mise à jour des champs pour remplir la
table des matières.
