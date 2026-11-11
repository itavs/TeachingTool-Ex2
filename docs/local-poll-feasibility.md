# Local Qwen3 8B Poll-Draft Feasibility — 2026-11-11

## Experiment boundary

Four single generations from short synthetic learning text, one comprehension and one opinion draft in each of Hebrew and English. No website implementation or database writes, Gemini access, external inference, billing, model download, commit or push. Each generated draft is shown to the user unedited; raw prompt/source/JSON/timing outputs remain in ignored .ai-lab/results/poll-quality in a unique run directory. The standalone probe is experiments/local_ai/poll_quality_probe.py; it requires the existing experiment-only Ollama service, which was stopped afterward.

Local model qwen3:8b / Qwen3 8B Q4_K_M, pinned manifest SHA-256 b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7, weights digest a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f. Existing model/blob presence, sizes and manifest identity verified. Ollama 0.40.14, cloud disabled, loopback 127.0.0.1:11435 with proxy bypass. The unrelated desktop Ollama service was not used. Settings: temperature 0.1, seed 42, context 8192, thinking false, max 768 generated tokens, JSON schema, no generation retries. The first local version/readiness probe timed out at three seconds while GPU discovery was still starting; no generation had occurred. The probe timeout was changed to 30 seconds and all four actual model calls then executed once.

## Learning material and expectations

Both language versions explicitly state that a database transaction groups operations; atomicity means all operations succeed or none take effect; rollback after a failure before commit cancels all transaction changes, including earlier successful operations; commit makes changes permanent. Four practice methods are supplied: a guided demonstration, independent sandbox experiments, small-group failure discussion and analysis of a written worked example. The complete source is in the probe script and ignored input/result records.

A comprehension answer must match these facts, have exactly one correct option and a complete source-supported explanation. An opinion question should explicitly ask for the student's preference among four reasonable methods, without any answer key or correctness assessment. Lecturer review/editing before publication remains mandatory; no runtime feature was enabled.

## Measured results

| Case | Wall time | Model load | Output generation | Content/readability assessment |
|---|---:|---:|---:|---|
| he_comprehension | 8.730 s | 5.395 s | 2.967 s | Not ready: CJK characters in all options, incomplete explanation, weak/ambiguous distractors. |
| en_comprehension | 2.432 s | 0.005 s | 2.248 s | Correct source-grounded rollback answer and explanation; four distinct options, one correct. |
| he_opinion | 2.006 s | 0.003 s | 1.794 s | Four reasonable options and no answer key, but ungrammatical/semantically corrupted question and weak personal-opinion framing. |
| en_opinion | 1.330 s | 0.003 s | 1.159 s | Clear personal preference with four acceptable options; learning topic wording is generic. |

The first case included a 5.395-second model load; later cases reused a resident model. Wall times do not prove language-specific throughput. No generation ended due to token length; all returned done_reason=stop. The Hebrew explanation therefore remained incomplete despite an ordinary stop, not an exhausted output cap.

## Explicit review

- Hebrew comprehension: the index identifies the first option, whose conceptual intent resembles the source's all-or-none definition, but every option contains CJK corruption in the transaction word. The second option's none is affected wording is an ambiguous near-paraphrase rather than a clean distractor; printed/ranked alternatives are unnatural and weak. The explanation stops after announcing that the text defines atomicity, without stating the definition. Exactly-one-index structure does not establish an unambiguous correct usable question. Not publication-ready.
- English comprehension: correct_index=1 (second option) says rollback undoes all transaction changes, including earlier operations, matching the material. Option 1's last-operation-only claim contradicts the source; option 3's permanent deletion is not rollback's stated undo behavior; option 4 incorrectly ties rollback to successful commit. The explanation accurately quotes/paraphrases the supplied fact. The question could specify before commit for extra precision, but within this supplied passage the intended correct option is unique. Readable as a lecturer-reviewed draft.
- Hebrew opinion: all four options faithfully name the four practice methods and contain no correct_index/explanation. The question uses a gender mismatch and an inappropriate phrase about selling experience. It asks which method contributes most rather than clearly eliciting the respondent's own preference, leaving possible best-method framing. It is not clear enough to publish without rewriting.
- English opinion: explicitly asks which method the respondent prefers; all four options are valid non-ranked preferences drawn from the text. No answer key/explanation exists, and none is evaluated as correct. Learning topic is generic; naming transactions would improve standalone clarity. This is a minor editorial improvement rather than a correctness defect.

All four outputs passed the existing website validate_input/validate_content functions when invoked without saving anything. This demonstrates the limits of current structural validation: field checks cannot detect script corruption, an incomplete nonempty explanation, factual uniqueness or opinion framing. No website test or model-generated quality check was used as a substitute for the manual source-to-output review above.

## Recommendation — proposal only

The English results support a small experimental draft-generation connection with lecturer review/editing and explicit publishing. The four-case evidence does not support treating bilingual generation as ready: both Hebrew drafts need substantive repair. Before a general bilingual button, strengthen the prompt and test again, validate language/script without blocking legitimate Hebrew/English code terms, check complete explanations and distinguish factual questions from opinions. Invalid generation must show an error rather than save prepared fallback content. None of these recommendations is implemented or approved by this experiment. Four short synthetic cases are not a broad accuracy/reliability benchmark. The site's real generation adapter remains disabled.

No generated draft was edited or published. The model was unloaded and the dedicated experiment service stopped. Gemini files remain separate/unchanged; no commit or push.

## Subsequent approved English integration

The user subsequently approved English-only local draft generation. Current provider/UI behavior, additional-topic end-to-end checks and unresolved semantic risks are recorded in [local-poll-generation.md](local-poll-generation.md). The four-case experiment above remains historical evidence; its Hebrew limitations are not treated as resolved.
