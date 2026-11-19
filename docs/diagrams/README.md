# Rendered architecture diagrams

These seven SVGs are static, zoomable document artifacts for assignment To Do 7.
The Mermaid blocks in [architecture.md](../architecture.md) remain the editable
source. No new application feature or test suite is introduced. Open individual
SVGs at full size; the class models and long sequences are too dense for a small
thumbnail. This is visual document review, not a UI/browser acceptance test.

| Diagram | Source section | Reviewed SVG |
|---|---|---|
| 1. Domain model | [Mermaid source](../architecture.md#class-and-interface-diagrams) | [Open full-size SVG](01-domain-model.svg) |
| 2. Video and poll interfaces | [Mermaid source](../architecture.md#class-and-interface-diagrams) | [Open full-size SVG](02-video-poll-interfaces.svg) |
| 3. Video processing sequence | [Mermaid source](../architecture.md#video-sequence) | [Open full-size SVG](03-video-sequence.svg) |
| 4. Poll generation/publication sequence | [Mermaid source](../architecture.md#poll-generation-and-publication-sequence) | [Open full-size SVG](04-poll-sequence.svg) |
| 5. Homework class model | [Mermaid source](../architecture.md#planned-homework-class-diagram) | [Open full-size SVG](05-homework-classes.svg) |
| 6. Homework request/review/publication sequence | [Mermaid source](../architecture.md#planned-homework-submission-to-publication-sequence) | [Open full-size SVG](06-homework-publication.svg) |
| 7. Local homework inference and evidence publication | [Mermaid source](../architecture.md#uc-05-feedback-control-flow) | [Open full-size SVG](07-homework-local-runtime.svg) |

## Render and visual review record

Mermaid CLI 12.2.0 / Mermaid 12.3.0 ran locally against the existing Chrome
executable in a separate temporary headless profile. No website was opened,
no personal browser profile/session was accessed, and the earlier local-site
browser permission denial was not bypassed. Renderer packages and temporary PNGs
remain outside Git under .local; only documentation artifacts are supplied here.
Official tool: [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli).

All seven were successfully rendered and visually inspected at overview/detail
level for readable labels, complete nodes/arrows, branch frames and clipping.
The seventh sequence initially failed actual parsing: a semicolon inside a
message was treated as a statement separator. Changing that punctuation to a
comma fixed the documentation source without changing its meaning or application
behavior. Sequence participant width was increased to avoid mid-word wrapping
of component names. No semantic/class responsibility was invented for layout.

[Render manifest](render-manifest.json) records exact Mermaid-source and SVG
hashes, renderer versions and layout settings. PNG previews used for inspection
are local-only; SVGs provide the portable review artifacts. Regenerate if a
Mermaid source block changes. Structural/application test results and model
quality evidence remain in [testing.md](../testing.md), separately from this review.

### Selected-group extension - 2026-11-18

Diagram 5 was regenerated with the existing offline renderer and visually
inspected after adding ReviewBatch, the homework_batches coordinator, resource
reservation and batch-job responsibility. Its source/SVG hashes are updated in
the manifest. Other diagrams retain their existing scope; the individual review
sequences still apply inside each group's per-feedback publication workflow.
This is not an application browser pass or model-quality evidence.
