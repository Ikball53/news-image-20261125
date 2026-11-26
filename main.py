"""Deliver the finished artwork to the grader.

The picture itself is finished already and ships next to this script as
entry.png. This runner does no drawing and no downloading: it just places
an exact copy of that file where the grader expects it, so the pixels the
grader sees are always the same ones we reviewed.
"""

import os
import sys

# Name of the artwork file that travels with this script.
ARTWORK_NAME = "entry.png"

# Fallback folder used when the grader does not point us anywhere.
DEFAULT_OUTPUT_DIR = "/output"

# How much data to move per read/write step (64 KiB).
CHUNK_SIZE = 65536


def script_folder():
    """Folder holding this script (and therefore the artwork)."""
    return os.path.dirname(os.path.abspath(__file__))


def pick_output_folder():
    """Decide where the copy should land.

    Priority: the grader's MAKEFUN_OUTPUT_DIR when it names a real
    directory, then /output when it exists, then the working directory.
    """
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    if os.path.isdir(DEFAULT_OUTPUT_DIR):
        return DEFAULT_OUTPUT_DIR
    return os.getcwd()


def copy_file(source_path, target_path):
    """Copy a file in chunks; return the number of bytes written."""
    written = 0
    with open(source_path, "rb") as source, open(target_path, "wb") as target:
        while True:
            block = source.read(CHUNK_SIZE)
            if not block:
                break
            target.write(block)
            written += len(block)
    return written


def main():
    source_path = os.path.join(script_folder(), ARTWORK_NAME)
    if not os.path.isfile(source_path):
        print(f"error: bundled image not found: {source_path}", file=sys.stderr)
        return 1

    expected_size = os.path.getsize(source_path)

    output_folder = pick_output_folder()
    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output directory {output_folder}: {exc}",
              file=sys.stderr)
        return 1

    target_path = os.path.join(output_folder, ARTWORK_NAME)
    try:
        written = copy_file(source_path, target_path)
    except OSError as exc:
        print(f"error: failed to write {target_path}: {exc}", file=sys.stderr)
        return 1

    if written != expected_size:
        print(
            f"error: byte count mismatch for {target_path}: "
            f"wrote {written} bytes, expected {expected_size}",
            file=sys.stderr,
        )
        return 1

    on_disk = os.path.getsize(target_path)
    if on_disk != expected_size:
        print(
            f"error: on-disk size mismatch for {target_path}: "
            f"found {on_disk} bytes, expected {expected_size}",
            file=sys.stderr,
        )
        return 1

    print(f"wrote {target_path} ({written} bytes, byte-identical copy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
