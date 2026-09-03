import ast
import importlib.util
import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
SOLUTION_PATH = ROOT / "solution" / "mnist_network.py"
PARTS_DIR = ROOT / "facilitator" / "parts"

sys.path.insert(0, str(ROOT / "facilitator"))
from build_file import assemble  # noqa: E402


def load_module(path: Path, name: str):
    assert path.exists(), f"Missing workshop artifact: {path.relative_to(ROOT)}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_linear_forward_performs_matrix_multiply_and_bias():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_linear")
    layer = workshop.Linear(2, 2)

    with torch.no_grad():
        layer.weights.copy_(torch.tensor([[1.0, 2.0], [3.0, 4.0]]))
        layer.bias.copy_(torch.tensor([0.5, -0.5]))

    output = layer.forward(torch.tensor([[2.0, 1.0]]))

    assert torch.equal(output, torch.tensor([[5.5, 7.5]]))


def test_relu_clamps_negative_values_without_changing_positive_values():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_relu")

    output = workshop.ReLU().forward(torch.tensor([-2.0, 0.0, 3.0]))

    assert torch.equal(output, torch.tensor([0.0, 0.0, 3.0]))


def test_network_maps_784_inputs_to_ten_scores_and_exposes_six_parameters():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_shapes")
    model = workshop.NeuralNetwork(784, 128, 10)

    output = model.forward(torch.zeros(4, 784))
    parameters = model.parameters()

    assert output.shape == (4, 10)
    assert len(parameters) == 6
    assert all(parameter.requires_grad for parameter in parameters)
    assert all(parameter.is_leaf for parameter in parameters)


def test_backward_and_manual_update_reduce_loss_on_a_fixed_problem():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_learning")
    torch.manual_seed(0)
    model = workshop.NeuralNetwork(2, 4, 2)
    x = torch.tensor([[2.0, 0.0], [0.0, 2.0]])
    target = torch.tensor([0, 1])

    first_loss = torch.nn.functional.cross_entropy(model.forward(x), target)
    first_loss.backward()
    assert all(parameter.grad is not None for parameter in model.parameters())

    with torch.no_grad():
        for parameter in model.parameters():
            parameter -= 0.1 * parameter.grad

    for parameter in model.parameters():
        parameter.grad.zero_()

    second_loss = torch.nn.functional.cross_entropy(model.forward(x), target)

    assert second_loss.item() < first_loss.item()
    assert all(torch.count_nonzero(p.grad) == 0 for p in model.parameters())


def test_accuracy_uses_the_largest_score_as_the_prediction():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_accuracy")
    scores = torch.tensor([[0.0, 3.0, 1.0], [4.0, 2.0, 0.0]])
    targets = torch.tensor([1, 2])

    assert workshop.accuracy(scores, targets) == 0.5


def test_solution_avoids_high_level_layers_and_optimizers():
    tree = ast.parse(SOLUTION_PATH.read_text())
    forbidden_attributes = {"Linear", "Sequential", "SGD", "Adam"}

    used_forbidden_names = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr in {"nn", "optim"}
        and node.attr in forbidden_attributes
    }

    assert used_forbidden_names == set()


# --------------------------------------------------------------- the parts
# facilitator/parts/ is the single source of truth: the notebook's STEP cells
# write those same fragments, and solution/mnist_network.py is generated from
# them. If these drift, the slides, the notebook, and the answer key disagree.

EXPECTED_PARTS = [
    "00_header.py",
    "01_linear.py",
    "02_relu.py",
    "03_network.py",
    "04_data.py",
    "05_main.py",
]


def test_the_expected_parts_exist():
    assert [p.name for p in sorted(PARTS_DIR.glob("*.py"))] == EXPECTED_PARTS


def test_parts_assemble_into_exactly_the_committed_solution():
    assert assemble(PARTS_DIR) == SOLUTION_PATH.read_text(), (
        "solution/mnist_network.py is stale - regenerate it with:\n"
        "  python3 facilitator/build_file.py facilitator/parts solution/mnist_network.py"
    )


def test_the_file_is_importable_after_every_step(tmp_path):
    """A student who stops after any STEP still has a file that runs."""

    for stop in range(len(EXPECTED_PARTS)):
        stage = tmp_path / f"stage{stop}"
        stage.mkdir()
        for name in EXPECTED_PARTS[: stop + 1]:
            (stage / name).write_text((PARTS_DIR / name).read_text())
        compile(assemble(stage), f"stage{stop}", "exec")


def test_every_part_fits_a_slide_code_panel():
    """Long lines wrap badly on a projector; keep the taught code narrow."""

    for part in sorted(PARTS_DIR.glob("*.py")):
        for number, line in enumerate(part.read_text().splitlines(), 1):
            assert len(line) <= 79, f"{part.name}:{number} is {len(line)} chars"
