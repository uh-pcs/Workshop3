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
