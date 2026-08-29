# Facilitator Guide — PCS Workshop Intro: Build a Neural Network

This is the teaching plan behind the workshop. Students do not need this file.
Read it once before the session, then keep the timing and recovery sections open
while you teach.

This workshop stands on its own. It assumes no prior PCS session and no earlier
lesson on matrix multiplication. Introduce every term — tensor, matrix
multiplication, logit, gradient, epoch — in plain language the first time it is
needed.

## The one idea to land

> **A neural network learns by making a guess, measuring how wrong it was, and
> slightly changing its weights.**

Everything in the hour serves that sentence. Keep this loop visible and point to
the current stage whenever the code changes:

**Forward Pass → Loss → Backpropagation → Update Weights → Repeat**

Avoid turning backpropagation into a calculus lecture. The explanation students
need today is:

> "PyTorch remembers the operations from the forward pass. `backward()` walks
> back through them and tells us how each weight contributed to the error."

## Why one Python file

The hour produces one meaningful artifact. The classes are not isolated
exercises:

- `Linear` becomes the learned matrix multiplication inside the network.
- `ReLU` gives the stacked layers a bend.
- `NeuralNetwork` turns the pieces into ten digit scores.
- The training loop makes that same network improve.

Students edit `/content/mnist_network.py` in Colab. The notebook is only a
workbench for setup, checkpoints, recovery, execution, inspection, and download.
Keep the Google Slides deck on the projector and return to the notebook only at
marked checkpoints.

## How a layer works — the standalone explanation

There is no earlier workshop to call back to. When you reach the layer slide,
say:

> "A layer takes every input number, combines it with adjustable weights, adds a
> bias, and produces a new set of numbers. The `@` symbol asks PyTorch to
> perform all of those multiply-and-add operations together."

Define rows, columns, and shapes in plain language so a newcomer can follow. The
shapes are the through-line: `(images, 784) @ (784, 128) + (128) → (images, 128)`.

## Before the room arrives

1. Open the Colab badge from the README in a signed-out or private browser.
2. Confirm the runtime hardware accelerator is **None**.
3. Run the setup cell and verify the repo clones, the starter file appears, and
   both MNIST splits download. If the download fails, the cell prints the error;
   retry, or switch networks.
4. Run the three checkpoint cells against the corresponding recovery files.
5. Run the final solution for 10 epochs, then 60 epochs, and note the wall time
   on the event machine so you can set expectations in the room.
6. Run the "see one real prediction" and "watch it learn" cells.
7. Confirm the Google Slides link opens without edit permission.
8. Put the setup slide on screen as students enter and ask them to run the first
   notebook cell immediately.

Run this preflight once the day before and again on the event network. Colab
runtimes change over time; the setup cell prints Python, PyTorch, and GPU status
so a failure starts with useful evidence.

## Timing — 60 minutes

| Time | Segment | Room checkpoint |
|---|---|---|
| 0:00–0:04 | Show a handwritten digit and ask whether a computer can read it | Setup cell prints `READY` |
| 0:04–0:08 | Establish the guess/error/change/repeat loop | Students can say the loop aloud |
| 0:08–0:12 | Turn 28×28 pixels into 784 numbers | Shape `784` is visible |
| 0:12–0:17 | Explain a layer as weighted sums plus a bias | Land the standalone layer explanation |
| 0:17–0:24 | Build `Linear` | Notebook Checkpoint 1 passes |
| 0:24–0:28 | Explain and build `ReLU` | Negative values become zero |
| 0:28–0:35 | Stack `NeuralNetwork` and trace dimensions | Checkpoint 2 passes |
| 0:35–0:40 | Load MNIST and interpret ten logits | Students identify `argmax` as the guess |
| 0:40–0:44 | Explain cross-entropy loss | Loss means wrongness, not accuracy |
| 0:44–0:49 | Backward, manual update, and gradient clearing | Checkpoint 3 passes |
| 0:49–0:53 | Assemble the complete training loop | Point to all five loop stages |
| 0:53–0:56 | Run 10 epochs and read output | Loss falls; accuracy rises past the 10% baseline |
| 0:56–0:58 | Show one real prediction and the learning curve | Students see a digit and the model's guess |
| 0:58–0:59 | Change 10 to 60 and rerun | Accuracy reaches roughly 85–90% |
| 0:59–1:00 | Recap and download the file | Students keep their artifact |

If setup runs slowly, teach the hook and the learning loop while MNIST downloads.

## Anchor the numbers

Before the first run, say what the scores mean:

> "Ten digits, so blind guessing is right about 10% of the time. After one epoch
> we are near 15%. Anything well above that is the network actually learning."

## Code reveal cadence

Each row corresponds to a coding slide. Show the chunk, explain its job, type it
with the room, save, then run the named checkpoint. Do not paste the full
solution at the beginning.

### Build `Linear`

Concept: a layer is a learned matrix multiplication plus a bias.

```python
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
```

Say: "The values start random. Learning means improving these values." Do not
derive the `std` formula; call it a sensible starting scale so early guesses are
neither tiny nor huge.

Expected Checkpoint 1 output:

```text
Linear:  (3, 784) -> (3, 128)

Checkpoint 1 passed - save and keep going.
```

Recovery: run `recover(1)` in the notebook.

### Build `ReLU`

Concept: without a bend, several linear transformations collapse into one larger
linear transformation.

```python
class ReLU:
    def forward(self, x):
        return x.clamp(min=0)
```

Use a spoken example: `[-2, 0, 3]` becomes `[0, 0, 3]`. Avoid discussing
derivatives unless a student asks after the workshop.

### Stack the network

Concept: each layer changes the representation while the shapes tell us what can
connect to what.

```python
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
```

Trace `784 → 128 → 128 → 10` with your finger before running anything.

Expected Checkpoint 2 output:

```text
Network:  (4, 784) -> (4, 10)   with 6 trainable tensors

Checkpoint 2 passed - save and keep going.
```

Recovery: run `recover(2)`.

### Load MNIST

Concept: flatten each image and scale pixel brightness from 0–255 into 0–1.

Use the `load_data()` function from `solution/mnist_network.py`. Pause after
`view(-1, 784)` and ask what `-1` means: "however many images there are." Note
that `dataset.data` is used directly, so no transform is required.

### Loss and backward

Concept: loss is one number describing wrongness; backward supplies a gradient
for every parameter.

```python
prediction = model.forward(x)
loss = torch.nn.functional.cross_entropy(prediction, target)
loss.backward()
```

Do not call logits probabilities. They are ten raw scores; cross-entropy knows
how to compare those scores with the correct digit. If a student asks for
probabilities, `prediction.softmax(dim=1)` is the answer, but it is not needed to
train.

### Update and clear

Concept: each gradient points toward more error, so subtract a small amount.

```python
with torch.no_grad():
    for parameter in model.parameters():
        parameter -= learning_rate * parameter.grad

for parameter in model.parameters():
    parameter.grad.zero_()
```

Say: "`no_grad()` means this is the change itself, not another operation PyTorch
should learn through." Then explain that gradients add by default, like writing
new directions on top of old directions without erasing the board.

Expected Checkpoint 3 output resembles:

```text
Learning:  loss 1.0247 -> 0.8123

Checkpoint 3 passed - your learning loop works.
```

The exact numbers may vary if the student changed initialization. Recovery:
`recover(3)`.

### Assemble and run

Use `main()` from the final solution as the reveal. Point to the five numbered
comments and make the room name each stage before execution.

Expected default output resembles:

```text
epoch   1  loss 2.4849  train_acc 0.1523  test_acc 0.1540
epoch  10  loss 1.6871  train_acc 0.6402  test_acc 0.6460
```

After changing `epochs = 10` to `epochs = 60`, expect the final accuracy to land
roughly between 0.85 and 0.90. The trend matters more than one exact value.

Final recovery: run `recover(4)`, reopen the file, and continue with the room.

### See one real prediction

After the run, the notebook imports `solution/inspect_model.py` and prints one
test image as text with the model's guess and the true digit. This is the
emotional payoff: the abstract accuracy number becomes one digit the class can
read. The "watch it learn" cell then plots loss and accuracy over the epochs.

## Common stumbles and quick fixes

- **`ModuleNotFoundError: mnist_network`** → the file was renamed or moved.
  Confirm `/content/mnist_network.py` exists in the Files panel.
- **Checkpoint still sees old code** → save the editor tab. Checkpoints already
  launch fresh processes, so saving is the missing step.
- **Shape mismatch near `@`** → compare adjacent dimensions in
  `784 → 128 → 128 → 10`; the inside numbers must match.
- **`parameter.grad` is `None`** → `loss.backward()` did not run, or the student
  forgot `requires_grad_()` on weights and bias.
- **"A leaf Variable that requires grad is being used in an in-place operation"**
  → move the weight update inside `with torch.no_grad():`.
- **Loss behaves strangely on the second epoch** → gradients were not cleared.
- **MNIST download fails** → the setup cell prints the underlying error. Retry,
  switch networks, or pair blocked students with a working neighbor and continue
  the core build; do not sacrifice the final payoff to network troubleshooting.
- **Colab runtime disappeared** → rerun setup, then use the latest recovery stage.
- **Accuracy differs slightly** → confirm `torch.manual_seed(0)` and focus on the
  downward-loss/upward-accuracy trend.

## Pacing radar and recovery

Use the three `Checkpoint N passed` messages as your room-wide pacing radar. At minute
49, anyone without Checkpoint 3 should use `recover(3)`. At minute 53, anyone
without a complete `main()` should use `recover(4)`. Recovery is not failure; it
protects the shared payoff.

If behind, trim in this order:

1. Demonstrate the optional learning-rate experiment instead of having everyone
   run it.
2. Shorten the logits discussion to "ten scores; biggest score wins."
3. Use recovery snapshots earlier.

Never cut the manual update, the final training run, the one real prediction, or
the one-minute recap.

## Close the loop

End on the same sentence you began with:

> "Your network made a guess, measured how wrong it was, changed its weights a
> little, and repeated. Matrix multiplication became a system that learns."

Then have students download `mnist_network.py` before the Colab runtime expires.
