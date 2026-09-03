"""PCS Workshop Intro: a neural network that reads handwritten digits."""

import torch
import torchvision


# Seeded so the whole room sees the same numbers. Real training does not seed.
torch.manual_seed(0)


def report(epoch, loss, model, x_test, target_test):
    """Print one progress line. Provided for you - not part of the lesson."""

    with torch.no_grad():
        test_acc = accuracy(model.forward(x_test), target_test)
    print(f"epoch {epoch:3d}   loss {loss.item():.4f}"
          f"   test_acc {test_acc:.4f}")


class Linear:
    """One learned matrix multiplication: x @ weights + bias."""

    def __init__(self, in_features, out_features):
        std = (2 / in_features) ** 0.5
        self.weights = torch.randn(in_features, out_features) * std
        self.bias = torch.zeros(out_features)

        self.weights.requires_grad_()
        self.bias.requires_grad_()

    def forward(self, x):
        return x @ self.weights + self.bias

    def parameters(self):
        return [self.weights, self.bias]


class ReLU:
    """Keep positive values, replace negative values with zero."""

    def forward(self, x):
        return x.clamp(min=0)


class NeuralNetwork:
    """Three Linear layers with a ReLU bend between each pair."""

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


def load_data():
    """Load MNIST and turn every 28x28 image into a row of 784 numbers."""

    train = torchvision.datasets.MNIST(
        root="./data", train=True, download=True)
    test = torchvision.datasets.MNIST(
        root="./data", train=False, download=True)

    x = train.data.float().view(-1, 784) / 255.0
    target = train.targets
    x_test = test.data.float().view(-1, 784) / 255.0
    target_test = test.targets
    return x, target, x_test, target_test


def accuracy(scores, targets):
    """The fraction of rows whose largest score names the right digit."""

    return (scores.argmax(dim=1) == targets).float().mean().item()


def main():
    x, target, x_test, target_test = load_data()
    model = NeuralNetwork(784, 128, 10)
    learning_rate = 0.1
    epochs = 10

    for epoch in range(1, epochs + 1):
        # 1. FORWARD PASS: make a guess.
        prediction = model.forward(x)

        # 2. LOSS: measure how wrong the guess was.
        loss = torch.nn.functional.cross_entropy(prediction, target)

        # 3. BACKPROPAGATION: find every weight's gradient.
        loss.backward()

        # 4. UPDATE WEIGHTS: take one small step downhill.
        with torch.no_grad():
            for parameter in model.parameters():
                parameter -= learning_rate * parameter.grad

        # 5. CLEAR the gradients, then repeat.
        for parameter in model.parameters():
            parameter.grad.zero_()

        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            report(epoch, loss, model, x_test, target_test)


if __name__ == "__main__":
    main()
