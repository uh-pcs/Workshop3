import ast
import importlib.util
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
SOLUTION_PATH = ROOT / "solution" / "mnist_network.py"


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
    assert all(torch.count_nonzero(parameter.grad) == 0 for parameter in model.parameters())


def test_accuracy_uses_the_largest_score_as_the_prediction():
    workshop = load_module(SOLUTION_PATH, "workshop_solution_accuracy")
    scores = torch.tensor([[0.0, 3.0, 1.0], [4.0, 2.0, 0.0]])
    targets = torch.tensor([1, 2])

    result = workshop.accuracy(scores, targets)

    assert result == 0.5


def test_solution_avoids_high_level_layers_and_optimizers():
    assert SOLUTION_PATH.exists(), "The solution must exist before its AST can be checked"
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


def test_every_facilitator_checkpoint_imports_without_running_training():
    checkpoint_dir = ROOT / "facilitator" / "checkpoints"
    expected = [
        "01-linear.py",
        "02-network.py",
        "03-learning-step.py",
        "04-complete.py",
    ]

    for index, filename in enumerate(expected):
        load_module(checkpoint_dir / filename, f"checkpoint_{index}")


def test_final_recovery_checkpoint_is_a_self_contained_complete_program():
    checkpoint = load_module(
        ROOT / "facilitator" / "checkpoints" / "04-complete.py",
        "complete_checkpoint",
    )

    assert checkpoint.NeuralNetwork is not None
    assert checkpoint.load_data is not None
    assert checkpoint.main is not None
