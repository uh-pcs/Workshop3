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

Students never open a file panel. The notebook has **five STEP cells**, one per
coding slide; typing into a cell and running it writes that piece of the file,
and every checkpoint reassembles `/content/mnist_network.py` from the pieces
written so far. Each STEP cell prints a progress checklist, so a student who
looks up mid-session can see exactly where the room is.

Keep the Google Slides deck on the projector. Slide kickers say `STEP 1`,
`STEP 2`, … so the slide names the cell to type into.

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
3. Run the setup cell and verify the repo clones and both MNIST splits
   download. It ends with `READY` and a progress checklist. If the download
   fails, the cell prints the error; retry, or switch networks.
4. Run `recover(5)`, then the three checkpoint cells, to confirm the reference
   code still passes.
5. Run the file for 10 epochs, then 60 epochs, and note the wall time on the
   event machine so you can set expectations in the room.
6. Run the "see it read one digit" and "learning curve" cells.
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
| 0:17–0:24 | Build `Linear` (slide 5 → STEP 1) | Checkpoint 1 passes |
| 0:24–0:28 | Build `ReLU` (slide 6 → STEP 2) | Negative values become zero |
| 0:28–0:35 | Stack `NeuralNetwork` (slide 7 → STEP 3) | Checkpoint 2 passes |
| 0:35–0:40 | Ten scores, then load MNIST (slides 8–9 → STEP 4) | Students identify `argmax` as the guess |
| 0:40–0:44 | Explain cross-entropy loss | Loss means wrongness, not accuracy |
| 0:44–0:49 | Backward, manual update, and gradient clearing | Checkpoint 3 passes |
| 0:49–0:53 | Assemble `main()` (slide 12 → STEP 5) | Point to all five loop stages |
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

Each block below is exactly what a coding slide shows and exactly what the
matching STEP cell must end up containing — `tests/test_slides_match_code.py`
enforces that. Show the chunk, explain its job, type it with the room, run the
cell, then run the named checkpoint. Do not paste the full solution up front.

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

Checkpoint 1 PASSED
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

Checkpoint 2 PASSED
```

Recovery: run `recover(2)`.

### Load MNIST  (slide 9 → STEP 4)

Concept: flatten each image and scale pixel brightness from 0–255 into 0–1, and
keep a separate test set.

Slide 9 shows `load_data()` and `accuracy()` exactly as students must type them.
Pause after `view(-1, 784)` and ask what `-1` means: "however many images there
are." Note that `dataset.data` is used directly, so no transform is required.
Ask why we hold back a test set: so accuracy measures learning, not memorising.

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

Checkpoint 3 PASSED
```

The exact numbers may vary if the student changed initialization. Recovery:
`recover(3)`.

### Assemble and run

Slide 12 shows `main()` in full — the same twenty lines students type into the
STEP 5 cell. Make the room name each of the five moves before you run anything.

Printing is done by `report()`, which the setup cell wrote for them, so nothing
but the five moves lives inside the loop.

Expected default output resembles:

```text
epoch   1   loss 2.4849   test_acc 0.1540
epoch   5   loss 1.9106   test_acc 0.4835
epoch  10   loss 1.6871   test_acc 0.6460
```

After changing `epochs = 10` to `epochs = 60`, expect the final accuracy to land
roughly between 0.85 and 0.90. The trend matters more than one exact value.

Final recovery: run `recover(5)` and continue with the room.

### See one real prediction

After the run, the notebook imports `solution/inspect_model.py` and prints one
test image as text with the model's guess and the true digit. This is the
emotional payoff: the abstract accuracy number becomes one digit the class can
read. The "watch it learn" cell then plots loss and accuracy over the epochs.

## Common stumbles and quick fixes

- **`ModuleNotFoundError: mnist_network`** → the file was renamed or moved.
  Confirm `/content/mnist_network.py` exists in the Files panel.
- **Checkpoint still sees old code** → the STEP cell above it was edited but not
  re-run. Running a STEP cell is what writes that piece of the file; the
  checkpoint then reassembles it. There is no separate save step any more.
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
without a complete `main()` should use `recover(5)`. Recovery is not failure; it
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
