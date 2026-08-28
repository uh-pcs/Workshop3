# Workshop 3 — Build a Neural Network That Reads Handwriting

Session 3 of the PCS **From Zero to AI** series.

In one hour, you will build a neural network in one Python file and teach it to
recognize handwritten digits from MNIST. You will write the layers, make the
forward pass, measure the loss, ask PyTorch for gradients, and update every
weight yourself.

The one idea to remember:

> **A neural network learns by making a guess, measuring how wrong it was, and
> slightly changing its weights.**

**Forward Pass → Loss → Backpropagation → Update Weights → Repeat**

Google Slides: [PCS Workshop 3 — Build a Neural Network That Reads Handwriting](https://docs.google.com/presentation/d/15u64H2RkaHIWpErKeOLNS99TGJjibNAxYQkEH4V18us/edit?usp=drivesdk)

---

## Start the workshop — one click

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/daryl-888/Workshop3/blob/main/mnist_workshop.ipynb)

1. Click **Open in Colab**.
2. Leave the runtime on the standard **CPU** setting. No GPU is required.
3. Run the setup cell at the top of the notebook.
4. In Colab's left sidebar, click the **folder** icon and double-click
   `/content/mnist_network.py`.
5. Follow the slides and build the file with the facilitator.
6. Save before each notebook checkpoint.
7. At the end, use the notebook's download cell to keep your Python file.

The notebook downloads MNIST during setup. Start that cell while the opening
slides are on screen so the data is ready when the code needs it.

## What you will build

```text
784 pixel values → 128 hidden values → 128 hidden values → 10 digit scores
```

The finished model uses:

- a manual `Linear` class for `x @ weights + bias`;
- a manual `ReLU` class;
- a manual `NeuralNetwork` class;
- PyTorch autograd for gradients;
- cross-entropy loss;
- a manual gradient-descent update;
- MNIST from torchvision;
- live test-accuracy output.

It deliberately does **not** use `torch.nn.Linear`, `torch.nn.Sequential`, or a
PyTorch optimizer. Those tools are useful after you understand what they hide.

## Checkpoints

The Colab notebook runs each checkpoint in a fresh Python process, so it always
tests the version you saved:

1. **Linear:** three images travel from 784 inputs to 128 outputs.
2. **Network:** four images become ten digit scores each.
3. **Learning:** one manual update makes a tiny fixed problem's loss smaller.

If you fall behind, the facilitator can use the notebook's recovery lane to
restore a known-good stage. Recovery exists to keep everyone in the final payoff.

## The payoff

The first run trains for 10 epochs. You should see loss fall and accuracy rise:

```text
epoch   1  loss 2.4849  test_acc 0.1540
epoch  10  loss 1.6871  test_acc 0.6460
```

Then change `epochs = 10` to `epochs = 60` and run again. On a standard Colab
CPU, the final test accuracy should land roughly between 85% and 90%. Exact
values and runtime can vary slightly.

## What's in this repository

- `mnist_workshop.ipynb` — Colab setup, checkpoints, recovery, execution, and download
- `starter/mnist_network.py` — the small file students begin with
- `solution/mnist_network.py` — the complete teaching solution
- `facilitator/checkpoints/` — staged recovery snapshots for the live room
- `FACILITATOR.md` — pedagogy, timing, code reveals, expected output, and quick fixes
- `EXTENSIONS.md` — optional experiments after the core hour
- `tests/` — behavioral and notebook-structure verification

## Run the solution locally instead

The live room should use Colab. Local setup is an optional fallback for someone
who already has Python and PyTorch installed:

```bash
git clone https://github.com/daryl-888/Workshop3.git
cd Workshop3
python solution/mnist_network.py
```

PyTorch installation differs by operating system. Use the official selector at
[pytorch.org/get-started](https://pytorch.org/get-started/locally/) rather than
spending workshop time debugging local packages.

On a memory-constrained local machine, edit `load_data()` to pass
`train_limit=20000`. The official Colab path uses all 60,000 training images.

## Troubleshooting

- **`ModuleNotFoundError: mnist_network`** — confirm the file still lives at
  `/content/mnist_network.py`.
- **A checkpoint shows old code** — save the Python editor tab, then rerun it.
- **A matrix-shape error mentions `@`** — trace `784 → 128 → 128 → 10`; adjacent
  dimensions must match.
- **An in-place leaf-variable error appears** — put the parameter update inside
  `with torch.no_grad():`.
- **`parameter.grad` is `None`** — confirm weights and biases call
  `requires_grad_()` and that `loss.backward()` ran.
- **MNIST download is slow** — let it continue while following the opening
  slides; pair with a neighbor if the event network blocks one runtime.

## Keep experimenting

Open [EXTENSIONS.md](EXTENSIONS.md) after the workshop to vary epochs, learning
rate, hidden size, individual predictions, batches, GPU execution, and the
high-level `torch.nn` version.

## License

MIT — see [LICENSE](LICENSE). Use it, remix it, and run it at your own club.
