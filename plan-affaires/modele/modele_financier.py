#!/usr/bin/env python3
"""Modèle financier prévisionnel du Complexe Havana (An 0 réel, An 1 à An 5 projetés).

Toutes les hypothèses sont explicites dans ce fichier. Le script produit
`modele.json` (utilisé par le générateur du plan d'affaires Word) et des
graphiques PNG dans `graphiques/`.
"""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "modele.json"
CHARTS = HERE / "graphiques"
CHARTS.mkdir(exist_ok=True)

YEARS = ["2026 (réel)", "An 1 – 2027", "An 2 – 2028", "An 3 – 2029", "An 4 – 2030", "An 5 – 2031"]
INFL = 0.03  # indexation annuelle des tarifs

# ---------------------------------------------------------------------------
# Revenus réels 2026 (système de réservation, 2025-09-15 au 2026-09-15)
# ---------------------------------------------------------------------------
REEL_2026 = {
    "terrains": 791894.29,
    "saisonniers": 43208.71,
    "chalets": 497722.97,   # chalets et chambres existantes (catégorie « chalet »)
    "cabanas": 199015.63,
}
REEL_2025_TOTAL = 1453605.16
REEL_2026_TOTAL = 1531841.68
# Revenus hors système de réservation, selon le budget interne (à valider)
AUTRES_2026 = {"restauration": 100000.0, "activites": 96700.0}


def idx(base, year):
    """Indexe un montant de base (An 1) à l'inflation pour l'année donnée (1..5)."""
    return base * (1 + INFL) ** (year - 1)


# ---------------------------------------------------------------------------
# Hypothèses d'exploitation par ligne de revenus
# ---------------------------------------------------------------------------
def revenus(year):
    r = {}
    if year == 0:
        r.update(REEL_2026)
        r["villas"] = 0.0
        r["hotel"] = 0.0
        r["spa"] = 0.0
        r["spectacles"] = 0.0
        r["sentier"] = 0.0
        r.update(AUTRES_2026)
        return r

    # Terrains de camping : 265 emplacements, tarifs indexés, léger gain
    # d'occupation à partir de l'An 2 (piscine et spa, animation).
    uplift = {1: 1.00, 2: 1.02, 3: 1.04, 4: 1.05, 5: 1.05}[year]
    r["terrains"] = REEL_2026["terrains"] * (1 + INFL) ** year * uplift

    # Terrains saisonniers : 35 existants, 35 nouveaux livrés pour l'An 2.
    sites = {1: 30, 2: 52, 3: 64, 4: 70, 5: 70}[year]
    r["saisonniers"] = sites * idx(3650, year)

    # Chalets existants (16) : rénovés 4 saisons pendant l'hiver 2027.
    # Été (184 nuits) et hiver (181 nuits). L'An 1 ne compte qu'un demi-hiver.
    ete_occ = {1: 0.58, 2: 0.62, 3: 0.65, 4: 0.67, 5: 0.68}[year]
    hiv_occ = {1: 0.15, 2: 0.25, 3: 0.30, 4: 0.33, 5: 0.35}[year]
    hiv_frac = {1: 0.5, 2: 1, 3: 1, 4: 1, 5: 1}[year]
    r["chalets"] = 16 * (184 * ete_occ * idx(235, year) + 181 * hiv_frac * hiv_occ * idx(210, year))

    # Villas (13) : livrées pour l'été 2027 (An 1 : 80 % de la saison).
    v_ete = {1: 0.50, 2: 0.55, 3: 0.60, 4: 0.63, 5: 0.65}[year]
    v_hiv = {1: 0.12, 2: 0.22, 3: 0.28, 4: 0.30, 5: 0.32}[year]
    v_frac = {1: 0.8, 2: 1, 3: 1, 4: 1, 5: 1}[year]
    r["villas"] = 13 * v_frac * (184 * v_ete * idx(275, year) + 181 * hiv_frac * v_hiv * idx(245, year))

    # Hôtel : 6 chambres existantes + 11 nouvelles livrées pour l'été 2027.
    # Modèle annuel : 365 nuits, occupation moyenne et tarif moyen.
    h_occ = {1: 0.40, 2: 0.45, 3: 0.52, 4: 0.55, 5: 0.57}[year]
    h_rooms = {1: 14.5, 2: 17, 3: 17, 4: 17, 5: 17}[year]  # An 1 : moyenne pondérée
    r["hotel"] = h_rooms * 365 * h_occ * idx(190, year)

    # Cabanas (13) : stable, indexé, léger gain avec le spa.
    r["cabanas"] = REEL_2026["cabanas"] * (1 + INFL) ** year * {1: 1.0, 2: 1.03, 3: 1.05, 4: 1.05, 5: 1.05}[year]

    # Restauration (Madera, café, mojito bar, cantine).
    # Restaurant ouvert en juillet 2027. Cible : 24 % à 26 % des revenus
    # d'hébergement à maturité (norme des centres de villégiature).
    hebergement = r["terrains"] + r["saisonniers"] + r["chalets"] + r["villas"] + r["hotel"] + r["cabanas"]
    fb_ratio = {1: 0.16, 2: 0.21, 3: 0.24, 4: 0.25, 5: 0.26}[year]
    r["restauration"] = hebergement * fb_ratio

    # Spa et piscine 4 saisons : ouverture juin 2028 (An 2).
    visites = {1: 0, 2: 4000, 3: 7500, 4: 9000, 5: 9500}[year]
    r["spa"] = visites * idx(55, year)

    # Spectacles et festivals (amphithéâtre) : billetterie nette, An 2.
    r["spectacles"] = {1: 0, 2: 120000, 3: 220000, 4: 280000, 5: 300000}[year] * (1 + INFL) ** (year - 2 if year >= 2 else 0)

    # Sentier lumineux : hiver 2028-2029 (An 2 partiel).
    r["sentier"] = {1: 0, 2: 45000, 3: 140000, 4: 165000, 5: 175000}[year]

    # Activités et concessions (jeux gonflables, partenariats 50/50).
    r["activites"] = {1: 105000, 2: 130000, 3: 145000, 4: 152000, 5: 158000}[year]
    return r


LIGNES = [
    ("terrains", "Terrains de camping (265)"),
    ("saisonniers", "Terrains saisonniers (35 → 70)"),
    ("chalets", "Chalets 4 saisons (16)"),
    ("villas", "Villas (13)"),
    ("hotel", "Hôtel (17 chambres)"),
    ("cabanas", "Cabanas prêt-à-camper (13)"),
    ("restauration", "Restauration et bars"),
    ("spa", "Spa et piscine 4 saisons"),
    ("spectacles", "Spectacles et festivals"),
    ("sentier", "Sentier lumineux"),
    ("activites", "Activités et concessions"),
]


# ---------------------------------------------------------------------------
# Charges d'exploitation
# ---------------------------------------------------------------------------
def charges(year, r):
    total_rev = sum(r.values())
    fb = r["restauration"]
    c = {}
    c["cout_ventes"] = fb * 0.33 + r["activites"] * 0.20
    sal_pct = {0: 0.39, 1: 0.36, 2: 0.34, 3: 0.33, 4: 0.325, 5: 0.32}[year]
    c["salaires"] = total_rev * sal_pct
    c["energie"] = {0: 242500, 1: 275000, 2: 400000, 3: 420000, 4: 435000, 5: 450000}[year]
    c["entretien"] = total_rev * 0.04
    c["marketing"] = total_rev * ({0: 0.03, 1: 0.035, 2: 0.035, 3: 0.03, 4: 0.03, 5: 0.03}[year])
    c["assurances"] = {0: 60000, 1: 95000, 2: 130000, 3: 134000, 4: 138000, 5: 142000}[year]
    c["taxes"] = {0: 54500, 1: 75000, 2: 130000, 3: 133000, 4: 136000, 5: 139000}[year]
    c["admin"] = total_rev * 0.025
    c["bancaires"] = total_rev * 0.015
    c["fournitures"] = total_rev * 0.025
    c["loyers"] = 42000 * (1.02 ** year)
    c["divers"] = total_rev * 0.02
    return c


CHARGES = [
    ("cout_ventes", "Coût des ventes (restauration, concessions)"),
    ("salaires", "Salaires et charges sociales"),
    ("energie", "Électricité, chauffage et propane"),
    ("entretien", "Entretien et réparations"),
    ("marketing", "Marketing et commercialisation"),
    ("assurances", "Assurances"),
    ("taxes", "Taxes municipales et scolaires"),
    ("admin", "Administration, honoraires, TI et télécoms"),
    ("bancaires", "Frais bancaires et de cartes"),
    ("fournitures", "Fournitures d'exploitation"),
    ("loyers", "Loyers et locations"),
    ("divers", "Divers et imprévus"),
]

# ---------------------------------------------------------------------------
# Investissement, financement et dette
# ---------------------------------------------------------------------------
PROJETS = [
    ("Phase 1", "Hôtel : de 6 à 17 chambres, exploitation 12 mois", 700000),
    ("Phase 1", "Restaurant Madera et salle de conférence", 800000),
    ("Phase 1", "Achèvement des 13 villas", 150000),
    ("Phase 1", "Chalets existants : mise à niveau 4 saisons", 150000),
    ("Phase 1", "35 terrains saisonniers additionnels", 700000),
    ("Phase 2", "Piscine et spa 4 saisons", 2000000),
    ("Phase 2", "Amphithéâtre", 500000),
    ("Phase 2", "Sentier lumineux", 500000),
]
CAPEX = sum(p[2] for p in PROJETS)
EMPLOIS = [
    ("Projets de développement (phases 1 et 2)", CAPEX),
    ("Contingence de construction (5 %)", 275000),
    ("Honoraires professionnels (plans, ingénierie, permis)", 175000),
    ("Frais de financement et juridiques", 75000),
    ("Refinancement de la dette existante", 5000000),
    ("Fonds de roulement de démarrage", 100000),
]
TOTAL_EMPLOIS = sum(e[1] for e in EMPLOIS)
PRET = 10300000
MISE_DE_FONDS = TOTAL_EMPLOIS - PRET
SOURCES = [
    ("Prêt à terme hypothécaire (demandé)", PRET),
    ("Mise de fonds des propriétaires et investisseurs privés", MISE_DE_FONDS),
]
TAUX = 0.07
AMORT_ANS = 25
VALEUR_SITE = 28000000

r_m = TAUX / 12
n = AMORT_ANS * 12
PAIEMENT_MENSUEL = PRET * r_m / (1 - (1 + r_m) ** -n)
SERVICE_DETTE_PLEIN = PAIEMENT_MENSUEL * 12


def dette():
    """Échéancier annuel. Moratoire de capital de 18 mois pendant la
    construction (jusqu'à l'ouverture de la phase 2) : An 1 intérêts seulement
    sur le solde moyen décaissé ; An 2 six mois d'intérêts seulement puis six
    mois de capital et intérêts ; An 3 à An 5 capital et intérêts (25 ans)."""
    rows = []
    solde_moyen_an1 = 5000000 + 2500000 * 0.75 + 3000000 * 0.20  # refinancement + décaissements
    interet1 = solde_moyen_an1 * TAUX
    rows.append({"an": 1, "interets": interet1, "capital": 0.0, "service": interet1, "solde_fin": PRET})
    solde = PRET
    for an in range(2, 6):
        interets = 0.0
        capital = 0.0
        for m in range(12):
            i = solde * r_m
            interets += i
            if an == 2 and m < 6:
                continue
            p = PAIEMENT_MENSUEL - i
            capital += p
            solde -= p
        rows.append({"an": an, "interets": interets, "capital": capital, "service": interets + capital, "solde_fin": solde})
    return rows


AMORT_EXISTANT = 150000  # amortissement comptable des actifs existants (hypothèse)
TAUX_AMORT_NOUVEAU = 0.04
TAUX_IMPOT = 0.20  # taux combiné moyen (petite entreprise et taux général)


def modele():
    years = []
    d = dette()
    cumul_tresorerie = 0.0
    for y in range(0, 6):
        r = revenus(y)
        c = charges(y, r)
        total_rev = sum(r.values())
        total_ch = sum(c.values())
        baiia = total_rev - total_ch
        if y == 0:
            amort = AMORT_EXISTANT
            interets = 5000000 * 0.075  # dette existante, hypothèse
            capital = 0.0
            service = interets + 0.0
        else:
            capex_cumule = 2500000 if y == 1 else CAPEX
            amort = AMORT_EXISTANT + capex_cumule * TAUX_AMORT_NOUVEAU
            row = d[y - 1]
            interets, capital, service = row["interets"], row["capital"], row["service"]
        bai = baiia - amort - interets
        impots = max(bai, 0) * TAUX_IMPOT
        benef_net = bai - impots
        capex_maintien = total_rev * 0.02 if y >= 1 else 0.0
        flux = baiia - impots - service - capex_maintien
        if y >= 1:
            cumul_tresorerie += flux
        years.append({
            "label": YEARS[y],
            "revenus": r,
            "charges": c,
            "total_revenus": total_rev,
            "total_charges": total_ch,
            "baiia": baiia,
            "marge_baiia": baiia / total_rev,
            "amortissement": amort,
            "interets": interets,
            "capital": capital,
            "service_dette": service,
            "bai": bai,
            "impots": impots,
            "benefice_net": benef_net,
            "capex_maintien": capex_maintien,
            "flux_libre": flux,
            "tresorerie_cumulee": cumul_tresorerie if y >= 1 else 0.0,
            "dscr": baiia / service if service else None,
            "couverture_interets": baiia / interets if interets else None,
            "solde_dette": d[y - 1]["solde_fin"] if y >= 1 else 5000000,
        })
    return years


def sensibilite(years):
    """DSCR An 3 et An 5 si les revenus sont inférieurs de 10 % et 15 %, en
    supposant que les charges variables baissent proportionnellement (60 %
    des charges sont variables) et que les charges fixes demeurent."""
    out = []
    for chute in (0.0, -0.10, -0.15, -0.20):
        row = {"scenario": f"Revenus {int(chute*100):+d} %" if chute else "Scénario de base"}
        for y in (2, 3, 5):
            yr = years[y]
            rev = yr["total_revenus"] * (1 + chute)
            var = yr["total_charges"] * 0.60 * (1 + chute)
            fixe = yr["total_charges"] * 0.40
            baiia = rev - var - fixe
            row[f"dscr_an{y}"] = baiia / yr["service_dette"]
            row[f"baiia_an{y}"] = baiia
        out.append(row)
    return out


def charts(years):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    navy, teal, gold, grey = "#0B2A4A", "#1B7F79", "#C9A227", "#8A94A6"
    palette = [navy, "#1F4E79", "#2E75B6", "#5B9BD5", "#9DC3E6", teal, "#3FA796", "#7FCDBB", gold, "#E0C36A", grey]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fmt_m = FuncFormatter(lambda v, _: f"{v/1e6:.1f} M$")
    labels = [y["label"].replace(" – ", "\n") for y in years]

    # 1. Revenus par source
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
    bottom = [0] * 6
    for (k, name), col in zip(LIGNES, palette):
        vals = [y["revenus"][k] for y in years]
        ax.bar(labels, vals, bottom=bottom, color=col, label=name, width=0.62)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, t in enumerate(bottom):
        ax.text(i, t + 60000, f"{t/1e6:.2f} M$", ha="center", fontsize=8, color=navy, fontweight="bold")
    ax.yaxis.set_major_formatter(fmt_m)
    ax.set_ylim(0, max(bottom) * 1.15)
    ax.legend(fontsize=6.5, ncol=3, frameon=False, loc="upper left")
    ax.set_title("Revenus par source", loc="left", fontsize=11, color=navy, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "revenus.png")
    plt.close(fig)

    # 2. BAIIA, service de la dette et DSCR
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    x = list(range(1, 6))
    b = [years[i]["baiia"] for i in x]
    s = [years[i]["service_dette"] for i in x]
    ax.bar([i - 0.18 for i in x], b, width=0.36, color=teal, label="BAIIA")
    ax.bar([i + 0.18 for i in x], s, width=0.36, color=grey, label="Service de la dette")
    ax.yaxis.set_major_formatter(fmt_m)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[i] for i in x])
    ax2 = ax.twinx()
    ds = [years[i]["dscr"] for i in x]
    ax2.plot(x, ds, color=navy, marker="o", linewidth=2, label="Ratio de couverture (DSCR)")
    for xi, v in zip(x, ds):
        ax2.text(xi, v + 0.08, f"{v:.2f}", ha="center", fontsize=8, color=navy, fontweight="bold")
    ax2.axhline(1.25, color=gold, linestyle="--", linewidth=1)
    ax2.text(5.35, 1.27, "Seuil 1,25", fontsize=7, color=gold, ha="right")
    ax2.set_ylim(0, max(ds) * 1.35)
    ax2.spines["top"].set_visible(False)
    ax2.set_ylabel("DSCR (x)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, frameon=False, loc="upper left", ncol=3)
    ax.set_title("Capacité de remboursement", loc="left", fontsize=11, color=navy, fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "dscr.png")
    plt.close(fig)

    # 3. Emplois et sources
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), dpi=200)
    for ax, data, title in ((axes[0], EMPLOIS, "Emplois"), (axes[1], SOURCES, "Sources")):
        vals = [d[1] for d in data]
        names = [d[0] for d in data]
        wedges, _ = ax.pie(vals, colors=palette[: len(vals)] if title == "Emplois" else [navy, teal], startangle=90, wedgeprops={"width": 0.38, "edgecolor": "white"})
        ax.set_title(f"{title} : {sum(vals)/1e6:.2f} M$", fontsize=10, color=navy, fontweight="bold")
        ax.legend(wedges, [f"{n} – {v/1e6:.2f} M$" for n, v in zip(names, vals)], fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, 0.02), frameon=False)
    fig.tight_layout()
    fig.savefig(CHARTS / "sources_emplois.png")
    plt.close(fig)

    # 4. Répartition des revenus An 5 vs 2026
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=200)
    for ax, yi, title in ((axes[0], 0, "2026 (réel)"), (axes[1], 5, "An 5 – 2031")):
        r = years[yi]["revenus"]
        items = [(name, r[k]) for k, name in LIGNES if r[k] > 0]
        wedges, _ = ax.pie([v for _, v in items], colors=[palette[[k for k, _ in LIGNES].index(k)] for k, _ in [(k, n) for k, n in LIGNES if r[k] > 0]], startangle=90, wedgeprops={"width": 0.38, "edgecolor": "white"})
        ax.set_title(f"{title} : {sum(v for _, v in items)/1e6:.2f} M$", fontsize=10, color=navy, fontweight="bold")
        ax.legend(wedges, [f"{n} {v/sum(x for _, x in items)*100:.0f} %" for n, v in items], fontsize=6.3, loc="upper center", bbox_to_anchor=(0.5, 0.02), frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(CHARTS / "repartition.png")
    plt.close(fig)

    # 5. Échéancier
    fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
    taches = [
        ("Clôture du financement", 0, 2, navy),
        ("Phase 1 : hôtel, restaurant, villas, chalets, saisonniers", 1, 6, teal),
        ("Ouverture phase 1 (saison 2027)", 6, 1, gold),
        ("Phase 2 : piscine-spa, amphithéâtre, sentier", 8, 9, teal),
        ("Ouverture phase 2 (saison 2028)", 17, 1, gold),
        ("Exploitation 12 mois, montée en régime", 18, 6, "#5B9BD5"),
    ]
    for i, (name, start, dur, col) in enumerate(taches):
        ax.barh(i, dur, left=start, color=col, height=0.55)
        ax.text(start + dur + 0.2, i, name, va="center", fontsize=7)
    ax.set_yticks([])
    ax.invert_yaxis()
    mois = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"] * 2
    mois[0] = "J\n2027"
    mois[12] = "J\n2028"
    ax.set_xticks(range(24))
    ax.set_xticklabels(mois, fontsize=7)
    ax.set_xlim(0, 33)
    ax.axvline(12, color=grey, linewidth=0.6, linestyle=":")
    ax.set_title("Échéancier de réalisation", loc="left", fontsize=11, color=navy, fontweight="bold")
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHARTS / "echeancier.png")
    plt.close(fig)


def main():
    years = modele()
    data = {
        "annees": years,
        "lignes": LIGNES,
        "charges": CHARGES,
        "projets": PROJETS,
        "emplois": EMPLOIS,
        "sources": SOURCES,
        "pret": PRET,
        "taux": TAUX,
        "amort_ans": AMORT_ANS,
        "paiement_mensuel": PAIEMENT_MENSUEL,
        "service_dette_plein": SERVICE_DETTE_PLEIN,
        "valeur_site": VALEUR_SITE,
        "ltv": PRET / VALEUR_SITE,
        "reel_2025_total": REEL_2025_TOTAL,
        "reel_2026_total": REEL_2026_TOTAL,
        "dette": dette(),
        "sensibilite": sensibilite(years),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    charts(years)
    # Résumé console
    print(f"{'Année':<14}{'Revenus':>12}{'Charges':>12}{'BAIIA':>12}{'Marge':>7}{'Service':>12}{'DSCR':>6}{'Bén. net':>12}{'Flux':>12}")
    for y in years:
        print(f"{y['label']:<14}{y['total_revenus']:>12,.0f}{y['total_charges']:>12,.0f}{y['baiia']:>12,.0f}{y['marge_baiia']*100:>6.1f}%{y['service_dette']:>12,.0f}{y['dscr']:>6.2f}{y['benefice_net']:>12,.0f}{y['flux_libre']:>12,.0f}")
    print("Paiement mensuel", f"{PAIEMENT_MENSUEL:,.0f}", "Service plein", f"{SERVICE_DETTE_PLEIN:,.0f}", "Mise de fonds", f"{MISE_DE_FONDS:,.0f}", "LTV", f"{PRET/VALEUR_SITE:.1%}")
    for y in years[1:]:
        print(y["label"], {k: round(v) for k, v in y["revenus"].items()})
    for s in sensibilite(years):
        print(s)


if __name__ == "__main__":
    main()
