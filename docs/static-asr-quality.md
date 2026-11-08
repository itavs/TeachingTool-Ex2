# STATIC Local ASR Quality Probe — 2026-11-08

## Scope and reproducibility

Local only; no downloads, API requests, payment, application/model-setting changes or rewriting of recognized speech. The existing VideoJob transcript and segments were preserved in an ignored snapshot and verified unchanged after the probe. The 13 outstanding Gemini files were unchanged.

Common sample: **00:55.000–01:35.000**, 40 seconds from STATIC-EXPLNATION.mp4. Selected from saved segment timestamps around dishwasher at 01:17.560–01:22.160, also covering the replacement-character region. Full source audio was decoded/resampled exactly as in production, then cropped by 16-kHz sample indices; the original MP4 was read only. WAV and raw output JSON stay under ignored .ai-lab/results/static-quality in a unique run directory. This crop changes context/decoder window boundaries relative to the original full-video run; its improvements cannot be attributed to forcing Hebrew.

Existing Systran/faster-whisper-medium revision 08e178d48790749d25932bbc082711ddcfdfbc4f; faster-whisper 1.2.1, CTranslate2 4.8.5, PyAV 16.0.0. CUDA float16, threads 8, one worker, beam 5, transcribe, VAD false, condition_on_previous_text false. The only changed argument between the paired runs was language=None versus language='he'. Both reuse one loaded model sequentially; second timing is a warm run, not an independent cold-load benchmark. Offline local-files-only loading and an exclusive media/ASR lock prevent downloads and concurrent website ASR. No prompt, glossary, translation or cleanup was added.

Model load: 1.675 s. Auto: 34.661 s; forced Hebrew: 34.506 s. Auto detected he. Audio hashes match; complete recognized strings differ. One nvidia-smi observation during inference showed 2,749 MiB used and 90% GPU utilization (not peak sampling).

## Locally retained comparison outputs

Raw side-by-side transcript outputs are retained only in ignored local experiment artifacts and are excluded from the published repository.

## Findings and evidence limits

Both cropped outputs have no U+FFFD and no dishwasher, unlike the saved full-video result. Both have more readable portions, but remain insufficiently reliable: an apparent contradiction (belong / do not belong to the object), suspicious words such as להרעכים and אמיק, and unstable phrasing persist. Auto says אירח where fixed Hebrew says ערך and drops אוקיי; these are observed differences, not verified corrections. Neither cropped output retains a Latin programming identifier; קר is Hebrew script and is not proof that a code identifier was preserved accurately. Whether any particular identifier was spoken in this exact window remains unverified against human listening. The pair is not identical despite automatic detection already selecting Hebrew; the runs differ in automatic-language-detection versus explicit-language processing, with no established explanation for every decoding variation.

There is no human reference and no reliable listening comparison here. Word accuracy, meaning, omissions, code-term preservation and WER remain unverified. Linguistic readability alone does not prove source accuracy. No model output was rewritten and neither result replaced the website transcript. Do not proceed as though Hebrew forcing resolves the quality problem.

## Local alternatives and next proposed experiment

Checked the project .ai-lab/models plus standard user Hugging Face, Whisper and Ollama cache locations. Only faster-whisper-medium was found as an ASR model. Ollama Qwen3 4b/8b text models are not substitutes for audio transcription. This is a bounded inventory of these locations, not a whole-disk guarantee.

Proposed next candidate, not downloaded or tested: **Whisper large-v3-turbo**, CTranslate2 conversion **dropbox-dash/faster-whisper-large-v3-turbo** (former mobiuslabsgmbh URL redirects there). Published model.bin approximately 1.62 GB plus approximately 3.8 MB tokenizer/vocabulary/config; budget roughly **1.63 GB download**. It is multilingual and supported by faster-whisper, so it can test a different ASR model using the established runtime rather than add another framework. OpenAI lists roughly 6 GB VRAM for turbo in its own implementation; that suggests feasibility on 8 GB but does not certify this conversion/configuration on this laptop. Use one unbatched float16 instance and confirm actual memory; prior int8_float16 failure remains a reason not to assume quantization works. No accuracy improvement is guaranteed.

Sources checked 2026-11-08: [model file listing](https://huggingface.co/dropbox-dash/faster-whisper-large-v3-turbo/tree/main), [OpenAI model card](https://huggingface.co/openai/whisper-large-v3-turbo), [Whisper resource table](https://github.com/openai/whisper), [faster-whisper turbo usage](https://github.com/SYSTRAN/faster-whisper). Download requires presenting this size/purpose to the user first; none occurred in this probe. Compare the candidate on the identical saved 40-second WAV before considering any website change.

## Subsequent approved turbo experiment

The user subsequently authorized downloading the proposed model and running the full STATIC recording. That experiment is now recorded separately in [static-turbo-quality.md](static-turbo-quality.md). The original paired-medium results above remain unchanged; the website still uses medium.
