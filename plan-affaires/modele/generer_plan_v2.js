// Générateur du plan d'affaires bancaire v2 du Complexe Havana.
// Lit modele_v2.json (scénario de base : phase 1a) et modele_v2_phase2.json (comparaison),
// plus les graphiques de graphiques_v2/. Usage : node generer_plan_v2.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, ImageRun, PageBreak, Header, Footer, PageNumber,
  TableOfContents, LevelFormat, VerticalAlign, TabStopType, LineRuleType,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, TextWrappingType,
} = require("docx");

const HERE = __dirname;
const M = JSON.parse(fs.readFileSync(path.join(HERE, "modele_v2.json"), "utf8"));
const M2 = fs.existsSync(path.join(HERE, "modele_v2_phase2.json")) ? JSON.parse(fs.readFileSync(path.join(HERE, "modele_v2_phase2.json"), "utf8")) : null;
const OUTPUT = path.join(HERE, "..", "Plan_affaires_Complexe_Havana_v2.docx");
const PHOTOS_META = path.join(HERE, "..", "photos", "photos_meta.json");
const PHOTOS = fs.existsSync(PHOTOS_META) ? JSON.parse(fs.readFileSync(PHOTOS_META, "utf8")) : {};
const CH = "graphiques_v2";

const NAVY = "0C4A5E", TEAL = "2BB5BF", GOLD = "F4B942", GREY = "6F8A90", LIGHT = "F5F2EA", MID = "CFE3E6", WHITE = "FFFFFF", INK = "1E2A2E";
const FONT = "Calibri";
const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1296;
const CONTENT_W = PAGE_W - 2 * MARGIN;

const fmt = (n, dec = 0) => { const neg = n < 0; const s = Math.abs(n).toFixed(dec); const [int, frac] = s.split("."); const g = int.replace(/\B(?=(\d{3})+(?!\d))/g, " "); return (neg ? "(" : "") + g + (frac ? "," + frac : "") + (neg ? ")" : ""); };
const money = (n) => fmt(n) + " $";
const moneyM = (n, dec = 2) => fmt(n / 1e6, dec) + " M$";
const pct = (x, dec = 1) => fmt(x * 100, dec) + " %";
const ratio = (x, dec = 2) => (x === null || x === undefined) ? "—" : fmt(x, dec) + " x";

const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: 21, color: INK, ...opts });
const P = (text, opts = {}) => { const { bold, italics, color, size, align, before = 0, after = 120, keepNext, indent } = opts; const runs = Array.isArray(text) ? text : [run(text, { bold, italics, color, size })]; return new Paragraph({ children: runs, alignment: align || AlignmentType.LEFT, spacing: { before, after, line: 276 }, keepNext, indent }); };
const NOTE = (text) => P(text, { italics: true, color: GREY, size: 18 });
const EMU = 914400;
const bleedImage = (meta, topIn, widthIn, heightIn) => new ImageRun({ type: "jpg", data: fs.readFileSync(path.join(HERE, "..", meta.file)), transformation: { width: Math.round(widthIn * 96), height: Math.round(heightIn * 96) }, floating: { horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 0 }, verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: Math.round(topIn * EMU) }, behindDocument: true, allowOverlap: true, lockAnchor: true, layoutInCell: false, wrap: { type: TextWrappingType.NONE } } });
const exactSpacer = (twips, extra = {}) => new Paragraph({ spacing: { before: 0, after: 0, line: twips, lineRule: LineRuleType.EXACT }, children: [], ...extra });
const LEAD = (text) => new Paragraph({ children: [new TextRun({ text, font: "Georgia", size: 25, italics: true, color: TEAL })], spacing: { before: 0, after: 240, line: 300 } });
const chapter = (num, title, slot, lead) => { const meta = PHOTOS[slot]; const out = []; out.push(new Paragraph({ pageBreakBefore: true, spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT }, children: meta ? [bleedImage(meta, 0.62, 8.5, 4.2)] : [] })); out.push(exactSpacer(meta ? 3800 : 200)); out.push(new Paragraph({ children: [run(num, { bold: true, size: 26, color: meta ? GOLD : TEAL })], spacing: { before: 0, after: 60 } })); out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: title, font: FONT, size: 46, bold: true, color: meta ? WHITE : NAVY })], spacing: { before: 0, after: 0 } })); out.push(exactSpacer(meta ? 1250 : 200)); if (lead) out.push(LEAD(lead)); return out; };
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: FONT, size: 27, bold: true, color: NAVY })], spacing: { before: 300, after: 120 }, keepNext: true });
const H3 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text, font: FONT, size: 22, bold: true, color: TEAL })], spacing: { before: 200, after: 80 }, keepNext: true });
const bullets = (items, ref = "puces") => items.map((t) => new Paragraph({ children: Array.isArray(t) ? t : [run(t)], numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 276 } }));
const numbered = (items) => items.map((t) => new Paragraph({ children: Array.isArray(t) ? t : [run(t)], numbering: { reference: "numeros", level: 0 }, spacing: { after: 80, line: 276 } }));
const border = (color = MID, size = 4) => ({ style: BorderStyle.SINGLE, size, color });
const noBorder = { style: BorderStyle.NONE, size: 0, color: WHITE };
const borders = (b) => ({ top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b });
const cell = (content, width, opts = {}) => { const { fill, align, bold, color, size, vAlign, margins, colSpan, italics, bordersOverride } = opts; const paras = (Array.isArray(content) ? content : [content]).map((c) => c instanceof Paragraph ? c : new Paragraph({ children: [run(String(c), { bold, color, size: size || 19, italics })], alignment: align || AlignmentType.LEFT, spacing: { before: 40, after: 40, line: 240 } })); return new TableCell({ children: paras, width: { size: width, type: WidthType.DXA }, shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined, verticalAlign: vAlign || VerticalAlign.CENTER, margins: margins || { top: 40, bottom: 40, left: 70, right: 70 }, columnSpan: colSpan, borders: bordersOverride }); };
const dataTable = (headers, rows, widths, opts = {}) => { const { numericFrom = 1, totalRows = [], boldRows = [], subheadRows = [], fontSize = 19 } = opts; const total = widths.reduce((a, b) => a + b, 0); const head = new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], { fill: NAVY, color: WHITE, bold: true, size: fontSize, align: i >= numericFrom ? AlignmentType.RIGHT : AlignmentType.LEFT })) }); const body = rows.map((r, ri) => { const isTotal = totalRows.includes(ri), isBold = boldRows.includes(ri), isSub = subheadRows.includes(ri); const fill = isTotal ? MID : isSub ? "E3F4F5" : ri % 2 === 1 ? LIGHT : WHITE; return new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, widths[i], { fill, bold: isTotal || isBold || isSub, size: fontSize, color: isSub ? NAVY : INK, align: i >= numericFrom ? AlignmentType.RIGHT : AlignmentType.LEFT })) }); }); return new Table({ rows: [head, ...body], width: { size: total, type: WidthType.DXA }, columnWidths: widths, borders: { top: noBorder, bottom: border(NAVY, 8), left: noBorder, right: noBorder, insideHorizontal: border(MID, 4), insideVertical: noBorder } }); };
const kpiRow = (items) => { const w = Math.floor(CONTENT_W / items.length); return new Table({ rows: [new TableRow({ children: items.map(({ label, value }) => new TableCell({ width: { size: w, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" }, borders: { top: border(TEAL, 18), bottom: noBorder, left: noBorder, right: { style: BorderStyle.SINGLE, size: 6, color: WHITE } }, margins: { top: 120, bottom: 120, left: 120, right: 120 }, children: [new Paragraph({ children: [run(value, { bold: true, size: 34, color: NAVY })], spacing: { after: 40 } }), new Paragraph({ children: [run(label, { size: 17, color: GREY })], spacing: { after: 0 } })] })) })], width: { size: w * items.length, type: WidthType.DXA }, columnWidths: items.map(() => w) }); };
const callout = (title, lines, accent = TEAL) => new Table({ rows: [new TableRow({ children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" }, borders: { left: border(accent, 24), top: noBorder, bottom: noBorder, right: noBorder }, margins: { top: 120, bottom: 120, left: 200, right: 160 }, children: [new Paragraph({ children: [run(title, { bold: true, color: NAVY, size: 21 })], spacing: { after: 80 } }), ...lines.map((l) => new Paragraph({ children: Array.isArray(l) ? l : [run(l, { size: 20 })], spacing: { after: 60, line: 264 } }))] })] })], width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W] });
const photoRun = (meta, maxWDxa, maxHDxa) => { const data = fs.readFileSync(path.join(HERE, "..", meta.file)); const maxW = maxWDxa / 1440 * 96, maxH = maxHDxa / 1440 * 96; const scale = Math.min(maxW / meta.width, maxH / meta.height); return new ImageRun({ type: "jpg", data, transformation: { width: Math.round(meta.width * scale), height: Math.round(meta.height * scale) } }); };
const photoCell = (meta, width, height, fallbackCaption) => { if (meta) { return new TableCell({ width: { size: width, type: WidthType.DXA }, borders: borders(noBorder), verticalAlign: VerticalAlign.CENTER, margins: { top: 0, bottom: 0, left: 0, right: 0 }, children: [new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 60 }, children: [photoRun(meta, width, height)] }), new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 0, line: 240 }, border: { top: { color: TEAL, size: 6, style: BorderStyle.SINGLE, space: 3 } }, children: [run(meta.caption || "", { size: 16, color: GREY })] })] }); } return new TableCell({ width: { size: width, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: "F7F8FA", color: "auto" }, borders: borders({ style: BorderStyle.DASHED, size: 8, color: GREY }), verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run("IMAGE À INSÉRER", { bold: true, color: GREY, size: 18 })], spacing: { after: 60 } }), new Paragraph({ alignment: AlignmentType.CENTER, children: [run(fallbackCaption, { italics: true, color: GREY, size: 19 })], spacing: { after: 0 } })] }); };
const placeholder = (caption, height = 2400, width = CONTENT_W, slot = null) => { const meta = slot ? PHOTOS[slot] : null; return new Table({ rows: [new TableRow({ height: meta ? undefined : { value: height, rule: "atLeast" }, children: [photoCell(meta, width, height, caption)] })], width: { size: width, type: WidthType.DXA }, columnWidths: [width], borders: borders(noBorder) }); };
const twoPlaceholders = (c1, c2, height = 2200, slot1 = null, slot2 = null) => { const w = Math.floor((CONTENT_W - 200) / 2); const gap = new TableCell({ width: { size: 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] }); const m1 = slot1 ? PHOTOS[slot1] : null, m2 = slot2 ? PHOTOS[slot2] : null; return new Table({ rows: [new TableRow({ height: (m1 && m2) ? undefined : { value: height, rule: "atLeast" }, children: [photoCell(m1, w, height, c1), gap, photoCell(m2, w, height, c2)] })], width: { size: w * 2 + 200, type: WidthType.DXA }, columnWidths: [w, 200, w], borders: borders(noBorder) }); };
const gallery = (items, fallbackCaption, height = 3600) => { if (!items || !items.length) return [placeholder(fallbackCaption, height)]; const w = Math.floor((CONTENT_W - 200) / 2), rowH = 3600; const rows = []; for (let i = 0; i < items.length; i += 2) { const cells = [photoCell(items[i], w, rowH, "")]; cells.push(new TableCell({ width: { size: 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] })); cells.push(items[i + 1] ? photoCell(items[i + 1], w, rowH, "") : new TableCell({ width: { size: w, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] })); rows.push(new TableRow({ cantSplit: true, children: cells })); rows.push(new TableRow({ height: { value: 160, rule: "exact" }, children: [new TableCell({ columnSpan: 3, width: { size: w * 2 + 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] })] })); } return [new Table({ rows, width: { size: w * 2 + 200, type: WidthType.DXA }, columnWidths: [w, 200, w], borders: borders(noBorder) })]; };
const figure = (file, widthIn, caption) => { const data = fs.readFileSync(path.join(HERE, CH, file)); const dims = { "revenus.png": [7.2, 3.6], "dscr.png": [7.2, 3.4], "sources_emplois.png": [7.2, 3.8], "repartition.png": [7.2, 3.4], "echeancier.png": [7.2, 2.9] }[file]; const w = Math.round(widthIn * 96), h = Math.round(widthIn * dims[1] / dims[0] * 96); return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, children: [new ImageRun({ type: "png", data, transformation: { width: w, height: h } })] }), new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [run(caption, { italics: true, size: 17, color: GREY })] })]; };
const spacer = (after = 120) => new Paragraph({ spacing: { after } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

// --- Données ----------------------------------------------------------------------
const Y = M.annees; const P5 = Y.slice(1); const Y6 = Y;
const heads6 = Y6.map((y) => y.label.replace(" – ", "\n"));
const heads5 = P5.map((y) => y.label.replace(" – ", "\n"));
const y0 = Y[0], y1 = Y[1], y2 = Y[2], y3 = Y[3], y5 = Y[5];
const W7 = [2700, 1160, 1160, 1160, 1160, 1160, 1148];
const W6 = [2900, 1350, 1350, 1350, 1350, 1348];
const senior = M.couches[0];
const totalEmplois = M.total_emplois;
const cb = M.coolbox_2026;

const children = [];

// --- Couverture ---------------------------------------------------------------------
const coverMeta = PHOTOS.couverture;
children.push(
  new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT }, children: coverMeta ? [bleedImage(coverMeta, 0, 8.5, 11)] : [] }),
  exactSpacer(7400),
  new Paragraph({ spacing: { after: 0 }, children: [run("PLAN D'AFFAIRES 2027 – 2031", { bold: true, size: 22, color: GOLD })] }),
  new Paragraph({ spacing: { before: 80, after: 0 }, children: [run("COMPLEXE HAVANA", { bold: true, size: 72, color: WHITE })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, children: [new TextRun({ text: "Du camping estival au centre de villégiature quatre saisons", font: "Georgia", size: 28, italics: true, color: WHITE })] }),
  new Paragraph({ spacing: { before: 260, after: 0 }, children: [run("Demande de financement : prêt hypothécaire de premier rang de " + moneyM(M.senior, 1) + " dans un montage de " + moneyM(totalEmplois, 1) + "   ·   Maricourt, Cantons-de-l'Est   ·   Septembre 2026", { size: 19, color: "D9F1F3" })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, children: [run("Document confidentiel", { size: 18, color: "A8D8DC" })] }),
  pageBreak(),
);

children.push(
  H2("Avis de confidentialité"),
  P("Ce plan d'affaires contient des renseignements confidentiels appartenant au Complexe Havana et à ses partenaires. Il est remis uniquement aux fins d'évaluation d'une demande de financement. Les projections reposent sur des hypothèses documentées dans le classeur financier joint (annexe H) ; chaque hypothèse y porte sa source ou la mention « hypothèse à valider ». Les résultats réels pourraient différer."),
  spacer(200),
  H2("Table des matières"),
  new TableOfContents("Table des matières", { hyperlink: true, headingStyleRange: "1-2" }),
  spacer(),
);

// --- 1. Sommaire exécutif ----------------------------------------------------------------
children.push(
  ...chapter("01", "Sommaire exécutif", "ban_1", "Un site exploité depuis dix ans, un produit quatre saisons déjà en place et des actifs prêts à être mis en valeur : le projet demande un financement dimensionné sur ses résultats."),
  kpiRow([
    { label: "Ventes 2026 mesurées (Pixum, avant taxes)", value: moneyM(M.reel_2026_total) },
    { label: "Investissements réalisés 2015-2023 (déclarés)", value: moneyM(M.immo_existantes_cout, 1) },
    { label: "Prêt senior demandé", value: moneyM(M.senior, 1) },
    { label: "Fonds propres sur l'argent neuf", value: pct(M.pct_fonds_propres_argent_neuf, 0) },
  ]),
  spacer(80),
  kpiRow([
    { label: "Revenus projetés An 5", value: moneyM(y5.total_revenus, 1) },
    { label: "BAIIA An 5", value: moneyM(y5.baiia, 1) },
    { label: "Couverture du prêt senior An 3", value: ratio(y3.dscr_senior) },
    { label: "Couverture bancaire, toutes couches, An 5", value: ratio(y5.dscr_bancaire) },
  ]),
  spacer(200),
  H2("L'entreprise"),
  P("Le Complexe Havana (Camping Havana Resort) exploite depuis 2015 un site de 274,57 acres (111,13 ha, trois lots) au 631-637, 7e Rang à Maricourt, dans les Cantons-de-l'Est. Le concept, unique au Québec, reproduit l'ambiance des destinations cubaines : piscine centrale avec bar, animation, musique et cuisine cubaines. L'inventaire compte 313 terrains de camping, 14 cabanas prêt-à-camper, une trentaine de chalets, six chambres d'hôtel en exploitation dans un bâtiment de 24 860 pi² pouvant en accueillir 17, une piscine extérieure, une usine d'épuration privée et 18 emplacements aménagés pour des unités Coolbox, dont 9 sont exploitées."),
  P("Les ventes enregistrées par le système de réservation sont passées de " + money(M.reel_2025_total) + " en 2025 à " + money(M.reel_2026_total) + " en 2026 (+5,4 %), avec un panier moyen en hausse de 15 % (158 $). S'y ajoutent la restauration et les activités (" + money(M.autres_2026.restauration + M.autres_2026.activites) + ") et la part de Havana dans les ventes des 9 unités Coolbox exploitées en 2026 (" + money(cb.redevance) + ")."),
  H2("Le projet"),
  P("Transformer l'exploitation estivale en centre de villégiature douze mois par année, en mettant en valeur les actifs existants. Travaux de " + moneyM(M.emplois[0][1], 2) + " réalisés à l'hiver et au printemps 2027 pour une ouverture en juillet 2027 :"),
  ...bullets([
    [run("Hôtel : ", { bold: true }), run("de 6 à 17 chambres, restaurant Madera et salle de conférence, exploitation douze mois.")],
    [run("Hébergement quatre saisons : ", { bold: true }), run("achèvement des 13 villas, hivernisation des 16 chalets, 20 unités Coolbox quatre saisons apportées par Coolbox HPA, dont 9 déjà en place sur les emplacements aménagés en 2022.")],
    [run("Saisonniers : ", { bold: true }), run("conversion de 40 terrains existants en contrats saisonniers, encaissés avant la saison.")],
  ]),
  H2("La demande de financement"),
  P("Le montage de " + money(totalEmplois) + " comprend les travaux, une contingence différenciée, les honoraires, la mise en conformité, les intérêts de construction, une réserve de service de la dette déposée à la clôture, le fonds de roulement et le refinancement de la dette existante. Il est financé en couches : un prêt hypothécaire de premier rang de " + money(M.senior) + " (tranche A à la clôture, tranche B par avancement des travaux), des couches publiques et partenaires sollicitées (" + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + ") et des fonds propres de " + money(M.fonds_propres) + ", soit " + pct(M.pct_fonds_propres_argent_neuf, 0) + " de l'argent neuf, dont l'apport en nature de " + money(M.apport_coolbox) + " de Coolbox HPA (20 unités quatre saisons)."),
  H2("Pourquoi le projet est finançable"),
  ...numbered([
    [run("Des revenus mesurés, pas estimés : ", { bold: true }), run("le modèle part des ventes 2026 du système de réservation et du budget de la direction, avec l'année 2026 publiée dans tous les tableaux.")],
    [run("Le produit quatre saisons existe déjà sur le site : ", { bold: true }), run("9 unités Coolbox ont généré " + money(cb.ca_ht) + " de ventes en un seul été 2026, soit " + money(cb.ca_ht / cb.unites) + " par unité ; le projet en exploite 20, propriété de Havana, apportées par Coolbox HPA.")],
    [run("Des actifs existants mis en valeur : ", { bold: true }), run("hôtel, chalets, emplacements Coolbox déjà desservis et terrains existants ; aucune construction lourde, un chantier de six mois en basse saison.")],
    [run("Un chantier à prix maîtrisé : ", { bold: true }), run("entrepreneur général licencié (Construction Prospère) à prix forfaitaire, cautionnements, retenue subordonnée, prix validés par un tiers.")],
    [run("Un prêt senior dimensionné sur la capacité : ", { bold: true }), run("couverture du service du prêt senior de " + ratio(y3.dscr_senior) + " en An 3 et " + ratio(y5.dscr_senior) + " en An 5 ; toutes couches confondues, " + ratio(y3.dscr_total) + " et " + ratio(y5.dscr_total) + ".")],
  ]),
  H2("Faits saillants financiers"),
  dataTable(["", ...heads6], [
    ["Revenus totaux", ...Y6.map((y) => money(y.total_revenus))],
    ["BAIIA", ...Y6.map((y) => money(y.baiia))],
    ["Marge BAIIA", ...Y6.map((y) => pct(y.marge_baiia))],
    ["Service du prêt senior", ...Y6.map((y) => money(y.service_senior))],
    ["Service de la dette, toutes couches", ...Y6.map((y) => money(y.service_dette))],
    ["Couverture du prêt senior (BAIIA / service senior)", ...Y6.map((y) => ratio(y.dscr_senior))],
    ["Couverture bancaire, toutes couches", ...Y6.map((y) => ratio(y.dscr_bancaire))],
    ["Bénéfice net", ...Y6.map((y) => money(y.benefice_net))],
  ], W7, { boldRows: [5, 6], fontSize: 17 }),
  NOTE("2026 : exercice de transition. An 1 : année de travaux, tranche B décaissée par avancement, moratoire de capital. Premier test de covenant proposé : exercice 2029."),
);

// --- 2. L'entreprise ------------------------------------------------------------------------
const reel = y0.revenus;
children.push(
  ...chapter("02", "L'entreprise", "ban_2", "Dix ans d'exploitation, 11,9 M$ investis dans le site, et une clientèle qui revient : la base sur laquelle le projet est construit."),
  H2("2.1 Historique"),
  P("Le site du 7e Rang à Maricourt a été acquis en octobre 2014 ; la famille Perrier en prend le contrôle en 2015 et fonde le Camping Havana Resort. De 2015 à 2023, la direction déclare 11 915 000 $ d'investissements (annexe A) : 200 terrains, rues, électricité et bloc sanitaire (2016), piscine centrale, rénovation complète de l'hôtel, 14 cabanas, usine d'épuration des eaux usées (2019-2020, 1,0 M$), une trentaine de chalets construits par vagues, 67 terrains et 20 terrains saisonniers additionnels (2021), 18 emplacements Coolbox (2022), chapiteau (2022-2023). La chronologie visuelle des travaux figure à l'annexe F."),
  P("Le concept s'articule autour d'une piscine centrale avec café-bar, où se déploient animation, musique et ambiance familiale. Une nouvelle direction est en place depuis 2025 ; la famille fondatrice assure la continuité de la vision. La présente version du plan intègre deux partenaires industriels : Coolbox HPA, fabricant des unités d'hébergement quatre saisons déjà exploitées sur le site, et Construction Prospère, entrepreneur général."),
  H2("2.2 Mission, vision et valeurs"),
  H3("Mission"),
  P("Offrir à tous nos invités un petit bout de Cuba afin qu'ils puissent se divertir, décrocher de leur quotidien et retrouver l'ambiance des grandes destinations vacances. Notre mission ultime : que chaque invité planifie son retour au moment de son départ."),
  H3("Vision"),
  P("Être le seul complexe d'hébergement et d'activités récréotouristiques au concept entièrement cubain au Québec, ouvert à l'année, reconnu pour son offre unique, son service personnalisé, ses pratiques conformes et durables et ses partenariats avec la communauté cubaine et locale."),
  H3("Valeurs"),
  ...bullets([
    [run("Chaleur et convivialité : ", { bold: true }), run("un accueil qui fait sentir chaque invité comme un membre de la famille.")],
    [run("Authenticité : ", { bold: true }), run("une expérience cubaine crédible, dans l'ambiance, la musique et l'assiette.")],
    [run("Rigueur : ", { bold: true }), run("des opérations, une conformité et une gestion financière disciplinées, appuyées sur des systèmes et des rapports au prêteur.")],
    [run("Bon voisinage : ", { bold: true }), run("un site qui vit avec son milieu : protocole de bruit, communication avec la municipalité et les voisins.")],
  ]),
  H2("2.3 Structure juridique et propriété"),
  dataTable(["Élément", "Détail"], [
    ["Société propriétaire des trois lots", "9504-5050 Québec inc. (Camping Havana Resort)"],
    ["Lots et superficie", "5 626 900 (hôtel, 43 183 m²), 6 040 494 (98 687 m²), 6 040 495 (camping, 969 255 m²) ; total 1 111 126 m² = 274,57 acres"],
    ["Siège social", "631, 7e Rang, Maricourt (Québec) J0E 2L2"],
    ["Actionnaires", "Famille Perrier ; partenaires industriels Coolbox HPA et Construction Prospère"],
    ["Zonage", "Récréotouristique (règlement 328-2007 de Maricourt), usage camping et hébergement en place depuis 2015"],
  ], [3200, 6448], { numericFrom: 99, fontSize: 18 }),
  H2("2.4 Actifs et installations"),
  dataTable(["Installation", "Quantité", "Tarif affiché", "Saison actuelle", "Après le projet"], [
    ["Terrains de camping (2 et 3 services)", "313 inventoriés", "65 $ à 90 $ / nuit", "Mai à octobre", "Inchangé"],
    ["Terrains saisonniers (contrats)", "≈ 12 en 2026", "3 650 $ / saison", "Mai à octobre", "Jusqu'à 70 par conversion de terrains existants"],
    ["Chalets", "16 en location", "235 $ / nuit", "Été", "Hivernisés, 4 saisons"],
    ["Chambres d'hôtel", "6", "190 $ / nuit", "Été", "17, ouvertes 12 mois"],
    ["Cabanas prêt-à-camper", "13 à 14", "200 $ / nuit", "Été", "Inchangé"],
    ["Villas (en construction)", "13", "275 $ / nuit", "À livrer", "Livrées en juillet 2027"],
    ["Unités Coolbox 4 saisons", "9 exploitées / 18 emplacements aménagés", "225 $ / nuit", "Été", "20 unités, propriété de Havana, été et hiver"],
    ["Piscine extérieure, bar de piscine, lac et plage", "1", "Inclus", "Été", "Inchangé"],
    ["Piscine intérieure, chapiteau 1 600 places, scène extérieure", "—", "—", "Existant", "Existant"],
    ["Usine d'épuration privée (Ecochem, 2019), 2 puits", "1", "—", "12 mois", "12 mois"],
  ], [3100, 1500, 1500, 1300, 2248], { numericFrom: 99, fontSize: 17 }),
  spacer(),
  twoPlaceholders("Vue aérienne des terrains de camping", "Cabanas", 3300, "actifs_terrains", "actifs_chalets"),
  spacer(),
  H2("2.5 Performance récente"),
  dataTable(["Catégorie (avant taxes, par date de transaction)", "Saison 2025", "Saison 2026", "Variation"], [
    ["Terrains de camping", money(837255.66), money(reel.terrains), "−5,4 %"],
    ["Chalets et chambres", money(400868.16), money(reel.chalets), "+24,2 %"],
    ["Cabanas prêt-à-camper", money(195575.47), money(reel.cabanas), "+1,8 %"],
    ["Terrains saisonniers", money(19731.89), money(reel.saisonniers), "+119,0 %"],
    ["Total des ventes du système de réservation", money(M.reel_2025_total), money(M.reel_2026_total), "+5,4 %"],
    ["Nombre de transactions / panier moyen", "10 587 / 137,30 $", "9 670 / 158,41 $", "−8,7 % / +15,4 %"],
    ["Ventes des unités Coolbox (plateforme Coolbox, 9 unités)", "—", money(cb.ca_ht), "—"],
    ["Restauration et activités (budget interne)", "—", money(M.autres_2026.restauration + M.autres_2026.activites), "—"],
  ], [4300, 1800, 1800, 1748], { totalRows: [4], fontSize: 18 }),
  spacer(),
  H3("Réconciliation des chiffres de revenus 2026"),
  P("Trois chiffres circulent pour 2026 ; le plan les réconcilie plutôt que d'en choisir un :"),
  dataTable(["Source", "Montant", "Ce qu'il mesure"], [
    ["Système de réservation (Pixum), saison 2025-09-15 → 2026-09-15", money(M.reel_2026_total), "Ventes encaissées d'hébergement, hors Coolbox, restauration et activités"],
    ["An 0 du présent modèle", money(y0.total_revenus), "Pixum + restauration et activités (budget interne) + part Havana des ventes Coolbox"],
    ["Budget d'exploitation de la direction", money(2630437.50), "Revenus modélisés à pleine capacité (unités × tarif × occupation)"],
  ], [4200, 1600, 3848], { numericFrom: 1, fontSize: 18 }),
);

// --- 3. Le projet ---------------------------------------------------------------------------
const projRows = [];
M.projets.forEach((p) => projRows.push([p[1], p[3] === "usine" ? "Forfait d'usine" : "Chantier", money(p[2])]));
projRows.push(["Sous-total des travaux", "", money(M.emplois[0][1])]);
projRows.push(["Contingence : 5 % sur les forfaits d'usine, 10 % sur les travaux de chantier", "", money(M.contingence)]);
projRows.push(["Total", "", money(M.emplois[0][1] + M.contingence)]);
children.push(
  ...chapter("03", "Le projet", "ban_3", "Mettre en valeur les actifs existants et ajouter la capacité qui se vend douze mois par année."),
  H2("3.1 Objectif"),
  P("Rendre le site vendable douze mois par année en s'appuyant sur les actifs existants : hôtel, chalets, emplacements Coolbox desservis, terrains. Chaque composante répond à l'un de deux critères : elle produit des revenus l'année même du décaissement, ou elle allonge la saison des unités existantes."),
  H2("3.2 Composantes et coûts"),
  dataTable(["Composante", "Type", "Coût"], projRows, [6000, 1500, 2148], { numericFrom: 2, totalRows: [M.projets.length, M.projets.length + 2], fontSize: 18 }),
  NOTE("Les coûts de chantier sont ceux de la direction, appuyés par les soumissions à forfait de Construction Prospère (annexe C). Le coût des unités Coolbox est le prix de catalogue 2026 : " + money(M.coolbox_unite) + " par unité installée, raccordée et meublée."),
  H2("3.3 Description des composantes"),
  H3("Hôtel : de 6 à 17 chambres, ouvert douze mois"),
  P("Rénovation intérieure du bâtiment de 1997 (24 860 pi²) pour exploiter les 17 unités prévues, avec salle de conférence attenante. L'hôtel devient le pivot de l'exploitation hivernale : couples, groupes, retraites d'entreprise."),
  twoPlaceholders("Entrée de l'hôtel", "Aile arrière de l'hôtel", 3000, "projet_hotel_entree", "projet_hotel_arriere"),
  spacer(80),
  H3("Restaurant Madera et salle de conférence"),
  P("Restaurant de cuisine cubaine et latino-américaine ouvert à la clientèle du site et au public régional, avec le café Cubano, la cantine et le Mojito bar. À maturité, la restauration et les bars représentent " + pct(M.hypotheses.fb_ratio["5"], 0) + " des revenus d'hébergement, sous le budget de la direction (cantine 100 000 $, café 200 000 $, Mojito bar 300 000 $, Madera 289 500 $)."),
  placeholder("Aqua Bar", 3400, CONTENT_W, "projet_resto"),
  spacer(80),
  H3("Vingt unités Coolbox quatre saisons"),
  P("Vingt unités 12×24 fabriquées en usine par Coolbox HPA (structure d'acier autoportante, isolation haute performance, thermopompe), apportées en nature au projet pour " + money(M.apport_coolbox) + " : les 9 déjà en place sur les emplacements aménagés en 2022, et 11 livrées pour juin 2027 (délai usine de 12 à 16 semaines). Elles appartiennent à Havana et 100 % de leurs ventes lui reviennent. Les 9 unités déjà exploitées sur le site par Coolbox HPA ont produit " + money(cb.ca_ht) + " de ventes durant l'été 2026, dont " + money(cb.part_havana) + " de part pour Havana."),
  H3("Villas, chalets et terrains saisonniers"),
  P("Achèvement des 13 villas en construction, hivernisation des 16 chalets (isolation, chauffage, plomberie) et conversion de 40 terrains 3 services existants en contrats saisonniers. Le saisonnier est encaissé avant la saison, de janvier à mars : c'est le revenu qui sécurise le printemps."),
  H3("Développement futur"),
  P("L'achèvement de la piscine intérieure et un spa quatre saisons constituent la prochaine étape de développement du site, prévue en 2029 et financée séparément sur les résultats du présent projet. Ils ne sont pas comptés dans les projections."),
  H2("3.4 Échéancier de réalisation"),
  ...figure("echeancier.png", 6.6, "Figure 1 – Échéancier de réalisation"),
  P("Les travaux se réalisent en basse saison, entre la clôture et juillet 2027, sans perturber l'exploitation estivale. Les unités Coolbox sont commandées à la clôture et livrées pour l'été. Les contrats saisonniers 2028 se vendent dès l'automne 2027."),
  H2("3.5 Partenaires de réalisation"),
  ...bullets([
    [run("Construction Prospère (Dolbeau-Mistassini), entrepreneur général : ", { bold: true }), run("contrat clé en main à prix forfaitaire par composante, licence RBQ, cautionnements d'exécution et de paiement, retenue contractuelle de 10 % convertie en billet subordonné.")],
    [run("Coolbox HPA, fabricant et partenaire : ", { bold: true }), run("apport en nature de 20 unités quatre saisons (" + money(M.apport_coolbox) + "), fiche technique, garantie du fabricant, plateforme de vente reservationcoolbox.ca (annexe J).")],
    "Professionnels : architecte, ingénieur, firme comptable, évaluateur agréé mandaté par l'institution.",
  ]),

  P("Les autorisations, permis, documents et pièces complémentaires requis seront fournis et pris en considération aux étapes subséquentes du projet, au fur et à mesure de sa progression, en collaboration avec l'institution financière et les professionnels mandatés."),
  H2("3.6 Plan d'aménagement du site"),
  P("Le plan ci-dessous localise les installations existantes : l'hôtel et les condos (02) à l'entrée, la piscine centrale (06) avec la scène et le café cubain (08), la zone de restauration (09), les cabanas (14), les emplacements Coolbox et le terrain de volleyball (16), l'amphithéâtre (18), le chapiteau (19) et les secteurs de terrains desservis. Les travaux du projet portent sur l'hôtel, le restaurant, les villas, les chalets, les emplacements Coolbox et les terrains existants convertis en saisonniers."),
  placeholder("Plan d'aménagement du site (2026)", 5600, CONTENT_W, "plan_site"),
  spacer(80),
  dataTable(["N°", "Installation", "N°", "Installation", "N°", "Installation"], [
    ["01", "Accueil", "08", "Scène et café cubain", "15", "Toilettes et stationnement"],
    ["02", "Hôtel, condos", "09", "Zone restauration", "16", "Coolbox et terrain de volleyball"],
    ["03", "Parc, jeux pour enfants", "10", "Salle communautaire", "17", "Toilettes, douches, buanderie"],
    ["04", "Kiosque de mangues", "11", "Dépanneur et cantine", "18", "Amphithéâtre"],
    ["05", "Jeux d'eau", "12", "Soucoupe volante", "19", "Chapiteau"],
    ["06", "Piscine", "13", "Location de triporteurs", "20", "Boutique Havana et informations"],
    ["07", "Toilettes", "14", "Cabanas", "21", "Jeux gonflables"],
  ], [500, 2716, 500, 2716, 500, 2716], { numericFrom: 99, fontSize: 16 }),
);

// --- 4. Marché ------------------------------------------------------------------------------------
children.push(
  ...chapter("04", "Analyse du marché", "ban_4", "Un marché de proximité de plusieurs millions de personnes, une région quatre saisons établie, et un produit hivernal déjà vendu ailleurs par le réseau Coolbox."),
  H2("4.1 Indicateurs de marché"),
  P("Sources nommées."),
  dataTable(["Indicateur", "Valeur", "Source"], [
    ["Occupation des campings du Québec, juin à août 2025", "≈ 75 % (74 % en 2024)", "Camping Québec, bilan de fréquentation 2025"],
    ["Occupation, Cantons-de-l'Est, été 2025", "≈ 76 %", "Camping Québec, bilan 2025"],
    ["Occupation des grands campings, 2015-2020", "75 % à 78 % ; saisonniers ≈ 62 % des sites", "Rapport Grenier 2021, p. 94-100 (Camping Québec)"],
    ["Occupation hôtelière, Cantons-de-l'Est, hiver 2025-2026", "≈ 42 %", "Tourisme Cantons-de-l'Est, communiqué hiver 2025-26"],
    ["Bassin à moins de 2 heures de route", "RMR de Montréal ≈ 4,3 M, RMR de Sherbrooke ≈ 0,23 M, Granby, Drummondville, Saint-Hyacinthe", "Statistique Canada, recensement 2021"],
    ["Population d'origine latino-américaine, RMR de Montréal", "≈ 137 850 (3,3 %)", "Statistique Canada, recensement 2021"],
    ["Distance", "1 h 15 de Montréal, 35 min de Sherbrooke et de Drummondville", "Site havanaresort.ca"],
  ], [3400, 3000, 3248], { numericFrom: 99, fontSize: 17 }),
  spacer(),
  H2("4.2 Tendances"),
  ...bullets([
    [run("Le confort et le prêt-à-camper : ", { bold: true }), run("cabanas, chalets et unités tout équipées croissent plus vite que le camping traditionnel et commandent des tarifs deux à trois fois supérieurs ; à Havana, les chalets ont progressé de 24 % en 2026.")],
    [run("L'expérience et l'animation : ", { bold: true }), run("les clients choisissent un lieu pour ce qu'ils y vivront autant que pour l'hébergement.")],
    [run("Les quatre saisons : ", { bold: true }), run("spas nordiques, sentiers illuminés et hébergements chauffés ont créé un marché hivernal de proximité dans les Cantons-de-l'Est.")],
  ]),
  H2("4.3 La preuve de l'hiver par le produit"),
  P("L'occupation hivernale projetée ne repose pas sur une hypothèse générale mais sur un produit qui existe : les unités Coolbox sont exploitées l'hiver sur d'autres destinations du réseau (fiches de ventes par site, annexe J). À Havana, elles n'ont été exploitées qu'en été jusqu'en 2026. Le plan retient pour les 20 unités du site une occupation hivernale de " + pct(M.hypotheses.coolbox_occ_hiver["1"], 0) + " en An 1 à " + pct(M.hypotheses.coolbox_occ_hiver["5"], 0) + " en An 5 (chalets : " + pct(M.hypotheses.chalets_occ_hiver["1"], 0) + " à " + pct(M.hypotheses.chalets_occ_hiver["5"], 0) + "), sous les taux observés dans le réseau."),
  H2("4.4 Clientèle cible"),
  dataTable(["Segment", "Profil", "Offre principale", "Saison"], [
    ["Familles", "Ménages avec enfants, rayon de 2 heures", "Terrains, cabanas, chalets, Coolbox, piscine, animation", "Été"],
    ["Couples et groupes d'amis", "25 à 55 ans, séjours courts", "Villas, hôtel, Coolbox, restaurant, spectacles", "4 saisons"],
    ["Saisonniers", "Retraités et familles fidèles", "Terrains saisonniers (jusqu'à 70)", "Mai à octobre"],
    ["Entreprises et groupes", "Réunions, retraites, mariages", "Hôtel, salle de conférence, restaurant", "Automne à printemps"],
    ["Communauté cubaine et latino-américaine", "≈ 137 850 personnes d'origine latino-américaine dans la RMR de Montréal", "Événements, festivals, restauration", "4 saisons"],
    ["Clientèle de jour", "Résidents de la région", "Restaurant, événements", "4 saisons"],
  ], [2000, 2800, 3100, 1748], { numericFrom: 99, fontSize: 17 }),
  H2("4.5 Concurrence"),
  P("Aucun établissement québécois n'offre une thématique cubaine intégrée ; la concurrence est indirecte. Les établissements ci-dessous situent les tarifs et les capacités de la région."),
  dataTable(["Établissement", "Offre", "Ce qu'on retient", "Notre différenciation"], [
    ["Camping Vacances Bromont (Bromont)", "≈ 543 emplacements, glissades d'eau, chalets 4 saisons", "Référence régionale de prix et de volume", "Thématique, piscine centrale avec bar, animation, tarifs sous le haut de gamme"],
    ["Camping de la Vallée Bleue (Lac-Brome)", "≈ 213 sites, forte part de saisonniers", "Modèle saisonnier de l'Estrie", "Programme d'animation et d'événements"],
    ["Camping des Baies (Windsor)", "≈ 170 sites, majorité de saisonniers", "Proximité de Maricourt", "Hébergement locatif diversifié, produit hiver"],
    ["Spas nordiques régionaux (Eastman, Bromont, Magog)", "Accès à la journée 65 $ à 80 $", "Repère tarifaire régional", "Spa intégré à un séjour, prix inférieur"],
    ["Hôtels et auberges de l'Estrie", "Chambres 3 étoiles", "Repère tarifaire de l'hôtel (190 $)", "Expérience immersive et activités sur place"],
  ], [2500, 2400, 2200, 2548], { numericFrom: 99, fontSize: 16 }),
);

// --- 5. Commercialisation ----------------------------------------------------------------------------
const sais = M.hypotheses.saisonniers_sites;
children.push(
  ...chapter("05", "Stratégie de commercialisation", "ban_5", "Vendre d'abord la nouvelle capacité à la clientèle existante, encaisser les saisonniers avant la saison, et nommer ce qui se vend l'hiver."),
  H2("5.1 Positionnement et tarification"),
  P("« Cuba à 90 minutes de Montréal, douze mois par année. » Une destination d'évasion accessible, festive et familiale, à un prix inférieur aux centres de villégiature haut de gamme de la région."),
  dataTable(["Produit", "Tarif de référence An 1", "Indexation", "Base"], [
    ["Terrain de camping", "Selon grille 2026 (65 $ à 90 $)", "3 % par année", "Grille affichée, annexe G"],
    ["Terrain saisonnier", "3 650 $ / saison", "3 % par année", "Contrats 2026"],
    ["Chalet 4 saisons", "235 $ été, 210 $ hiver", "3 % par année", "Tarif 2026"],
    ["Villa", "275 $ été, 245 $ hiver", "3 % par année", "Direction"],
    ["Chambre d'hôtel", "190 $ / nuit", "3 % par année", "Tarif 2026"],
    ["Unité Coolbox", "225 $ été, 199 $ hiver", "3 % par année", "Tarif affiché 2023"],
    ["Cabana prêt-à-camper", "200 $ / nuit", "3 % par année", "Tarif 2026"],
  ], [2500, 2700, 1700, 2748], { numericFrom: 99, fontSize: 18 }),
  H2("5.2 Plan de vente des terrains saisonniers"),
  P("Point de départ réel : environ 12 contrats payés en 2026 (" + money(reel.saisonniers) + "). Les ventes de contrats 2027 ouvrent en septembre-octobre 2026 auprès des campeurs réguliers, avec dépôt à la signature et solde en mars. Trajectoire retenue : " + [0, 1, 2, 3, 4, 5].map((i) => sais[String(i)]).join(" → ") + " contrats, sur des terrains existants convertis."),
  dataTable(["", ...heads6], [
    ["Contrats saisonniers", ...[0, 1, 2, 3, 4, 5].map((i) => String(sais[String(i)]))],
    ["Ventes nettes à réaliser dans l'année", "—", ...[1, 2, 3, 4, 5].map((i) => String(sais[String(i)] - sais[String(i - 1)]))],
    ["Revenus saisonniers", ...Y6.map((y) => money(y.revenus.saisonniers))],
  ], W7, { fontSize: 17 }),
  H2("5.3 Ce qui se vend l'hiver 2027-2028"),
  P("Le premier hiver repose sur des produits nommés : l'hôtel (17 chambres) et la salle de conférence livrés en juillet 2027, les 16 chalets hivernisés à l'automne 2027 et les 20 unités Coolbox quatre saisons."),
  dataTable(["Produit d'hiver", "Période", "Unités mobilisées", "Source de la demande"], [
    ["Retraites et réunions d'entreprise en semaine", "Novembre à avril", "Hôtel, salle, restaurant", "Entreprises de Sherbrooke, Drummondville, Granby ; ventes directes"],
    ["Fêtes et jour de l'An cubain", "20 déc. – 3 janv.", "Hôtel, chalets, Coolbox", "Clientèle estivale, communauté latino-américaine"],
    ["Grand Prix Ski-Doo de Valcourt (février)", "Fin de semaine de février", "Toutes les unités chauffées", "Forfaits hébergement + navette"],
    ["Relâche scolaire", "Début mars", "Chalets, Coolbox, hôtel", "Familles du Grand Montréal"],
    ["Fins de semaine motoneige et plein air", "Janvier à mars", "Coolbox, chalets", "Sentiers régionaux"],
  ], [2900, 1700, 2300, 2748], { numericFrom: 99, fontSize: 17 }),
  H2("5.4 Distribution et réservation"),
  ...bullets([
    "Terrains, cabanas, chalets et chambres actuelles : reservationcamping.ca (Solutions Web Pixum), 9 670 transactions en 2026.",
    "Unités Coolbox : plateforme reservationcoolbox.ca déjà active, " + money(cb.ca_ht) + " de ventes en 2026 pour 9 unités ; canal étendu aux 20 unités.",
    "Hôtel et villas : système de gestion hôtelière et gestionnaire de canaux (Booking, Expedia, Airbnb) ; commissions de plateformes inscrites aux charges (section 8).",
    "Groupes et entreprises : ressource de vente dédiée dès l'automne 2026 ; forfaits hiver, mariages, retraites.",
  ]),
  H2("5.5 Promotion et budget par canal"),
  dataTable(["Canal", "An 1", "An 2", "Contenu"], [
    ["Publicité numérique géociblée (Meta, Google), infolettre", money(y1.charges.marketing * 0.45), money(y2.charges.marketing * 0.45), "Rayon de 2 heures, clientèle passée, communauté latino-américaine"],
    ["Tourisme Cantons-de-l'Est, Camping Québec, guides et campagnes régionales", money(y1.charges.marketing * 0.15), money(y2.charges.marketing * 0.15), "Adhésions, participation aux campagnes hiver et été"],
    ["Relations médias, créateurs de contenu, lancement de l'hôtel", money(y1.charges.marketing * 0.15), money(y2.charges.marketing * 0.15), "Ouverture juillet 2027, hiver 2027-2028"],
    ["Événements signature et programmation", money(y1.charges.marketing * 0.15), money(y2.charges.marketing * 0.15), "Festival cubain, soirées, Fêtes"],
    ["Réputation en ligne et service client", money(y1.charges.marketing * 0.10), money(y2.charges.marketing * 0.10), "Réponse à 100 % des avis, sondage de séjour, suivi mensuel"],
    ["Total marketing (3,5 % puis 3 % des revenus)", money(y1.charges.marketing), money(y2.charges.marketing), "Commissions de plateformes comptées à part"],
  ], [3600, 1300, 1300, 3448], { totalRows: [5], fontSize: 17 }),
  twoPlaceholders("Visuel de campagne", "Visuel de campagne", 3200, "promo_1", "promo_2"),
  H2("5.6 Tableau de bord pour le prêteur"),
  dataTable(["Indicateur (trimestriel)", "Départ 2026", ...heads5], [
    ["Contrats saisonniers signés", String(sais["0"]), ...[1, 2, 3, 4, 5].map((i) => String(sais[String(i)]))],
    ["Occupation estivale des chalets", "≈ 55 %", ...[1, 2, 3, 4, 5].map((i) => pct(M.hypotheses.chalets_occ_ete[String(i)], 0))],
    ["Occupation hivernale des chalets", "0 %", ...[1, 2, 3, 4, 5].map((i) => pct(M.hypotheses.chalets_occ_hiver[String(i)], 0))],
    ["Occupation annuelle de l'hôtel", "—", ...[1, 2, 3, 4, 5].map((i) => pct(M.hypotheses.hotel_occ[String(i)], 0))],
    ["Occupation estivale des unités Coolbox", "—", ...[1, 2, 3, 4, 5].map((i) => pct(M.hypotheses.coolbox_occ_ete[String(i)], 0))],
    ["Restauration et bars / revenus d'hébergement", "6,5 %", ...[1, 2, 3, 4, 5].map((i) => pct(M.hypotheses.fb_ratio[String(i)], 0))],
    ["Panier moyen par transaction", "158 $", "—", "—", "—", "—", "—"],
  ], [3000, 1100, 1110, 1110, 1110, 1110, 1108], { fontSize: 17 }),
);

// --- 6. Exploitation ----------------------------------------------------------------------------------
children.push(
  ...chapter("06", "Plan d'exploitation", "ban_6", "Passer de six à douze mois d'activité : effectifs construits poste par poste, infrastructures suivies par des ingénieurs, entretien au niveau réel."),
  H2("6.1 Organisation"),
  P("Cinq services : hébergement et réservations, restauration, animation et événements, entretien et infrastructures, administration. Chaque service relève d'un responsable qui rend compte à la direction générale."),
  H2("6.2 Effectifs"),
  P("La masse salariale est le résultat d'un tableau d'effectifs (postes, mois, heures, taux horaire chargé) présenté dans le classeur financier, et non un pourcentage cible. Elle représente " + pct(y1.charges.salaires / y1.total_revenus, 0) + " des revenus en An 1 et " + pct(y5.charges.salaires / y5.total_revenus, 0) + " en An 5, en ligne avec la normalisation de l'évaluation par les revenus de 2021 (30 %). Recrutement : logement des employés sur le site, postes à l'année, partenariats avec les écoles hôtelières."),
  dataTable(["Poste", "Été (ETP)", "Hiver (ETP)", "Base"], [
    ["Direction générale et finances", "2", "2", "Salariés à l'année"],
    ["Accueil et réservations (hôtel 24/7 dès juillet 2027)", "5", "4", "≈ 4,2 ETP pour une réception 24/7"],
    ["Entretien ménager et buanderie", "8", "3", "1 ETP par 8 à 10 unités louées"],
    ["Restauration (cuisine et service)", "8", "3", "Restaurant ouvert 12 mois, service réduit l'hiver"],
    ["Animation, événements, sécurité", "6", "1", "Programmation d'été"],
    ["Entretien des terrains, bâtiments, infrastructures", "5", "2", "Usine d'épuration, chauffage, déneigement"],
    ["Total approximatif", "34", "15", "Détail mensuel dans le classeur (annexe H)"],
  ], [4200, 1300, 1300, 2848], { totalRows: [6], fontSize: 17 }),
  H2("6.3 Eau, énergie et infrastructures"),
  ...bullets([
    "Usine d'épuration privée (2019, 1,0 M$), conçue dans l'optique d'une expansion ; suivi par ingénieur pour l'exploitation douze mois.",
    "Puits et eau potable : suivi réglementaire en continu.",
    "Énergie : le poste passe de " + money(y0.charges.energie) + " (2026) à " + money(y5.charges.energie) + " en An 5 ; étude d'efficacité énergétique (thermopompes, enveloppe de l'hôtel) et programmes Hydro-Québec affaires, non comptés dans les projections.",
    "Entretien : 8 % des revenus (norme de l'évaluation 2021) plus 2 % d'immobilisations de maintien ; véhicules et essence inscrits séparément.",
  ]),
  H2("6.4 Systèmes et rapports au prêteur"),
  ...bullets([
    "Réservations : Pixum (camping) et plateforme Coolbox (unités) ; système hôtelier avec gestionnaire de canaux pour l'hôtel et les villas.",
    "Point de vente restauration intégré à la comptabilité ; comptabilité et paie par une firme comptable externe ; états financiers audités à compter de l'exercice 2028.",
    "Rapports trimestriels : tableau de bord (5.6), ventes par catégorie, encaisse, avancement des travaux.",
  ]),
  H2("6.5 Unités Coolbox : exploitation"),
  P("Les 20 unités Coolbox appartiennent à Havana et entrent dans l'hypothèque mobilière. Elles sont vendues par la plateforme reservationcoolbox.ca et par les canaux du site ; le ménage, l'accueil et l'entretien courant sont assurés par les équipes de Havana, l'entretien du fabricant et la garantie par Coolbox HPA."),
);

// --- 7. Équipe -------------------------------------------------------------------------------------------
children.push(
  ...chapter("07", "Équipe de direction et partenaires", "ban_7", "Une direction renouvelée, la famille fondatrice, et deux partenaires industriels qui construisent et exploitent déjà sur le site."),
  dataTable(["Nom", "Rôle", "Responsabilités dans le projet"], [
    ["Dominic Perrier", "Direction générale, fondateur", "Concept, opérations, animation et relations avec la clientèle depuis 2015"],
    ["Famille Perrier", "Actionnaires", "Continuité de la vision, relations avec la clientèle"],
    ["Direction des opérations, restauration et administration", "Responsables de service", "Hébergement, entretien, saisonniers ; restaurant Madera et événements ; comptabilité, trésorerie et rapports au prêteur"],
    ["Francis Tremblay – Coolbox HPA", "Partenaire industriel", "Unités quatre saisons, plateforme de vente, exploitation des 9 unités existantes"],
    ["Jean-Sébastien Tremblay – Construction Prospère", "Entrepreneur général", "Contrat à forfait, cautionnements, calendrier de chantier"],
  ], [2400, 2400, 4848], { numericFrom: 99, fontSize: 18 }),
  spacer(),
  H2("Conseillers externes"),
  ...bullets([
    "Firme comptable : états financiers, audit dès 2028, classeur financier.",
    "Conseiller juridique : contrats des partenaires et du financement.",
    "Architecte et ingénieur : hôtel, restaurant, infrastructures.",
    "Évaluateur agréé mandaté par l'institution.",
  ]),
);

// --- 8. Plan financier -----------------------------------------------------------------------------------
const emploisRows = M.emplois.map((e) => [e[0], money(e[1]), pct(e[1] / totalEmplois)]);
emploisRows.push(["Total des emplois", money(totalEmplois), "100 %"]);
const sourcesRows = M.sources.map((s) => [s[0], money(s[1]), pct(s[1] / totalEmplois), s[2]]);
sourcesRows.push(["Total des sources", money(totalEmplois), "100 %", ""]);
const revRows = M.lignes.map(([k, name]) => [name, ...Y6.map((y) => money(y.revenus[k]))]);
revRows.push(["Total des revenus", ...Y6.map((y) => money(y.total_revenus))]);
const chRows = M.charges.map(([k, name]) => [name, ...Y6.map((y) => money(y.charges[k]))]);
chRows.push(["Total des charges d'exploitation", ...Y6.map((y) => money(y.total_charges))]);
const resRows = [
  ["BAIIA", ...Y6.map((y) => money(y.baiia))],
  ["Marge BAIIA", ...Y6.map((y) => pct(y.marge_baiia))],
  ["Amortissement comptable", ...Y6.map((y) => money(y.amortissement))],
  ["Intérêts (toutes couches)", ...Y6.map((y) => money(y.interets))],
  ["Bénéfice avant impôts", ...Y6.map((y) => money(y.bai))],
  ["Impôts (12,2 % jusqu'à 500 k$, 26,5 % au-delà)", ...Y6.map((y) => money(y.impots))],
  ["Bénéfice net", ...Y6.map((y) => money(y.benefice_net))],
];
const cfRows = [
  ["Bénéfice net", ...Y6.map((y) => money(y.benefice_net))],
  ["Plus : amortissement", ...Y6.map((y) => money(y.amortissement))],
  ["Flux de trésorerie d'exploitation", ...Y6.map((y) => money(y.benefice_net + y.amortissement))],
  ["Moins : remboursement de capital (toutes couches)", ...Y6.map((y) => money(-y.capital))],
  ["Moins : immobilisations de maintien (2 % des revenus)", ...Y6.map((y) => money(-y.capex_maintien))],
  ["Flux de trésorerie disponible", ...Y6.map((y) => money(y.flux_libre))],
  ["Trésorerie cumulée depuis la clôture (hors réserve et fonds de roulement)", ...Y6.map((y) => money(y.tresorerie_cumulee))],
];
const coucheRows = M.couches.map((c) => [c.nom, money(c.montant), c.taux ? pct(c.taux, 1) : "0 %", c.amort_ans + " ans", c.moratoire_mois + " mois", money(c.paiement_mensuel)]);
const serviceRows = M.couches.map((c) => [c.nom.split(" (")[0].split(" –")[0].split(" :")[0], ...[0, 1, 2, 3, 4].map((i) => money(c.rows[i] ? c.rows[i].service : 0))]);
serviceRows.push(["Service total", ...P5.map((y) => money(y.service_dette))]);
const debtRows = senior.rows.map((d) => [`An ${d.an}`, money(d.interets), money(d.capital), money(d.service), money(d.solde_fin)]);
const B5 = M.bilan; const bm = (f) => B5.map((b) => money(f(b)));
const bilanRows = [
  ["ACTIF", "", "", "", "", ""],
  ["Encaisse (fonds de roulement, réserve de service de la dette, flux cumulés)", ...bm((b) => b.encaisse)],
  ["Immobilisations existantes au coût déclaré, nettes de l'amortissement", ...bm((b) => b.immo_existantes_nettes)],
  ["Nouvelles immobilisations (projet et maintien), nettes", ...bm((b) => b.immo_nouvelles_nettes)],
  ["Frais reportés (conformité, intérêts capitalisés, frais de financement)", ...bm((b) => b.frais_reportes)],
  ["Total de l'actif", ...bm((b) => b.actif_total)],
  ["PASSIF", "", "", "", "", ""],
  ["Portion courante de la dette", ...bm((b) => b.portion_courante)],
  ["Dette à long terme (toutes couches)", ...bm((b) => b.dette_lt)],
  ["Total du passif", ...bm((b) => b.passif_total)],
  ["AVOIR", "", "", "", "", ""],
  ["Avoir pro forma à l'ouverture", ...bm((b) => b.avoir_ouverture)],
  ["Bénéfices non répartis cumulés", ...bm((b) => b.bnr_cumules)],
  ["Total de l'avoir", ...bm((b) => b.avoir_total)],
  ["Total du passif et de l'avoir", ...bm((b) => b.passif_total + b.avoir_total)],
];
const ratioRows = [
  ["Couverture du prêt senior (BAIIA / service senior)", ...P5.map((y) => ratio(y.dscr_senior))],
  ["Couverture toutes couches (BAIIA / service total)", ...P5.map((y) => ratio(y.dscr_total))],
  ["Couverture bancaire ((BAIIA − impôts − maintien) / service total)", ...P5.map((y) => ratio(y.dscr_bancaire))],
  ["Couverture des intérêts", ...P5.map((y) => ratio(y.couverture_interets))],
  ["Dette senior / BAIIA", ...P5.map((y) => ratio(y.solde_senior / y.baiia, 1))],
  ["Dette totale / BAIIA", ...P5.map((y) => ratio(y.solde_total / y.baiia, 1))],
  ["Dette / avoir (bilan pro forma)", ...B5.map((b) => ratio(b.dette_sur_avoir))],
  ["Marge BAIIA", ...P5.map((y) => pct(y.marge_baiia))],
];
const sensRows = M.sensibilite.map((s) => [s.scenario, ratio(s.dscr_an2), ratio(s.dscr_an3), ratio(s.dscr_an5), ratio(s.dscr_banc_an3), ratio(s.dscr_banc_an5)]);
const cap = M.capacite;
const dpaCats = M.dpa.categories;
const dpaRows = dpaCats.map((c) => [c.nom, pct(c.taux, 0), money(c.base), ...c.dpa.map((v) => money(v))]);
dpaRows.push(["Total de la DPA", "", money(dpaCats.reduce((a, c) => a + c.base, 0)), ...M.dpa.total.map((v) => money(v))]);
const debtFullRows = senior.complet.map((d) => [`An ${d.an}`, money(d.interets), money(d.capital), money(d.service), money(d.solde_fin)]);
debtFullRows.push(["Total", money(senior.complet.reduce((a, d) => a + d.interets, 0)), money(senior.complet.reduce((a, d) => a + d.capital, 0)), money(senior.complet.reduce((a, d) => a + d.service, 0)), "—"]);
const hyp = M.hypotheses;
const hypRows = [
  ["Point de départ", "Ventes Pixum 2026 " + money(M.reel_2026_total) + " ; restauration et activités " + money(M.autres_2026.restauration + M.autres_2026.activites) + " ; part Coolbox " + money(cb.redevance), "Rapports Pixum (annexe G), budget de la direction, avis de redevance 2026 (annexe J)"],
  ["Indexation des tarifs", "3 % par année", "Pratique de l'industrie"],
  ["Terrains de camping", "Base 2026 indexée, gain d'occupation 0 % à 4 %", "Pixum 2026 ; aucune capacité nouvelle"],
  ["Terrains saisonniers", [0, 1, 2, 3, 4, 5].map((i) => hyp.saisonniers_sites[String(i)]).join(" → ") + " contrats à 3 650 $ indexés", "12 contrats réels en 2026 ; conversion de terrains existants"],
  ["Chalets (16)", "Été " + pct(hyp.chalets_occ_ete["1"], 0) + " → " + pct(hyp.chalets_occ_ete["5"], 0) + " à 235 $ ; hiver " + pct(hyp.chalets_occ_hiver["1"], 0) + " → " + pct(hyp.chalets_occ_hiver["5"], 0) + " à 210 $ ; An 1 : nov.-déc. seulement", "Réel 2026 : chalets et chambres 497 723 $ ; hivernisation à l'automne 2027"],
  ["Villas (13)", "Été " + pct(hyp.villas_occ_ete["1"], 0) + " → " + pct(hyp.villas_occ_ete["5"], 0) + " à 275 $ ; hiver " + pct(hyp.villas_occ_hiver["1"], 0) + " → " + pct(hyp.villas_occ_hiver["5"], 0) + " ; An 1 : demi-saison", "Livraison en juillet 2027"],
  ["Hôtel", "6 chambres jan.-juin 2027 puis 17 ; occupation " + pct(hyp.hotel_occ["1"], 0) + " → " + pct(hyp.hotel_occ["5"], 0) + " à 190 $", "Sous l'occupation hôtelière régionale ; montée graduelle"],
  ["Unités Coolbox (20, propriété Havana)", "Été " + pct(hyp.coolbox_occ_ete["1"], 0) + " → " + pct(hyp.coolbox_occ_ete["5"], 0) + " à 225 $ ; hiver " + pct(hyp.coolbox_occ_hiver["1"], 0) + " → " + pct(hyp.coolbox_occ_hiver["5"], 0) + " à 199 $ ; 100 % des ventes à Havana", "Réseau Coolbox sur base annuelle : ≈ 40 000 $ par unité par année ; 9 unités à Havana : " + money(cb.ca_ht / cb.unites) + " par unité en un seul été 2026"],
    ["Restauration et bars", pct(hyp.fb_ratio["1"], 0) + " → " + pct(hyp.fb_ratio["5"], 0) + " des revenus d'hébergement", "Réel 2026 : 6,5 % ; budget de la direction à maturité ≈ 890 000 $"],
  ["Spectacles", money(hyp.spectacles["2"]) + " → " + money(hyp.spectacles["5"]) + " de billetterie brute ; cachets et technique 55 %", "Scène et chapiteau existants ; budget de la direction 200 000 $ / 33 000 $"],
  ["Salaires et charges sociales", "39 % (2026) → 36 % An 1 → 30 % An 5", "Tableau d'effectifs ; normalisation Grenier 2021 (30 %)"],
  ["Entretien ; immobilisations de maintien", "8 % ; 2 % des revenus", "Grenier 2021 (8 %) ; pratique bancaire"],
  ["Énergie", money(y1.charges.energie) + " An 1 → " + money(y5.charges.energie) + " An 5", "Budget de la direction (210 000 $ → 480 000 $)"],
  ["Commissions de plateformes", "15 % sur 40 % des nuitées hôtel, villas et Coolbox", "Conditions usuelles des plateformes"],
  ["Amortissement comptable ; DPA", "Linéaire par catégorie ; DPA cat. 1, 6, 8, 17 avec demi-année (annexe K)", "Classement par catégorie fiscale (annexe K)"],
  ["Impôts", "12,2 % jusqu'à 500 k$ de bénéfice, 26,5 % au-delà", "Taux combinés PME"],
  ["Dette existante (2026)", money(M.tranche_a) + " à 7,5 % (intérêts seulement)", "Refinancée à la clôture"],
];
children.push(
  ...chapter("08", "Plan financier", "ban_8", "Des projections qui partent de 2026 tel qu'il est, un montage en couches, et des ratios calculés comme la banque les calcule."),
  H2("8.1 Hypothèses clés"),
  dataTable(["Hypothèse", "Valeur", "Source ou statut"], hypRows, [2300, 3900, 3448], { numericFrom: 99, fontSize: 16 }),
  H2("8.2 Coût du projet et financement"),
  dataTable(["Emplois", "Montant", "Part"], emploisRows, [6200, 1900, 1548], { totalRows: [emploisRows.length - 1], fontSize: 17 }),
  spacer(120),
  dataTable(["Sources", "Montant", "Part", "Statut"], sourcesRows, [4700, 1500, 900, 2548], { totalRows: [sourcesRows.length - 1], fontSize: 16 }),
  NOTE("Argent neuf (emplois hors refinancement) : " + money(M.argent_neuf) + " ; fonds propres : " + money(M.fonds_propres) + ", soit " + pct(M.pct_fonds_propres_argent_neuf, 0) + ". Les couches marquées « à solliciter » sont déposées en parallèle de la présente demande."),
  ...figure("sources_emplois.png", 6.4, "Figure 2 – Emplois et sources de financement"),
  H3("Capacité d'endettement senior (An 3)"),
  dataTable(["Méthode", "Montant"], [
    ["Service de la dette couvert 1,25 fois par le BAIIA moins maintien (7 %, 25 ans)", money(cap.methode_dscr_125)],
    ["5 fois le BAIIA de l'An 3", money(cap.methode_5x_baiia)],
    ["65 % d'une valeur par le revenu (BAIIA moins maintien × 0,8 ÷ 9,5 %)", money(cap.methode_ltv_65_revenu)],
    ["Prêt senior demandé", money(M.senior)],
  ], [7000, 2648], { totalRows: [3], fontSize: 18 }),
  NOTE("Le prêt senior demandé se situe à l'intérieur de la fourchette des trois méthodes."),
  H3("Structure du prêt senior et conditions de déboursement"),
  dataTable(["Modalité", "Proposition"], [
    ["Tranche A", money(M.tranche_a) + " à la clôture : refinancement de la dette existante"],
    ["Tranche B", money(M.tranche_b) + " en prêt de construction, déboursé par avancement des travaux sur certificats de l'architecte, converti en prêt à terme à la réception des travaux"],
    ["Taux et amortissement", pct(senior.taux, 1) + ", 25 ans ; paiement mensuel " + money(senior.paiement_mensuel) + " ; sensibilités à 8 %, 9 % et 20 ans en 8.7"],
    ["Moratoire de capital", "12 mois (construction) ; intérêts de construction capitalisés aux emplois"],
    ["Réserve de service de la dette", money(M.reserve_service) + " (6 mois de paiements) déposée à la clôture, financée par les fonds propres"],
    ["Conditions préalables au premier déboursement", "Permis municipaux ; contrat à forfait et cautionnements de l'entrepreneur ; fonds propres déposés ; assurance chantier"],
    ["Garanties", "Hypothèque de premier rang sur les trois lots ; hypothèque mobilière sur les équipements (rapport 2023, 2,05 M$) et sur les 20 unités Coolbox ; cession d'assurances ; cautionnements des actionnaires."],
    ["Engagements financiers", "Aucun test avant l'exercice 2029 ; ensuite couverture bancaire ≥ 1,25 sur douze mois glissants ; dette / avoir ≤ 3,0 ; blocage des dividendes et des frais de gestion aux parties liées tant que la couverture est < 1,35 ; états financiers audités ; rapports trimestriels"],
  ], [2800, 6848], { numericFrom: 99, fontSize: 17 }),
  H2("8.3 État des résultats prévisionnels"),
  ...figure("revenus.png", 6.5, "Figure 3 – Revenus par source, 2026 et An 1 à An 5"),
  dataTable(["Revenus", ...heads6], revRows, W7, { totalRows: [revRows.length - 1], fontSize: 15 }),
  spacer(120),
  dataTable(["Charges d'exploitation", ...heads6], chRows, W7, { totalRows: [chRows.length - 1], fontSize: 15 }),
  spacer(120),
  dataTable(["Résultats", ...heads6], resRows, W7, { boldRows: [0, 6], fontSize: 16 }),
  NOTE("2026 : exercice de transition, charges du budget de la direction et dette existante en intérêts seulement."),
  ...figure("repartition.png", 6.2, "Figure 4 – Répartition des revenus : 2026 et An 5"),
  H2("8.4 Flux de trésorerie et service de la dette"),
  dataTable(["Flux de trésorerie (méthode indirecte)", ...heads6], cfRows, W7, { boldRows: [2, 5, 6], fontSize: 15 }),
  spacer(120),
  P("Trésorerie mensuelle : le budget de la direction montre un creux cumulé d'environ 300 000 $ de novembre à avril hors service de dette. Le plan y répond par la réserve de service de la dette, le fonds de roulement de " + money(M.emplois.find((e) => e[0].startsWith("Fonds de roulement"))[1]) + ", les contrats saisonniers encaissés de janvier à mars et une marge d'exploitation renouvelable saisonnière (facilité distincte, dimensionnée sur le tableau mensuel du classeur)."),
  H3("Couches de financement"),
  dataTable(["Couche", "Montant", "Taux", "Amortissement", "Moratoire", "Paiement mensuel"], coucheRows, [3600, 1300, 900, 1200, 1100, 1548], { fontSize: 16 }),
  spacer(120),
  dataTable(["Service annuel par couche", ...heads5], serviceRows, W6, { totalRows: [serviceRows.length - 1], fontSize: 16 }),
  pageBreak(),
  dataTable(["Prêt senior", "Intérêts", "Capital", "Service", "Solde en fin d'année"], debtRows, [2000, 1900, 1900, 1900, 1948], { fontSize: 17 }),
  ...figure("dscr.png", 6.5, "Figure 5 – BAIIA, service de la dette et couverture"),
  pageBreak(),
  H2("8.5 Bilan prévisionnel (pro forma)"),
  P("Le bilan est établi au coût : immobilisations existantes au coût des investissements réalisés (" + money(M.immo_existantes_cout) + ", annexe A) moins un amortissement cumulé de " + money(M.amort_cumule_2026) + ", dette existante refinancée, fonds propres injectés. Il balance chaque année."),
  dataTable(["Bilan au 31 décembre", ...heads5], bilanRows, W6, { subheadRows: [0, 6, 10], totalRows: [5, 9, 13, 14], fontSize: 15 }),
  H2("8.6 Ratios financiers"),
  dataTable(["Ratio", ...heads5], ratioRows, W6, { boldRows: [0, 2], fontSize: 17 }),
  callout("Lecture des ratios", [
    "Le prêt senior est couvert " + ratio(y2.dscr_senior) + " en An 2 et " + ratio(y3.dscr_senior) + " en An 3. En ajoutant toutes les couches, la couverture atteint " + ratio(y3.dscr_total) + " en An 3 et " + ratio(y5.dscr_total) + " en An 5 ; en définition bancaire (après impôts et immobilisations de maintien), " + ratio(y3.dscr_bancaire) + " et " + ratio(y5.dscr_bancaire) + ". L'An 1 est une année de construction et l'An 2 la première année d'exploitation douze mois : le plan ne propose aucun test de covenant avant l'exercice 2029.",
  ]),
  H2("8.7 Analyse de sensibilité"),
  P("Part variable des charges calculée à partir de la structure du modèle (" + pct(M.part_variable, 0) + "), et non forfaitaire. Les scénarios portent sur le service de toutes les couches."),
  dataTable(["Scénario", "Toutes couches An 2", "An 3", "An 5", "Bancaire An 3", "Bancaire An 5"], sensRows, [3400, 1300, 1150, 1150, 1350, 1298], { boldRows: [0], fontSize: 16 }),
  P("Le prêt senior demeure couvert dans tous les scénarios dès l'An 3. Les baisses de revenus de 10 % et plus ramènent la couverture de l'ensemble des couches sous 1,25 : la réserve de service de la dette, les saisonniers encaissés d'avance et le blocage des distributions couvrent cette transition. Le spa, non compté, constitue un potentiel additionnel."),
  H2("8.8 Seuil de rentabilité"),
  P("À l'An 3, les charges fixes (" + pct(1 - M.part_variable, 0) + " des charges) et le service de la dette totalisent environ " + moneyM(y3.total_charges * (1 - M.part_variable) + y3.service_dette, 2) + " ; avec une marge sur charges variables de " + pct(1 - y3.total_charges * M.part_variable / y3.total_revenus, 0) + ", le seuil de rentabilité en trésorerie se situe autour de " + moneyM((y3.total_charges * (1 - M.part_variable) + y3.service_dette) / (1 - y3.total_charges * M.part_variable / y3.total_revenus), 1) + " de revenus, soit " + pct(((y3.total_charges * (1 - M.part_variable) + y3.service_dette) / (1 - y3.total_charges * M.part_variable / y3.total_revenus)) / y3.total_revenus, 0) + " des revenus projetés."),
);

// --- 9. Risques ---------------------------------------------------------------------------------------------
children.push(
  ...chapter("09", "Risques et mesures d'atténuation", "ban_9", "Chaque risque a un responsable et une mesure."),
  dataTable(["Risque", "Probabilité / impact", "Mesures"], [
    ["Dépassement des coûts ou retard de chantier", "Moyen / élevé", "Contrat à forfait Construction Prospère, cautionnements, contingence 5 % / 10 %, décaissements par avancement sur certificats, unités Coolbox à prix fixe d'usine"],
    ["Montée en régime plus lente de l'hiver", "Moyen / élevé", "Produit hiver éprouvé (Coolbox), programme d'hiver nommé (5.3), réserve de service de la dette, aucun test de covenant avant 2029, blocage des distributions"],
    ["Voisinage et bruit", "Faible / moyen", "Protocole de bruit (heures, orientation de la scène, nombre d'événements), communication avec la municipalité et les voisins"],
    ["Météo et saison estivale défavorable", "Moyen / moyen", "Saisonniers encaissés d'avance, hôtel et unités chauffées, restauration, assurance pertes d'exploitation"],
    ["Main-d'œuvre", "Élevé / moyen", "Logement sur le site, postes à l'année, partenariats avec les écoles hôtelières"],
    ["Hausse des taux d'intérêt", "Moyen / moyen", "Taux fixe 5 ans sur le senior ; sensibilités à 8 % et 9 % en 8.7"],
    ["Dépendance à la direction", "Moyen / élevé", "Responsables de service, assurance personne clé, rapports trimestriels au prêteur"],
  ], [2700, 1500, 5448], { numericFrom: 99, fontSize: 16 }),
);

// --- 10. Conclusion ------------------------------------------------------------------------------------------
children.push(
  ...chapter("10", "Conclusion et demande", "ban_10"),
  LEAD("Un site qui vend déjà " + moneyM(M.reel_2026_total, 1) + " par année, 11,9 M$ investis, un produit quatre saisons en place : le Complexe Havana demande un prêt senior de " + moneyM(M.senior, 1) + " dans un montage de " + moneyM(totalEmplois, 1) + " pour ouvrir douze mois par année."),
  P("Le projet demande à la banque de financer des travaux ciblés, construits par un entrepreneur licencié à prix forfaitaire sur des actifs existants, avec des fonds propres de " + pct(M.pct_fonds_propres_argent_neuf, 0) + " de l'argent neuf et un prêt senior couvert " + ratio(y3.dscr_senior) + " en An 3."),
  callout("Demande", [
    [run("Prêt hypothécaire de premier rang de " + money(M.senior), { bold: true, size: 20 })],
    "Tranche A de " + money(M.tranche_a) + " à la clôture (refinancement) ; tranche B de " + money(M.tranche_b) + " en prêt de construction convertible à la réception des travaux.",
    "Amortissement de 25 ans, moratoire de capital de 12 mois, réserve de service de la dette de 6 mois déposée à la clôture.",
    "Couches complémentaires sollicitées : " + money(M.couches.slice(1).reduce((a, c) => a + c.montant, 0)) + " ; fonds propres : " + money(M.fonds_propres) + ", dont " + money(M.apport_coolbox) + " en nature (20 unités Coolbox).",
    "Clôture souhaitée en janvier 2027, pour un début des travaux à l'hiver 2027 et une ouverture en juillet 2027.",
  ]),
  P("Nous remercions l'institution de l'attention portée à ce dossier et demeurons disponibles pour une visite du site."),
  spacer(200),
  P("_______________________________", { after: 0 }), P("Dominic Perrier, direction générale", { after: 0 }), P("Complexe Havana", { after: 0 }), P("514 774-7979 · havanaresort.ca"),
);

// --- Annexes ---------------------------------------------------------------------------------------------------
children.push(
  ...chapter("A", "Annexes", "ban_annexes"),
  P("Les documents ci-dessous accompagnent le plan d'affaires. Les pièces complémentaires seront fournies et prises en considération aux étapes subséquentes du projet, au fur et à mesure de sa progression."),
  dataTable(["Annexe", "Contenu"], [
    ["A", "États financiers, état de la dette existante, historique des investissements 2015-2023 (11 915 000 $)"],
    ["B", "Rapports d'évaluation : Grenier 2021 (méthode du revenu), Leblanc 2024 (hôtel) et 2025 (camping), rapport d'équipements 2023 (2 052 200 $), rôle municipal 2024-2026"],
    ["C", "Soumissions à forfait : Construction Prospère par composante, Coolbox HPA (9 unités, validité 12 mois)"],
    ["D", "Plans, permis municipaux et documents d'infrastructures (usine d'épuration 2019)"],
    ["E", "Curriculum vitæ de la direction ; fiches Construction Prospère et Coolbox HPA"],
    ["F", "Chronologie visuelle des travaux 2015-2023, cartes du site 2023 et 2026, photos"],
    ["G", "Rapports du système de réservation 2025 et 2026 ; grille tarifaire"],
    ["H", "Classeur financier (hypothèses, investissement, couches de dette, résultats, trésorerie, bilan, ratios, sensibilité, DPA)"],
    ["I", "Lettres d'appui et des partenaires"],
    ["J", "Contrat de partenariat Coolbox, avis et calcul de redevance 2026, ventes d'hiver du réseau, fiche technique des unités"],
    ["K", "Cédule de DPA par catégorie fiscale ; tableau d'amortissement complet du prêt senior"],
  ], [900, 8748], { numericFrom: 99, fontSize: 17 }),
  pageBreak(),
  H2("Annexe K – Tableau d'amortissement complet du prêt senior"),
  NOTE("Prêt de " + money(M.senior) + " à " + pct(senior.taux, 1) + ", 25 ans, paiement mensuel de " + money(senior.paiement_mensuel) + " après le moratoire de 12 mois ; An 1 : intérêts sur le solde moyen décaissé."),
  dataTable(["Année", "Intérêts", "Capital", "Service", "Solde en fin d'année"], debtFullRows, [1600, 2000, 2000, 2000, 2048], { totalRows: [debtFullRows.length - 1], fontSize: 15 }),
  pageBreak(),
  H2("Annexe K – Cédule de DPA par catégorie fiscale"),
  NOTE("Investissement capitalisé (travaux, contingence et honoraires au prorata) et frais de financement, solde dégressif avec règle de demi-année."),
  dataTable(["Catégorie", "Taux", "Base", "DPA 2027", "DPA 2028", "DPA 2029", "DPA 2030", "DPA 2031"], dpaRows, [2448, 650, 1250, 1060, 1060, 1060, 1060, 1060], { totalRows: [dpaRows.length - 1], fontSize: 14 }),
);

// --- Quatrième de couverture -----------------------------------------------------------------
const backMeta = PHOTOS.dos;
const backChildren = [
  new Paragraph({ spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT }, children: backMeta ? [bleedImage(backMeta, 0, 8.5, 11)] : [] }),
  exactSpacer(5200),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [run("COMPLEXE HAVANA", { bold: true, size: 40, color: WHITE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 0 }, children: [new TextRun({ text: "Un petit bout de Cuba, douze mois par année", font: "Georgia", size: 24, italics: true, color: GOLD })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 0 }, children: [run("631, 7e Rang, Maricourt (Québec)  J0E 2L2", { size: 20, color: "D9F1F3" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 0 }, children: [run("514 774-7979   ·   havanaresort.ca", { size: 20, color: "D9F1F3" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 0 }, children: [run("Plan d'affaires 2027 – 2031, version 2   ·   Document confidentiel", { size: 17, color: "A8D8DC" })] }),
];

const header = new Header({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], border: { bottom: { color: MID, size: 4, style: BorderStyle.SINGLE, space: 4 } }, children: [run("Complexe Havana", { bold: true, size: 17, color: NAVY }), run("\tPlan d'affaires 2027 – 2031 · v2", { size: 17, color: GREY })] })] });
const footer = new Footer({ children: [new Paragraph({ tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], children: [run("Confidentiel", { size: 16, color: GREY }), new TextRun({ children: ["\tPage ", PageNumber.CURRENT], font: FONT, size: 16, color: GREY })] })] });
const doc = new Document({
  creator: "Complexe Havana", title: "Plan d'affaires 2027-2031 v2 – Complexe Havana", description: "Demande de financement",
  styles: { default: { document: { run: { font: FONT, size: 21, color: INK } } }, paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 40, bold: true, color: NAVY }, paragraph: { spacing: { before: 0, after: 200 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 27, bold: true, color: NAVY }, paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: TEAL }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
  ] },
  numbering: { config: [
    { reference: "puces", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } }, run: { color: TEAL } } }] },
    { reference: "numeros", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { color: NAVY, bold: true } } }] },
  ] },
  features: { updateFields: true },
  sections: [
    { properties: { titlePage: true, page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: 1200, bottom: 1100, left: MARGIN, right: MARGIN, header: 560, footer: 560 } } }, headers: { default: header, first: new Header({ children: [] }) }, footers: { default: footer, first: new Footer({ children: [] }) }, children },
    { properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: 1200, bottom: 1100, left: MARGIN, right: MARGIN, header: 560, footer: 560 } } }, headers: { default: new Header({ children: [] }) }, footers: { default: new Footer({ children: [] }) }, children: backChildren },
  ],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUTPUT, buf); console.log("Écrit :", OUTPUT, Math.round(buf.length / 1024), "ko"); });
