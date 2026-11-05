"""Download one official SYSTRAN model; never call a hosted inference service."""
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / ".ai-lab"
os.environ["HF_HOME"] = str(LAB / "hf-cache")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import HfApi, snapshot_download

start = time.perf_counter()
repo = "Systran/faster-whisper-medium"
info = HfApi().model_info(repo, files_metadata=True, token=False)
patterns = ["config.json", "model.bin", "tokenizer.json", "vocabulary.txt", "vocabulary.json", "preprocessor_config.json"]
files = [{"name": f.rfilename, "size": f.size} for f in info.siblings if f.rfilename in patterns]
print(json.dumps({"repo": repo, "revision": info.sha, "files": files}), flush=True)
snapshot_download(repo, revision=info.sha, token=False, allow_patterns=patterns,
                  local_dir=LAB / "models" / "faster-whisper-medium")
result = {"repo": repo, "revision": info.sha, "files": files,
          "download_wall_s": time.perf_counter() - start}
target = Path(__file__).parent / "results" / "asr_model.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result), flush=True)
