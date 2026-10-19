import test from "node:test";
import assert from "node:assert/strict";
import { validatePublicationDates } from "./publication-dates.mjs";
const inventory = {
  papers: [{ record_id: "foundation/dust3r", paper_source_identity: "arxiv:2312.14132" }],
};
const fixture = () => ({
  schema_version: 1,
  records: [
    {
      record_id: "foundation/dust3r",
      source_identity: "arxiv:2312.14132",
      date: "2023-12-21",
      precision: "day",
      source_kind: "arxiv_v1",
      source_url: "https://arxiv.org/abs/2312.14132v1",
      verification: "verified",
    },
  ],
});
test("verified first publication metadata retains source and precision", () => {
  const record = validatePublicationDates(fixture(), inventory).get("foundation/dust3r");
  assert.equal(record.date, "2023-12-21");
  assert.equal(record.precision, "day");
  assert.equal(record.source_kind, "arxiv_v1");
});
test("missing, duplicate or wrong-source dates cannot enter a build", () => {
  for (const mutate of [
    (m) => m.records.pop(),
    (m) => m.records.push(m.records[0]),
    (m) => (m.records[0].source_identity = "arxiv:0000.00000"),
  ]) {
    const data = fixture();
    mutate(data);
    assert.throws(() => validatePublicationDates(data, inventory));
  }
});
test("venue or revision dates cannot silently replace arXiv v1 provenance", () => {
  const data = fixture();
  data.records[0].source_kind = "publisher";
  assert.throws(() => validatePublicationDates(data, inventory), /v1 first publication/);
});
test("unknown dates require explicit coverage and no fabricated calendar value", () => {
  const data = fixture();
  Object.assign(data.records[0], {
    date: null,
    precision: "unknown",
    verification: "unknown",
    source_kind: "unknown",
  });
  assert.equal(validatePublicationDates(data, inventory).get("foundation/dust3r").date, null);
  data.records[0].precision = "day";
  assert.throws(() => validatePublicationDates(data, inventory));
});
