# Primary-contribution classification

[Back to the collection](../README.md)

Each paper has one canonical note and one primary folder. Decide from the research problem, required inputs, predicted outputs, central method and evaluation target. A possible downstream use or a keyword in the title does not establish the primary category. Cross-cutting tags can describe secondary tasks without adding duplicate paper entries.

| Folder                         | Primary filing criterion                                                                                                                                                          |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Foundation                     | The five approved starting models: CroCo, CroCo v2, DUSt3R, MASt3R and VGGT.                                                                                                      |
| Model Extensions               | Reusable acceleration, compression, adaptation, reliability or pretraining/learning interventions for geometry models.                                                            |
| 3D Reconstruction              | Scene geometry and systems that jointly recover maps and camera trajectories, including full SfM and SLAM.                                                                        |
| Dynamic Scenes                 | Temporal scene change, motion, deformation or temporal correspondence is central to the problem. Streaming input alone is insufficient.                                           |
| Gaussian Splatting             | Gaussian/splat representations, rendering or novel-view synthesis are central contributions. A method may also handle motion or estimate poses.                                   |
| Scene Understanding            | Semantic labels, object segmentation, scene graphs, physical properties or other task-level meaning attached to geometry.                                                         |
| Scene Reasoning                | Hidden/amodal structure, completion or spatial/generative reasoning beyond the observed geometry.                                                                                 |
| Robotics                       | Robot policy/action, robot-specific calibration, multi-robot collaboration or onboard constraints are central to the method and evaluation. Possible robotic use is insufficient. |
| Surveys, Benchmarks & Analysis | Evaluation metrics, benchmarks, surveys, reliability audits or failure analysis are the central contribution.                                                                     |
| Pose                           | The principal task is camera/object pose, registration, localization or visual odometry, rather than joint reconstruction of a scene and its trajectory.                          |
| Medical                        | Domain-specific medical/endoscopic imagery, supervision or acquisition constraints determine the method.                                                                          |

## Review scope and judgment calls

The [2026-10-19 decision record](../data/classification-review-2026-10-19.json) covers all 337 notes: 60 moves, 249 retained entries and 28 boundary cases held in their existing folders. The source task supplied a full collection note review. The implementation review independently read the primary abstracts for all 60 moving papers and PRISM's method Section 3.1. This is not a claim that all 337 PDFs, publication venues, numeric tables or scientific summaries were freshly revalidated.

MIRAGE and the three full-SfM moves (G-MASt3R-SfM, Glob3R and GLUEMAP) retain medium-confidence editorial judgments in the decision record. MIRAGE combines metric trajectories and Gaussian reconstruction; full SfM jointly estimates poses and scene structure. CoMo3R-SLAM remains in Robotics for multi-robot collaboration and Noctif3R for onboard execution constraints. Other unresolved boundary cases remain unmoved and are listed explicitly in the record.

FVO/CalfVO, IDT/MVID and the reported FlowR note/source mismatch are separate unresolved content/version issues. This reclassification preserves their detailed text and reviewed card snapshots instead of silently rewriting them.

## Links, cards and future maintenance

Keep one canonical note at its final path and update internal links. Do not add per-paper move stubs to category directories. Historical external GitHub file URLs do not automatically redirect; the [central path guide](paper-path-migrations.md) supplies final targets and immutable previous-commit permalinks. Flatten historical mappings to final canonical targets, preserving the paper's source identity.

Retain exact reviewed PNG bytes, register compatibility PNG aliases separately, and regenerate inventories, card progress, Featured selections, category indexes and counts. A moved canonical card path stays pending main publication until its remote hash and note link are verified after a main merge. Historical source/image reviews remain historical evidence.

When reviewing a future paper, record its problem, inputs, outputs, contribution, source URL/revision, primary folder, secondary tags and any unresolved boundary. A category move is a classification decision; it does not certify the paper's results or change its publication status.
