# Havana-1 — Plan d'affaires Complexe Havana 2027-2031

Projet de Francis Tremblay (Coolbox / Construction Prospère) : demande de financement de 10,3 M$ pour transformer le camping Havana Resort (Maricourt, Cantons-de-l'Est) en centre de villégiature quatre saisons. Toujours répondre en français.

## Livrable courant (2026-09-03)
- `plan-affaires/Plan_affaires_Complexe_Havana_HD.docx` et `.pdf` : **version de référence**, 32 pages. Produite sur le poste de Francis à partir du .docx généré, puis retravaillée :
  - photos passées en super-résolution IA (Real-ESRGAN) ; graphiques et carte du site agrandis sans IA (l'IA brouille les petits textes) ;
  - pages 12-13 et 18-19 fusionnées (plus de puces ni de ligne de tableau orphelines) ;
  - ancienne page 34 (deux photos Coolbox seules) retirée.
- `plan-affaires/Plan_affaires_Complexe_Havana.docx/.pdf` : sortie brute du générateur (35 pages, images à 200 dpi). Ne pas l'envoyer telle quelle.

## Pipeline du générateur
```
cd plan-affaires/modele
python3 modele_financier.py     # -> modele.json + graphiques/
python3 preparer_photos.py      # photos/*.jpg -> photos/prepare/ + photos_meta.json
node generer_plan.js            # -> ../Plan_affaires_Complexe_Havana.docx (paquet npm « docx »)
```
Si tu régénères le document, la version HD n'est PAS régénérée automatiquement : il faut refaire les trois corrections ci-dessus (ou les intégrer dans `generer_plan.js` : éviter les puces orphelines après l'échéancier, garder le tableau 5.5 entier, ne pas produire la page « photos Coolbox » seule).

## Règles
- Les photos sources dans `photos/` sont de basse résolution ; `preparer_photos.py` les étire à 200 dpi, d'où la pixellisation. Ne jamais réduire davantage ; viser 300 dpi si les sources le permettent.
- Chiffres = ceux de `modele/modele.json` et des fichiers `sources/`. Jamais de promesse de rendement dans un document investisseur.
- Ce dépôt sert à continuer le travail depuis le mobile (sessions Claude Code en nuage). Ce qui touche Outlook, Word ou le portail Coolbox se fait sur le poste de Francis, pas ici.
