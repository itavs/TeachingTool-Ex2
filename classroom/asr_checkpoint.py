"""Pinned, already-tested offline checkpoint identity; no Django/GPU imports."""
import hashlib
from pathlib import Path

REPO = 'dropbox-dash/faster-whisper-large-v3-turbo'
REVISION = '0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf'
FILE_SHA256 = {
    'config.json': 'b0253ea6c0d3bea6b1e19e91a02acfd3b53f4467362efcb5a3e6b16c9b3a9b7e',
    'model.bin': 'e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da',
    'tokenizer.json': '297b13372ac43916285644fb9687add3cc62ee2a1adb60da3dc25cc94c1871fd',
    'vocabulary.json': 'c69260f2ab26d659b7c398f9a2b2b48ed0df16c3b47d7326782fd9cba71690c1',
    'preprocessor_config.json': '7ccc62c6f2765af1f3b46c00c9b5894426835a05021c8b9c01eecb6dfb542711',
}


def verify_checkpoint(directory):
    """Fail closed for missing/corrupt/different model or tokenizer files."""
    for name, expected in FILE_SHA256.items():
        with (Path(directory) / name).open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != expected:
                raise ValueError('Local transcription checkpoint differs from the tested revision')


def is_expected_metadata(metadata):
    return (isinstance(metadata, dict) and metadata.get('repo') == REPO
            and metadata.get('revision') == REVISION
            and metadata.get('sha256_verified') is True)
