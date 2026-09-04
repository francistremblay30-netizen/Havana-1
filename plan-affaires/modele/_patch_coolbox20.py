"""20 unités Coolbox propriété de Havana + restauration et bars : patch du modèle et du générateur."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

def patch(path, pairs):
    s = open(path, encoding="utf8").read()
    for a, b in pairs:
        assert a in s, f"introuvable : {a[:70]!r}"
        s = s.replace(a, b)
    open(path, "w", encoding="utf8").write(s)

patch(os.path.join(HERE, "modele_financier_v2.py"), [
    ('    "fb_ratio": {1: 0.08, 2: 0.14, 3: 0.18, 4: 0.19, 5: 0.20},          # restauration sans alcool',
     '    "fb_ratio": {1: 0.12, 2: 0.17, 3: 0.20, 4: 0.22, 5: 0.23},          # restaurant, café, cantine et bars (budget de la direction à maturité ≈ 890 k$)'),
    ('    ("restauration", "Restauration"),', '    ("restauration", "Restauration et bars"),'),
])

R = [
    ('run("achèvement des 13 villas, hivernisation des 16 chalets, 9 unités Coolbox quatre saisons sur les emplacements aménagés en 2022.")',
     'run("achèvement des 13 villas, hivernisation des 16 chalets, 20 unités Coolbox quatre saisons apportées par Coolbox HPA, dont 9 déjà en place sur les emplacements aménagés en 2022.")'),
    ('des couches publiques et partenaires sollicitées (" + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + ") et des fonds propres de " + money(M.fonds_propres) + ", soit " + pct(M.pct_fonds_propres_argent_neuf, 0) + " de l\'argent neuf."',
     'des couches publiques et partenaires sollicitées (" + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + ") et des fonds propres de " + money(M.fonds_propres) + ", soit " + pct(M.pct_fonds_propres_argent_neuf, 0) + " de l\'argent neuf, dont l\'apport en nature de " + money(M.apport_coolbox) + " de Coolbox HPA (20 unités quatre saisons)."'),
    ('run("9 unités Coolbox ont généré " + money(cb.ca_ht) + " de ventes en un seul été 2026, soit " + money(cb.ca_ht / cb.unites) + " par unité ; la grappe A en ajoute 9, fabriquées en usine à prix fixe.")',
     'run("9 unités Coolbox ont généré " + money(cb.ca_ht) + " de ventes en un seul été 2026, soit " + money(cb.ca_ht / cb.unites) + " par unité ; le projet en exploite 20, propriété de Havana, apportées par Coolbox HPA.")'),
    ('S\'y ajoutent la restauration et les activités (" + money(M.autres_2026.restauration + M.autres_2026.activites) + ", budget interne à valider) et la part de Havana dans les ventes des unités Coolbox (" + money(cb.redevance) + " en 2026, contrat de partenariat)."',
     'S\'y ajoutent la restauration et les activités (" + money(M.autres_2026.restauration + M.autres_2026.activites) + ") et la part de Havana dans les ventes des 9 unités Coolbox exploitées en 2026 (" + money(cb.redevance) + ")."'),
    ('["Unités Coolbox 4 saisons (propriété Coolbox HPA)", "9 exploitées / 18 emplacements", "225 $ / nuit", "Été", "Été et hiver"],',
     '["Unités Coolbox 4 saisons", "9 exploitées / 18 emplacements aménagés", "225 $ / nuit", "Été", "20 unités, propriété de Havana, été et hiver"],'),
    ('    ["Unités Coolbox 4 saisons (nouvelles)", "0", "225 $ été, 199 $ hiver", "—", "9, livrées en mai 2027"],\n', ''),
    ('H3("Neuf unités Coolbox quatre saisons"),', 'H3("Vingt unités Coolbox quatre saisons"),'),
    ('P("Neuf unités 12×24 fabriquées en usine par Coolbox HPA (structure d\'acier autoportante, isolation haute performance, thermopompe), installées sur 9 des 18 emplacements aménagés et desservis en 2022. Délai usine de 12 à 16 semaines ; livraison en mai 2027. Les 9 unités',
     'P("Vingt unités 12×24 fabriquées en usine par Coolbox HPA (structure d\'acier autoportante, isolation haute performance, thermopompe), apportées en nature au projet pour " + money(M.apport_coolbox) + " : les 9 déjà en place sur les emplacements aménagés en 2022, et 11 livrées pour juin 2027 (délai usine de 12 à 16 semaines). Elles appartiennent à Havana et 100 % de leurs ventes lui reviennent. Les 9 unités'),
    ('P("Restaurant de cuisine cubaine et latino-américaine ouvert à la clientèle du site et au public régional, avec le café Cubano et la cantine. Les projections ne comptent que la restauration ; le bar constitue un potentiel additionnel non compté."),',
     'P("Restaurant de cuisine cubaine et latino-américaine ouvert à la clientèle du site et au public régional, avec le café Cubano, la cantine et le Mojito bar. À maturité, la restauration et les bars représentent " + pct(hyp.fb_ratio["5"], 0) + " des revenus d\'hébergement, sous le budget de la direction (cantine 100 000 $, café 200 000 $, Mojito bar 300 000 $, Madera 289 500 $)."),'),
    ('[run("Coolbox HPA, fabricant : ", { bold: true }), run("soumission à prix fixe valide 12 mois pour les 9 unités, fiche technique quatre saisons, garantie du fabricant, exploitation des 9 unités existantes sous le contrat de partenariat (annexe J).")],',
     '[run("Coolbox HPA, fabricant et partenaire : ", { bold: true }), run("apport en nature de 20 unités quatre saisons (" + money(M.apport_coolbox) + "), fiche technique, garantie du fabricant, plateforme de vente reservationcoolbox.ca (annexe J).")],'),
    ('Le plan retient pour les unités du site une occupation hivernale de', 'Le plan retient pour les 20 unités du site une occupation hivernale de'),
    ('"Unités Coolbox : plateforme reservationcoolbox.ca déjà active (contrat de partenariat), " + money(cb.ca_ht) + " de ventes en 2026 ; canal étendu aux 9 nouvelles unités.",',
     '"Unités Coolbox : plateforme reservationcoolbox.ca déjà active, " + money(cb.ca_ht) + " de ventes en 2026 pour 9 unités ; canal étendu aux 20 unités.",'),
    ('les 16 chalets hivernisés à l\'automne 2027 et les 9 nouvelles unités Coolbox."),', 'les 16 chalets hivernisés à l\'automne 2027 et les 20 unités Coolbox quatre saisons."),'),
    ('["Restauration / revenus d\'hébergement", "6,5 %",', '["Restauration et bars / revenus d\'hébergement", "6,5 %",'),
    ('  H2("6.5 Partenariat Coolbox : partage contractuel"),\n  P("Pour les 9 unités propriété de Coolbox HPA, le contrat de partenariat prévoit que les unités demeurent la propriété exclusive du fabricant (exclues des garanties offertes), que l\'assurance responsabilité de 2 M$ est portée par Coolbox et que les ventes transitent par sa plateforme ; Havana reçoit 50 % des ventes moins le transport. Les 9 nouvelles unités appartiennent à l\'emprunteur et entrent dans l\'hypothèque mobilière."),',
     '  H2("6.5 Unités Coolbox : exploitation"),\n  P("Les 20 unités Coolbox appartiennent à Havana et entrent dans l\'hypothèque mobilière. Elles sont vendues par la plateforme reservationcoolbox.ca et par les canaux du site ; le ménage, l\'accueil et l\'entretien courant sont assurés par les équipes de Havana, l\'entretien du fabricant et la garantie par Coolbox HPA."),'),
    ('["Nouvelles unités Coolbox (9)", "Été " + pct(hyp.coolbox_occ_ete["1"], 0) + " → " + pct(hyp.coolbox_occ_ete["5"], 0) + " à 225 $ ; hiver " + pct(hyp.coolbox_occ_hiver["1"], 0) + " → " + pct(hyp.coolbox_occ_hiver["5"], 0) + " à 199 $ ; An 1 : 80 % de l\'été", "9 unités existantes : " + money(cb.ca_ht / cb.unites) + " par unité en un été 2026 ; données d\'hiver du réseau (annexe J)"],',
     '["Unités Coolbox (20, propriété Havana)", "Été " + pct(hyp.coolbox_occ_ete["1"], 0) + " → " + pct(hyp.coolbox_occ_ete["5"], 0) + " à 225 $ ; hiver " + pct(hyp.coolbox_occ_hiver["1"], 0) + " → " + pct(hyp.coolbox_occ_hiver["5"], 0) + " à 199 $ ; 100 % des ventes à Havana", "9 unités existantes : " + money(cb.ca_ht / cb.unites) + " par unité en un été 2026 ; données d\'hiver du réseau (annexe J)"],'),
    ('["Part Havana des unités Coolbox HPA", money(hyp.redevance_base) + " indexé (50 % des ventes 2026)", "Contrat de partenariat Coolbox (annexe J)"],\n', ''),
    ('["Restauration", pct(hyp.fb_ratio["1"], 0) + " → " + pct(hyp.fb_ratio["5"], 0) + " des revenus d\'hébergement", "Réel 2026 : 6,5 % ; bar non compté"],',
     '["Restauration et bars", pct(hyp.fb_ratio["1"], 0) + " → " + pct(hyp.fb_ratio["5"], 0) + " des revenus d\'hébergement", "Réel 2026 : 6,5 % ; budget de la direction à maturité ≈ 890 000 $"],'),
    ('et sur les 9 nouvelles unités Coolbox ; cession d\'assurances', 'et sur les 20 unités Coolbox ; cession d\'assurances'),
    ('Le bar et le spa, non comptés, constituent un potentiel additionnel."),', 'Le spa, non compté, constitue un potentiel additionnel."),'),
    ('"Couches complémentaires sollicitées : " + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + " ; fonds propres : " + money(M.fonds_propres) + ".",',
     '"Couches complémentaires sollicitées : " + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + " ; fonds propres : " + money(M.fonds_propres) + ", dont " + money(M.apport_coolbox) + " en nature (20 unités Coolbox).",'),
]
patch(os.path.join(HERE, "generer_plan_v2.js"), R)
print("patch coolbox20 ok")
