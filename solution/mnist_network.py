"""Workshop 3 final solution: a neural network built from PyTorch tensors."""

import torch
import torchvision


torch.manual_seed(0)


class Linear:
    """One learned matrix multiplication: x @ weights + bias."""

    def __init__(self, in_features, out_features):
        self.weights = torch.randn(in_features, out_features) * (
            2 / in_features
        ) ** 0.5
        self.bias = torch.zeros(out_features)

        self.weights.requires_grad_()
        self.bias.requires_grad_()

    def forward(self, x):
        return x @ self.weights + self.bias

    def parameters(self):
        return [self.weights, self.bias]


class ReLU:
    """Keep positive values and replace negative values with zero."""

    def forward(self, x):
        return x.clamp(min=0)


class NeuralNetwork:
    """Three linear layers with a ReLU bend between each pair."""

    def __init__(self, input_size, hidden_size, output_size):
        self.layer1 = Linear(input_size, hidden_size)
        self.layer2 = Linear(hidden_size, hidden_size)
        self.layer3 = Linear(hidden_size, output_size)

        self.relu1 = ReLU()
        self.relu2 = ReLU()

    def forward(self, x):
        x = self.layer1.forward(x)
        x = self.relu1.forward(x)

        x = self.layer2.forward(x)
        x = self.relu2.forward(x)

        x = self.layer3.forward(x)
        return x

    def parameters(self):
        return (
            self.layer1.parameters()
            + self.layer2.parameters()
            + self.layer3.parameters()
        )


def load_data(root="./data", train_limit=None):
    """Download MNIST and turn every 28x28 image into 784 numbers."""

    train_data = torchvision.datasets.MNIST(
        root=root,
        train=True,
        download=True,
    )
    test_data = torchvision.datasets.MNIST(
        root=root,
        train=False,
        download=True,
    )

    x = train_data.data.float().view(-1, 784) / 255.0
    target = train_data.targets
    if train_limit is not None:
        x = x[:train_limit]
        target = target[:train_limit]

    x_test = test_data.data.float().view(-1, 784) / 255.0
    target_test = test_data.targets
    return x, target, x_test, target_test


def accuracy(scores, targets):
    """Return the fraction of rows whose largest score names the right digit."""

    guesses = scores.argmax(dim=1)
    return (guesses == targets).float().mean().item()


def main():
    x, target, x_test, target_test = load_data()
    model = NeuralNetwork(784, 128, 10)

    learning_rate = 0.1
    epochs = 10  # Final experiment: change this to 60.

    for epoch in range(1, epochs + 1):
        # 1. FORWARD PASS: make a guess.
        prediction = model.forward(x)

        # 2. LOSS: measure how wrong the guess was.
        loss = torch.nn.functional.cross_entropy(prediction, target)

        # 3. BACKPROPAGATION: calculate every weight's gradient.
        loss.backward()

        # 4. UPDATE WEIGHTS: take a small step in the better direction.
        with torch.no_grad():
            for parameter in model.parameters():
                parameter -= learning_rate * parameter.grad

        # Gradients add up by default, so clear them before the next guess.
        for parameter in model.parameters():
            parameter.grad.zero_()

        # 5. REPEAT, pausing occasionally to watch learning happen.
        if epoch == 1 or epoch % 10 == 0 or epoch == epochs:
            with torch.no_grad():
                test_accuracy = accuracy(model.forward(x_test), target_test)

            print(
                f"epoch {epoch:3d}  "
                f"loss {loss.item():.4f}  "
                f"test_acc {test_accuracy:.4f}"
            )


if __name__ == "__main__":
    main()
