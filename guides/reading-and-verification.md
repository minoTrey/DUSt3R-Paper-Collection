# Reading and verification

[Back to the collection](../README.md)

Document counts are not counts of fully verified papers. Read each result with its source, protocol and limitations.

## Category indexes and Featured papers

The [complete list](../docs/papers-list.md) and category READMEs group papers by the year recorded in each Overview's `Venue`, newest first. For a preprint, this is its recorded preprint year. A `Verification` date records a check, not a publication date. Entries with no recorded year appear last; years are not inferred from review dates or title text. Within a year, entries use stable slug order rather than an inferred month or day. Extensions and Surveys retain their topic groups below each year.

Featured papers are editorial reading routes that balance recent work with representative methods and task coverage. They are not performance rankings or an exhaustive list of recent papers. [Curated settings](../data/category-featured.json) record the review date, explicit order, selection type and reason for every choice. Preprints can be selected and are labeled **Preprint**; conference/journal venues that lack a stored `CONFIRMED` verdict are labeled **Venue unconfirmed**. Selection does not change a note's verification status or establish peer review.

To maintain these indexes, edit the curated settings and, when needed, [topic memberships](../data/category-groups.json), then regenerate and validate:

```sh
python tools/build_papers_list.py
python tools/build_papers_list.py --check
python -m unittest discover -s tools -p 'test_*.py'
python tools/verify_all.py
```

Keep Foundation limited to CroCo, CroCo v2, DUSt3R, MASt3R and VGGT. Update `reviewed_on` when reviewing Featured choices. The generator validates category coverage, canonical IDs, duplicate selections and nonempty reasons. Do not edit generated README blocks directly.

## Reading results responsibly

Keep each number beside its source table, dataset, camera inputs, units and alignment protocol.
The same metric name does not make results comparable when GT poses, scale treatment or completed sequences differ.
Start with [Surveys & Analysis](../docs/surveys) for comparisons under a shared protocol.

## Verification

Metadata and results in this collection are checked by scripts in [`tools/`](../tools):

| Check                     | What it does                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------- |
| `verify_metadata.py`      | Venue, authors, arXiv ID against arXiv + DBLP + Semantic Scholar + Crossref           |
| `verify_benchmarks.py`    | Selected numeric tokens in tables against source PDF text; labels need source review  |
| `verify_index_numbers.py` | Checks README numeric claims against paper documents                                  |
| `check_structure.py`      | Seven-section structure and Overview field schema                                     |
| `update_stats.py`         | Document/category counts and the confirmed-venue histogram — generated from documents |

Each paper's Overview carries a `Verification` field:

- **CONFIRMED** — venue proven by DBLP, a publisher DOI, OpenReview, CVF openaccess, or an
  author-maintained badge
- **LIKELY** — a publication candidate or author claim needs corroboration and identity checks
- **PREPRINT** — stored metadata checks found no publication record; indexing delays remain possible
- **UNKNOWN** — publication venue remains unverified, even if the arXiv paper is available.
  The venue says `arXiv preprint`, and the Verification field or a Note states what is missing.

### What verification does not cover

Stated plainly, because a checkmark that overstates itself is worse than none:

- **Benchmark verification does not run in CI.** Source PDFs are gitignored, so it is a
  local gate. CI checks structure, counts, links, and formatting only.
- **Default benchmark checks extract decimals.** `--int` also checks selected integer
  tokens, but cannot establish that the labels, units, or protocols are correct.
  A matching value elsewhere in the PDF can still conceal a wrong table.
- **Coverage is aggregate.** A paper can score above threshold while containing one wholly
  fabricated table. Seven papers were caught this way, after passing an earlier sweep.
- **Prose is weaker than tables.** Derived claims in body text get less scrutiny than the
  tables they cite.

[`log.md`](../log.md) records what was found and fixed, including the failure modes above.
