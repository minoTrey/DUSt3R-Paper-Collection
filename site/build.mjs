import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import MarkdownIt from "markdown-it";
import texmath from "markdown-it-texmath";
import katex from "katex";
import { loadThumbnails, thumbnailFor } from "./thumbnails.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
function arg(name, fallback) {
  const at = args.indexOf(name);
  return at < 0 ? fallback : args[at + 1];
}
export function basePath(value) {
  if (
    !value ||
    !value.startsWith("/") ||
    value.includes("..") ||
    value.includes("//") ||
    /[?#\\]/.test(value)
  )
    throw new Error("Base path must be an absolute URL path without traversal, query or fragment.");
  return value.replace(/\/+$/, "") + "/";
}
const base = basePath(arg("--base", "/DUSt3R-Paper-Collection/"));
const folder = arg("--out", "_site");
if (!/^_site(?:-[a-z0-9-]+)?$/.test(folder))
  throw new Error("Output must be a direct workspace folder named _site or _site-<name>.");
const output = path.resolve(root, folder);
if (path.dirname(output) !== root || output === root) throw new Error("Unsafe build output path.");
const repo = "https://github.com/minoTrey/DUSt3R-Paper-Collection";
const escape = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
const sha = (value) => crypto.createHash("sha256").update(value).digest("hex");
const source = JSON.parse(
  execFileSync(
    process.env.PYTHON || (process.platform === "win32" ? "python" : "python3"),
    ["-X", "utf8", "tools/extract_meta.py", "--json"],
    { cwd: root, encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } },
  ),
);
const names = {
  foundation: "Foundation",
  extensions: "Model Extensions",
  reconstruction: "3D Reconstruction",
  dynamic: "Dynamic Scenes",
  "gaussian-splatting": "Gaussian Splatting",
  understanding: "Scene Understanding",
  reasoning: "Scene Reasoning",
  robotics: "Robotics",
  surveys: "Surveys & Analysis",
  pose: "Pose Estimation",
  medical: "Medical",
};
const md = new MarkdownIt({ html: true, linkify: true, typographer: false }).use(texmath, {
  engine: katex,
  delimiters: "dollars",
  katexOptions: { throwOnError: false, trust: false, output: "htmlAndMathml" },
});
const textMarkdown = new MarkdownIt({ html: true });
const plain = (value) =>
  textMarkdown
    .renderInline(value || "")
    .replace(/<[^>]*>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
const inventory = JSON.parse(
  fs.readFileSync(path.join(root, "data/paper-card-inventory.json"), "utf8"),
);
const byNote = new Map(inventory.papers.map((p) => [p.note_path, p]));
const thumbnails = loadThumbnails(root, inventory);
const canonical = new Set(source.map((p) => p.file));
const assets = new Set();
const relativeAsset = (logical) => {
  assets.add(logical);
  return base + logical;
};
function localURL(url, note) {
  if (/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(url)) return url;
  const [raw, fragment] = url.split("#");
  const logical = path.posix.normalize(
    path.posix.join(path.posix.dirname(note), decodeURI(raw || "")),
  );
  const end = fragment ? "#" + fragment : "";
  if (canonical.has(logical)) return base + "papers/" + logical.slice(5, -3) + "/" + end;
  const category = logical.match(/^docs\/([^/]+)(?:\/README\.md)?\/?$/);
  if (category && names[category[1]]) return base + "?category=" + category[1] + end;
  if (logical === "README.md" || logical === "docs/papers-list.md") return base + end;
  if (logical.startsWith("assets/")) return relativeAsset(logical) + end;
  return repo + "/blob/main/" + logical + end;
}
function renderNote(text, note) {
  // Only the duplicate presentation heading/card block is omitted from the view.
  // The Markdown source and all substantive note sections remain unchanged.
  let body = text
    .replace(/^# .+\r?\n/, "")
    .replace(/^<!-- PAPER-CARD:en -->\r?\n.*?^<!-- \/PAPER-CARD -->\r?\n/gms, "");
  let rendered = md.render(body);
  const counts = new Map();
  rendered = rendered.replace(/<h([2-6])>(.*?)<\/h\1>/gs, (_, level, title) => {
    let id = plain(title)
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s_-]/gu, "")
      .replace(/\s/g, "-");
    const count = counts.get(id) || 0;
    counts.set(id, count + 1);
    if (count) id += "-" + count;
    return `<h${level} id="${escape(id)}">${title}</h${level}>`;
  });
  rendered = rendered.replace(
    /\b(src|href)=(['"])(.*?)\2/g,
    (_, key, quote, url) =>
      `${key}=${quote}${escape(localURL(url.replace(/&amp;/g, "&"), note))}${quote}`,
  );
  rendered = rendered.replace(/<img\b/g, '<img loading="lazy" decoding="async"');
  rendered = rendered
    .replace(
      /<table>/g,
      '<div class="table-scroll" tabindex="0" aria-label="Scrollable research table"><table>',
    )
    .replace(/<\/table>/g, "</table></div>");
  return rendered;
}
const papers = source
  .map((rec) => {
    const row = byNote.get(rec.file);
    if (!row) throw new Error("Missing canonical inventory row: " + rec.file);
    const text = fs.readFileSync(path.join(root, rec.file), "utf8");
    const year = +(rec.fields.Venue?.match(/\b(20\d{2})\b/)?.[1] || 0);
    const links = [
      ...(rec.fields.Links || "").matchAll(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g),
    ].map((m) => ({ label: m[1], url: m[2] }));
    const purpose = plain(rec.fields["TL;DR"] || row.title);
    const posterBytes = fs.readFileSync(path.join(root, row.planned_card_path));
    const summaryPreview = {
      path: row.planned_card_path,
      width: posterBytes.readUInt32BE(16),
      height: posterBytes.readUInt32BE(20),
      sha256: sha(posterBytes),
      alt: `Complete visual summary for ${row.short_title}; conceptual diagrams and source qualifications remain in the original image.`,
    };

    return {
      id: row.record_id,
      title: row.title,
      shortTitle: row.short_title,
      category: rec.cat,
      categoryName: names[rec.cat],
      year,
      venue: rec.fields.Venue,
      purpose,
      authors: plain(rec.fields.Authors),
      preprint: /arxiv|preprint/i.test(rec.fields.Venue),
      url: base + "papers/" + row.record_id + "/",
      image: relativeAsset(row.planned_card_path),
      thumbnail: thumbnailFor(row.record_id, thumbnails, summaryPreview),
      summaryPreview,
      links,
      search: [row.title, purpose, rec.fields.Authors, rec.cat, names[rec.cat], rec.arxiv_id]
        .join(" ")
        .toLocaleLowerCase(),
      note: rec.file,
      noteSha256: sha(text),
      sourceIdentity: row.paper_source_identity,
      html: renderNote(text, rec.file),
    };
  })
  .sort((a, b) => b.year - a.year || a.id.localeCompare(b.id, "en"));
if (
  !papers.length ||
  papers.length !== inventory.total_papers ||
  new Set(papers.map((p) => p.id)).size !== papers.length
)
  throw new Error("Canonical note coverage must match the unique inventory records.");
const icon = `<svg viewBox="0 0 36 36" aria-hidden="true"><path d="m7 27 11-20 11 20Z M7 27l22-10M18 7v20"/><circle cx="7" cy="27" r="3"/><circle cx="18" cy="7" r="3"/><circle cx="29" cy="27" r="3"/></svg>`;
const header = `<header class="site-header"><a class="brand" href="${base}" aria-label="DUSt3R Paper Collection home">${icon}<span>DUSt3R<span class="brand-sub">Paper Collection</span></span></a><nav aria-label="Main navigation"><a href="${base}#papers">Browse papers</a><a href="${repo}">Repository</a></nav></header>`;
const footer = `<footer class="site-footer"><p>Read the method. Check the source.</p><p>Notes and visual summaries from the <a href="${repo}">DUSt3R Paper Collection</a>. Original papers remain the source of evidence.</p></footer>`;
function shell(title, content, detail = false) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Source-linked notes and visual summaries for feed-forward 3D research."><meta name="theme-color" content="#fcfdff"><title>${escape(title)} | DUSt3R Paper Collection</title><link rel="stylesheet" href="${base}site.css">${detail ? `<link rel="stylesheet" href="${base}vendor/katex/katex.min.css">` : ""}<script defer src="${base}app.js"></script></head><body data-base="${base}"><a class="skip-link" href="#main">Skip to content</a>${header}<main id="main">${content}</main>${footer}</body></html>`;
}
const categoryOptions = Object.entries(names)
  .map(([id, name]) => `<option value="${id}">${escape(name)}</option>`)
  .join("");
const years = [...new Set(papers.map((p) => p.year).filter(Boolean))].sort((a, b) => b - a);
function listingCard(p, forceFallback = false) {
  const art = forceFallback ? { ...p.summaryPreview, kind: "visual_summary" } : p.thumbnail;
  const image = `<img data-src="${relativeAsset(art.path)}" data-summary-src="${p.image}" data-summary-width="${p.summaryPreview.width}" data-summary-height="${p.summaryPreview.height}" width="${art.width}" height="${art.height}" loading="lazy" decoding="async" alt="${escape(art.alt)}">`;
  return `<article class="paper-item" data-paper="${escape(p.id)}"><a class="paper-image" data-thumbnail-kind="${art.kind}" style="--summary-ratio:${p.summaryPreview.width} / ${p.summaryPreview.height}" href="${p.url}" aria-label="Read ${escape(p.shortTitle)}">${image}</a><div class="paper-caption"><div class="paper-meta"><span>${escape(p.categoryName)}</span><span>${p.year || "Year not recorded"}</span></div><h2><a class="paper-title" href="${p.url}">${escape(p.title)}</a></h2><p class="paper-purpose" title="${escape(p.purpose)}">${escape(p.purpose)}</p></div></article>`;
}
const list = papers.map((p) => listingCard(p)).join("\n");
const data = papers.map(
  ({ html, noteSha256, sourceIdentity, thumbnail, summaryPreview, ...p }) => p,
);
const intro = `<section class="intro"><div><h1>From images<br>to 3D.</h1><p class="intro-description">Source-linked notes and visual summaries for geometric vision.</p></div><aside class="reading-route"><p>Start with the foundations</p><div>${[
  "croco",
  "croco-v2",
  "dust3r",
  "mast3r",
  "vggt",
]
  .map((slug) => {
    const p = papers.find((p) => p.id === "foundation/" + slug);
    return `<a href="${p.url}">${escape(p.shortTitle)}</a>`;
  })
  .join(
    "",
  )}</div><p class="route-caption">Then follow the problem across ${Object.keys(names).length} research categories.</p></aside></section>`;
const filters = `<section class="catalog" id="papers" aria-label="Paper library"><form id="filters" class="filters" role="search"><div class="search-field"><label for="query">Search the collection</label><input id="query" name="q" type="search" placeholder="Paper, method, author or question" autocomplete="off"></div><div><label for="category">Category</label><select id="category" name="category"><option value="">All categories</option>${categoryOptions}</select></div><div><label for="year">Year</label><select id="year" name="year"><option value="">All years</option>${years.map((y) => `<option>${y}</option>`).join("")}</select></div><button class="reset" type="reset">Reset filters</button></form><div class="results-bar"><p id="result-count" role="status" aria-live="polite">${papers.length} papers</p><p>Newest year first</p></div><div id="empty-state" class="empty-state" hidden><h2>No papers match these filters.</h2><p>Try a broader search or clear the filters to browse the collection.</p><button type="button" id="clear-empty">Clear filters</button></div><div class="paper-grid">${list}</div><noscript><p>All papers are listed. Enable JavaScript to use search and filters.</p></noscript></section><script type="application/json" id="paper-data">${JSON.stringify(data).replaceAll("<", "\\u003c")}</script>`;
fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, "index.html"), shell("Research library", intro + filters));
if (args.includes("--thumbnail-preview")) {
  const samples = ["croco", "croco-v2", "dust3r", "mast3r", "vggt"].map((s) =>
    papers.find((p) => p.id === "foundation/" + s),
  );
  const fallback = papers.find((p) => p.id === "extensions/filt3r");
  const preview = `<section class="thumbnail-study"><h1>Five foundations. A clearer first look.</h1><p>Dedicated listing thumbnails. Full visual summaries stay in the paper details.</p><div class="paper-grid">${samples.map((p) => listingCard(p)).join("")}</div><h2>When a thumbnail is unavailable</h2><div class="fallback-example">${listingCard(fallback, true)}</div></section>`;
  fs.mkdirSync(path.join(output, "thumbnail-preview"));
  fs.writeFileSync(
    path.join(output, "thumbnail-preview/index.html"),
    shell("Thumbnail study", preview),
  );
}
const classificationReview = JSON.parse(
  fs.readFileSync(path.join(root, "data/classification-review-2026-10-19.json"), "utf8"),
);
const issueIDs = new Set(
  classificationReview.separate_metadata_issues.map((issue) => issue.record_id),
);
for (const paper of papers) {
  const actions = paper.links
    .map(
      (link) =>
        `<a class="source-link" href="${escape(link.url)}">${escape(link.label === "Paper" ? "Original paper" : link.label)}</a>`,
    )
    .join("");
  const content = `<div class="detail-wrap"><a class="back-link" data-back href="${base}">Back to papers</a><header class="detail-heading"><div class="paper-meta"><a href="${base}?category=${paper.category}">${escape(paper.categoryName)}</a><span>${escape(paper.venue)}</span>${paper.preprint ? '<span class="preprint-label">Preprint</span>' : ""}</div><h1>${escape(paper.title)}</h1><p class="detail-purpose">${escape(paper.purpose)}</p><div class="source-actions">${actions}<a href="${repo}/blob/main/${paper.note}">Markdown note</a></div>${issueIDs.has(paper.id) ? '<p class="review-note">A source-version or content issue is recorded for this note. This page preserves the existing reviewed snapshot; consult the original paper and <a href="' + repo + '/blob/main/data/classification-review-2026-10-19.json">review record</a>.</p>' : ""}</header><div class="detail-layout"><aside class="poster-panel"><a href="${paper.image}" class="poster-link" aria-label="Open full-size visual summary for ${escape(paper.shortTitle)}"><img class="detail-poster" src="${paper.image}" alt="Existing English visual summary for ${escape(paper.shortTitle)}" decoding="async" fetchpriority="high"></a><a class="full-image" href="${paper.image}">Open full-size image</a><p>Visual summary. Read the note and original paper for protocols and limitations.</p></aside><article class="note-content" aria-label="Paper note">${paper.html}</article></div></div>`;
  const destination = path.join(output, "papers", paper.id, "index.html");
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, shell(paper.shortTitle, content, true));
}
for (const file of ["site.css", "app.js"])
  fs.copyFileSync(path.join(root, "site", file), path.join(output, file));
for (const logical of assets) {
  const src = path.resolve(root, logical);
  if (!src.startsWith(root + path.sep) || !fs.statSync(src).isFile())
    throw new Error("Missing local asset: " + logical);
  const target = path.join(output, logical);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(src, target);
}
const mathAssets = path.join(output, "vendor/katex");
fs.mkdirSync(mathAssets, { recursive: true });
fs.copyFileSync(
  path.join(root, "node_modules/katex/dist/katex.min.css"),
  path.join(mathAssets, "katex.min.css"),
);
fs.copyFileSync(path.join(root, "node_modules/katex/LICENSE"), path.join(mathAssets, "LICENSE"));
fs.cpSync(path.join(root, "node_modules/katex/dist/fonts"), path.join(mathAssets, "fonts"), {
  recursive: true,
});
fs.writeFileSync(path.join(output, ".nojekyll"), "");
fs.writeFileSync(
  path.join(output, "404.html"),
  shell(
    "Page not found",
    `<section class="not-found"><h1>This page is not in the collection.</h1><p>Browse the current papers to find the canonical note.</p><a class="source-link" href="${base}">Browse papers</a></section>`,
  ),
);
const manifest = {
  base,
  papers: papers.length,
  categories: Object.fromEntries(
    Object.keys(names).map((cat) => [cat, papers.filter((p) => p.category === cat).length]),
  ),
  assets: assets.size,
  dedicatedThumbnails: Object.keys(thumbnails.thumbnails).length,
  textFallbacks: 0,
  summaryFallbacks: papers.length - Object.keys(thumbnails.thumbnails).length,
  source: "Existing canonical Markdown notes and unchanged PNG assets",
  records: papers.map((p) => ({
    id: p.id,
    year: p.year,
    note: p.note,
    noteSha256: p.noteSha256,
    sourceIdentity: p.sourceIdentity,
    image: p.image,
    thumbnail:
      p.thumbnail.kind === "image"
        ? { kind: "image", path: base + p.thumbnail.path, sha256: p.thumbnail.sha256 }
        : {
            kind: "visual_summary",
            path: base + p.summaryPreview.path,
            sha256: p.summaryPreview.sha256,
          },
    url: p.url,
  })),
};
fs.writeFileSync(
  path.join(output, "build-manifest.json"),
  JSON.stringify(manifest, null, 2) + "\n",
);
console.log(
  `Built ${papers.length} canonical paper pages and the gallery at ${folder}; base ${base}; ${assets.size} unchanged local assets.`,
);
