"""Recovery checkpoint after students finish the Linear class."""

import torch


torch.manual_seed(0)


class Linear:
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
