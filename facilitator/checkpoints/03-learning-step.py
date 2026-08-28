"""Recovery checkpoint after loss, backward, update, and gradient clearing."""

import torch


torch.manual_seed(0)


class Linear:
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
    def forward(self, x):
        return x.clamp(min=0)


class NeuralNetwork:
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


def learning_step(model, x, target, learning_rate=0.1):
    prediction = model.forward(x)
    loss = torch.nn.functional.cross_entropy(prediction, target)
    loss.backward()

    with torch.no_grad():
        for parameter in model.parameters():
            parameter -= learning_rate * parameter.grad

    for parameter in model.parameters():
        parameter.grad.zero_()

    return loss.item()
