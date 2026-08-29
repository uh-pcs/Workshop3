import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = ("Workshop 1", "Workshop 2", "Workshop 3", "Workshop1", "Workshop2")


def notebook_markdown():
    notebook = json.loads((ROOT / "mnist_workshop.ipynb").read_text())
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
    )


def visible_copy():
    parts = [
        (ROOT / "README.md").read_text(),
        (ROOT / "FACILITATOR.md").read_text(),
        (ROOT / "EXTENSIONS.md").read_text(),
        notebook_markdown(),
    ]
    slides = ROOT / "docs" / "slides.md"
    if slides.exists():
        parts.append(slides.read_text())
    return "\n".join(parts)


def test_workshop_is_presented_as_the_intro():
    text = visible_copy()
    assert "PCS Workshop Intro" in text
    for forbidden in FORBIDDEN:
        assert forbidden not in text, forbidden


def test_repository_urls_point_at_the_org():
    readme = (ROOT / "README.md").read_text()
    assert "github.com/uh-pcs/Workshop3" in readme
    assert "github/uh-pcs/Workshop3/blob/main/mnist_workshop.ipynb" in readme


def test_notebook_colab_title_uses_the_intro_name():
    notebook = json.loads((ROOT / "mnist_workshop.ipynb").read_text())
    colab = notebook["metadata"].get("colab", {})
    if "name" in colab:
        assert "PCS Workshop Intro" in colab["name"]
        for forbidden in FORBIDDEN:
            assert forbidden not in colab["name"], forbidden
