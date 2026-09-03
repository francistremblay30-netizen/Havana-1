// Générateur du plan d'affaires Word du Complexe Havana.
// Lit modele.json (produit par modele_financier.py) et les graphiques PNG.
// Usage : node generer_plan.js  → ../Plan_affaires_Complexe_Havana.docx

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, ImageRun, PageBreak, Header, Footer, PageNumber,
  TableOfContents, LevelFormat, VerticalAlign, TabStopType,
} = require("docx");

const HERE = __dirname;
const M = JSON.parse(fs.readFileSync(path.join(HERE, "modele.json"), "utf8"));
const OUTPUT = path.join(HERE, "..", "Plan_affaires_Complexe_Havana.docx");
const PHOTOS_META = path.join(HERE, "..", "photos", "photos_meta.json");
const PHOTOS = fs.existsSync(PHOTOS_META) ? JSON.parse(fs.readFileSync(PHOTOS_META, "utf8")) : {};

// --- Palette et typographie --------------------------------------------------
const NAVY = "0B2A4A", TEAL = "1B7F79", GOLD = "C9A227", GREY = "8A94A6", LIGHT = "F2F4F7", MID = "D9DEE7", WHITE = "FFFFFF", INK = "1F2933";
const FONT = "Calibri";
const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1296; // US Letter, marges 0,9 po
const CONTENT_W = PAGE_W - 2 * MARGIN; // 9648 DXA

// --- Formatage ----------------------------------------------------------------
const fmt = (n, dec = 0) => {
  const neg = n < 0;
  const s = Math.abs(n).toFixed(dec);
  const [int, frac] = s.split(".");
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return (neg ? "(" : "") + grouped + (frac ? "," + frac : "") + (neg ? ")" : "");
};
const money = (n) => fmt(n) + " $";
const moneyK = (n) => fmt(n / 1000) + " k$";
const moneyM = (n, dec = 2) => fmt(n / 1e6, dec).replace(".", ",") + " M$";
const pct = (x, dec = 1) => fmt(x * 100, dec) + " %";
const ratio = (x, dec = 2) => fmt(x, dec) + " x";

// --- Briques de mise en page ------------------------------------------------------
const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: 21, color: INK, ...opts });

const P = (text, opts = {}) => {
  const { bold, italics, color, size, align, before = 0, after = 120, keepNext, indent } = opts;
  const runs = Array.isArray(text) ? text : [run(text, { bold, italics, color, size })];
  return new Paragraph({ children: runs, alignment: align || AlignmentType.LEFT, spacing: { before, after, line: 276 }, keepNext, indent });
};

const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: FONT, size: 40, bold: true, color: NAVY })],
  spacing: { before: 0, after: 200 },
  border: { bottom: { color: TEAL, size: 12, style: BorderStyle.SINGLE, space: 6 } },
  pageBreakBefore: true,
});
const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: FONT, size: 27, bold: true, color: NAVY })],
  spacing: { before: 300, after: 120 }, keepNext: true,
});
const H3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: FONT, size: 22, bold: true, color: TEAL })],
  spacing: { before: 200, after: 80 }, keepNext: true,
});
// Titre-message (style conseil) : une phrase qui énonce le point clé de la section.
const LEAD = (text) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 24, italics: true, color: TEAL })],
  spacing: { before: 0, after: 200, line: 276 },
});

const bullets = (items, ref = "puces") => items.map((t) => new Paragraph({
  children: Array.isArray(t) ? t : [run(t)],
  numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 276 },
}));
const numbered = (items) => items.map((t) => new Paragraph({
  children: Array.isArray(t) ? t : [run(t)],
  numbering: { reference: "numeros", level: 0 }, spacing: { after: 80, line: 276 },
}));

const border = (color = MID, size = 4) => ({ style: BorderStyle.SINGLE, size, color });
const noBorder = { style: BorderStyle.NONE, size: 0, color: WHITE };
const borders = (b) => ({ top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b });

const cell = (content, width, opts = {}) => {
  const { fill, align, bold, color, size, vAlign, margins, colSpan, italics, bordersOverride } = opts;
  const paras = (Array.isArray(content) ? content : [content]).map((c) =>
    c instanceof Paragraph ? c : new Paragraph({
      children: [run(String(c), { bold, color, size: size || 19, italics })],
      alignment: align || AlignmentType.LEFT, spacing: { before: 40, after: 40, line: 240 },
    }));
  return new TableCell({
    children: paras, width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
    verticalAlign: vAlign || VerticalAlign.CENTER,
    margins: margins || { top: 40, bottom: 40, left: 70, right: 70 },
    columnSpan: colSpan, borders: bordersOverride,
  });
};

// Tableau de données : en-tête marine, lignes alternées, colonnes numériques à droite.
const dataTable = (headers, rows, widths, opts = {}) => {
  const { numericFrom = 1, totalRows = [], boldRows = [], subheadRows = [], fontSize = 19 } = opts;
  const total = widths.reduce((a, b) => a + b, 0);
  const head = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(h, widths[i], { fill: NAVY, color: WHITE, bold: true, size: fontSize, align: i >= numericFrom ? AlignmentType.RIGHT : AlignmentType.LEFT })),
  });
  const body = rows.map((r, ri) => {
    const isTotal = totalRows.includes(ri), isBold = boldRows.includes(ri), isSub = subheadRows.includes(ri);
    const fill = isTotal ? MID : isSub ? "E4EEF5" : ri % 2 === 1 ? LIGHT : WHITE;
    return new TableRow({
      cantSplit: true,
      children: r.map((v, i) => cell(v, widths[i], { fill, bold: isTotal || isBold || isSub, size: fontSize, color: isSub ? NAVY : INK, align: i >= numericFrom ? AlignmentType.RIGHT : AlignmentType.LEFT })),
    });
  });
  return new Table({ rows: [head, ...body], width: { size: total, type: WidthType.DXA }, columnWidths: widths, borders: borders(border(MID, 4)) });
};

// Rangée d'indicateurs clés.
const kpiRow = (items) => {
  const w = Math.floor(CONTENT_W / items.length);
  const widths = items.map(() => w);
  return new Table({
    rows: [new TableRow({
      children: items.map(({ label, value }) => new TableCell({
        width: { size: w, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" },
        borders: { top: border(TEAL, 18), bottom: noBorder, left: noBorder, right: { style: BorderStyle.SINGLE, size: 6, color: WHITE } },
        margins: { top: 120, bottom: 120, left: 120, right: 120 },
        children: [
          new Paragraph({ children: [run(value, { bold: true, size: 30, color: NAVY })], spacing: { after: 40 } }),
          new Paragraph({ children: [run(label, { size: 17, color: GREY })], spacing: { after: 0 } }),
        ],
      })),
    })],
    width: { size: w * items.length, type: WidthType.DXA }, columnWidths: widths,
  });
};

// Encadré (message clé, mise en garde).
const callout = (title, lines, accent = TEAL) => new Table({
  rows: [new TableRow({
    children: [new TableCell({
      width: { size: CONTENT_W, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" },
      borders: { left: border(accent, 24), top: noBorder, bottom: noBorder, right: noBorder },
      margins: { top: 120, bottom: 120, left: 200, right: 160 },
      children: [
        new Paragraph({ children: [run(title, { bold: true, color: NAVY, size: 21 })], spacing: { after: 80 } }),
        ...lines.map((l) => new Paragraph({ children: Array.isArray(l) ? l : [run(l, { size: 20 })], spacing: { after: 60, line: 264 } })),
      ],
    })],
  })],
  width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W],
});

// Image réelle (si une photo est associée à l'emplacement) ou espace réservé.
const photoRun = (meta, maxWDxa, maxHDxa) => {
  const data = fs.readFileSync(path.join(HERE, "..", meta.file));
  const maxW = maxWDxa / 1440 * 96, maxH = maxHDxa / 1440 * 96;
  const scale = Math.min(maxW / meta.width, maxH / meta.height);
  return new ImageRun({ type: "jpg", data, transformation: { width: Math.round(meta.width * scale), height: Math.round(meta.height * scale) } });
};
const photoCell = (meta, width, height, fallbackCaption) => {
  if (meta) {
    return new TableCell({
      width: { size: width, type: WidthType.DXA }, borders: borders(noBorder), verticalAlign: VerticalAlign.CENTER,
      margins: { top: 0, bottom: 0, left: 0, right: 0 },
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [photoRun(meta, width, height)] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [run(meta.caption || "", { italics: true, size: 17, color: GREY })] }),
      ],
    });
  }
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: "F7F8FA", color: "auto" },
    borders: borders({ style: BorderStyle.DASHED, size: 8, color: GREY }), verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [run("IMAGE À INSÉRER", { bold: true, color: GREY, size: 18 })], spacing: { after: 60 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [run(fallbackCaption, { italics: true, color: GREY, size: 19 })], spacing: { after: 0 } }),
    ],
  });
};
const placeholder = (caption, height = 2400, width = CONTENT_W, slot = null) => {
  const meta = slot ? PHOTOS[slot] : null;
  return new Table({
    rows: [new TableRow({ height: meta ? undefined : { value: height, rule: "atLeast" }, children: [photoCell(meta, width, height, caption)] })],
    width: { size: width, type: WidthType.DXA }, columnWidths: [width], borders: borders(noBorder),
  });
};
const twoPlaceholders = (c1, c2, height = 2200, slot1 = null, slot2 = null) => {
  const w = Math.floor((CONTENT_W - 200) / 2);
  const gap = new TableCell({ width: { size: 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] });
  const m1 = slot1 ? PHOTOS[slot1] : null, m2 = slot2 ? PHOTOS[slot2] : null;
  return new Table({
    rows: [new TableRow({ height: (m1 && m2) ? undefined : { value: height, rule: "atLeast" }, children: [photoCell(m1, w, height, c1), gap, photoCell(m2, w, height, c2)] })],
    width: { size: w * 2 + 200, type: WidthType.DXA }, columnWidths: [w, 200, w], borders: borders(noBorder),
  });
};
// Galerie de photos sur deux colonnes.
const gallery = (items, fallbackCaption, height = 3600) => {
  if (!items || !items.length) return [placeholder(fallbackCaption, height)];
  const w = Math.floor((CONTENT_W - 200) / 2), rowH = 3600;
  const rows = [];
  for (let i = 0; i < items.length; i += 2) {
    const cells = [photoCell(items[i], w, rowH, "")];
    cells.push(new TableCell({ width: { size: 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] }));
    cells.push(items[i + 1] ? photoCell(items[i + 1], w, rowH, "") : new TableCell({ width: { size: w, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] }));
    rows.push(new TableRow({ cantSplit: true, children: cells }));
    rows.push(new TableRow({ height: { value: 160, rule: "exact" }, children: [new TableCell({ columnSpan: 3, width: { size: w * 2 + 200, type: WidthType.DXA }, borders: borders(noBorder), children: [new Paragraph("")] })] }));
  }
  return [new Table({ rows, width: { size: w * 2 + 200, type: WidthType.DXA }, columnWidths: [w, 200, w], borders: borders(noBorder) })];
};

const figure = (file, widthIn, caption) => {
  const data = fs.readFileSync(path.join(HERE, "graphiques", file));
  // Les graphiques sont produits à 200 ppp ; ratio calculé à partir de la taille de figure.
  const dims = { "revenus.png": [7.2, 3.6], "dscr.png": [7.2, 3.4], "sources_emplois.png": [7.2, 3.6], "repartition.png": [7.2, 3.4], "echeancier.png": [7.2, 2.6] }[file];
  const w = Math.round(widthIn * 96), h = Math.round(widthIn * dims[1] / dims[0] * 96);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, children: [new ImageRun({ type: "png", data, transformation: { width: w, height: h } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [run(caption, { italics: true, size: 17, color: GREY })] }),
  ];
};

const spacer = (after = 120) => new Paragraph({ spacing: { after } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

// --- Données du modèle ---------------------------------------------------------------
const Y = M.annees; // 0 = 2026 réel, 1..5 projetés
const P5 = Y.slice(1);
const yearHeads = P5.map((y) => y.label.replace(" – ", "\n"));
const revLine = (k) => P5.map((y) => money(y.revenus[k]));
const chLine = (k) => P5.map((y) => money(y.charges[k]));

// =====================================================================================
// CONTENU
// =====================================================================================
const children = [];

// --- Page couverture -----------------------------------------------------------------
children.push(
  new Paragraph({ spacing: { before: 1800, after: 0 }, children: [run("COMPLEXE HAVANA", { bold: true, size: 64, color: NAVY })] }),
  new Paragraph({ spacing: { before: 60, after: 0 }, children: [run("Maricourt, Cantons-de-l'Est", { size: 24, color: GREY })], border: { bottom: { color: TEAL, size: 18, style: BorderStyle.SINGLE, space: 10 } } }),
  new Paragraph({ spacing: { before: 400, after: 100 }, children: [run("Plan d'affaires 2027 – 2031", { bold: true, size: 44, color: NAVY })] }),
  new Paragraph({ spacing: { before: 0, after: 100 }, children: [run("Du camping estival au centre de villégiature quatre saisons", { size: 28, color: TEAL, italics: true })] }),
  new Paragraph({ spacing: { before: 0, after: 500 }, children: [run("Demande de financement de " + moneyM(M.pret, 1), { size: 26, color: INK })] }),
  placeholder("Photo de couverture : vue aérienne du site ou piscine centrale avec le café-bar (haute résolution)", 6600, CONTENT_W, "couverture"),
  new Paragraph({ spacing: { before: 500, after: 60 }, children: [run("Présenté à : ", { bold: true, color: NAVY }), run("[Nom de l'institution financière]")] }),
  new Paragraph({ spacing: { after: 60 }, children: [run("Préparé par : ", { bold: true, color: NAVY }), run("La direction du Complexe Havana")] }),
  new Paragraph({ spacing: { after: 60 }, children: [run("Date : ", { bold: true, color: NAVY }), run("Septembre 2026")] }),
  new Paragraph({ spacing: { before: 300, after: 0 }, children: [run("DOCUMENT CONFIDENTIEL", { bold: true, size: 18, color: GREY })] }),
  pageBreak(),
);

// --- Avis et table des matières --------------------------------------------------------
children.push(
  H2("Avis de confidentialité"),
  P("Ce plan d'affaires contient des renseignements confidentiels et exclusifs appartenant au Complexe Havana. Il est remis uniquement aux fins d'évaluation d'une demande de financement. Toute reproduction ou divulgation, en tout ou en partie, sans le consentement écrit de la direction est interdite. Les projections financières reposent sur des hypothèses jugées raisonnables au moment de la rédaction ; les résultats réels pourraient différer."),
  spacer(200),
  H2("Table des matières"),
  new TableOfContents("Table des matières", { hyperlink: true, headingStyleRange: "1-2" }),
  spacer(),
);

// --- 1. Sommaire exécutif --------------------------------------------------------------
const y3 = Y[3], y5 = Y[5], y1 = Y[1];
children.push(
  H1("1. Sommaire exécutif"),
  LEAD("Un concept unique au Québec, un site qui affiche complet chaque été et une expansion structurée vers une exploitation douze mois par année."),
  kpiRow([
    { label: "Revenus 2026 (réels, avant taxes)", value: moneyM(M.reel_2026_total) },
    { label: "Valeur estimée du site (2025)", value: moneyM(M.valeur_site, 0) },
    { label: "Financement demandé", value: moneyM(M.pret, 1) },
    { label: "Ratio prêt-valeur", value: pct(M.ltv, 0) },
  ]),
  spacer(80),
  kpiRow([
    { label: "Revenus projetés An 5", value: moneyM(y5.total_revenus, 1) },
    { label: "BAIIA An 5", value: moneyM(y5.baiia, 1) },
    { label: "Couverture de la dette An 3", value: ratio(y3.dscr) },
    { label: "Couverture de la dette An 5", value: ratio(y5.dscr) },
  ]),
  spacer(200),
  H2("L'entreprise"),
  P("Le Complexe Havana est un centre de villégiature de 263 acres situé sur le 7e rang à Maricourt, dans les Cantons-de-l'Est, à environ 90 minutes de Montréal. Fondé en 2015 par la famille Perrier, il propose une expérience de vacances inspirée des grandes destinations cubaines : piscine centrale avec café-bar, animation, musique et cuisine cubaines. L'offre d'hébergement compte aujourd'hui 265 terrains de camping, 35 terrains saisonniers, 16 chalets, 6 chambres et 13 cabanas prêt-à-camper."),
  P("Le concept a rencontré un franc succès. Le site affiche complet pendant la majeure partie de la saison estivale et les revenus d'hébergement enregistrés par le système de réservation ont progressé de " + moneyM(M.reel_2025_total) + " en 2025 à " + moneyM(M.reel_2026_total) + " en 2026, soit une hausse de 5,4 %, malgré une capacité d'accueil saturée."),
  H2("Le projet"),
  P("L'entreprise est à un point charnière : la demande dépasse la capacité en été et le site demeure fermé une grande partie de l'année. Le projet consiste à transformer le camping estival en centre récréotouristique ouvert douze mois par année, en deux phases réalisées sur 18 mois :"),
  ...bullets([
    [run("Phase 1 (hiver-printemps 2027, 2,5 M$) : ", { bold: true }), run("hôtel porté de 6 à 17 chambres, restaurant Madera et salle de conférence, achèvement des 13 villas, mise à niveau quatre saisons des chalets existants et aménagement de 35 terrains saisonniers additionnels.")],
    [run("Phase 2 (automne 2027-printemps 2028, 3,0 M$) : ", { bold: true }), run("piscine et spa quatre saisons, amphithéâtre et sentier lumineux.")],
  ]),
  H2("La demande de financement"),
  P("Le Complexe Havana sollicite un prêt à terme hypothécaire de " + money(M.pret) + ", qui servira à financer les projets de développement (" + moneyM(M.emplois[0][1], 1) + " plus contingence et honoraires) et à refinancer la dette existante de 5,0 M$ dans une structure unique. Les propriétaires et des investisseurs privés injectent " + money(M.emplois.reduce((a, e) => a + e[1], 0) - M.pret) + ". Le prêt est garanti par une hypothèque de premier rang sur un site évalué à " + moneyM(M.valeur_site, 0) + " en 2025, pour un ratio prêt-valeur de " + pct(M.ltv, 0) + "."),
  H2("Pourquoi le projet est solide"),
  ...numbered([
    [run("Une demande démontrée : ", { bold: true }), run("le site affiche complet en été ; la croissance passe par la capacité et la durée d'exploitation, non par la recherche de nouveaux clients.")],
    [run("Un actif de grande valeur : ", { bold: true }), run("un ratio prêt-valeur de " + pct(M.ltv, 0) + " laisse une marge de sécurité importante au prêteur.")],
    [run("Des revenus diversifiés : ", { bold: true }), run("l'hébergement quatre saisons, la restauration, le spa et les événements réduisent la dépendance à la saison estivale.")],
    [run("Une capacité de remboursement confortable : ", { bold: true }), run("ratio de couverture du service de la dette de " + ratio(y1.dscr) + " dès l'An 1 et de " + ratio(y3.dscr) + " en An 3, avec un moratoire de capital de 18 mois pendant la construction.")],
    [run("Une direction renouvelée : ", { bold: true }), run("nouvelle direction depuis 2025, appuyée sur la structure familiale fondatrice et sur un système de gestion des réservations éprouvé.")],
  ]),
  H2("Faits saillants financiers"),
  dataTable(
    ["", ...yearHeads],
    [
      ["Revenus totaux", ...P5.map((y) => money(y.total_revenus))],
      ["BAIIA", ...P5.map((y) => money(y.baiia))],
      ["Marge BAIIA", ...P5.map((y) => pct(y.marge_baiia))],
      ["Service de la dette", ...P5.map((y) => money(y.service_dette))],
      ["Ratio de couverture (DSCR)", ...P5.map((y) => ratio(y.dscr))],
      ["Bénéfice net", ...P5.map((y) => money(y.benefice_net))],
    ],
    [2600, 1410, 1410, 1410, 1410, 1408], { boldRows: [4] },
  ),
);

// --- 2. L'entreprise ----------------------------------------------------------------------
const reel = Y[0].revenus;
children.push(
  H1("2. L'entreprise"),
  LEAD("Dix ans d'exploitation, un concept qui n'existe nulle part ailleurs au Québec et un site de 263 acres qui vaut 28 M$."),
  H2("2.1 Historique"),
  P("En 2015, la famille Perrier fait l'acquisition d'un vaste terrain de 263 acres sur le 7e rang à Maricourt, dans les Cantons-de-l'Est, et fonde le Camping Havana Resort. L'ambition est claire dès le départ : créer un complexe touristique unique qui permet de « voyager à Cuba en restant au Québec »."),
  P("Le concept s'articule autour d'une piscine centrale avec café-bar intégré, où se déploient l'animation, la musique et l'ambiance festive et familiale des grandes destinations vacances. Au fil des saisons, l'offre s'est enrichie de chalets, de cabanas prêt-à-camper, d'un premier bâtiment hôtelier de six chambres et d'activités récréatives. Le camping est aujourd'hui devenu trop petit pour la demande."),
  H2("2.2 Mission, vision et valeurs"),
  H3("Mission"),
  P("Offrir à tous nos invités un petit bout de Cuba afin qu'ils puissent se divertir, décrocher de leur quotidien et retrouver l'ambiance des plus grandes destinations vacances. L'accueil chaleureux n'est qu'un prélude au service impeccable que reçoivent les invités tout au long d'un séjour qui se veut mémorable. Notre mission ultime : que chaque invité planifie son retour au moment de son départ."),
  H3("Vision"),
  P("Être le seul et unique complexe d'hébergement et d'activités récréotouristiques au concept entièrement cubain au Québec, ouvert à l'année, reconnu pour son offre unique, son service personnalisé, ses pratiques durables et ses partenariats avec la communauté cubaine et locale."),
  H3("Valeurs"),
  ...bullets([
    [run("Chaleur et convivialité : ", { bold: true }), run("un accueil qui fait sentir chaque invité comme un membre de la famille.")],
    [run("Authenticité : ", { bold: true }), run("une expérience cubaine crédible, dans l'ambiance, la musique et l'assiette.")],
    [run("Rigueur : ", { bold: true }), run("des opérations et une gestion financière disciplinées, appuyées sur des systèmes.")],
    [run("Durabilité : ", { bold: true }), run("un site protégé, des pratiques responsables et un ancrage dans la communauté.")],
  ]),
  H2("2.3 Structure juridique et propriété"),
  dataTable(
    ["Élément", "Détail"],
    [
      ["Raison sociale", "[À compléter : nom légal de la société]"],
      ["Forme juridique", "[Société par actions (Québec ou fédérale)]"],
      ["Numéro d'entreprise (NEQ)", "[À compléter]"],
      ["Date de constitution", "[À compléter]"],
      ["Actionnaires et pourcentage détenu", "[Famille Perrier : à détailler par actionnaire]"],
      ["Siège social", "7e rang, Maricourt (Québec)"],
      ["Exercice financier", "[À confirmer]"],
    ],
    [3400, 6248], { numericFrom: 99 },
  ),
  H2("2.4 Direction"),
  P("Le Complexe Havana s'est doté d'une nouvelle direction en 2025, mandatée pour mener le projet d'exploitation douze mois. La structure familiale fondatrice demeure en place et assure la continuité de la vision et des relations avec la clientèle. L'équipe est présentée à la section 7."),
  H2("2.5 Actifs et installations actuelles"),
  dataTable(
    ["Installation", "Quantité", "Tarif de référence", "Saison d'exploitation"],
    [
      ["Terrains de camping (services 2 et 3)", "265", "90 $ / nuit", "Mai à octobre"],
      ["Terrains saisonniers", "35", "3 650 $ / saison", "Mai à octobre"],
      ["Chalets", "16", "235 $ / nuit", "Mai à octobre"],
      ["Chambres d'hôtel", "6", "190 $ / nuit", "Mai à octobre"],
      ["Cabanas prêt-à-camper", "13", "200 $ / nuit", "Mai à octobre"],
      ["Villas (en construction)", "13", "275 $ / nuit", "À livrer en 2027"],
      ["Piscine centrale et café-bar", "1", "Inclus", "Été"],
      ["Cantine, jeux gonflables, concessions", "—", "Variable", "Été"],
    ],
    [3600, 1300, 2300, 2448], { numericFrom: 1 },
  ),
  spacer(),
  twoPlaceholders("Vue aérienne du site (263 acres)", "Piscine centrale et café-bar en saison", 3300, "aerienne", "piscine"),
  spacer(),
  H2("2.6 Performance récente"),
  P("Les revenus enregistrés par le système de réservation (reservationcamping.ca) illustrent la vigueur de la demande. Les revenus ont progressé de 5,4 % en 2026 avec 8,7 % de transactions en moins : le panier moyen par réservation est passé de 137 $ à 158 $, porté par les chalets (+24 %)."),
  dataTable(
    ["Catégorie de revenus (avant taxes)", "2025", "2026", "Variation"],
    [
      ["Terrains de camping", money(837255.66), money(reel.terrains), "−5,4 %"],
      ["Chalets et chambres", money(400868.16), money(reel.chalets), "+24,2 %"],
      ["Cabanas prêt-à-camper", money(195575.47), money(reel.cabanas), "+1,8 %"],
      ["Terrains saisonniers", money(19731.89), money(reel.saisonniers), "+119,0 %"],
      ["Frais d'administration", money(173.95), money(0), "—"],
      ["Total des revenus d'hébergement", money(M.reel_2025_total), money(M.reel_2026_total), "+5,4 %"],
      ["Nombre de transactions", "10 587", "9 670", "−8,7 %"],
      ["Revenu moyen par transaction", "137,30 $", "158,41 $", "+15,4 %"],
    ],
    [3800, 1950, 1950, 1948], { totalRows: [5] },
  ),
  spacer(),
  callout("Note sur les données historiques", [
    "Les revenus ci-dessus proviennent des rapports du système de réservation (par date de transaction). Ils excluent la restauration, les activités et les concessions, estimées à environ 197 000 $ en 2026 selon le budget interne. Les états financiers vérifiés ou de mission d'examen des trois derniers exercices sont fournis à l'annexe A et font foi.",
  ], GOLD),
);

// --- 3. Le projet -----------------------------------------------------------------------------
const proj = M.projets;
const phaseRows = [];
["Phase 1", "Phase 2"].forEach((ph) => {
  const items = proj.filter((p) => p[0] === ph);
  phaseRows.push([ph === "Phase 1" ? "Phase 1 — Hiver et printemps 2027 (ouverture saison 2027)" : "Phase 2 — Automne 2027 et printemps 2028 (ouverture saison 2028)", "", ""]);
  items.forEach((p) => phaseRows.push([p[1], ph, money(p[2])]));
  phaseRows.push(["Sous-total " + ph.toLowerCase(), "", money(items.reduce((a, p) => a + p[2], 0))]);
});
phaseRows.push(["Total des projets de développement", "", money(M.emplois[0][1])]);
children.push(
  H1("3. Le projet : un centre de villégiature quatre saisons"),
  LEAD("Huit composantes, deux phases, dix-huit mois : doubler la capacité en hébergement quatre saisons et ajouter des revenus de restauration, de spa et d'événements."),
  H2("3.1 Objectif"),
  P("Rendre le site accessible à l'année et passer d'un camping estival à un centre récréotouristique complet. Le projet répond à deux constats : la capacité d'hébergement est saturée en été, et les actifs (piscine, bâtiments, terrain) sont sous-utilisés de novembre à avril. Chaque composante a été choisie pour l'un de ces deux leviers : ajouter de la capacité vendable ou allonger la saison."),
  H2("3.2 Composantes et coûts"),
  dataTable(["Composante", "Phase", "Coût estimé"], phaseRows, [6200, 1400, 2048], { numericFrom: 2, subheadRows: [0, 7], totalRows: [6, 11, 12] }),
  spacer(),
  P("Les estimations proviennent de la direction et seront appuyées par des soumissions d'entrepreneurs (annexe C). Une contingence de 5 % et des honoraires professionnels de 175 000 $ s'ajoutent au budget de financement (section 8).", { italics: true, color: GREY, size: 19 }),
  H2("3.3 Description des composantes"),
  H3("Hôtel : de 6 à 17 chambres, ouvert douze mois"),
  P("Rénovation et agrandissement du bâtiment hôtelier existant pour porter la capacité à 17 chambres isolées et chauffées, avec une salle de conférence attenante. L'hôtel devient la pierre angulaire de l'exploitation hivernale : clientèle de couples, de groupes et d'entreprises (réunions, retraites, mariages hors saison)."),
  H3("Restaurant Madera et salle de conférence"),
  P("Aménagement d'un restaurant de cuisine cubaine et latino-américaine dans l'hôtel, ouvert à la clientèle du site et au public régional. Le restaurant, le café Cubano et le Mojito bar forment un pôle de restauration qui capte une part des dépenses des invités aujourd'hui réalisées hors site."),
  H3("Villas et chalets quatre saisons"),
  P("Achèvement des 13 villas en construction et mise à niveau des 16 chalets existants (isolation, chauffage, plomberie hivernale) pour une location à l'année. Ces 29 unités constituent l'offre d'hébergement privé haut de gamme du site."),
  H3("Terrains saisonniers"),
  P("Aménagement de 35 terrains saisonniers additionnels (services, électricité, voirie), pour un total de 70. Les saisonniers procurent des revenus récurrents encaissés avant la saison, ce qui stabilise la trésorerie printanière."),
  H3("Piscine et spa quatre saisons"),
  P("Construction d'une piscine intérieure-extérieure chauffée et d'un spa de type nordique (bains chauds, sauna, aires de détente). Le spa attire une clientèle de jour en toute saison et prolonge la durée des séjours en hiver. Il s'agit de l'investissement le plus important du projet et du principal moteur de fréquentation hivernale."),
  H3("Amphithéâtre et sentier lumineux"),
  P("L'amphithéâtre extérieur accueille spectacles, soirées cubaines et festivals ; le sentier lumineux, un parcours nocturne illuminé exploité d'octobre à avril, crée une raison de visiter le site en basse saison."),
  spacer(),
  twoPlaceholders("Rendu ou esquisse : hôtel 17 chambres et restaurant Madera", "Rendu ou esquisse : piscine et spa quatre saisons", 3300, "projet_hotel", "projet_spa"),
  spacer(),
  placeholder("Plan d'aménagement du site : localisation des phases 1 et 2 (hôtel, villas, terrains saisonniers, spa, amphithéâtre, sentier)", 5600, CONTENT_W, "plan_site"),
  H2("3.4 Échéancier de réalisation"),
  ...figure("echeancier.png", 6.5, "Figure 1 – Échéancier des phases 1 et 2"),
  P("La phase 1 est réalisée en basse saison pour ne pas perturber l'exploitation estivale 2027. La phase 2 démarre à la fermeture de la saison 2027 et ouvre pour l'été 2028. La structure de financement proposée prévoit un moratoire de capital de 18 mois aligné sur cette séquence."),
  H2("3.5 Permis, réglementation et fournisseurs"),
  ...bullets([
    "Conformité au zonage municipal de Maricourt et, le cas échéant, autorisations de la CPTAQ pour les usages en zone agricole : [statut à confirmer, documents à l'annexe D].",
    "Permis de construction, certificat d'autorisation environnementale (traitement des eaux, prélèvement d'eau) : [statut à confirmer].",
    "Permis de restauration (MAPAQ) et permis d'alcool (RACJ) pour le restaurant et les bars : [à obtenir avant l'ouverture].",
    "Entrepreneur général et professionnels (architecte, ingénieur) : [noms et soumissions à l'annexe C].",
  ]),
);

// --- 4. Analyse du marché ---------------------------------------------------------------------
children.push(
  H1("4. Analyse du marché"),
  LEAD("Le camping et le plein air demeurent parmi les segments les plus dynamiques du tourisme québécois ; la demande se déplace vers le confort, les expériences et les quatre saisons."),
  H2("4.1 L'industrie du camping et de la villégiature au Québec"),
  P("Le camping est une activité de masse au Québec : plusieurs centaines d'établissements et plus de 200 000 emplacements accueillent chaque été des centaines de milliers de ménages. Depuis 2020, la fréquentation s'est maintenue à des niveaux élevés et la clientèle s'est rajeunie et diversifiée. Trois tendances structurent l'industrie :"),
  ...bullets([
    [run("Le confort et le prêt-à-camper : ", { bold: true }), run("cabanas, chalets et unités tout équipées croissent plus vite que le camping traditionnel et commandent des tarifs deux à trois fois supérieurs.")],
    [run("L'expérience et l'animation : ", { bold: true }), run("les clients choisissent un lieu pour ce qu'ils y vivront (piscine, spectacles, thématique) autant que pour l'hébergement.")],
    [run("Les quatre saisons : ", { bold: true }), run("spas nordiques, sentiers illuminés et hébergements chauffés ont créé un marché hivernal de proximité qui n'existait pas il y a dix ans.")],
  ]),
  P("[Insérer les statistiques les plus récentes de Camping Québec, de l'Institut de la statistique du Québec et de Tourisme Cantons-de-l'Est : nombre d'établissements, taux d'occupation moyen, dépenses touristiques régionales.]", { italics: true, color: GREY, size: 19 }),
  H2("4.2 La région des Cantons-de-l'Est"),
  P("Les Cantons-de-l'Est comptent parmi les régions touristiques les plus fréquentées du Québec, à moins de deux heures de Montréal et à proximité de Sherbrooke, de Granby et de la frontière américaine. La région est reconnue pour ses spas, ses vignobles, ses stations de ski et ses lacs, ce qui en fait une destination quatre saisons établie. Maricourt se situe au cœur de ce bassin, à distance de route d'environ 4,5 millions de personnes."),
  placeholder("Carte de localisation : Maricourt, distances routières depuis Montréal, Sherbrooke, Drummondville, Granby et la frontière", 3000, CONTENT_W, "carte"),
  H2("4.3 Clientèle cible"),
  dataTable(
    ["Segment", "Profil", "Offre principale", "Saison"],
    [
      ["Familles", "Ménages avec enfants, rayon de 2 heures", "Terrains, cabanas, chalets, piscine, animation", "Été"],
      ["Couples et groupes d'amis", "25 à 55 ans, séjours courts", "Villas, hôtel, spa, restaurant, spectacles", "4 saisons"],
      ["Saisonniers", "Retraités et familles, fidèles", "Terrains saisonniers (70)", "Mai à octobre"],
      ["Entreprises et groupes", "Réunions, retraites, mariages", "Hôtel, salle de conférence, restaurant", "Automne à printemps"],
      ["Communauté cubaine et latino", "Diaspora du Grand Montréal", "Événements, festivals, restauration", "4 saisons"],
      ["Clientèle de jour", "Résidents de la région", "Spa, restaurant, sentier lumineux", "4 saisons"],
    ],
    [2000, 2600, 3300, 1748], { numericFrom: 99 },
  ),
  H2("4.4 Concurrence"),
  P("Aucun établissement québécois n'offre une thématique cubaine intégrée. La concurrence est donc indirecte et se répartit en trois groupes."),
  dataTable(
    ["Groupe", "Exemples (à compléter)", "Forces", "Notre avantage"],
    [
      ["Campings familiaux de l'Estrie et de la Montérégie", "[Nom, municipalité, nombre de sites]", "Prix, proximité, fidélité", "Thématique, animation, piscine centrale, hébergement varié"],
      ["Centres de villégiature et spas", "[Nom, municipalité]", "Notoriété, offre spa", "Rapport qualité-prix, ambiance festive, capacité de groupe"],
      ["Hôtels et auberges de la région", "[Nom, municipalité]", "Confort, réseau de distribution", "Expérience immersive, activités sur place, restauration thématique"],
    ],
    [2500, 2300, 2300, 2548], { numericFrom: 99 },
  ),
  H2("4.5 Positionnement et avantages concurrentiels"),
  ...bullets([
    [run("Un concept protégé par sa singularité : ", { bold: true }), run("dix ans de notoriété et une clientèle fidèle, difficilement reproductibles.")],
    [run("Un site de 263 acres : ", { bold: true }), run("l'espace pour croître sans acquérir de terrain.")],
    [run("Une demande excédentaire : ", { bold: true }), run("le site affiche complet ; l'ajout de capacité se vend à la clientèle existante.")],
    [run("Un portefeuille de revenus diversifié après le projet : ", { bold: true }), run("hébergement, restauration, spa, événements et saisonniers.")],
  ]),
);

// --- 5. Stratégie de commercialisation --------------------------------------------------------------
children.push(
  H1("5. Stratégie de commercialisation"),
  LEAD("Vendre d'abord la nouvelle capacité à la clientèle existante, puis conquérir les marchés de l'hiver et des groupes."),
  H2("5.1 Positionnement"),
  P("« Cuba à 90 minutes de Montréal, douze mois par année. » Le Complexe Havana se positionne comme une destination d'évasion accessible, festive et familiale, à un prix inférieur à celui des centres de villégiature haut de gamme de la région, avec une expérience qu'aucun concurrent n'offre."),
  H2("5.2 Offre et tarification"),
  dataTable(
    ["Produit", "Tarif de référence An 1", "Indexation", "Base de comparaison"],
    [
      ["Terrain de camping", "90 $ / nuit", "3 % par année", "Campings 3 services de la région"],
      ["Terrain saisonnier", "3 650 $ / saison", "3 % par année", "Saisonniers de l'Estrie"],
      ["Chalet 4 saisons", "235 $ été, 210 $ hiver", "3 % par année", "Chalets locatifs régionaux"],
      ["Villa", "275 $ été, 245 $ hiver", "3 % par année", "Hébergement haut de gamme régional"],
      ["Chambre d'hôtel", "190 $ / nuit", "3 % par année", "Hôtels 3 étoiles de l'Estrie"],
      ["Cabana prêt-à-camper", "200 $ / nuit", "3 % par année", "Prêt-à-camper des parcs et campings"],
      ["Accès spa (journée)", "55 $", "3 % par année", "Spas nordiques régionaux (65 $ à 80 $)"],
    ],
    [2500, 2500, 1700, 2948], { numericFrom: 99 },
  ),
  H2("5.3 Distribution et réservation"),
  ...bullets([
    "Réservation en ligne par reservationcamping.ca (Solutions Web Pixum), déjà en place et utilisé pour près de 10 000 transactions par année.",
    "Ajout de l'hôtel et des villas aux plateformes de distribution hôtelière (Booking, Expedia, Airbnb) pour la clientèle hors Québec et hors saison.",
    "Forfaits : hébergement + spa, hébergement + spectacle, escapade hivernale, séjours corporatifs.",
    "Ventes de groupes et corporatives par une ressource dédiée à partir de l'An 1.",
  ]),
  H2("5.4 Promotion"),
  ...bullets([
    [run("Marketing numérique : ", { bold: true }), run("réseaux sociaux (base d'abonnés existante), publicité ciblée par rayon géographique, infolettre à la clientèle passée, référencement.")],
    [run("Relations médias et influenceurs : ", { bold: true }), run("lancement de l'hôtel, du spa et du sentier lumineux ; accueil de créateurs de contenu.")],
    [run("Partenariats : ", { bold: true }), run("Tourisme Cantons-de-l'Est, Camping Québec, associations de la communauté cubaine et latino-américaine, entreprises régionales pour les événements corporatifs.")],
    [run("Événements signature : ", { bold: true }), run("festival cubain estival, soirées à l'amphithéâtre, programmation hivernale du sentier lumineux.")],
  ]),
  P("Le budget de commercialisation est fixé à 3,5 % des revenus les deux premières années, puis à 3 %, conformément aux pratiques de l'industrie de l'hébergement."),
  H2("5.5 Objectifs commerciaux"),
  dataTable(
    ["Indicateur", ...yearHeads],
    [
      ["Occupation estivale des chalets", "58 %", "62 %", "65 %", "67 %", "68 %"],
      ["Occupation hivernale des chalets", "15 %", "25 %", "30 %", "33 %", "35 %"],
      ["Occupation annuelle de l'hôtel", "40 %", "45 %", "52 %", "55 %", "57 %"],
      ["Terrains saisonniers loués", "30", "52", "64", "70", "70"],
      ["Entrées au spa", "—", "4 000", "7 500", "9 000", "9 500"],
      ["Revenus de restauration / hébergement", "16 %", "21 %", "24 %", "25 %", "26 %"],
    ],
    [3400, 1250, 1250, 1250, 1250, 1248],
  ),
  spacer(),
  placeholder("Exemples de matériel promotionnel : visuels de campagne, affiche du festival cubain, capture du site web", 4200, CONTENT_W, "promo"),
);

// --- 6. Plan d'exploitation -------------------------------------------------------------------------
children.push(
  H1("6. Plan d'exploitation"),
  LEAD("Une organisation qui passe de 6 à 12 mois d'activité : effectifs, systèmes et fournisseurs sont dimensionnés en conséquence."),
  H2("6.1 Organisation des opérations"),
  P("Les opérations se répartissent en cinq services : hébergement et réservations, restauration et bars, spa et activités, entretien et infrastructures, administration. Chaque service est dirigé par un responsable qui relève de la direction générale. La saison estivale (mai à octobre) demeure la période de pointe ; l'hiver est exploité avec une équipe réduite centrée sur l'hôtel, les chalets, le spa, le restaurant et le sentier lumineux."),
  H2("6.2 Ressources humaines"),
  dataTable(
    ["Catégorie", "Actuel (été)", "Actuel (hiver)", "Projeté (été)", "Projeté (hiver)"],
    [
      ["Direction et gestion", "1 à 2", "1", "6", "6"],
      ["Employés horaires (accueil, entretien, animation, restauration)", "15 à 20", "0", "25 à 30", "12 à 15"],
      ["Employés logés sur le site", "5", "3", "8", "5"],
      ["Total approximatif", "20 à 27", "4", "40 à 45", "23 à 26"],
    ],
    [3800, 1450, 1450, 1450, 1498], { totalRows: [3] },
  ),
  P("La masse salariale représente 36 % des revenus en An 1 et 32 % en An 5, dans la fourchette observée dans l'hébergement de villégiature. Le logement sur place, un avantage concurrentiel pour le recrutement en région, est maintenu. Les besoins en main-d'œuvre étrangère temporaire ou en partenariats avec des écoles hôtelières seront évalués pour la restauration."),
  H2("6.3 Systèmes et fournisseurs"),
  ...bullets([
    "Réservations et facturation : reservationcamping.ca (Solutions Web Pixum), rapports de revenus par catégorie et par période.",
    "Point de vente restauration, bars et boutique : [système à sélectionner], intégré à la comptabilité.",
    "Comptabilité et paie : [firme comptable externe], états financiers annuels et rapports trimestriels au prêteur.",
    "Fournisseurs : alimentation et boissons (distributeurs régionaux), propane, produits d'entretien, traitement des eaux.",
    "Partenaires de concessions à revenus partagés (50/50) : pizza, churros, triporteur, jeux et autres.",
  ]),
  H2("6.4 Entretien, sécurité et environnement"),
  ...bullets([
    "Usine de traitement des eaux sur le site ; capacité à confirmer par l'ingénieur pour l'exploitation douze mois.",
    "Programme d'entretien préventif des bâtiments, de la piscine, du spa et des véhicules ; budget de 4 % des revenus plus 2 % de dépenses en immobilisations de maintien.",
    "Assurances des bâtiments, responsabilité civile et véhicules révisées à la livraison de chaque phase.",
    "Pratiques durables : gestion des déchets, efficacité énergétique des nouveaux bâtiments, protection des milieux naturels du site.",
  ]),
);

// --- 7. Équipe de direction ------------------------------------------------------------------------------
children.push(
  H1("7. Équipe de direction"),
  LEAD("Une direction renouvelée en 2025, appuyée sur la famille fondatrice et sur des conseillers externes."),
  dataTable(
    ["Nom", "Poste", "Expérience et responsabilités dans le projet"],
    [
      ["[Nom]", "Direction générale", "[Parcours, années d'expérience en hébergement ou en gestion ; responsable du financement et de la réalisation du projet]"],
      ["[Nom]", "Direction des opérations", "[Parcours ; hébergement, entretien, saisonniers]"],
      ["[Nom]", "Direction restauration et événements", "[Parcours ; restaurant Madera, bars, amphithéâtre]"],
      ["[Nom]", "Direction finances et administration", "[Parcours ; comptabilité, rapports au prêteur, paie]"],
      ["[Nom]", "Ventes et marketing", "[Parcours ; groupes, corporatif, numérique]"],
      ["Famille Perrier", "Fondateurs et actionnaires", "Vision du concept, relations avec la clientèle, continuité"],
    ],
    [1800, 2600, 5248], { numericFrom: 99 },
  ),
  spacer(),
  placeholder("Organigramme de l'entreprise (direction générale, cinq services, responsables)", 2600, CONTENT_W, "organigramme"),
  spacer(),
  H2("Conseillers externes"),
  ...bullets([
    "Comptable : [firme]",
    "Conseiller juridique : [firme]",
    "Architecte et ingénieur : [firmes]",
    "Évaluateur agréé : [firme ayant produit l'évaluation de 28 M$ en 2025]",
  ]),
  P("Les curriculum vitæ des membres de la direction sont présentés à l'annexe E.", { italics: true, color: GREY, size: 19 }),
);

// --- 8. Plan financier --------------------------------------------------------------------------------------
const emploisRows = M.emplois.map((e) => [e[0], money(e[1]), pct(e[1] / M.emplois.reduce((a, x) => a + x[1], 0))]);
const totalEmplois = M.emplois.reduce((a, x) => a + x[1], 0);
emploisRows.push(["Total des emplois", money(totalEmplois), "100 %"]);
const sourcesRows = M.sources.map((s) => [s[0], money(s[1]), pct(s[1] / totalEmplois)]);
sourcesRows.push(["Total des sources", money(totalEmplois), "100 %"]);

const revRows = M.lignes.map(([k, name]) => [name, ...revLine(k)]);
revRows.push(["Total des revenus", ...P5.map((y) => money(y.total_revenus))]);
const chRows = M.charges.map(([k, name]) => [name, ...chLine(k)]);
chRows.push(["Total des charges d'exploitation", ...P5.map((y) => money(y.total_charges))]);
const resRows = [
  ["BAIIA", ...P5.map((y) => money(y.baiia))],
  ["Marge BAIIA", ...P5.map((y) => pct(y.marge_baiia))],
  ["Amortissement", ...P5.map((y) => money(y.amortissement))],
  ["Intérêts sur la dette", ...P5.map((y) => money(y.interets))],
  ["Bénéfice avant impôts", ...P5.map((y) => money(y.bai))],
  ["Impôts sur le revenu (20 %)", ...P5.map((y) => money(y.impots))],
  ["Bénéfice net", ...P5.map((y) => money(y.benefice_net))],
];
const cfRows = [
  ["BAIIA", ...P5.map((y) => money(y.baiia))],
  ["Moins : impôts", ...P5.map((y) => money(-y.impots))],
  ["Moins : intérêts", ...P5.map((y) => money(-y.interets))],
  ["Moins : remboursement de capital", ...P5.map((y) => money(-y.capital))],
  ["Moins : immobilisations de maintien (2 %)", ...P5.map((y) => money(-y.capex_maintien))],
  ["Flux de trésorerie disponible", ...P5.map((y) => money(y.flux_libre))],
  ["Trésorerie cumulée (depuis l'An 1)", ...P5.map((y) => money(y.tresorerie_cumulee))],
];
const debtRows = M.dette.map((d) => [`An ${d.an}`, money(d.interets), money(d.capital), money(d.service), money(d.solde_fin)]);
const ratioRows = [
  ["Ratio de couverture du service de la dette (BAIIA / service)", ...P5.map((y) => ratio(y.dscr))],
  ["Ratio de couverture des intérêts (BAIIA / intérêts)", ...P5.map((y) => ratio(y.couverture_interets))],
  ["Dette à terme / BAIIA", ...P5.map((y) => ratio(y.solde_dette / y.baiia, 1))],
  ["Marge BAIIA", ...P5.map((y) => pct(y.marge_baiia))],
  ["Marge nette", ...P5.map((y) => pct(y.benefice_net / y.total_revenus))],
  ["Ratio prêt-valeur (solde / 28 M$)", ...P5.map((y) => pct(y.solde_dette / M.valeur_site, 0))],
];
const sensRows = M.sensibilite.map((s) => [s.scenario, ratio(s.dscr_an2), ratio(s.dscr_an3), ratio(s.dscr_an5)]);
const W6 = [2900, 1350, 1350, 1350, 1350, 1348];

children.push(
  H1("8. Plan financier"),
  LEAD("Des projections bâties sur les revenus réels de 2026, des hypothèses d'occupation prudentes et une structure de financement qui respecte les ratios bancaires dès la première année."),
  H2("8.1 Hypothèses clés"),
  dataTable(
    ["Hypothèse", "Valeur", "Justification"],
    [
      ["Point de départ", "Revenus réels 2026 : " + money(M.reel_2026_total), "Rapports du système de réservation"],
      ["Indexation des tarifs", "3 % par année", "Inflation et pratique de l'industrie"],
      ["Occupation hôtel (annuelle)", "40 % An 1 → 57 % An 5", "Sous la moyenne des hôtels de l'Estrie ; montée en régime graduelle"],
      ["Occupation chalets et villas (été)", "50 % à 58 % An 1 → 65 % à 68 % An 5", "Historique 2026 : environ 55 % à 60 %"],
      ["Occupation chalets et villas (hiver)", "12 % à 15 % An 1 → 32 % à 35 % An 5", "Nouveau marché ; hypothèse prudente"],
      ["Restauration", "16 % An 1 → 26 % An 5 des revenus d'hébergement", "Norme des centres de villégiature : 25 % à 35 %"],
      ["Coût des ventes restauration", "33 %", "Norme de l'industrie : 30 % à 35 %"],
      ["Salaires et charges sociales", "36 % An 1 → 32 % An 5 des revenus", "Hébergement de villégiature : 30 % à 38 %"],
      ["Énergie", "275 k$ An 1 → 450 k$ An 5", "Chauffage des bâtiments, piscine et spa"],
      ["Entretien et immobilisations de maintien", "4 % + 2 % des revenus", "Pratique bancaire"],
      ["Amortissement comptable", "150 k$ existant + 4 % des nouveaux actifs", "Hypothèse ; à aligner sur les états financiers"],
      ["Impôts", "20 % combiné", "Taux moyen petite entreprise et taux général"],
      ["Prêt à terme", money(M.pret) + " à " + pct(M.taux, 1) + ", 25 ans", "Moratoire de capital de 18 mois pendant la construction"],
    ],
    [2900, 3100, 3648], { numericFrom: 99, fontSize: 18 },
  ),
  H2("8.2 Coût du projet et financement"),
  P("Le budget de financement regroupe les projets de développement, la contingence, les honoraires, les frais et le refinancement de la dette existante afin de consolider l'ensemble de la dette dans un seul prêt hypothécaire de premier rang."),
  dataTable(["Emplois", "Montant", "Part"], emploisRows, [5600, 2200, 1848], { totalRows: [emploisRows.length - 1] }),
  spacer(120),
  dataTable(["Sources", "Montant", "Part"], sourcesRows, [5600, 2200, 1848], { totalRows: [sourcesRows.length - 1] }),
  ...figure("sources_emplois.png", 6.2, "Figure 2 – Emplois et sources de financement"),
  H3("Structure de financement proposée"),
  dataTable(
    ["Modalité", "Proposition"],
    [
      ["Type", "Prêt à terme hypothécaire, premier rang"],
      ["Montant", money(M.pret)],
      ["Taux d'intérêt (hypothèse)", pct(M.taux, 1) + " fixe ou variable"],
      ["Amortissement", "25 ans"],
      ["Moratoire de capital", "18 mois (période de construction, jusqu'à l'ouverture de la phase 2)"],
      ["Paiement mensuel après moratoire", money(M.paiement_mensuel)],
      ["Décaissements", "Refinancement à la clôture ; projets par avancement des travaux sur présentation des factures"],
      ["Garanties", "Hypothèque de premier rang sur le site (valeur estimée 28 M$), hypothèque mobilière sur les équipements, cession d'assurances, [cautionnement des actionnaires : à confirmer]"],
      ["Engagements financiers proposés", "DSCR minimal de 1,25 x à compter de l'An 2 ; états financiers annuels révisés ; rapports trimestriels"],
    ],
    [3000, 6648], { numericFrom: 99 },
  ),
  H2("8.3 État des résultats prévisionnels"),
  ...figure("revenus.png", 6.5, "Figure 3 – Revenus par source, 2026 (réel) et An 1 à An 5"),
  dataTable(["Revenus", ...yearHeads], revRows, W6, { totalRows: [revRows.length - 1], fontSize: 18 }),
  spacer(120),
  dataTable(["Charges d'exploitation", ...yearHeads], chRows, W6, { totalRows: [chRows.length - 1], fontSize: 18 }),
  spacer(120),
  dataTable(["Résultats", ...yearHeads], resRows, W6, { boldRows: [0, 6], fontSize: 18 }),
  spacer(),
  ...figure("repartition.png", 6.2, "Figure 4 – Répartition des revenus : 2026 (réel) et An 5"),
  H2("8.4 Flux de trésorerie et service de la dette"),
  dataTable(["Flux de trésorerie", ...yearHeads], cfRows, W6, { boldRows: [5, 6], fontSize: 18 }),
  spacer(120),
  dataTable(["Échéancier du prêt", "Intérêts", "Capital", "Service total", "Solde en fin d'année"], debtRows, [2000, 1900, 1900, 1900, 1948]),
  ...figure("dscr.png", 6.5, "Figure 5 – BAIIA, service de la dette et ratio de couverture"),
  H2("8.5 Ratios financiers"),
  dataTable(["Ratio", ...yearHeads], ratioRows, W6, { boldRows: [0] }),
  spacer(),
  callout("Lecture des ratios", [
    "Le ratio de couverture du service de la dette atteint " + ratio(y1.dscr) + " en An 1 (intérêts seulement) et " + ratio(Y[2].dscr) + " en An 2, première année de remboursement de capital, puis dépasse 1,75 x à compter de l'An 3. Le ratio prêt-valeur de " + pct(M.ltv, 0) + " à la clôture et la dette à terme ramenée à " + ratio(y5.solde_dette / y5.baiia, 1) + " le BAIIA en An 5 situent le dossier dans les normes de prudence des institutions financières pour l'hébergement touristique.",
  ]),
  H2("8.6 Analyse de sensibilité"),
  P("Le tableau suivant mesure le ratio de couverture si les revenus étaient inférieurs aux projections, en supposant que 60 % des charges sont variables et que les charges fixes demeurent inchangées."),
  dataTable(["Scénario", "DSCR An 2", "DSCR An 3", "DSCR An 5"], sensRows, [3600, 2000, 2000, 2048], { boldRows: [0] }),
  spacer(),
  P("Même avec des revenus inférieurs de 15 % aux projections, le ratio de couverture demeure au-dessus de 1,25 x dès l'An 3 et au-dessus de 1,65 x en An 5. L'An 2 est l'année charnière : la trésorerie dégagée en An 1, la mise de fonds et la valeur du site couvrent ce risque de transition. La direction propose en outre de constituer une réserve de service de la dette équivalant à trois mois de paiements à même les flux de l'An 1."),
  H2("8.7 Seuil de rentabilité"),
  P("À maturité (An 3), les charges fixes (salaires de base, énergie, assurances, taxes, loyers, administration, soit environ 40 % des charges) et le service de la dette totalisent environ " + moneyM(Y[3].total_charges * 0.4 + Y[3].service_dette, 2) + ". Avec une marge sur charges variables d'environ 59 %, le seuil de rentabilité en trésorerie se situe autour de " + moneyM((Y[3].total_charges * 0.4 + Y[3].service_dette) / (1 - (Y[3].total_charges * 0.6 / Y[3].total_revenus)), 1) + " de revenus, soit " + pct(((Y[3].total_charges * 0.4 + Y[3].service_dette) / (1 - (Y[3].total_charges * 0.6 / Y[3].total_revenus))) / Y[3].total_revenus, 0) + " des revenus projetés de l'An 3."),
  H2("8.8 États financiers historiques"),
  P("Les états financiers des exercices 2024, 2025 et 2026, l'état de la dette existante et le rapport d'évaluation du site (28 M$, 2025) sont présentés aux annexes A et B. [Insérer un tableau sommaire : revenus, BAIIA, bénéfice net, actif total, dette et avoir des actionnaires pour les trois derniers exercices.]", { italics: true, color: GREY, size: 19 }),
);

// --- 9. Risques ---------------------------------------------------------------------------------------------------
children.push(
  H1("9. Risques et mesures d'atténuation"),
  LEAD("Les principaux risques sont identifiés, mesurés et couverts par des mesures concrètes ou par la structure de financement."),
  dataTable(
    ["Risque", "Probabilité / impact", "Mesures d'atténuation"],
    [
      ["Dépassement des coûts ou retard de construction", "Moyen / élevé", "Contingence de 5 %, soumissions fermes, phasage en basse saison, moratoire de capital de 18 mois, décaissements par avancement"],
      ["Montée en régime plus lente de l'hiver (hôtel, chalets, spa)", "Moyen / moyen", "Hypothèses d'occupation hivernale prudentes (12 % à 35 %), sensibilité à −15 % couverte dès l'An 3, réserve de service de la dette"],
      ["Météo et saison estivale défavorable", "Moyen / moyen", "Diversification des revenus (saisonniers encaissés d'avance, hôtel, spa, restauration), assurance pertes d'exploitation"],
      ["Pénurie de main-d'œuvre", "Élevé / moyen", "Logement des employés sur le site, recrutement à l'année (postes stables), partenariats avec écoles, travailleurs étrangers temporaires"],
      ["Hausse des taux d'intérêt", "Moyen / moyen", "Option de taux fixe sur 5 ans ; une hausse de 1 point réduit le DSCR An 3 d'environ 0,10 x"],
      ["Réglementation (zonage, environnement, permis)", "Faible / élevé", "Vérifications préalables avant la clôture, professionnels mandatés, conditions de décaissement"],
      ["Dépendance à la direction", "Faible / moyen", "Équipe de cinq responsables, structure familiale, assurance personnes clés"],
      ["Concurrence accrue (spas, glamping)", "Moyen / faible", "Concept unique, clientèle fidèle, prix compétitifs, notoriété de dix ans"],
    ],
    [2900, 1700, 5048], { numericFrom: 99, fontSize: 18 },
  ),
);

// --- 10. Conclusion -------------------------------------------------------------------------------------------------
children.push(
  H1("10. Conclusion et demande"),
  LEAD("Un actif de 28 M$, une demande démontrée et un plan phasé : le Complexe Havana demande un prêt de " + moneyM(M.pret, 1) + " pour devenir une destination quatre saisons."),
  P("Depuis 2015, le Complexe Havana a bâti un concept que personne d'autre n'offre au Québec et une clientèle qui remplit le site chaque été. Le projet présenté ici ne repose pas sur la conquête d'un marché incertain : il répond à une demande existante en ajoutant de la capacité et en ouvrant le site toute l'année."),
  P("Les projections, construites à partir des revenus réels de 2026 et d'hypothèses d'occupation prudentes, font passer les revenus de " + moneyM(Y[0].total_revenus, 1) + " à " + moneyM(y5.total_revenus, 1) + " en cinq ans, avec une marge BAIIA de " + pct(y5.marge_baiia, 0) + " et un ratio de couverture du service de la dette de " + ratio(y5.dscr) + " en An 5. Le ratio prêt-valeur de " + pct(M.ltv, 0) + " procure au prêteur une sécurité exceptionnelle."),
  callout("Demande", [
    [run("Prêt à terme hypothécaire de premier rang de " + money(M.pret), { bold: true, size: 20 })],
    "Amortissement de 25 ans, moratoire de capital de 18 mois, décaissements par avancement des travaux.",
    "Mise de fonds des propriétaires et investisseurs privés : " + money(totalEmplois - M.pret) + ".",
    "Clôture souhaitée : [mois et année], pour un début des travaux de la phase 1 à l'automne 2026 ou à l'hiver 2027.",
  ]),
  spacer(200),
  P("Nous remercions l'institution de l'attention portée à ce dossier et demeurons disponibles pour une visite du site et toute information complémentaire."),
  spacer(400),
  P("_______________________________", { after: 0 }),
  P("[Nom], direction générale", { after: 0 }),
  P("Complexe Havana", { after: 0 }),
  P("[Téléphone] · [Courriel]"),
);

// --- Annexes ---------------------------------------------------------------------------------------------------
children.push(
  H1("Annexes"),
  P("Les documents suivants accompagnent le plan d'affaires et sont fournis dans un cahier distinct ou en pièces jointes."),
  dataTable(
    ["Annexe", "Contenu", "Statut"],
    [
      ["A", "États financiers des exercices 2024, 2025 et 2026 ; état de la dette existante", "[À insérer]"],
      ["B", "Rapport d'évaluation du site (28 M$, 2025)", "[À insérer]"],
      ["C", "Soumissions des entrepreneurs et estimations détaillées par composante", "[À insérer]"],
      ["D", "Plans, permis, confirmations de zonage et autorisations", "[À insérer]"],
      ["E", "Curriculum vitæ des membres de la direction", "[À insérer]"],
      ["F", "Photos du site, rendus et plan d'aménagement", "[À insérer]"],
      ["G", "Rapports de revenus du système de réservation, saisons 2025 et 2026", "Disponibles"],
      ["H", "Modèle financier détaillé (hypothèses et calculs mensuels)", "Disponible sur demande"],
      ["I", "Lettres d'appui (municipalité, Tourisme Cantons-de-l'Est, partenaires)", "[À obtenir]"],
    ],
    [1000, 6600, 2048], { numericFrom: 99 },
  ),
  spacer(),
  ...gallery(PHOTOS.galerie, "Annexe F – Galerie photos : hébergements, piscine, animation, restauration, vues du site en quatre saisons"),
);

// =====================================================================================
// DOCUMENT
// =====================================================================================
const header = new Header({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    border: { bottom: { color: MID, size: 4, style: BorderStyle.SINGLE, space: 4 } },
    children: [run("Complexe Havana", { bold: true, size: 17, color: NAVY }), run("\tPlan d'affaires 2027 – 2031", { size: 17, color: GREY })],
  })],
});
const footer = new Footer({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    children: [run("Confidentiel", { size: 16, color: GREY }), new TextRun({ children: ["\tPage ", PageNumber.CURRENT], font: FONT, size: 16, color: GREY })],
  })],
});

const doc = new Document({
  creator: "Complexe Havana",
  title: "Plan d'affaires 2027-2031 – Complexe Havana",
  description: "Demande de financement",
  styles: {
    default: { document: { run: { font: FONT, size: 21, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 40, bold: true, color: NAVY }, paragraph: { spacing: { before: 0, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 27, bold: true, color: NAVY }, paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: TEAL }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "puces", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } }, run: { color: TEAL } } }] },
      { reference: "numeros", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { color: NAVY, bold: true } } }] },
    ],
  },
  features: { updateFields: true },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: 1200, bottom: 1100, left: MARGIN, right: MARGIN, header: 560, footer: 560 } } },
    headers: { default: header },
    footers: { default: footer },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUTPUT, buf);
  console.log("Écrit :", OUTPUT, Math.round(buf.length / 1024), "ko");
});
