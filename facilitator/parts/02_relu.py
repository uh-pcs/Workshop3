class ReLU:
    """Keep positive values, replace negative values with zero."""

    def forward(self, x):
        return x.clamp(min=0)
