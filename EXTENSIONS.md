# Optional Experiments — after the workshop

The core hour ends when your network learns. These experiments change one idea at
a time so you can predict the result before you run it.

Several of them use the helpers in `solution/inspect_model.py`, which the notebook
already imports as `inspect_model`.

## 1. Repeat more or less

Change `epochs` to `1`, `10`, `30`, or `60`.

**Predict first:** what should happen to loss and accuracy as the network gets
more chances to update its weights?

## 2. Change the step size

Try these learning rates one at a time:

```python
learning_rate = 0.01
learning_rate = 0.1
learning_rate = 1.0
```

A tiny step may learn slowly. A large step may jump past useful weights and make
loss unstable. This is why the workshop says weights change **slightly**.

## 3. Change the hidden size

```python
model = NeuralNetwork(784, 32, 10)
model = NeuralNetwork(784, 256, 10)
```

Smaller hidden layers use fewer weights and may learn less. Larger layers have
more capacity but require more matrix-multiply work.

## 4. See individual guesses

Add this after training:

```python
with torch.no_grad():
    scores = model.forward(x_test[:10])
    guesses = scores.argmax(dim=1)

print("guesses:", guesses.tolist())
print("answers:", target_test[:10].tolist())
```

Accuracy is a summary. These two lines let you see the actual digit guesses. The
notebook's `inspect_model.show_digit(...)` cell draws one of them as text.

## 5. Turn scores into probabilities

The ten outputs are raw scores (logits), not probabilities. One line converts
them:

```python
probabilities = model.forward(x_test[:1]).softmax(dim=1)
print(probabilities.round(decimals=2))
```

`argmax` picks the same digit either way; softmax just makes the confidence
readable.

## 6. Look at what the first layer learned

```python
inspect_model.layer1_weight_grid(model)
```

Each hidden unit has 784 weights — one per pixel. Reshaped to 28×28, some of them
look like strokes and blobs the unit is searching for.

## 7. Break the initialization

In `Linear.__init__`, replace the `std` line with `std = 1.0`, then with
`std = 0.01`, and train again.

Too large and the first guesses are wild; too small and every hidden value is
nearly zero and learning barely moves. The `(2 / in_features) ** 0.5` scale keeps
the first pass in a useful range.

## 8. Train on smaller batches

The workshop uses all 60,000 training images at once so the learning loop stays
visually simple. Real systems often update after smaller batches. Split `x` and
`target` into chunks and repeat the same five stages for each chunk.

Notice that batching does not change the central idea. It only changes how many
examples contribute to each update.

## 9. Move the tensors to a GPU

GPUs are fast at the large matrix multiplications a forward pass is made of.
Create weights, biases, images, and targets on the same CUDA device, then run the
unchanged learning loop there.

This is outside the core hour because device-management boilerplate can hide the
learning idea when you first meet it.

## 10. Compare with PyTorch's high-level tools

Once you understand the manual version, rebuild it with `torch.nn.Linear`,
`torch.nn.ReLU`, and an optimizer. Those tools are shorter because they package
the exact responsibilities you implemented yourself:

- layers own parameters;
- autograd calculates gradients;
- the optimizer updates and clears them.

The manual workshop is not a different kind of neural network. It is the same
machinery with the covers removed.
