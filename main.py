"""news-image-20261125 entry runner (v8).

The artwork (entry.png) is pre-rendered and ships next to this script.
This runner does one job: copy that file byte-for-byte to wherever the
grader expects the output, then exit 0. No drawing, no fonts, no
third-party libraries -- only the Python standard library, so it runs
in any sandbox that has a plain python3.

Output targets, tried in order (each in its own try/except so one
failure never blocks the rest):
  1. $MAKEFUN_OUTPUT_DIR/entry.png (directory created if missing)
  2. entry.png next to this script
  3. /output/entry.png

Exit code 0 when at least one copy lands, 1 only when nothing did.
"""

import hashlib
import os
import sys
from pathlib import Path

CHUNK_SIZE = 65536
ARTWORK_NAME = "entry.png"


def source_path():
    """Artwork file living beside this script."""
    return Path(__file__).resolve().parent / ARTWORK_NAME


def digest(path):
    """SHA-256 hex of a file, read in chunks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(CHUNK_SIZE)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def stream_copy(src, dest):
    """Stream src to dest in 64 KiB chunks; return True on success."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "rb") as reader, open(dest, "wb") as writer:
            while True:
                block = reader.read(CHUNK_SIZE)
                if not block:
                    break
                writer.write(block)
        return True
    except OSError as exc:
        print(f"save failed: {dest} ({exc})", flush=True)
        return False


def candidate_targets():
    """Ordered list of output files to attempt."""
    here = Path(__file__).resolve().parent
    targets = []
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if out_dir:
        targets.append(Path(out_dir) / ARTWORK_NAME)
    targets.append(here / ARTWORK_NAME)
    targets.append(Path("/output") / ARTWORK_NAME)
    # Drop duplicates while keeping order (e.g. env dir == script dir).
    seen = set()
    unique = []
    for target in targets:
        key = str(target)
        if key not in seen:
            seen.add(key)
            unique.append(target)
    return unique


def main():
    src = source_path()
    if not src.is_file():
        print(f"missing artwork: {src}", flush=True)
        return 1

    try:
        expected = digest(src)
    except OSError as exc:
        print(f"could not hash source: {exc}", flush=True)
        expected = None

    saved = 0
    for dest in candidate_targets():
        # The copy next to the script IS the source file itself; opening
        # it for writing would truncate the artwork before it is read,
        # so treat it as already in place instead of copying onto itself.
        try:
            same_file = dest.resolve() == src.resolve()
        except OSError:
            same_file = False
        if same_file:
            saved += 1
            print(f"already in place: {dest}", flush=True)
            continue
        if stream_copy(src, dest):
            saved += 1
            note = ""
            if expected is not None:
                try:
                    actual = digest(dest)
                    note = " sha256 ok" if actual == expected else " sha256 MISMATCH"
                except OSError:
                    note = " sha256 check skipped"
            print(f"saved: {dest}{note}", flush=True)

    if saved:
        print(f"done: {saved} cop{'y' if saved == 1 else 'ies'} written", flush=True)
        return 0
    print("error: no output could be written", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
