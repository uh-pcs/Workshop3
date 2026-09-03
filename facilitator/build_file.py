#!/usr/bin/env python3
"""Assemble `mnist_network.py` from the numbered parts in a directory.

One source of truth, three consumers:

* the Colab notebook writes a part per STEP cell, then calls this to rebuild
  `/content/mnist_network.py` before each checkpoint;
* `facilitator/parts/` holds the reference parts, used for recovery in the room;
* `solution/mnist_network.py` is generated from those reference parts, so the
  slides, the notebook, and the answer key can never drift apart.

Regenerate the committed solution:

    python3 facilitator/build_file.py facilitator/parts solution/mnist_network.py
"""

import sys
from pathlib import Path


def assemble(parts_dir):
    """Concatenate every `NN_name.py` in `parts_dir`, in numeric order."""

    parts = sorted(Path(parts_dir).glob("*.py"))
    if not parts:
        raise SystemExit(f"No parts found in {parts_dir}")
    bodies = [p.read_text().strip("\n") for p in parts]
    return "\n\n\n".join(bodies) + "\n"


def build(parts_dir, out_path):
    text = assemble(parts_dir)
    Path(out_path).write_text(text)
    return text


if __name__ == "__main__":
    parts_dir = sys.argv[1] if len(sys.argv) > 1 else "facilitator/parts"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "solution/mnist_network.py"
    text = build(parts_dir, out_path)
    print(f"wrote {out_path}  ({text.count(chr(10))} lines)")
