# English paper summary cards

This guide proposes the storage and review workflow for future English summary cards. It does not create cards or mark them complete. Existing paper notes remain the source-linked reading material; a card supplements a note.

## Inventory and scope

- [JSON inventory](../data/paper-card-inventory.json): one record per current paper note, with title, category, note path, paper source, explicitly stored PDF links, project/code links and note hash.
- [CSV inventory](../data/paper-card-inventory.csv): the same core fields for batch selection. It is UTF-8 with a BOM for spreadsheet readers.
- [Inventory audit](../data/paper-card-inventory-audit.json): counts, coverage against the complete/category indexes, duplicate identities, missing fields, short-name collisions and core-paper links.

Regenerate and check the exports with:

```bash
python tools/build_card_inventory.py
python tools/build_card_inventory.py --check
```

The exporter reads the current note titles and Overview links. It does not invent project links, extract another paper's citation from Related Work, or treat venue verification as a completed card review. A missing project link means **not recorded in the note**, not that no project exists. Explicit PDF links are included only when they refer to the same arXiv ID.

Check `audit_passed` and the audit's `blocking_findings` before selecting a production batch. Note hashes use UTF-8 text with LF line endings and exclude only the marked summary-card presentation block. A `card_production_status` of `not_started` means no reviewed integration is recorded in this repository. Check delivered Library assets and pending batches before commissioning or generating another card; this field does not prove that no card exists externally.

Use the full title and `paper_source_identity` to resolve identity. Abbreviations can collide: the current collection contains separate Scal3R papers and separate Wat3R/WAT3R papers. Their different source IDs and slugs must remain separate card jobs.

The current DUSt3R and MASt3R notes store the same Project Page URL. The export preserves that value. Verify the destination against the paper or author repository before attributing it on a card.

Start with DUSt3R, MASt3R and VGGT, which appear first in the export. This ordering is a production convenience, not a ranking of research quality. Review later work in bounded batches rather than marking the whole inventory complete at once.

## Proposed file location

Use the inventory's `planned_card_path`:

```text
assets/paper-cards/en/<category>/<slug>.png
```

The category and full slug prevent short-name collisions. The planned path is metadata, not a claim that the asset exists. `card_asset_present` checks only that path; presence alone does not establish source accuracy, visual quality or publication.

Keep originals or editable production sources separately from web copies when needed. Preserve aspect ratio when preparing a web copy. A missing card must not produce a broken image link or a placeholder that looks like a completed result.

## Proposed note placement

After a card passes source and visual review, place it immediately after the note's H1, before existing figures and the seven required sections. Preserve the existing architecture figure, captions, Results tables, source citations and limitations.

Use a marked block only when the actual asset has been checked. For a note in `docs/<category>/`, the relative asset path starts with `../../assets/`. The following is a template, not a published card:

```markdown
<!-- PAPER-CARD:en -->
[![English summary card for PAPER TITLE.](../../assets/paper-cards/en/CATEGORY/SLUG.png)](../../assets/paper-cards/en/CATEGORY/SLUG.png)
<!-- /PAPER-CARD -->
```

The image should also open at a readable size. Keep card source/version information in the progress record and retain the note's links to the original paper.

## Proposed progress tracking

Maintain the separate [progress records](../data/paper-card-progress.jsonl). Manually reviewed status belongs there; the generated inventory only copies it. DUSt3R, MASt3R and VGGT are published on main. The next 28 supplied cards have source and image review records in the [batch audit](../data/paper-card-reviews/batch-2026-10-16.json). A reviewed card awaiting main publication has `production_status: ready`; only a card whose exact bytes and note link have been verified on main may have `production_status: complete` and `status: published`. The supplied 42-card batch has a separate [source and image audit](../data/paper-card-reviews/batch-42-2026-10-16.json). Its exact bytes and note/source links were verified on main at `c8367506df111a0466ea41c130fd6b98702ab5db`; that batch brought the published total to 73. Unrecorded cards remain outside the repository integration workflow; their external production state is unknown. Batch 003 adds 45 reviewed cards with a separate [source and image audit](../data/paper-card-reviews/batch-003-2026-10-16.json). Its 45 image hashes and note/source links were verified at main commit `831c9c43a0615d39ff7b65d74bd7c9c5b39ad70b`. The current total is 118 published cards and 219 notes without a recorded repository integration.

Each progress record should contain:

| Field                                  | Meaning                                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `record_id`, `paper_source_identity`   | Match the inventory note and source paper; retain both when resolving moves or aliases.                  |
| `status`                               | One of the evidence-based states below.                                                                  |
| `source_note_sha256`, `paper_revision` | The note snapshot and original-paper version used to make the card. Do not infer an unrecorded revision. |
| `asset_path`, `asset_sha256`           | The received card and the exact reviewed bytes.                                                          |
| `review_evidence`                      | Source tables/pages or sections, visual inspection, and unresolved issues.                               |
| `published_commit`                     | Populate only after the asset and note link are present on main.                                         |

Use these states:

| State             | Required evidence                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `not_started`     | No reviewed repository integration record; external asset availability is unknown.                                         |
| `asset_received`  | A real file has been received and associated with the correct source identity.                                             |
| `source_reviewed` | The English wording, diagrams, numbers and qualifications were checked against the original paper.                         |
| `visual_reviewed` | The actual image opens and its text, diagrams, labels and clipping were inspected; record browser verification separately. |
| `published`       | The reviewed bytes and note link are verified on main, with a recorded commit.                                             |

Record issues separately and keep the last supported state. A generated file, successful image decode, category-banner approval or CI pass is not evidence that a paper card's claims were reviewed. If the note or paper revision changes, compare it with the recorded source snapshot and re-review affected card content.

After a card PR merges, verify the asset hash and note link at the main merge commit, then update its publication record. A follow-up metadata change can record that verified commit without claiming that unpublished work is complete. The exporter rejects `ready`/`complete` records with stale source or asset hashes, and rejects `complete` records without a published state and commit. Remote main verification remains a separate review step.

## Card content and review

Use English and lead with the research problem, a concrete input and output, and the method that connects them. Explain a difficult term with a small example when it helps. Distinguish a conceptual example from an actual experimental result.

Retain source-specific limits. Every numeric result needs its dataset, units, protocol and source table/figure. Do not compare incompatible metrics or turn an explanatory simulation into a real robot success claim. If the source does not provide a usable number, explain the finding without inventing one.

For each card, keep the original paper link and the collection note link. Add a project/code link only when its identity is verified. Do not replace the existing note with automatically inferred prose or treat the inventory's stored metadata as a fresh paper audit.

## Resolve legacy production jobs

Before placing a delivered card, resolve its exact legacy `record_id` through [paper-path-migrations.json](../data/paper-path-migrations.json). Each changed record supplies the old/new record IDs, note paths, canonical card paths and the same paper source identity. Unlisted records are unchanged. The importable `tools/paper_paths.py` module provides `resolve(value)` or `resolve(value, "note_path")` / `resolve(value, "card_path")`.

Use the current inventory destination after resolving the identity. Preserve the source review and card hash. Existing legacy PNGs are retained as byte-identical compatibility aliases; they are not extra card jobs. Foundation’s per-paper move notices were removed from the folder. Resolve those retired note URLs through the [central path guide](paper-path-migrations.md); GitHub does not automatically redirect them. Any remaining registered move notice is excluded from metadata, indexes and counts. Historical review manifests keep the identities and paths used at their review time; migration history connects them to current progress records.
