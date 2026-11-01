# Statement of Work
## Web-Based Teaching Tool - Draft

## 1. Purpose

This document defines the intended work, deliverables, boundaries, and review
points for Exercise 2 in Introduction to Software Engineering (OOP / OOD).
The project addresses the need for simpler classroom tools that support
learning and make practical use of AI.

The assignment emphasizes implementable design and reuse over writing code
from scratch. It nevertheless requires a working web demonstration and a
class presentation of approximately ten minutes (AS-08, AS-09, AS-14).

Requirement sources, approval status, and unresolved interpretations are
maintained in the
[Decisions and Assumptions Register](decisions-and-assumptions.md).
Detailed behavior and proposed acceptance checks belong in the
[SRS](SRS.md); the project overview belongs in [README](../README.md).

## 2. Sources and Approved Direction

| Basis | Meaning for this work |
|-------|-----------------------|
| Assignment requirements | AS-01 through AS-14 identify the handout requirements and guidance. |
| D-01 | The user approved planning for all five capabilities to be genuinely active in the demo. This coverage is not yet a lecturer-confirmed interpretation of the required implementation scope. |
| D-02 | Python is the main language for the server and AI processing; the future web interface should favor simplicity. |
| D-03 | All project documents are in English; explanations and progress summaries to the user are in Hebrew. |

The reviewed handout does not specify a programming language. No conflict with
Python was found; this finding does not select a framework or AI service.
No web framework, frontend solution, storage system, AI provider, or hosting
platform is selected by this document.

## 3. Planned Capability Coverage

The baseline covers the five capabilities below. The proposed workflows are
options for a manageable individual-project demo, not approved restrictions.
Changing or dropping a capability requires a user decision.

| Capability and source | Required planning outcome | Open basic-demo proposal | Material boundary requiring approval |
|-----------------------|---------------------------|--------------------------|--------------------------------------|
| Attendance (AS-01) | Automatic attendance and lecturer access to an online/offline spreadsheet of student details. | Record an identified student's entry into a meeting automatically, prevent duplicates, show a live table, and provide a downloadable spreadsheet (P-02, P-03). | Entry through a link does not prove physical classroom presence. The trigger, identity evidence, fields, and spreadsheet behavior remain open (Q-01, Q-02). |
| Comments and suggestions (AS-02) | Student comments and suggestions in real time / offline. | Retain identified comments, display them to the lecturer in real time, and allow later submission over the internet (P-04). | Interpreting offline as asynchronous online use excludes disconnected use and synchronization. That interpretation and comment visibility are not approved (Q-02, Q-07). |
| Automatic polls (AS-03) | Lecturers can create simple polls about current learning material. | Use actual model processing to generate a single-choice question from short pasted text; let the lecturer review and publish it; collect one response per student and show the distribution (P-05). | Input limits, generation method, editing, voting rules, and one-active-poll scope remain proposals (Q-03). |
| Class-video summary (AS-04) | The lecturer receives an ML-generated summary derived from a class video. | Upload a one-to-two-minute video, extract audio, transcribe it, and produce an actual model-generated summary in one agreed language (P-06). | This proposal omits visual-only information and full-length lessons. It requires approval; uploading a prepared transcript alone would not demonstrate the proposed video-processing path (Q-04). |
| Homework review and comparison (AS-05) | Students and teachers receive deep LLM reviews, including comparison with other students' work. | Review about three short text submissions for one assignment against instructions and criteria; produce substantive individual feedback and actual cross-submission comparison (P-07, P-08). | Text-only input, workload, review depth, comparison visibility, and privacy rules remain open. Numeric grading, plagiarism judgments, and code execution are proposed exclusions only (Q-05, Q-07). |

The proposed administrative boundary is one course, one lecturer, and one active
meeting (P-01). Neither the actual class size nor a concurrency limit has been
approved. AS-06 requires actual classroom operation, and AS-07 requires a simple
smartphone web experience; a small presentation dataset alone cannot establish
that these requirements have been met (Q-06).

Moodle, Zoom, and university personal-information-system integrations are not
required by the handout (AS-08). Their absence does not remove the requirement
to process a video or perform any other capability.

## 4. Project Deliverables

The full assignment includes the deliverables below. Completion evidence must
reflect the actual implementation and verification, rather than the presence
of a plan alone.

| Deliverable | Assignment basis | Completion evidence to produce later |
|-------------|------------------|--------------------------------------|
| Repository and README problem/scope definition | AS-10 | A repository with a README that describes the problem, scope, documentation, and actual project status. |
| SoW, SRS, and main use cases | AS-12 | Documents updated as questions are resolved and implementation clarifies behavior. |
| Technical tools report | AS-11 | Actual trials of every suggested tool, with observed suitability, failures, and limits separated from plans. |
| Main software components | AS-13 | Documented responsibilities and interfaces consistent with the selected design. |
| Low-level class diagrams and sequence diagrams | AS-13 | Diagrams aligned with the implemented responsibilities and principal workflows. |
| Testing strategy addressing the classes | AS-13 | Planned class-level and integration checks tied to requirements; later execution evidence reported separately. |
| Implemented or composed web demo | AS-09, AS-14, D-01 | All five capabilities operating genuinely within the approved scope. |
| In-class demonstration | AS-06, AS-07, AS-09, AS-14 | Observed classroom use and an approximately ten-minute presentation, with disclosed limitations. |
| Short conclusion and results account | AS-14 | What worked, what was actually checked, failures, limitations, and remaining gaps. |

No specific submission packaging, templates, or assessment rubric is assumed;
these remain questions for the user or lecturer (Q-08).

## 5. Student Responsibilities

This is an individual assignment. The student is responsible for:

- **Planning and design:** interpreting the assignment, resolving scope
  questions, evaluating tools, and maintaining requirements, component
  responsibilities, class diagrams, and sequence diagrams.
- **Implementation and integration:** implementing or composing the web
  application so that the five capabilities operate within the agreed scope.
- **Verification:** defining the testing strategy, checking components and
  integrated workflows, evaluating actual classroom and smartphone behavior,
  and recording observed results, failures, and limitations.
- **Presentation and submission:** preparing and rehearsing the demonstration,
  keeping documents consistent with the delivered behavior, and submitting
  the required artifacts and short conclusion according to confirmed rules.

AI assistance and reused tools may be documented separately where required.
Their use does not transfer responsibility for the design, correctness,
verification, or submission away from the student.

## 6. Indicative Milestones

The user describes an individual assignment with about three weeks available.
The exact deadline is unconfirmed. The sequence below is an indicative project
plan, not a confirmed calendar.

1. **Requirements and scope:** prepare and refine README, SoW, SRS, and the
   decisions register, retaining unresolved scope explicitly.
2. **Scope resolution and feasibility:** obtain material decisions, trial
   candidate tools, and choose an implementable design. Resolve cost and
   data-use constraints before paid or external processing.
3. **Incremental implementation and documentation:** implement approved paths,
   update components and diagrams, and check each capability as it becomes
   available.
4. **Integration, classroom checks, and rehearsal:** verify the combined
   workflow under agreed conditions, measure actual AI processing times,
   rehearse the presentation, and address routine defects.
5. **Submission preparation and conclusion:** align documents with observed
   behavior, record results and limitations, and package according to confirmed
   submission instructions.

The remaining time must cover design and written deliverables as well as the
demo. If feasibility conflicts with the five-capability target or approved
scope, the student records the conflict for an explicit scope decision rather
than silently reducing the deliverables.

## 7. Dependencies and Risks

| Dependency or risk | Required handling |
|--------------------|-------------------|
| Unresolved attendance, offline, and input-scope interpretations | Keep P-02 through P-07 conditional and resolve Q-01 through Q-05 before implementing the affected paths. |
| Actual class conditions and smartphone access | Confirm devices, user count, connectivity, and access location; do not equate a small local demo with classroom readiness (Q-06). |
| Identity, authorization, and student-data exposure | Obtain the user's decisions about consent, permitted AI inputs, review visibility, retention, and deletion before real-data processing (P-08, Q-07). |
| AI availability, output quality, cost, and processing time | Trial proposed tools later, use actual inputs, record observed results, and seek approval for payment. No budget or performance guarantee is assumed. |
| Ten-minute presentation feasibility | Measure actual video and review processing time and rehearse before claiming the presentation fits (P-09, Q-09). |
| Unknown deadline and submission rules | Confirm Q-08 and adjust the plan explicitly if needed. |

## 8. Demo and Assignment Acceptance

Future acceptance requires genuine operation of all five capabilities under
the scope the user eventually approves, with evidence of actual classroom and
smartphone suitability. Detailed checks and criteria are drafted in SRS.md;
they are not completed tests or final acceptance thresholds.

Prepared inputs may support a demo if their nature is disclosed. A prerecorded
screen, canned AI answer, or simulated action cannot establish that a required
capability works. Previously processed output must be labeled, and cannot
replace a requirement for live completion without approval (P-09, Q-09).
Failures and partial processing must not be presented as successful outcomes.

## 9. Project Status

Initial requirements drafts have been prepared: README, SoW, SRS, and the
decisions register (D-04). These documents describe intended work and open
proposals, not completed application behavior. No application implementation,
AI experiment, or runtime verification has been completed. Components,
diagrams, tools evaluation, testing, the demo, and the conclusion remain
project deliverables to develop and verify.
