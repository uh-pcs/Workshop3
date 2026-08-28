"""Optional helpers for looking inside the trained network.

This is NOT part of the file you build in the workshop. The notebook imports it
after training so the room can see a real prediction, the model's mistakes, the
pictures its first layer learned, and the learning curve.

Every function here uses only the classes you wrote in ``mnist_network.py``.
"""

import torch

from mnist_network import NeuralNetwork, accuracy, load_data


def quick_train(epochs=15, learning_rate=0.1):
    """Train a fresh network and return it with the test data and a history.

    This repeats the same five-step loop from ``main()`` so we end up with a
    trained model living here in the notebook, ready to inspect.
    """

    x, target, x_test, target_test = load_data()
    model = NeuralNetwork(784, 128, 10)
    history = {"epoch": [], "loss": [], "test_acc": []}

    for epoch in range(1, epochs + 1):
        prediction = model.forward(x)
        loss = torch.nn.functional.cross_entropy(prediction, target)
        loss.backward()

        with torch.no_grad():
            for parameter in model.parameters():
                parameter -= learning_rate * parameter.grad

        for parameter in model.parameters():
            parameter.grad.zero_()

        with torch.no_grad():
            test_acc = accuracy(model.forward(x_test), target_test)

        history["epoch"].append(epoch)
        history["loss"].append(loss.item())
        history["test_acc"].append(test_acc)
        print(f"epoch {epoch:3d}  loss {loss.item():.4f}  test_acc {test_acc:.4f}")

    return model, x_test, target_test, history


def predict(model, images):
    """Return the model's guessed digit for each row of ``images``."""

    with torch.no_grad():
        return model.forward(images).argmax(dim=1)


def show_digit(image_row, guess=None, truth=None):
    """Print one 784-value image as ASCII art."""

    pixels = image_row.detach().reshape(28, 28)
    ramp = " .:-=+*#%@"
    for row in pixels:
        print("".join(ramp[min(int(value.item() * 10), 9)] for value in row))
    if guess is not None or truth is not None:
        print(f"\nmodel's guess: {guess}    true digit: {truth}")


def worst_mistakes(model, x_test, target_test, k=8):
    """Return the indices of the most confident wrong predictions."""

    with torch.no_grad():
        probabilities = model.forward(x_test).softmax(dim=1)

    guesses = probabilities.argmax(dim=1)
    wrong = guesses != target_test
    confidence = probabilities.max(dim=1).values.clone()
    confidence[~wrong] = -1.0
    return confidence.argsort(descending=True)[:k].tolist()


def plot_history(history):
    """Plot loss and test accuracy over epochs (needs matplotlib)."""

    import matplotlib.pyplot as plt

    figure, (left, right) = plt.subplots(1, 2, figsize=(10, 4))

    left.plot(history["epoch"], history["loss"], marker="o")
    left.set_title("loss goes down")
    left.set_xlabel("epoch")
    left.set_ylabel("loss")

    right.plot(history["epoch"], history["test_acc"], marker="o", color="green")
    right.axhline(0.1, linestyle="--", color="gray", label="blind guessing")
    right.set_title("accuracy goes up")
    right.set_xlabel("epoch")
    right.set_ylabel("test accuracy")
    right.set_ylim(0, 1)
    right.legend()

    figure.tight_layout()
    plt.show()


def layer1_weight_grid(model, rows=8, cols=16):
    """Show each first-layer weight column as a 28x28 picture (needs matplotlib)."""

    import matplotlib.pyplot as plt

    weights = model.layer1.weights.detach()
    figure, axes = plt.subplots(rows, cols, figsize=(cols, rows))
    for index, axis in enumerate(axes.flat):
        axis.axis("off")
        if index < weights.shape[1]:
            axis.imshow(weights[:, index].reshape(28, 28), cmap="RdBu")
    figure.suptitle("what each hidden unit looks for")
    plt.show()
