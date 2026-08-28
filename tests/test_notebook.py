import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "mnist_workshop.ipynb"


def load_notebook():
    assert NOTEBOOK_PATH.exists(), "The Colab workbench has not been created"
    return json.loads(NOTEBOOK_PATH.read_text())


def code_sources(notebook):
    return [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]


def test_notebook_is_valid_version_four_json_with_python_code_cells():
    notebook = load_notebook()

    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["kernelspec"]["language"] == "python"
    for source in code_sources(notebook):
        ast.parse(source)


def test_setup_clones_public_repo_copies_starter_and_preloads_mnist():
    notebook = load_notebook()
    setup = code_sources(notebook)[0]

    assert "https://github.com/daryl-888/Workshop3.git" in setup
    assert "starter/mnist_network.py" in setup
    assert "/content/mnist_network.py" in setup
    assert "torchvision.datasets.MNIST" in setup
    assert "torch.cuda.is_available()" in setup


def test_checkpoints_run_student_file_in_fresh_python_processes():
    notebook = load_notebook()
    sources = code_sources(notebook)
    checkpoint_sources = [source for source in sources if "CHECKPOINT" in source]

    assert len(checkpoint_sources) == 3
    assert all("subprocess.run" in source for source in checkpoint_sources)
    assert all("sys.executable" in source for source in checkpoint_sources)
    assert any("Linear" in source and "(3, 128)" in source for source in checkpoint_sources)
    assert any("NeuralNetwork" in source and "(4, 10)" in source for source in checkpoint_sources)
    assert any("loss_after < loss_before" in source for source in checkpoint_sources)


def test_notebook_has_recovery_final_run_and_file_download_actions():
    notebook = load_notebook()
    combined = "\n".join(code_sources(notebook))

    assert "04-complete.py" in combined
    assert "mnist_network.py" in combined
    assert "files.download" in combined
    assert "Final run" in combined
