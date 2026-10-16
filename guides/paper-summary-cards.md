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

Check `audit_passed` and the audit's `blocking_findings` before selecting a production batch. Note hashes use UTF-8 text with LF line endings so the same content has the same hash on Windows and Linux.

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

Maintain a separate `data/paper-card-progress.jsonl` when production starts. Do not store manually reviewed status in a generated inventory that will be overwritten. No progress file or completed-card entries are created by this preparation.

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

| State             | Required evidence                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `not_started`     | No received card asset.                                                                                       |
| `asset_received`  | A real file has been received and associated with the correct source identity.                                |
| `source_reviewed` | The English wording, diagrams, numbers and qualifications were checked against the original paper.            |
| `visual_reviewed` | The actual image opens correctly; text, links, layout and labeling were checked at the intended display size. |
| `published`       | The reviewed bytes and note link are verified on main, with a recorded commit.                                |

Record issues separately and keep the last supported state. A generated file, successful image decode, category-banner approval or CI pass is not evidence that a paper card's claims were reviewed. If the note or paper revision changes, compare it with the recorded source snapshot and re-review affected card content.

## Card content and review

Use English and lead with the research problem, a concrete input and output, and the method that connects them. Explain a difficult term with a small example when it helps. Distinguish a conceptual example from an actual experimental result.

Retain source-specific limits. Every numeric result needs its dataset, units, protocol and source table/figure. Do not compare incompatible metrics or turn an explanatory simulation into a real robot success claim. If the source does not provide a usable number, explain the finding without inventing one.

For each card, keep the original paper link and the collection note link. Add a project/code link only when its identity is verified. Do not replace the existing note with automatically inferred prose or treat the inventory's stored metadata as a fresh paper audit.
