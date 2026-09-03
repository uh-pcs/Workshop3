"""The deck and the file the students build must show the same code.

Slides 5, 7, 9 and 12 put real Python on the projector. If someone edits the
solution without editing `slides/build_deck.py` (or the reverse), the room ends
up typing code that does not match what the checkpoints expect. That happened
once; these tests make it impossible to happen quietly.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "slides" / "build_deck.py"
PARTS_DIR = ROOT / "facilitator" / "parts"

sys.path.insert(0, str(ROOT / "facilitator"))
from build_file import assemble  # noqa: E402


def slide_code_panels():
    """Every `code_panel([...])` literal in the deck builder, as line lists."""

    tree = ast.parse(DECK.read_text())
    panels = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", None) != "code_panel":
            continue
        if not node.args or not isinstance(node.args[0], ast.List):
            continue
        if not all(isinstance(e, ast.Constant) for e in node.args[0].elts):
            continue
        panels.append([e.value for e in node.args[0].elts])
    return panels


def python_panels():
    """The panels that show real Python, not a shape formula or a diagram."""

    return [
        lines
        for lines in slide_code_panels()
        if any(line.lstrip().startswith(("def ", "class ")) for line in lines)
        or any("torch." in line for line in lines)
    ]


def stripped(lines):
    return [line.strip() for line in lines if line.strip()]


def test_the_deck_actually_shows_python():
    panels = python_panels()

    assert len(panels) >= 5, f"only found {len(panels)} code panels with Python"


def test_every_line_of_slide_code_appears_verbatim_in_the_students_file():
    """Indentation may differ (a slide can show a fragment); the code may not."""

    file_lines = stripped(assemble(PARTS_DIR).splitlines())

    for lines in python_panels():
        for line in stripped(lines):
            assert line in file_lines, (
                f"slide shows a line that is not in the file the students build:\n"
                f"    {line}\n"
                f"Fix slides/build_deck.py or facilitator/parts/, then rebuild both."
            )


def test_slide_code_keeps_the_same_order_as_the_file():
    """Typing a panel top to bottom must build the file top to bottom.

    Matched as a subsequence, not a contiguous run: a panel legitimately skips
    the docstrings and the numbered `# 1. FORWARD PASS` comments in the file.
    """

    file_lines = stripped(assemble(PARTS_DIR).splitlines())

    for lines in python_panels():
        panel = stripped(lines)
        cursor = 0
        for line in panel:
            remaining = file_lines[cursor:]
            assert line in remaining, (
                f"slide code is out of order relative to the file.\n"
                f"    {line!r} does not appear after the line before it."
            )
            cursor += remaining.index(line) + 1


def test_the_taught_class_definitions_are_shown_in_full():
    """A student cannot type a method that was never on screen (see: parameters)."""

    shown = {line for lines in python_panels() for line in stripped(lines)}

    required = [
        "class Linear:",
        "class ReLU:",
        "class NeuralNetwork:",
        "def load_data():",
        "def accuracy(scores, targets):",
        "def main():",
        "def parameters(self):",
        "def forward(self, x):",
    ]
    for line in required:
        assert line in shown, f"the deck never shows `{line}`"


def test_each_step_slide_is_labelled_with_its_notebook_step():
    """The kicker is how a student knows which cell to type into."""

    deck = DECK.read_text()

    for step in range(1, 6):
        assert f'kicker("STEP {step}' in deck, f"no slide is labelled STEP {step}"


def facilitator_python_blocks():
    """Every ```python fence in the facilitator guide."""

    text = (ROOT / "FACILITATOR.md").read_text()
    blocks, current = [], None
    for line in text.splitlines():
        if line.strip() == "```python":
            current = []
        elif line.strip() == "```" and current is not None:
            blocks.append(current)
            current = None
        elif current is not None:
            current.append(line)
    return blocks


def test_facilitator_code_reveals_match_the_students_file():
    """The guide is what the facilitator types on screen; it must agree too."""

    file_lines = stripped(assemble(PARTS_DIR).splitlines())

    for block in facilitator_python_blocks():
        cursor = 0
        for line in stripped(block):
            remaining = file_lines[cursor:]
            assert line in remaining, (
                f"FACILITATOR.md shows a line that is not in the students' file, "
                f"or shows it out of order:\n    {line}"
            )
            cursor += remaining.index(line) + 1
