# Local Summary Probe on Saved Turbo Transcripts — 2026-11-08

## Scope and exact inputs

Two local generations only, using the already installed Qwen3 8B via Ollama CLI and a dedicated loopback-only experiment service (127.0.0.1:11435, OLLAMA_NO_CLOUD=1). The CLI communicates with the local Ollama process; no external-provider API request, model download, retranscription, payment or website implementation occurred. Existing website transcription settings/results remain unchanged. The experiment service was started for this run; the loaded model was stopped after both cases.

Inputs are the complete saved turbo experiment outputs (not medium, not excerpts):

- STATIC: .ai-lab/results/static-turbo/20261108T141154877729Z/turbo-full.json, Hebrew.
- SHORT: .ai-lab/results/short-turbo/20261108T141733118396Z/turbo-full.json, English.

Both ASR inputs identify dropbox-dash/faster-whisper-large-v3-turbo revision 0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf. The exact input text, hashes, prompt, untouched model stdout, generated paragraph/points and CLI timing diagnostics remain in ignored .ai-lab/results/turbo-summary-probe, one unique run directory. Published notes do not embed raw full transcripts.

## Runtime and generation settings

- Qwen3 8B / qwen3:8b, Q4_K_M. Installed local manifest SHA-256 b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7; weights layer a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f. Local manifest/blob presence and sizes were checked before CLI execution.
- Bundled Ollama client/server 0.40.14; the unrelated desktop service on port 11434 was not used or changed.
- Thinking disabled (--think=false and /no_think), JSON output, context 8192, one model/slot, temperature 0.6 / top_k 20 / top_p 0.95 / repeat_penalty 1 from the installed model parameters. No seed override or custom token cap; prompt requests at most 150 words total. Hard 600-second CLI timeout, no retries. One call per input.
- Prompt requests one short paragraph plus 3–5 points in the recording's language, transcript-only grounding, preservation of negations and inheritance direction, omission of unclear/corrupt/unsupported details, no guessed identifiers, and no explanation of topics merely announced for a later lesson.
- Logs confirm CUDA buffers and an 8192-token context. Some buffers are host-side; no claim of exclusively GPU-resident computation or a new peak VRAM measurement.

## Observed timings

| Case | CLI wall time | Model load | Prompt evaluation | Output generation |
|---|---:|---:|---:|---:|
| STATIC | 10.098 s | 4.919 s | 0.692 s | 4.182 s |
| SHORT | 2.863 s | 0.004 s | 0.192 s | 2.510 s |

STATIC was the first load; SHORT reused the resident model. These single runs do not establish a language-speed difference or a latency guarantee. Both produced one paragraph and the requested point count (STATIC 4, SHORT 3). Raw outputs are displayed to the user without post-editing; review findings below are separate from the generated text.

## Claim-by-claim transcript grounding review

This compares summaries with the supplied ASR text, not with the recording or a human reference. Supported here means supported by that transcript; it does not certify the transcript's factual or word accuracy.

| Output claim | Source support / assessment |
|---|---|
| STATIC paragraph: the lecture guides defining both static variables and static functions | Overstatement. The opening announces both, but the supplied excerpt develops static variables, not how to define a static function. The prompt explicitly prohibited elaborating merely announced topics; this failure remains. |
| STATIC paragraph and point 1: instance variables are created separately for each object | Directly supported by the repeated explanation that another object gets another set of variables in memory. Central distinction preserved. |
| STATIC paragraph and point 2: a static variable is shared by all objects (of the class) | Sharing is directly supported. Same-class scope is a reasonable interpretation of the single-class example, not stated verbatim as a general rule. |
| STATIC paragraph / point 3: static means the variable belongs to the class rather than the object | Not directly stated in this form. The transcript states not belonging to an object and sharing among objects; class ownership is an added conceptual inference. The phrase about the nature of the class is also awkward Hebrew. Under strict transcript-only requirements this should be omitted or qualified. |
| STATIC paragraph: not newly created for every object, exists only once | Not recreated per object is directly supported. Only once is a stronger inferred paraphrase within that class/example, not an explicit general lifetime/count claim in the transcript. |
| STATIC point 4: cannot access the static variable through an object | The speaker makes that claim near the end, so it is transcript-grounded. This review does not certify a universal programming-language rule or validate the lecturer's code. |
| STATIC negation handling | The central object-specific versus shared/non-object distinction is retained. The unclear 00:58–01:02 ASR phrase is not repeated; omission does not establish that its spoken meaning was recovered. |
| SHORT paragraph: OOP is popular and organizes code around objects | Direct support in the opening; point 1 repeats the organization theme. Classes are explicitly used in the examples. |
| SHORT paragraph: classes are blueprints for instances with attributes and methods | Supported by the vehicle/attributes/methods/blueprint/instance passage. |
| SHORT paragraph: boat inherits from vehicle and adds its own functionality | Correct source direction preserved: class boat inherits vehicle functions/data and has its own methods. No reversal was found. |
| SHORT paragraph and point 2: inheritance lets new classes inherit properties/methods from existing classes | Supported paraphrase of the example. Functions/data versus properties/methods does not reverse the relationship. |
| SHORT paragraph and point 3: mutable object state complicates debugging, especially when passed around | Direct support in the closing critique. No new recommendation/fact was found. |

No summary edits/corrections or second attempts were made. English is coherent and closely grounded. Hebrew preserves the essential contrast but contains an announced-topic overclaim and conceptual extrapolations despite the prompt. No invented garbled code-variable name was reproduced.

## Recommendation (proposal, not approved implementation)

The observations support an initial, explicitly labeled draft-summary integration for lecturer review, with a replaceable local provider, fixed paragraph/3–5-point validation, unchanged access/retention rules, visible automatic-error warning and access to the transcript. They do not justify presenting Hebrew output as fully verified or automatically publishing it to students. Before treating quality as accepted, include regression checks for merely announced topics, class-ownership extrapolation, negation scope and boat-to-vehicle direction; tighten the prompt and validate on further samples in a separately approved stage. Local loading/generation should remain outside the request and the ASR model should be unloaded before loading Qwen on this 8-GB GPU. These are recommendations only: the website summarizer remains disabled.

Only the standalone probe and these documentation findings were added/updated; website regression tests were not run for this experiment. The script was compiled and both real CLI generations executed. Gemini hashes were checked unchanged. No commit or push.

## Subsequent approved integration

The user subsequently approved an initial website/worker integration. The earlier disabled-status statements above describe the initial experiment. Current behavior, prompt revisions, successful English route and rejected wrong-language STATIC route are recorded in [local-summaries.md](local-summaries.md) and testing.md. Initial-prompt findings above remain historical evidence rather than a quality pass.
