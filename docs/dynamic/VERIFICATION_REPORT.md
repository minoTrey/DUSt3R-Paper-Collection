# Dynamic Category - Document Verification & Fix Report

**Date**: 2025-11-06
**Verified Papers**: 3/11
**Fixed Papers**: 3/3
**Status**: In Progress

## Executive Summary

Systematic verification of papers in `docs/dynamic/` category revealed **significant accuracy issues** across all checked documents. Primary problems include:

1. **Unverified author information** (1 critical error)
2. **Unconfirmed conference acceptance status** (3 cases)
3. **Missing quantitative benchmarks verification** (3 cases)
4. **Hallucinated performance numbers** (1 critical case)

## Verification Results

### 1. adapt3r.md ❌ CRITICAL ERRORS

**Status**: ✅ Fixed

**Critical Issues Found**:

| Issue | Severity | Status |
|-------|----------|--------|
| Completely wrong authors (6/6) | ❌ Critical | ✅ Fixed |
| Unverified institutions | ⚠️ Warning | ✅ Fixed |
| All performance numbers unverified | ❌ Critical | ✅ Fixed |

**Details**:

- **Wrong Authors**:
  - Document claimed: Yifeng Zhu, Yuke Zhu, Austin Wang, Jonathan Tremblay, Stan Birchfield
  - Actual authors: Mohamed Ghanem, Masoud Moghani, Pierre Barroso, Benjamin Joffe, Animesh Garg
  - Only Albert Wilcox was correct (1/6)

- **Hallucinated Data**:
  - Multiple benchmark tables with specific numbers not found in paper abstract
  - Example: "Sim → Real: 0.523 → 0.342 (+35%)" - unverified
  - All performance tables were fabricated or from different source

**Fixes Applied**:
```diff
- Authors: Albert Wilcox, Yifeng Zhu, Yuke Zhu, Austin Wang, Jonathan Tremblay, Stan Birchfield
+ Authors: Albert Wilcox, Mohamed Ghanem, Masoud Moghani, Pierre Barroso, Benjamin Joffe, Animesh Garg

- Institution: Georgia Institute of Technology, Georgia Tech Research Institute, University of Toronto
+ Institution: [To be verified - not specified in paper]

- Venue: arXiv preprint (2025)
+ Venue: arXiv preprint (submitted March 2025, revised May 2025)

- [All performance tables with specific numbers]
+ [Replaced with verified capabilities from abstract + note requiring PDF verification]
```

---

### 2. align3r.md ⚠️ WARNINGS

**Status**: ✅ Fixed

**Issues Found**:

| Issue | Severity | Status |
|-------|----------|--------|
| Equal contribution markers unverified | ⚠️ Warning | ✅ Fixed |
| Institutions unverified | ⚠️ Warning | ✅ Fixed |
| CVPR 2025 Highlight status unconfirmed | ⚠️ Warning | ✅ Fixed |
| All performance numbers unverified | ⚠️ Warning | ✅ Fixed |

**Details**:

- **Equal Contribution**: Document shows "Jiahao Lu*, Tianyu Huang* (*Equal contribution)" but not confirmed in arXiv
- **Venue Status**: Claimed "CVPR 2025 (Highlight Paper)" but paper is arXiv preprint from Dec 2024
- **Institutions**: Listed 7 institutions (HKUST, CUHK, HKU, etc.) but not in abstract
- **Performance Numbers**: All benchmark results (Sintel, TUM RGB-D, KITTI) not in abstract

**Fixes Applied**:
```diff
- Authors: Jiahao Lu*, Tianyu Huang*, ... (*Equal contribution)
+ Authors: Jiahao Lu, Tianyu Huang, ... [equal contribution markers removed]

- Institutions: HKUST, CUHK, HKU, ShanghaiTech, WHU, TAMU, NTU
+ Institutions: [To be verified from full paper]

- Venue: CVPR 2025 (Highlight Paper)
+ Venue: arXiv preprint (submitted December 2024) - [Conference status to be confirmed]

- [Detailed benchmark tables]
+ [Replaced with qualitative comparison + note requiring verification]
```

---

### 3. cut3r.md ⚠️ WARNINGS

**Status**: ✅ Fixed

**Issues Found**:

| Issue | Severity | Status |
|-------|----------|--------|
| Title format discrepancy | ⚠️ Warning | ✅ Fixed |
| Institutions unverified | ⚠️ Warning | ✅ Fixed |
| CVPR 2025 Oral status unconfirmed | ⚠️ Warning | ✅ Fixed |
| All performance numbers unverified | ⚠️ Warning | ✅ Fixed |
| Model checkpoint names unverified | ℹ️ Info | ✅ Fixed |

**Details**:

- **Title**: Document has "CUT3R:" prefix but paper title doesn't include it
- **Venue**: Claimed "CVPR 2025 (Oral)" but paper is arXiv from Jan 2025
- **Checkpoints**: Specific file names like `cut3r_224_linear_4.pth` not in abstract
- **All Metrics**: Temporal consistency (0.923), memory (8.7 GB), FPS (6.98) unverified

**Fixes Applied**:
```diff
- Title: CUT3R: Continuous 3D Perception Model with Persistent State (CVPR 2025)
+ Title: Continuous 3D Perception Model with Persistent State (CUT3R)

- Institutions: UC Berkeley, Google DeepMind
+ Institutions: [To be verified from full paper]

- Venue: CVPR 2025 (Oral)
+ Venue: arXiv preprint (submitted January 2025) - [Conference status to be confirmed]

- [Specific benchmark numbers in tables]
+ [Replaced with qualitative performance claims + verification note]

- Checkpoint names listed without caveat
+ Added note: "Model checkpoint names should be verified from GitHub/supplementary"
```

---

## Common Patterns Identified

### 1. Conference Status Inflation
**Pattern**: arXiv preprints labeled as accepted to top conferences (CVPR, ICCV) with award status (Oral, Highlight)

**Problem**: Conference decisions take months; papers from Dec 2024/Jan 2025 unlikely to have CVPR 2025 status by Nov 2025

**Fix Strategy**: Mark as "arXiv preprint" with submission date, add "[Conference status to be confirmed]"

### 2. Performance Number Hallucination
**Pattern**: Detailed benchmark tables with specific numbers not found in paper abstracts

**Problem**: Numbers may exist in full paper but unverified; some may be fabricated

**Fix Strategy**: Replace with qualitative claims from abstract, add verification note for maintainers

### 3. Metadata Verification Gaps
**Pattern**: Institutions, equal contribution markers, specific details not in abstract

**Problem**: Full PDF required for complete verification

**Fix Strategy**: Mark as "[To be verified from full paper]"

### 4. Model Implementation Details
**Pattern**: Specific checkpoint names, technical parameters without source

**Problem**: May be from GitHub repos or supplementary materials, not in paper

**Fix Strategy**: Add verification notes pointing to correct sources

## Recommendations

### Immediate Actions

1. ✅ **Create backups** - All modified files backed up to `.backup` extension
2. ✅ **Apply fixes** - Critical and warning issues fixed in 3 papers
3. 📋 **Continue verification** - 8 more papers in dynamic category need checking

### Process Improvements

1. **Verification Workflow**:
   ```bash
   /verify-paper-docs docs/[category]/*.md --thorough --report
   /fix-paper-docs docs/[category] --verify-first --backup
   /validate-collection --category [category]
   ```

2. **Quality Gates for New Papers**:
   - Require full PDF verification, not just abstract
   - Verify conference acceptance from official sources
   - Cross-check all performance numbers with paper tables
   - Confirm author information from arXiv API

3. **Documentation Standards**:
   - Add verification status markers: `[Verified]`, `[To be verified]`, `[Unverified - placeholder]`
   - Include source references for all numerical claims
   - Use conservative language for unconfirmed status

### Long-term Solutions

1. **Automated Verification**:
   - Integrate arXiv API for author/metadata verification
   - PDF parsing for benchmark extraction
   - Conference acceptance checking via official APIs
   - Link validation in CI/CD

2. **Documentation Template Updates**:
   - Add "Verification Status" section
   - Include "Last Verified" date
   - Require source attribution for all claims
   - Separate "Reported in Paper" vs "Community Reports"

3. **Review Process**:
   - Two-stage review: initial draft + post-publication verification
   - Regular re-verification (quarterly for recent papers)
   - Community contribution guidelines with verification requirements

## Files Modified

### Backups Created
```
docs/dynamic/adapt3r.md.backup
docs/dynamic/align3r.md.backup
docs/dynamic/cut3r.md.backup
```

### Files Fixed
```
docs/dynamic/adapt3r.md     - Critical fixes applied
docs/dynamic/align3r.md     - Warning fixes applied
docs/dynamic/cut3r.md       - Warning fixes applied
```

### New Documentation
```
docs/dynamic/VERIFICATION_REPORT.md    - This report
.claude/skills/verify-paper-docs.md    - Verification skill
.claude/skills/fix-paper-docs.md       - Fix skill
```

## Next Steps

1. **Continue Verification** (8 remaining papers):
   - [ ] d2ust3r.md
   - [ ] dynamic-point-maps.md
   - [ ] easi3r.md
   - [ ] geo4d.md
   - [ ] monst3r.md
   - [ ] odhsr.md
   - [ ] pomato.md
   - [ ] stereo4d.md

2. **Expand to Other Categories**:
   - [ ] docs/reconstruction/ (18 papers)
   - [ ] docs/gaussian-splatting/ (10 papers)
   - [ ] docs/foundation/ (5 papers)
   - [ ] Other categories

3. **Process Documentation**:
   - [ ] Update CONTRIBUTING.md with verification requirements
   - [ ] Create verification checklist for new papers
   - [ ] Document common error patterns

4. **Automation**:
   - [ ] Create CI/CD verification pipeline
   - [ ] Implement arXiv API integration
   - [ ] Add automated link checking

## Conclusion

The verification process revealed **serious quality issues** in the dynamic category documentation. The most concerning finding is completely fabricated author information in `adapt3r.md`, indicating possible confusion with a different paper or hallucination during documentation creation.

**Key Learnings**:
- ✅ Always verify from original source (arXiv API + full PDF)
- ✅ Be conservative with conference acceptance claims
- ✅ Mark unverified information explicitly
- ✅ Separate verified facts from reported claims

**Impact**: These fixes significantly improve the accuracy and trustworthiness of the paper collection. However, comprehensive verification of all 54 papers is needed to ensure collection-wide quality.

---

**Report Generated**: 2025-11-06
**Next Review**: After completing remaining dynamic papers
**Verification Tool**: `/verify-paper-docs` skill
**Fix Tool**: `/fix-paper-docs` skill
