import fs from "node:fs";
import path from "node:path";
import dates from "./publication-date-utils.js";

export function validatePublicationDates(metadata, inventory) {
  if (metadata.schema_version !== 1 || !Array.isArray(metadata.records))
    throw new Error("Publication dates require schema 1 and explicit records.");
  const expected = new Map(inventory.papers.map((p) => [p.record_id, p.paper_source_identity]));
  const result = new Map();
  for (const item of metadata.records) {
    if (
      !expected.has(item.record_id) ||
      result.has(item.record_id) ||
      expected.get(item.record_id) !== item.source_identity
    )
      throw new Error("Publication date canonical source identity or coverage mismatch.");
    dates.parts(item);
    if (item.date != null) {
      if (item.verification !== "verified" || !/^https:\/\//.test(item.source_url || ""))
        throw new Error("A known publication date requires verified primary-source provenance.");
      if (item.source_identity.startsWith("arxiv:") && item.source_kind !== "arxiv_v1")
        throw new Error("arXiv dates must use v1 first publication, never a venue or update date.");
      if (!item.source_identity.startsWith("arxiv:") && item.source_kind !== "publisher")
        throw new Error("Non-arXiv dates require original publisher provenance.");
    } else if (item.verification !== "unknown") {
      throw new Error("An unknown date must be explicitly marked unknown.");
    }
    result.set(item.record_id, {
      date: item.date,
      precision: item.precision,
      source_kind: item.source_kind,
      source_url: item.source_url,
      verification: item.verification,
    });
  }
  if (result.size !== expected.size)
    throw new Error(
      "Publication dates must explicitly cover every canonical paper, including unknown dates.",
    );
  return result;
}

export function loadPublicationDates(root, inventory) {
  return validatePublicationDates(
    JSON.parse(fs.readFileSync(path.join(root, "data/publication-dates.json"), "utf8")),
    inventory,
  );
}
