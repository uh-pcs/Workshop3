import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "mnist_workshop.ipynb"

STEP_PARTS = [
    "01_linear.py",
    "02_relu.py",
    "03_network.py",
    "04_data.py",
    "05_main.py",
]


def load_notebook():
    assert NOTEBOOK_PATH.exists(), "The Colab workbench has not been created"
    return json.loads(NOTEBOOK_PATH.read_text())


def code_sources(notebook):
    return [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]


def markdown_sources(notebook):
    return [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
    ]


def without_magics(source):
    """Blank out IPython magics and shell escapes so the rest can be parsed."""

    return "\n".join(
        "" if line.lstrip().startswith(("%", "!")) else line
        for line in source.splitlines()
    )


def test_notebook_is_valid_version_four_json_with_python_code_cells():
    """Every runnable cell must parse.

    `%%writefile` cells are skipped: their body is file content for the student
    to fill in, never executed as notebook code.
    """

    notebook = load_notebook()

    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["kernelspec"]["language"] == "python"
    for source in code_sources(notebook):
        if "%%writefile" in source:
            continue
        ast.parse(without_magics(source))


def test_setup_clones_the_org_repo_and_preloads_mnist():
    setup = code_sources(load_notebook())[0]

    assert "https://github.com/uh-pcs/Workshop3.git" in setup
    assert "facilitator/parts/00_header.py" in setup
    assert "/content/mnist_network.py" in setup
    assert "torchvision.datasets.MNIST" in setup
    assert "torch.cuda.is_available()" in setup


def test_setup_defines_the_build_progress_check_and_recover_helpers():
    setup = code_sources(load_notebook())[0]

    for helper in ("def progress(", "def build(", "def run_check(", "def recover("):
        assert helper in setup, helper


def test_there_is_one_writefile_step_cell_per_part_in_order():
    """Each STEP cell writes exactly one numbered part, in the taught order."""

    sources = code_sources(load_notebook())
    written = [
        re.search(r"%%writefile\s+/content/parts/(\S+)", source).group(1)
        for source in sources
        if "%%writefile" in source
    ]

    assert written == STEP_PARTS


def test_step_cells_are_empty_scaffolds_for_the_student_to_type_into():
    """Students type the code from the slides; the cells must not pre-fill it."""

    for source in code_sources(load_notebook()):
        if "%%writefile" not in source:
            continue
        body = [
            line
            for line in source.splitlines()[1:]
            if line.strip() and not line.strip().startswith("#")
        ]
        assert body == [], f"STEP cell already contains code: {body}"


def test_every_step_cell_names_the_slide_it_matches():
    """The room must be able to see which slide a cell belongs to."""

    for source in code_sources(load_notebook()):
        if "%%writefile" in source:
            assert re.search(r"slide \d+", source), source.splitlines()[:2]


def test_three_checkpoints_run_the_students_file_through_run_check():
    sources = code_sources(load_notebook())
    checks = [s for s in sources if "run_check(" in s and "def run_check" not in s]

    assert len(checks) == 3
    assert any("Linear" in s and "(3, 128)" in s for s in checks)
    assert any("NeuralNetwork" in s and "(4, 10)" in s for s in checks)
    assert any("loss_after < loss_before" in s for s in checks)


def test_checkpoints_explain_the_failure_instead_of_raising_a_bare_assertion():
    """A red traceback in a live room stalls a beginner; give them a hint."""

    checks = [
        s
        for s in code_sources(load_notebook())
        if "run_check(" in s and "def run_check" not in s
    ]

    for source in checks:
        assert "raise SystemExit" in source
        assert "assert " not in source


def test_the_recovery_lane_covers_every_step():
    sources = code_sources(load_notebook())
    calls = sorted(
        int(m.group(1))
        for s in sources
        if (m := re.match(r"\s*recover\((\d)\)", s))
    )

    assert calls == [1, 2, 3, 4, 5]


def test_notebook_runs_the_file_and_offers_the_download():
    combined = "\n".join(code_sources(load_notebook()))

    assert "files.download" in combined
    assert str("subprocess.run([sys.executable, str(WORK_FILE)]") in combined


def test_the_notebook_explains_that_file_save_is_not_how_you_keep_your_work():
    combined = "\n".join(markdown_sources(load_notebook()))

    assert "File → Save" in combined
    assert "mnist_network.py" in combined
