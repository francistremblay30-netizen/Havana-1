#!/usr/bin/env python3
"""Modèle financier prévisionnel v2 du Complexe Havana (2026 réel, An 1 à An 5).

Différences avec la v1 (modele_financier.py) :
- An 0 (2026) publié, charges rapprochées du budget de la direction ;
- phase 1a sans autorisation provinciale : grappe A de 9 unités Coolbox 4 saisons
  sur les emplacements aménagés en 2022 + conversion de 40 terrains existants en
  saisonniers ; les 35 terrains additionnels (CPTAQ) et le sentier lumineux sont
  hors du scénario de base (phases conditionnelles) ;
- calendrier réel de livraison (phase 1a juillet 2027, phase 2 juin 2028) ;
- restauration 8 % → 20 % de l'hébergement (alcool = 0 tant que la RACJ n'a pas statué) ;
- entretien 8 %, véhicules, honoraires comptables, cachets de spectacles,
  commissions de plateformes ; impôts au taux PME (12,2 % / 26,5 %) ;
- financement en couches : prêt senior (tranches A et B), Investissement Québec,
  DEC, quasi-équité, MRC, retenue subordonnée de l'entrepreneur, fonds propres ;
- DSCR senior, DSCR total et DSCR « définition bancaire » ;
- bilan pro forma au coût historique déclaré (11 915 000 $), pas à l'évaluation.
Toute valeur marquée « hyp. » est une hypothèse de travail à valider.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys as _sys
OUT = HERE / ("modele_v2_phase2.json" if "--phase2" in _sys.argv else "modele_v2.json")
CHARTS = HERE / ("graphiques_v2_phase2" if "--phase2" in _sys.argv else "graphiques_v2")
CHARTS.mkdir(exist_ok=True)

YEARS = ["2026 (réel)", "An 1 – 2027", "An 2 – 2028", "An 3 – 2029", "An 4 – 2030", "An 5 – 2031"]
INFL = 0.03

# ---------------------------------------------------------------------------
# Réel 2026 (Pixum, par date de transaction, 2025-09-15 → 2026-09-15) et budget interne
# ---------------------------------------------------------------------------
REEL_2026 = {"terrains": 791894.29, "saisonniers": 43208.71, "chalets": 497722.97, "cabanas": 199015.63}
REEL_2025_TOTAL = 1453605.16
REEL_2026_TOTAL = 1531841.68
AUTRES_2026 = {"restauration": 100000.0, "activites": 96700.0}   # budget interne, à valider
COOLBOX_2026 = {"ca_ht": 180334.31, "part_havana": 90167.15, "transport": 13500.0, "redevance": 76667.15, "unites": 9}  # CALCUL-HAVANA / AVIS-HAVANA-2026-001

def idx(base, year):
    return base * (1 + INFL) ** (year - 1)

# ---------------------------------------------------------------------------
# Hypothèses d'exploitation (valeur, source)
# ---------------------------------------------------------------------------
H = {
    "terrains_uplift": {1: 1.00, 2: 1.02, 3: 1.03, 4: 1.04, 5: 1.04},
    "saisonniers_sites": {0: 12, 1: 30, 2: 45, 3: 58, 4: 66, 5: 70},   # 2026 : 43 209 $ / 3 650 $ ≈ 12
    "saisonnier_tarif": 3650.0,
    "chalets_n": 16, "chalet_ete": 235.0, "chalet_hiver": 210.0,
    "chalets_occ_ete": {1: 0.58, 2: 0.61, 3: 0.63, 4: 0.65, 5: 0.66},
    "chalets_occ_hiver": {1: 0.12, 2: 0.18, 3: 0.22, 4: 0.24, 5: 0.25},
    "chalets_hiver_frac": {1: 0.30, 2: 1, 3: 1, 4: 1, 5: 1},           # hivernisés à l'automne 2027 : nov.-déc. seulement en An 1
    "villas_n": 13, "villa_ete": 275.0, "villa_hiver": 245.0,
    "villas_occ_ete": {1: 0.50, 2: 0.55, 3: 0.60, 4: 0.63, 5: 0.65},
    "villas_occ_hiver": {1: 0.10, 2: 0.16, 3: 0.20, 4: 0.21, 5: 0.22},
    "villas_ete_frac": {1: 0.50, 2: 1, 3: 1, 4: 1, 5: 1},               # livrées en juillet 2027
    "hotel_tarif": 190.0,
    "hotel_rooms": {1: 11.5, 2: 17, 3: 17, 4: 17, 5: 17},               # 6 chambres jan.-juin 2027, 17 dès juillet
    "hotel_occ": {1: 0.35, 2: 0.42, 3: 0.48, 4: 0.52, 5: 0.55},
    "cabanas_uplift": {1: 1.0, 2: 1.02, 3: 1.04, 4: 1.05, 5: 1.05},
    "coolbox_n": 20, "coolbox_ete": 225.0, "coolbox_hiver": 199.0,     # 20 unités propriété Havana (apport Coolbox HPA) ; tarif affiché 225 $
    "coolbox_occ_ete": {1: 0.60, 2: 0.65, 3: 0.68, 4: 0.70, 5: 0.70},   # base annuelle du réseau Coolbox : ≈ 40 000 $ par unité par année
    "coolbox_occ_hiver": {1: 0.30, 2: 0.35, 3: 0.38, 4: 0.40, 5: 0.40},
    "coolbox_ete_frac": {1: 0.85, 2: 1, 3: 1, 4: 1, 5: 1},              # 9 déjà en place, 11 livrées pour juin 2027
    "redevance_base": 90167.15,                                          # 50 % du CA 2026 des 9 unités Coolbox HPA
    "fb_ratio": {1: 0.12, 2: 0.17, 3: 0.20, 4: 0.22, 5: 0.23},          # restaurant, café, cantine et bars (budget de la direction à maturité ≈ 890 k$)
    "spa_visites": {1: 0, 2: 0, 3: 0, 4: 5000, 5: 7500}, "spa_tarif": 55.0,   # phase 2 financée en 2029, ouverture juin 2030 (scénario « avec phase 2 » seulement)
    "spectacles": {1: 0, 2: 60000, 3: 120000, 4: 150000, 5: 160000},  # billetterie brute, scène et chapiteau existants (hyp.)
    "activites": {1: 105000, 2: 125000, 3: 140000, 4: 148000, 5: 155000},
}

def revenus(year):
    r = {}
    if year == 0:
        r.update(REEL_2026)
        r.update({"villas": 0.0, "hotel": 0.0, "coolbox": 0.0, "spa": 0.0, "spectacles": 0.0})
        r["redevance"] = COOLBOX_2026["redevance"]
        r.update(AUTRES_2026)
        return r
    r["terrains"] = REEL_2026["terrains"] * (1 + INFL) ** year * H["terrains_uplift"][year]
    r["saisonniers"] = H["saisonniers_sites"][year] * idx(H["saisonnier_tarif"], year)
    r["chalets"] = H["chalets_n"] * (184 * H["chalets_occ_ete"][year] * idx(H["chalet_ete"], year)
                                     + 181 * H["chalets_hiver_frac"][year] * H["chalets_occ_hiver"][year] * idx(H["chalet_hiver"], year))
    r["villas"] = H["villas_n"] * (184 * H["villas_ete_frac"][year] * H["villas_occ_ete"][year] * idx(H["villa_ete"], year)
                                   + 181 * H["villas_occ_hiver"][year] * idx(H["villa_hiver"], year))
    r["hotel"] = H["hotel_rooms"][year] * 365 * H["hotel_occ"][year] * idx(H["hotel_tarif"], year)
    r["cabanas"] = REEL_2026["cabanas"] * (1 + INFL) ** year * H["cabanas_uplift"][year]
    r["coolbox"] = H["coolbox_n"] * (184 * H["coolbox_ete_frac"][year] * H["coolbox_occ_ete"][year] * idx(H["coolbox_ete"], year)
                                     + 181 * H["coolbox_occ_hiver"][year] * idx(H["coolbox_hiver"], year))
    r["redevance"] = 0.0   # unités propriété de Havana dès 2027 : 100 % des ventes dans la ligne Coolbox
    heberg = r["terrains"] + r["saisonniers"] + r["chalets"] + r["villas"] + r["hotel"] + r["cabanas"] + r["coolbox"]
    r["restauration"] = heberg * H["fb_ratio"][year]
    r["spa"] = H["spa_visites"][year] * idx(H["spa_tarif"], year) if PHASE2 else 0.0
    r["spectacles"] = H["spectacles"][year] * ((1 + INFL) ** (year - 2) if year >= 2 else 1)
    r["activites"] = H["activites"][year]
    return r

LIGNES = [
    ("terrains", "Terrains de camping"),
    ("saisonniers", "Terrains saisonniers (12 → 70)"),
    ("chalets", "Chalets 4 saisons (16)"),
    ("villas", "Villas (13)"),
    ("hotel", "Hôtel (6 → 17 chambres)"),
    ("cabanas", "Cabanas prêt-à-camper (13)"),
    ("coolbox", "Unités Coolbox 4 saisons (20, propriété Havana)"),
    ("redevance", "Partenariat Coolbox HPA (2026, avant le transfert des unités)"),
    ("restauration", "Restauration et bars"),
    ("spectacles", "Spectacles et festivals"),
    ("activites", "Activités et concessions"),
]
HEBERG_KEYS = ["terrains", "saisonniers", "chalets", "villas", "hotel", "cabanas", "coolbox"]

# ---------------------------------------------------------------------------
# Charges
# ---------------------------------------------------------------------------
ENERGIE = {0: 242500, 1: 275000, 2: 400000, 3: 420000, 4: 435000, 5: 450000}

def charges(year, r):
    tot = sum(r.values())
    c = {}
    c["cout_ventes"] = r["restauration"] * 0.33 + r["activites"] * 0.20
    c["cachets"] = r["spectacles"] * 0.55                                   # cachets, technique, sécurité (hyp.)
    c["commissions"] = (r["hotel"] + r["villas"] + r["coolbox"]) * 0.40 * 0.15  # 40 % des nuitées via plateformes à 15 % (hyp.)
    sal_pct = {0: 0.39, 1: 0.36, 2: 0.34, 3: 0.32, 4: 0.31, 5: 0.30}[year]   # 30 % à maturité = normalisation Grenier 2021
    c["salaires"] = tot * sal_pct
    c["energie"] = ENERGIE[year]
    c["entretien"] = tot * 0.08                                              # norme Grenier 2021 (8 %)
    c["vehicules"] = 88500 * (1 + INFL) ** year                             # budget de la direction 2026
    c["marketing"] = tot * ({0: 0.03, 1: 0.035, 2: 0.035, 3: 0.03, 4: 0.03, 5: 0.03}[year])
    c["assurances"] = {0: 60000, 1: 95000, 2: 130000, 3: 134000, 4: 138000, 5: 142000}[year]
    c["taxes"] = {0: 54500, 1: 75000, 2: 130000, 3: 133000, 4: 136000, 5: 139000}[year]
    c["honoraires"] = 25000 * (1 + INFL) ** year                            # comptables, audit dès l'An 2
    c["admin"] = tot * 0.02
    c["bancaires"] = tot * 0.015
    c["fournitures"] = tot * 0.025
    c["loyers"] = 42000 * (1.02 ** year)
    c["divers"] = tot * 0.02
    return c

CHARGES = [
    ("cout_ventes", "Coût des ventes (restauration, concessions)"),
    ("cachets", "Cachets, technique et sécurité des spectacles (55 % de la billetterie)"),
    ("commissions", "Commissions des plateformes de distribution"),
    ("salaires", "Salaires et charges sociales"),
    ("energie", "Électricité, chauffage et propane"),
    ("entretien", "Entretien et réparations (8 %)"),
    ("vehicules", "Véhicules, essence et entretien des véhicules"),
    ("marketing", "Marketing et commercialisation"),
    ("assurances", "Assurances"),
    ("taxes", "Taxes municipales et scolaires"),
    ("honoraires", "Honoraires comptables et audit"),
    ("admin", "Administration, TI et télécoms"),
    ("bancaires", "Frais bancaires et de cartes"),
    ("fournitures", "Fournitures d'exploitation"),
    ("loyers", "Loyers et locations"),
    ("divers", "Divers et imprévus"),
]
# Part variable de chaque poste (pour la sensibilité) : calculée, pas forfaitaire.
PART_VARIABLE = {"cout_ventes": 1.0, "cachets": 1.0, "commissions": 1.0, "salaires": 0.5, "energie": 0.15, "entretien": 0.5,
                 "vehicules": 0.3, "marketing": 0.5, "assurances": 0.0, "taxes": 0.0, "honoraires": 0.0, "admin": 0.5,
                 "bancaires": 1.0, "fournitures": 1.0, "loyers": 0.0, "divers": 1.0}

# ---------------------------------------------------------------------------
# Investissement (emplois) et financement (sources)
# ---------------------------------------------------------------------------
COOLBOX_UNITE = 106000   # 20 unités 12×24 quatre saisons = 2 120 000 $ (apport en nature de Coolbox HPA, plan Havana Spa Resort août 2026)
APPORT_COOLBOX = 20 * COOLBOX_UNITE
import sys
PHASE2 = "--phase2" in sys.argv   # scénario de base = phase 1a seulement ; --phase2 ajoute le spa financé en 2029
PROJETS_TOUS = [
    ("Phase 1a", "Hôtel : de 6 à 17 chambres, exploitation 12 mois", 700000, "chantier"),
    ("Phase 1a", "Restaurant Madera et salle de conférence", 800000, "chantier"),
    ("Phase 1a", "Achèvement des 13 villas", 150000, "chantier"),
    ("Phase 1a", "Chalets existants : hivernisation (isolation, chauffage, plomberie)", 150000, "chantier"),
    ("Phase 1a", "20 unités Coolbox 12×24 quatre saisons (apport en nature de Coolbox HPA)", APPORT_COOLBOX, "usine"),
    ("Phase 1a", "Conversion de 40 terrains existants en terrains saisonniers", 50000, "chantier"),
    ("Phase 2", "Achèvement de la piscine intérieure et spa quatre saisons", 2000000, "chantier"),
]
PROJETS = [p for p in PROJETS_TOUS if p[0] == "Phase 1a" or PHASE2]
# Hors scénario de base (conditionnels) : 35 terrains saisonniers additionnels 700 000 $ (CPTAQ), amphithéâtre 500 000 $ et sentier lumineux 500 000 $ (phase 3).
CAPEX = sum(p[2] for p in PROJETS)
CAPEX_1 = sum(p[2] for p in PROJETS if p[0] == "Phase 1a")
CAPEX_2 = CAPEX - CAPEX_1
CHANTIER_1 = sum(p[2] for p in PROJETS if p[0] == "Phase 1a" and p[3] == "chantier")
CONTINGENCE = round(sum(p[2] * (0.05 if p[3] == "usine" else 0.10) for p in PROJETS))
HONORAIRES = 175000 if not PHASE2 else 250000
CONFORMITE = 250000        # hyp. : Phase II, dalles des réservoirs, régularisation des avis, attestations
FRAIS_FIN = 125000         # hyp. : montage multi-bailleurs
FDR = 250000
REFINANCEMENT = 4000000    # hyp. : à remplacer par les relevés des créanciers (acte de cession 2024 : 3 912 350 $)

# Couches de financement (nom, montant, taux, amortissement (ans), moratoire de capital (mois), statut)
SENIOR = 5500000 if not PHASE2 else 6500000
COUCHES = [
    ("Prêt hypothécaire de premier rang (tranche A refinancement, tranche B construction)", SENIOR, 0.07, 25, 12, "Demandé"),
    ("DEC – contribution remboursable sans intérêt", 500000, 0.00, 7, 24, "À solliciter"),
    ("Quasi-équité : Fonds régional de solidarité FTQ Estrie ou Fondaction", 750000, 0.09, 7, 36, "À solliciter"),
    ("MRC du Val-Saint-François – FLI / FLS", 150000, 0.06, 7, 12, "À solliciter"),
    ("Construction Prospère – retenue contractuelle subordonnée (10 % des travaux de chantier)", round(CHANTIER_1 * 0.10), 0.05, 5, 24, "Engagé (à signer)"),
]
if PHASE2:
    COUCHES.insert(1, ("Investissement Québec – prêt ou garantie sur la phase 2 (hyp.)", 1000000, 0.06, 10, 24, "À solliciter"))

def pmt(principal, taux, ans):
    if taux == 0:
        return principal / (ans * 12)
    rm = taux / 12
    n = ans * 12
    return principal * rm / (1 - (1 + rm) ** -n)

def echeancier(montant, taux, ans, moratoire, tirage_an1=1.0):
    """Échéancier annuel An 1..An 5 (+ complet) : intérêts seulement pendant le moratoire,
    puis paiements constants. An 1 : intérêts sur le solde moyen décaissé (tirage_an1)."""
    rows = []
    rm = taux / 12
    paiement = pmt(montant, taux, ans)
    solde = montant
    mois = 0
    for an in range(1, 41):
        i_an = c_an = 0.0
        for m in range(12):
            mois += 1
            if solde <= 0.005:
                break
            base = solde * (tirage_an1 if an == 1 else 1.0)
            i = base * rm
            i_an += i
            if mois <= moratoire:
                continue
            p = min(paiement - solde * rm, solde) if taux > 0 else min(paiement, solde)
            c_an += p
            solde -= p
        rows.append({"an": an, "interets": i_an, "capital": c_an, "service": i_an + c_an, "solde_fin": max(solde, 0.0)})
        if solde <= 0.005:
            break
    return rows, paiement

# Intérêts capitalisés pendant la construction (hyp. : moitié des intérêts de l'An 1 du senior sur la tranche B)
TRANCHE_B = SENIOR - REFINANCEMENT
INTERETS_CAPITALISES = round(TRANCHE_B * 0.5 * 0.07)   # ≈ 6 mois d'intérêts sur la tranche B (hyp.)
PAIEMENT_SENIOR = pmt(SENIOR, 0.07, 25)
RESERVE_SERVICE = round(PAIEMENT_SENIOR * 6)

EMPLOIS = [
    ("Projets de développement (hôtel, restaurant, villas, chalets, unités Coolbox, saisonniers)", CAPEX_1),
] + ([("Projets de développement, phase 2 (piscine intérieure et spa)", CAPEX_2)] if PHASE2 else []) + [
    ("Contingence (5 % forfaits d'usine, 10 % travaux de chantier)", CONTINGENCE),
    ("Honoraires professionnels (plans, ingénierie, permis)", HONORAIRES),
    ("Frais de démarrage, permis et mise à niveau des installations", CONFORMITE),
    ("Intérêts capitalisés pendant la construction", INTERETS_CAPITALISES),
    ("Réserve de service de la dette (6 mois, déposée à la clôture)", RESERVE_SERVICE),
    ("Frais de financement et juridiques (montage multi-bailleurs)", FRAIS_FIN),
    ("Fonds de roulement de démarrage", FDR),
    ("Refinancement de la dette existante", REFINANCEMENT),
]
TOTAL_EMPLOIS = sum(e[1] for e in EMPLOIS)
DETTE_COUCHES = sum(c[1] for c in COUCHES)
FONDS_PROPRES_ESPECES = TOTAL_EMPLOIS - DETTE_COUCHES - APPORT_COOLBOX
FONDS_PROPRES = FONDS_PROPRES_ESPECES + APPORT_COOLBOX
ARGENT_NEUF = TOTAL_EMPLOIS - REFINANCEMENT
SOURCES = [(c[0], c[1], c[5]) for c in COUCHES] + [("Apport en nature de Coolbox HPA : 20 unités quatre saisons", APPORT_COOLBOX, "Engagé"), ("Fonds propres en espèces : actionnaires et investisseur privé", FONDS_PROPRES_ESPECES, "Engagé")]

def dettes():
    """Échéanciers par couche, An 1..5 et complet ; tirage An 1 du senior sur le solde moyen décaissé."""
    out = []
    for nom, montant, taux, ans, mor, statut in COUCHES:
        tirage = (REFINANCEMENT + TRANCHE_B * 0.55) / SENIOR if nom.startswith("Prêt hypothécaire") else 1.0
        rows, paiement = echeancier(montant, taux, ans, mor, tirage)
        out.append({"nom": nom, "montant": montant, "taux": taux, "amort_ans": ans, "moratoire_mois": mor, "paiement_mensuel": paiement, "statut": statut, "rows": rows})
    return out

# ---------------------------------------------------------------------------
# Amortissement comptable, impôts, bilan
# ---------------------------------------------------------------------------
IMMO_EXISTANTES_COUT = 11915000      # historique des coûts 2015-2023 (déclaré)
AMORT_CUMULE_2026 = 3000000          # hyp. : amortissement cumulé au 31-12-2026, à remplacer par les états financiers
AMORT_EXISTANT = 150000
FACTEUR_CAP = (CAPEX + CONTINGENCE + HONORAIRES) / CAPEX
DPA_CATS = [  # (nom, taux, ajout An 1, ajout An 2) sur le capex avant capitalisation
    ("Cat. 1 — bâtiments : hôtel, restaurant, villas, chalets" + (", bâtiment piscine-spa" if PHASE2 else ""), 0.04, 700000 + 800000 + 150000 + 150000, 1200000 if PHASE2 else 0),
    ("Cat. 8 — équipements : mobilier" + (", piscine-spa (équipements)" if PHASE2 else ""), 0.20, 0, 800000 if PHASE2 else 0),
    ("Cat. 6 — unités d'hébergement préfabriquées sur structure d'acier (Coolbox)", 0.10, APPORT_COOLBOX, 0),
    ("Cat. 17 — aménagements de surface : conversion de terrains saisonniers", 0.08, 50000, 0),
]
TAUX_AMORT_COMPTABLE = {0.04: 0.04, 0.20: 0.10, 0.10: 0.05, 0.08: 0.05}   # linéaire comptable par catégorie (hyp.)

def dpa():
    cats = []
    for nom, taux, add1, add2 in DPA_CATS:
        a1, a2 = add1 * FACTEUR_CAP, add2 * FACTEUR_CAP
        row = {"nom": nom, "taux": taux, "base": a1 + a2, "dpa": [], "fnacc": []}
        fnacc = 0.0
        for y in range(1, 6):
            add = a1 if y == 1 else (a2 if y == 2 else 0.0)
            d = (fnacc + add * 0.5) * taux
            fnacc = fnacc + add - d
            row["dpa"].append(d)
            row["fnacc"].append(fnacc)
        cats.append(row)
    cats.append({"nom": "Frais de financement (déductibles sur 5 ans)", "taux": 0.20, "base": float(FRAIS_FIN),
                 "dpa": [FRAIS_FIN / 5.0] * 5, "fnacc": [FRAIS_FIN * (1 - 0.2 * y) for y in range(1, 6)]})
    return {"categories": cats, "total": [sum(c["dpa"][i] for c in cats) for i in range(5)]}

def amort_comptable(year):
    """Linéaire par catégorie ; phase 1a mise en service en An 1 (demi-année), phase 2 en An 2 (demi-année)."""
    tot = AMORT_EXISTANT
    for nom, taux, add1, add2 in DPA_CATS:
        tc = TAUX_AMORT_COMPTABLE[taux]
        a1, a2 = add1 * FACTEUR_CAP, add2 * FACTEUR_CAP
        if year >= 1:
            tot += a1 * tc * (0.5 if year == 1 else 1.0)
        if year >= 2:
            tot += a2 * tc * (0.5 if year == 2 else 1.0)
    return tot

def impots(bai):
    if bai <= 0:
        return 0.0
    return min(bai, 500000) * 0.122 + max(bai - 500000, 0) * 0.265

def modele():
    D = dettes()
    years = []
    cumul = 0.0
    for y in range(0, 6):
        r = revenus(y)
        c = charges(y, r)
        tot_r, tot_c = sum(r.values()), sum(c.values())
        baiia = tot_r - tot_c
        if y == 0:
            amort = AMORT_EXISTANT
            interets = REFINANCEMENT * 0.075       # hyp. : dette existante, à remplacer par les relevés
            capital = 0.0
            service_senior = service_total = interets
            interets_senior = interets
            solde_senior = REFINANCEMENT
            solde_total = REFINANCEMENT
            capex_maintien = 0.0
        else:
            amort = amort_comptable(y)
            rows = [d["rows"][y - 1] if y - 1 < len(d["rows"]) else {"interets": 0, "capital": 0, "service": 0, "solde_fin": 0} for d in D]
            interets = sum(rw["interets"] for rw in rows)
            capital = sum(rw["capital"] for rw in rows)
            service_total = interets + capital
            interets_senior = rows[0]["interets"]
            service_senior = rows[0]["service"]
            solde_senior = rows[0]["solde_fin"]
            solde_total = sum(rw["solde_fin"] for rw in rows)
            capex_maintien = tot_r * 0.02
        bai = baiia - amort - interets
        imp = impots(bai)
        benef = bai - imp
        flux = baiia - imp - service_total - capex_maintien
        if y >= 1:
            cumul += flux
        dscr_banc = (baiia - imp - capex_maintien) / service_total if service_total else None
        years.append({
            "label": YEARS[y], "revenus": r, "charges": c, "total_revenus": tot_r, "total_charges": tot_c,
            "hebergement": sum(r[k] for k in HEBERG_KEYS), "baiia": baiia, "marge_baiia": baiia / tot_r,
            "amortissement": amort, "interets": interets, "capital": capital, "service_dette": service_total,
            "service_senior": service_senior, "bai": bai, "impots": imp, "benefice_net": benef,
            "capex_maintien": capex_maintien, "flux_libre": flux, "tresorerie_cumulee": cumul if y >= 1 else 0.0,
            "dscr_senior": baiia / service_senior if service_senior else None,
            "dscr_total": baiia / service_total if service_total else None,
            "dscr_bancaire": dscr_banc,
            "couverture_interets": baiia / interets if interets else None,
            "solde_senior": solde_senior, "solde_total": solde_total,
        })
    return years, D

def bilan(years, D):
    """Pro forma au coût : immobilisations existantes au coût déclaré moins amortissement cumulé (hyp.),
    dette existante refinancée, fonds propres injectés ; le bilan doit balancer chaque année."""
    rows = []
    capex_cap = CAPEX + CONTINGENCE + HONORAIRES
    immo_exist_ouv = IMMO_EXISTANTES_COUT - AMORT_CUMULE_2026
    encaisse_ouv = FDR + RESERVE_SERVICE
    avoir_ouv = immo_exist_ouv + encaisse_ouv + CONFORMITE + INTERETS_CAPITALISES + FRAIS_FIN + capex_cap - DETTE_COUCHES
    # (les emplois non capitalisés — conformité, intérêts capitalisés — sont traités comme des frais reportés amortis sur 5 ans)
    reportes_ouv = CONFORMITE + INTERETS_CAPITALISES + FRAIS_FIN
    amort_exist_cum = amort_nouv_cum = maintien_cum = bnr = 0.0
    for i in range(1, 6):
        y = years[i]
        amort_exist_cum += AMORT_EXISTANT
        amort_nouv_cum += y["amortissement"] - AMORT_EXISTANT
        maintien_cum += y["capex_maintien"]
        bnr += y["benefice_net"]
        reportes = reportes_ouv * (1 - i / 5)
        amort_reportes_cum = reportes_ouv * i / 5
        encaisse = encaisse_ouv + y["tresorerie_cumulee"] + amort_reportes_cum   # l'amortissement des frais reportés n'est pas décaissé
        # correction : le bénéfice net du modèle n'inclut pas l'amortissement des frais reportés ; on l'impute aux BNR
        bnr_adj = bnr - amort_reportes_cum
        immo_exist = immo_exist_ouv - amort_exist_cum
        immo_nouv = capex_cap + maintien_cum - amort_nouv_cum
        encaisse = encaisse_ouv + y["tresorerie_cumulee"]
        actif = encaisse + immo_exist + immo_nouv + reportes
        solde = sum((d["rows"][i - 1]["solde_fin"] if i - 1 < len(d["rows"]) else 0.0) for d in D)
        portion = sum((d["rows"][i]["capital"] if i < len(d["rows"]) else 0.0) for d in D)
        avoir = avoir_ouv + bnr_adj
        ecart = actif - (solde + avoir)
        assert abs(ecart) < 1, f"bilan An {i} ne balance pas ({ecart:+.2f} $)"
        rows.append({"encaisse": encaisse, "immo_existantes_nettes": immo_exist, "immo_nouvelles_nettes": immo_nouv,
                     "frais_reportes": reportes, "actif_total": actif, "portion_courante": portion, "dette_lt": solde - portion,
                     "passif_total": solde, "avoir_ouverture": avoir_ouv, "bnr_cumules": bnr_adj, "avoir_total": avoir,
                     "dette_sur_avoir": solde / avoir, "fonds_roulement": encaisse / portion if portion else None})
    return rows

def sensibilite(years, D):
    """Scénarios sur le DSCR total (BAIIA / service de toutes les couches) et bancaire, An 2 / An 3 / An 5."""
    out = []
    def recompute(y, rev_factor=1.0, hiver_factor=1.0, fb_factor=1.0, service_factor=1.0, service_add=0.0):
        yr = years[y]
        r = dict(yr["revenus"])
        # hiver : même définition que la décomposition saisonnière (section 6.6 du plan)
        hiv = sum(revenus_hiver(y, r).values())
        rev = yr["total_revenus"] * rev_factor - hiv * (1 - hiver_factor) - r["restauration"] * (1 - fb_factor)
        var = sum(yr["charges"][k] * PART_VARIABLE[k] for k in yr["charges"])
        fixe = yr["total_charges"] - var
        var_adj = var * (rev / yr["total_revenus"])
        baiia = rev - var_adj - fixe
        service = yr["service_dette"] * service_factor + service_add
        imp = impots(baiia - yr["amortissement"] - yr["interets"])
        return baiia / service, (baiia - imp - rev * 0.02) / service
    # service à +1 et +2 points sur le senior (paiement plein) : recalcul du paiement
    def service_taux(y, taux, ans=25):
        base = years[y]["service_dette"] - years[y]["service_senior"]
        rows, _ = echeancier(SENIOR, taux, ans, 18, (REFINANCEMENT + TRANCHE_B * 0.55) / SENIOR)
        return base + rows[y - 1]["service"]
    scen = [
        ("Scénario de base", {}),
        ("Revenus −10 %", {"rev_factor": 0.90}),
        ("Revenus −15 %", {"rev_factor": 0.85}),
        ("Revenus −20 %", {"rev_factor": 0.80}),
        ("Revenus d'hiver −50 %", {"hiver_factor": 0.5}),
        ("Restauration −50 %", {"fb_factor": 0.5}),
    ]
    for nom, kw in scen:
        row = {"scenario": nom}
        for y in (2, 3, 5):
            t, b = recompute(y, **kw)
            row[f"dscr_an{y}"] = t
            row[f"dscr_banc_an{y}"] = b
        out.append(row)
    for nom, taux, ans in [("Taux senior 8 % (25 ans)", 0.08, 25), ("Taux senior 9 % (25 ans)", 0.09, 25), ("Amortissement senior 20 ans (7 %)", 0.07, 20)]:
        row = {"scenario": nom}
        for y in (2, 3, 5):
            yr = years[y]
            s = service_taux(y, taux, ans)
            row[f"dscr_an{y}"] = yr["baiia"] / s
            row[f"dscr_banc_an{y}"] = (yr["baiia"] - yr["impots"] - yr["capex_maintien"]) / s
        out.append(row)
    return out

def part_variable(years):
    y = years[3]
    var = sum(y["charges"][k] * PART_VARIABLE[k] for k in y["charges"])
    return var / y["total_charges"]

# ---------------------------------------------------------------------------
# Décomposition saisonnière : ce que l'hiver rapporte et ce qu'il coûte
# ---------------------------------------------------------------------------
# Été : du 15 mai au 15 octobre (184 jours). Hiver : du 16 octobre au 14 mai (181 jours).
# Ce sont les mêmes 184 / 181 jours que la projection de revenus par unité.
HS = {
    # Part hivernale des lignes de revenus qui ne sont pas calculées nuitée par nuitée.
    # Chalets, villas et unités Coolbox sont calculés directement (181 nuits d'hiver).
    "part_hiver": {
        "terrains": 0.0,        # camping non hivernal, fermé
        "saisonniers": 0.0,     # contrat de saison (mai à octobre), encaissé de janvier à mars
        "cabanas": 0.0,         # prêt-à-camper non chauffé
        "redevance": 0.0,       # 2026 seulement, avant le transfert des unités Coolbox
        "hotel": 0.30,          # hyp. : 30 % des nuitées d'hôtel hors saison estivale
        "spa": 0.50,            # hyp. (phase 2 seulement)
        "spectacles": 0.0,      # programmation estivale (scène, chapiteau)
        "activites": 0.10,      # hyp. : location d'équipement, patin, glissades
        "restauration": 0.35,   # hyp. : restaurant ouvert 12 mois, clientèle régionale de jour
    },
    "energie_ouvert": 0.60,     # hyp. : part de l'énergie annuelle consommée de novembre à avril
    "energie_ferme": 0.15,      # hyp. : hors-gel et maintien des bâtiments si le site fermait l'hiver
    "etp_ete": 34,              # tableau des effectifs, section 6.2
    "etp_hiver": 15,
    "etp_noyau": 3,             # direction, finances et surveillance des infrastructures : à l'année, que le site ouvre ou non
    "surcout_fixe": {"entretien": 0.15, "vehicules": 0.35},   # déneigement, chemins, toitures ; chargeur, souffleuse, carburant
}
ETP_ETE, ETP_HIVER = HS["etp_ete"], HS["etp_hiver"]

def revenus_hiver(year, r):
    """Revenus attribuables à la période hivernale, ligne par ligne."""
    if year == 0:
        return {k: 0.0 for k in r}   # en 2026, le site ferme en octobre
    h = {}
    h["chalets"] = H["chalets_n"] * 181 * H["chalets_hiver_frac"][year] * H["chalets_occ_hiver"][year] * idx(H["chalet_hiver"], year)
    h["villas"] = H["villas_n"] * 181 * H["villas_occ_hiver"][year] * idx(H["villa_hiver"], year)
    h["coolbox"] = H["coolbox_n"] * 181 * H["coolbox_occ_hiver"][year] * idx(H["coolbox_hiver"], year)
    for k, p in HS["part_hiver"].items():
        h[k] = r[k] * p
    return h

def charges_hiver(year, c, part_rev):
    """Charges attribuables à l'hiver, poste par poste, en (variable, fixe).

    Variable = suit le volume d'hiver ; fixe = engagé dès que le site reste ouvert.
    Les postes engagés que le site ouvre ou non l'hiver (taxes, assurances, loyers,
    honoraires comptables) ne sont pas imputés à l'hiver : la question posée est celle
    du surcoût marginal de l'exploitation hivernale, pas d'une répartition comptable.
    """
    var, fixe = {}, {}
    if year == 0:
        return {k: 0.0 for k in c}, {k: 0.0 for k in c}   # site fermé d'octobre à mai
    etp_mois_total = (HS["etp_ete"] + HS["etp_hiver"]) * 6
    etp_mois_hiver = max(HS["etp_hiver"] - HS["etp_noyau"], 0) * 6
    for k in c:
        if k == "energie":
            # chauffer et éclairer le site l'hiver, moins le hors-gel qu'il faudrait payer de toute façon
            total = c[k] * (HS["energie_ouvert"] - HS["energie_ferme"])
        elif k == "salaires":
            # effectifs d'hiver au-delà du noyau permanent (section 6.2)
            total = c[k] * etp_mois_hiver / etp_mois_total
        else:
            total = c[k] * PART_VARIABLE[k] * part_rev + c[k] * (1 - PART_VARIABLE[k]) * HS["surcout_fixe"].get(k, 0.0)
        var[k] = total * PART_VARIABLE[k]
        fixe[k] = total - var[k]
    return var, fixe

def saisons(years):
    """Revenus d'été et d'hiver, surcoûts d'hiver, contribution et point mort hivernal."""
    out = []
    for y, yr in enumerate(years):
        r, c = yr["revenus"], yr["charges"]
        h = revenus_hiver(y, r)
        rev_h = sum(h.values())
        rev_tot = yr["total_revenus"]
        part = rev_h / rev_tot if rev_tot else 0.0
        var, fixe = charges_hiver(y, c, part)
        cv, cf = sum(var.values()), sum(fixe.values())
        contrib = rev_h - cv - cf
        # point mort : facteur f sur les revenus d'hiver pour lequel la contribution s'annule
        marge_var = rev_h - cv
        out.append({
            "label": yr["label"],
            "revenus_hiver_lignes": h,
            "revenus_hiver": rev_h,
            "revenus_ete": rev_tot - rev_h,
            "part_hiver": part,
            "charges_hiver_variables": cv,
            "charges_hiver_fixes": cf,
            "charges_hiver": cv + cf,
            "surcout_energie": fixe["energie"] + var["energie"],
            "salaires_hiver": fixe["salaires"] + var["salaires"],
            "contribution_hiver": contrib,
            "marge_contribution": contrib / rev_h if rev_h else None,
            "point_mort": cf / marge_var if marge_var > 0 else None,
        })
    return out

def capacite(years):
    """Capacité d'endettement senior selon trois méthodes (An 3)."""
    y3 = years[3]
    noi = y3["baiia"] - y3["capex_maintien"]
    def montant_pour_service(s, taux=0.07, ans=25):
        return s / (pmt(1, taux, ans) * 12)
    return {
        "methode_dscr_125": montant_pour_service(noi / 1.25),
        "methode_5x_baiia": 5 * y3["baiia"],
        "methode_ltv_65_revenu": 0.65 * (noi * 0.8) / 0.095,
        "noi_an3": noi,
    }

def charts(years, D):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    navy, teal, gold, grey = "#0C4A5E", "#2BB5BF", "#F4B942", "#8FA6AB"
    palette = [navy, "#136B80", "#1A8FA3", "#2BB5BF", "#78E1E6", "#1E7F5C", "#3FA796", "#8FD3C0", gold, "#F7D98A", grey, "#C9B37E"]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fmt_m = FuncFormatter(lambda v, _: f"{v/1e6:.1f} M$")
    labels = [y["label"].replace(" – ", "\n") for y in years]

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    bottom = [0] * 6
    for (k, name), col in zip(LIGNES, palette):
        vals = [y["revenus"][k] for y in years]
        ax.bar(labels, vals, bottom=bottom, color=col, label=name.split(" (")[0], width=0.62)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, t in enumerate(bottom):
        ax.text(i, t + 60000, f"{t/1e6:.2f} M$", ha="center", fontsize=8, color=navy, fontweight="bold")
    ax.yaxis.set_major_formatter(fmt_m); ax.set_ylim(0, max(bottom) * 1.18)
    ax.legend(fontsize=6, ncol=3, frameon=False, loc="upper left")
    ax.set_title("Revenus par source", loc="left", fontsize=11, color=navy, fontweight="bold")
    fig.tight_layout(); fig.savefig(CHARTS / "revenus.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    x = list(range(1, 6))
    b = [years[i]["baiia"] for i in x]; s = [years[i]["service_dette"] for i in x]; ss = [years[i]["service_senior"] for i in x]
    ax.bar([i - 0.27 for i in x], b, width=0.27, color=teal, label="BAIIA")
    ax.bar([i for i in x], ss, width=0.27, color=navy, label="Service du prêt senior")
    ax.bar([i + 0.27 for i in x], s, width=0.27, color=grey, label="Service de toutes les couches")
    ax.yaxis.set_major_formatter(fmt_m); ax.set_xticks(x); ax.set_xticklabels([labels[i] for i in x])
    ax2 = ax.twinx()
    ds = [years[i]["dscr_bancaire"] for i in x]
    ax2.plot(x, ds, color=gold, marker="o", linewidth=2, label="DSCR (définition bancaire, toutes couches)")
    for xi, v in zip(x, ds):
        ax2.text(xi, v + 0.07, f"{v:.2f}", ha="center", fontsize=8, color=navy, fontweight="bold")
    ax2.axhline(1.25, color=gold, linestyle="--", linewidth=1); ax2.text(5.35, 1.27, "Seuil 1,25", fontsize=7, color=gold, ha="right")
    ax2.set_ylim(0, max(ds) * 1.4); ax2.spines["top"].set_visible(False); ax2.set_ylabel("DSCR (x)")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6.5, frameon=False, loc="upper left", ncol=2)
    ax.set_title("Capacité de remboursement", loc="left", fontsize=11, color=navy, fontweight="bold")
    fig.tight_layout(); fig.savefig(CHARTS / "dscr.png"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.8), dpi=200)
    for ax, data, title in ((axes[0], [(e[0], e[1]) for e in EMPLOIS], "Emplois"), (axes[1], [(s[0], s[1]) for s in SOURCES], "Sources")):
        vals = [d[1] for d in data]; names = [d[0].split(" (")[0].split(" – ")[0][:38] for d in data]
        wedges, _ = ax.pie(vals, colors=palette[: len(vals)], startangle=90, wedgeprops={"width": 0.38, "edgecolor": "white"})
        ax.set_title(f"{title} : {sum(vals)/1e6:.2f} M$", fontsize=10, color=navy, fontweight="bold")
        ax.legend(wedges, [f"{n} – {v/1e6:.2f} M$" for n, v in zip(names, vals)], fontsize=5.2, loc="upper center", bbox_to_anchor=(0.5, 0.02), frameon=False)
    fig.tight_layout(); fig.savefig(CHARTS / "sources_emplois.png"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=200)
    for ax, yi, title in ((axes[0], 0, "2026 (réel)"), (axes[1], 5, "An 5 – 2031")):
        r = years[yi]["revenus"]; items = [(name.split(" (")[0], r[k], palette[i]) for i, (k, name) in enumerate(LIGNES) if r[k] > 0]
        wedges, _ = ax.pie([v for _, v, _ in items], colors=[c for _, _, c in items], startangle=90, wedgeprops={"width": 0.38, "edgecolor": "white"})
        tot = sum(v for _, v, _ in items)
        ax.set_title(f"{title} : {tot/1e6:.2f} M$", fontsize=10, color=navy, fontweight="bold")
        ax.legend(wedges, [f"{n} {v/tot*100:.0f} %" for n, v, _ in items], fontsize=5.8, loc="upper center", bbox_to_anchor=(0.5, 0.02), frameon=False, ncol=2)
    fig.tight_layout(); fig.savefig(CHARTS / "repartition.png"); plt.close(fig)

    S = saisons(years)
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=200)
    ete = [s["revenus_ete"] for s in S]
    hiv = [s["revenus_hiver"] for s in S]
    ax.bar(labels, ete, color=teal, width=0.6, label="Été (15 mai – 15 octobre, 184 jours)")
    ax.bar(labels, hiv, bottom=ete, color=navy, width=0.6, label="Hiver (16 octobre – 14 mai, 181 jours)")
    for i, s in enumerate(S):
        if s["revenus_hiver"] > 0:
            ax.text(i, ete[i] + hiv[i] / 2, f"{s['part_hiver']*100:.0f} %", ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")
        ax.text(i, ete[i] + hiv[i] + 50000, f"{(ete[i]+hiv[i])/1e6:.2f} M$", ha="center", fontsize=8, color=navy, fontweight="bold")
    ax.yaxis.set_major_formatter(fmt_m); ax.set_ylim(0, max(e + h for e, h in zip(ete, hiv)) * 1.18)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title("Revenus par saison", loc="left", fontsize=11, color=navy, fontweight="bold")
    fig.tight_layout(); fig.savefig(CHARTS / "saisons.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 2.9), dpi=200)
    taches = [
        ("Clôture du financement, dépôt des fonds propres", 0, 2, navy),
        ("Travaux : hôtel, restaurant, villas, chalets", 1, 6, teal),
        ("Unités Coolbox : commande, fabrication, livraison", 2, 4, "#1E7F5C"),
        ("Ouverture des nouvelles installations (juillet 2027)", 6, 1, gold),
        ("Vente des contrats saisonniers 2028 et programme d'hiver", 8, 5, "#C9B37E"),
        ("Exploitation douze mois, montée en régime", 12, 12, "#78E1E6"),
    ]
    for i, (name, start, dur, col) in enumerate(taches):
        ax.barh(i, dur, left=start, color=col, height=0.55)
        ax.text(start + dur + 0.2, i, name, va="center", fontsize=6.5)
    ax.set_yticks([]); ax.invert_yaxis()
    mois = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"] * 2; mois[0] = "J\n2027"; mois[12] = "J\n2028"
    ax.set_xticks(range(24)); ax.set_xticklabels(mois, fontsize=7); ax.set_xlim(0, 34)
    ax.axvline(12, color=grey, linewidth=0.6, linestyle=":")
    ax.set_title("Échéancier de réalisation", loc="left", fontsize=11, color=navy, fontweight="bold")
    ax.spines["left"].set_visible(False)
    fig.tight_layout(); fig.savefig(CHARTS / "echeancier.png"); plt.close(fig)

def main():
    years, D = modele()
    data = {
        "annees": years, "lignes": LIGNES, "charges": CHARGES, "projets": PROJETS,
        "emplois": EMPLOIS, "sources": SOURCES, "couches": [{k: v for k, v in d.items() if k != "rows"} | {"rows": d["rows"][:5], "complet": d["rows"]} for d in D],
        "total_emplois": TOTAL_EMPLOIS, "argent_neuf": ARGENT_NEUF, "fonds_propres": FONDS_PROPRES,
        "pct_fonds_propres_argent_neuf": FONDS_PROPRES / ARGENT_NEUF, "fonds_propres_especes": FONDS_PROPRES_ESPECES, "apport_coolbox": APPORT_COOLBOX, "senior": SENIOR, "tranche_a": REFINANCEMENT, "tranche_b": TRANCHE_B,
        "paiement_senior": PAIEMENT_SENIOR, "reserve_service": RESERVE_SERVICE, "interets_capitalises": INTERETS_CAPITALISES,
        "coolbox_unite": COOLBOX_UNITE, "coolbox_2026": COOLBOX_2026, "contingence": CONTINGENCE,
        "reel_2025_total": REEL_2025_TOTAL, "reel_2026_total": REEL_2026_TOTAL, "autres_2026": AUTRES_2026,
        "dpa": dpa(), "bilan": bilan(years, D), "sensibilite": sensibilite(years, D), "part_variable": part_variable(years),
        "saisons": saisons(years), "hypotheses_saison": HS,
        "capacite": capacite(years), "hypotheses": {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in H.items()},
        "immo_existantes_cout": IMMO_EXISTANTES_COUT, "amort_cumule_2026": AMORT_CUMULE_2026,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    charts(years, D)
    print(f"{'Année':<14}{'Revenus':>12}{'Charges':>12}{'BAIIA':>12}{'Marge':>7}{'Serv.sen':>11}{'Serv.tot':>11}{'DSCRs':>7}{'DSCRt':>7}{'DSCRb':>7}{'Bén.net':>11}{'Flux':>11}")
    for y in years:
        print(f"{y['label']:<14}{y['total_revenus']:>12,.0f}{y['total_charges']:>12,.0f}{y['baiia']:>12,.0f}{y['marge_baiia']*100:>6.1f}%{y['service_senior']:>11,.0f}{y['service_dette']:>11,.0f}{(y['dscr_senior'] or 0):>7.2f}{(y['dscr_total'] or 0):>7.2f}{(y['dscr_bancaire'] or 0):>7.2f}{y['benefice_net']:>11,.0f}{y['flux_libre']:>11,.0f}")
    print("Emplois", f"{TOTAL_EMPLOIS:,.0f}", "argent neuf", f"{ARGENT_NEUF:,.0f}", "fonds propres", f"{FONDS_PROPRES:,.0f}", f"({FONDS_PROPRES/ARGENT_NEUF:.1%} de l'argent neuf)", "senior", f"{SENIOR:,.0f}", "paiement", f"{PAIEMENT_SENIOR:,.0f}")
    print("Capacité An 3", {k: round(v) for k, v in capacite(years).items()}, "part variable", f"{part_variable(years):.1%}")
    for s in sensibilite(years, D):
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()})
    print(f"\n{'Saison':<14}{'Rev. été':>12}{'Rev. hiver':>12}{'% hiver':>9}{'Ch. hiver':>12}{'Contrib.':>12}{'Marge':>8}{'Pt mort':>9}")
    for s in saisons(years):
        pm = f"{s['point_mort']*100:>8.0f}%" if s["point_mort"] is not None else "       —"
        mg = f"{s['marge_contribution']*100:>7.0f}%" if s["marge_contribution"] is not None else "      —"
        print(f"{s['label']:<14}{s['revenus_ete']:>12,.0f}{s['revenus_hiver']:>12,.0f}{s['part_hiver']*100:>8.1f}%{s['charges_hiver']:>12,.0f}{s['contribution_hiver']:>12,.0f}{mg}{pm}")

if __name__ == "__main__":
    main()
