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
