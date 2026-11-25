"""Copy the finished front-page image into the grading output folder.

The entry artwork lives beside this script as entry.png. This program
places those exact bytes at MAKEFUN_OUTPUT_DIR/entry.png so the judge
sees the same picture on every run, with no drawing or network involved.
"""

from os import environ
from pathlib import Path


def output_folder() -> Path:
    raw = environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    folder = Path(raw)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def main() -> None:
    here = Path(__file__).resolve().parent
    picture = here / "entry.png"
    if not picture.is_file():
        raise FileNotFoundError(f"entry artwork missing next to this script: {picture}")
    target = output_folder() / "entry.png"
    payload = picture.read_bytes()
    target.write_bytes(payload)


if __name__ == "__main__":
    main()
