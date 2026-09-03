# PCS Workshop Intro — Build a Neural Network That Reads Handwriting

In one hour, you will build a neural network in one Python file and teach it to
recognize handwritten digits from MNIST. You will write the layers, make the
forward pass, measure the loss, ask PyTorch for gradients, and update every
weight yourself.

The one idea to remember:

> **A neural network learns by making a guess, measuring how wrong it was, and
> slightly changing its weights.**

**Forward Pass → Loss → Backpropagation → Update Weights → Repeat**

Slides:

- In the room: [PCS Workshop Intro — Build a Neural Network That Reads Handwriting](https://docs.google.com/presentation/d/15u64H2RkaHIWpErKeOLNS99TGJjibNAxYQkEH4V18us/edit?usp=drivesdk)
- Offline copy in this repo: [`slides/pcs-workshop-intro.pdf`](slides/pcs-workshop-intro.pdf)

---

## Start the workshop — one click

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/uh-pcs/Workshop3/blob/main/mnist_workshop.ipynb)

1. Click **Open in Colab**.
2. Leave the runtime on the standard **CPU** setting. No GPU is required.
3. Run the setup cell at the top of the notebook.
4. Work down the notebook. There are **five STEP cells**, each labelled with the
   slide it matches — type the code from the slide into the cell and run it.
5. Run each **Checkpoint** cell when you reach it. Every STEP cell prints a
   progress checklist so you always know where you are.
6. At the end, run the "see it read one digit" and "learning curve" cells, then
   use the download cell to keep your Python file.

Everything happens in the notebook cells, in order — you never need Colab's file
panel. Your work is `mnist_network.py`, which the notebook assembles from your
STEP cells; keep it with the **download cell**, not Colab's **File → Save**.

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
- live train and test accuracy output.

It deliberately does **not** use `torch.nn.Linear`, `torch.nn.Sequential`, or a
PyTorch optimizer. Those tools are useful after you understand what they hide.

## The five steps

Each STEP cell writes one piece of the file, and the notebook reassembles
`mnist_network.py` before every checkpoint:

| Step | Slide | You write | Checkpoint |
|---|---|---|---|
| 1 | 5 | `class Linear` | three images: `(3, 784) → (3, 128)` |
| 2 | 6 | `class ReLU` | — |
| 3 | 7 | `class NeuralNetwork` | four images: `(4, 784) → (4, 10)`, 6 tensors |
| 4 | 9 | `load_data`, `accuracy` | — |
| 5 | 12 | `main` | the real training run |

The imports, the seed, and a small `report()` printing helper are written for you
so the training loop stays pure.

Checkpoints run your file in a fresh Python process and explain what went wrong
in one line rather than dumping a traceback. If you fall behind, the facilitator
can call `recover(n)` to fill in the reference code through STEP *n*.

## The payoff

The first run trains for 10 epochs. Random guessing scores about 10%. You should
see loss fall and accuracy rise well past that:

```text
epoch   1   loss 2.4849   test_acc 0.1540
epoch   5   loss 1.9106   test_acc 0.4835
epoch  10   loss 1.6871   test_acc 0.6460
```

Then change `epochs = 10` to `epochs = 60` and run again. On a standard Colab
CPU, the final test accuracy should land roughly between 85% and 90%. Exact
values and runtime can vary slightly.

After training, the notebook prints one real test image as text with the model's
guess beside the true digit, and plots the loss and accuracy curves.

## What's in this repository

- `mnist_workshop.ipynb` — the Colab workbench: setup, five STEP cells, checkpoints, the run, inspection, recovery, download
- `facilitator/parts/` — **the source of truth.** One file per STEP; the notebook writes these, and the slides show them
- `facilitator/build_file.py` — concatenates the parts into `mnist_network.py`
- `solution/mnist_network.py` — generated from the parts; the answer key
- `solution/inspect_model.py` — optional helpers to see digits, mistakes, weights, and curves
- `FACILITATOR.md` — pedagogy, timing, code reveals, expected output, and quick fixes
- `EXTENSIONS.md` — optional experiments after the core hour
- `slides/` — offline PDF of the deck and `build_deck.py`, which generates it
- `tests/` — behaviour, notebook structure, and **slide/code agreement**
- `docs/design-history/` — the design and planning notes behind this workshop

Because the parts feed the file, the slides, and the notebook, the three can
never drift apart — `tests/test_slides_match_code.py` fails if they do.

## Run the solution locally instead

The live room should use Colab. Local setup is an optional fallback for someone
who already has Python and PyTorch installed:

```bash
git clone https://github.com/uh-pcs/Workshop3.git
cd Workshop3
python solution/mnist_network.py
```

To follow the slides locally instead of reading the answer key, start from
`facilitator/parts/00_header.py` and add each STEP yourself:

```bash
cp facilitator/parts/00_header.py mnist_network.py
```

PyTorch installation differs by operating system. Use the official selector at
[pytorch.org/get-started](https://pytorch.org/get-started/locally/) rather than
spending workshop time debugging local packages.

On a memory-constrained machine, train on fewer images by slicing right after
`load_data()`: `x, target = x[:20000], target[:20000]`. Colab uses all 60,000.

## Regenerate the solution and the deck

```bash
python3 facilitator/build_file.py facilitator/parts solution/mnist_network.py
python3 slides/build_deck.py
python3 -m pytest -q
```

## Troubleshooting

- **`ModuleNotFoundError: mnist_network`** — confirm the file still lives at
  `/content/mnist_network.py`.
- **A checkpoint shows old code** — re-run the STEP cell above it, then the
  checkpoint. Running a STEP cell is what saves that piece of your file.
- **A matrix-shape error mentions `@`** — trace `784 → 128 → 128 → 10`; adjacent
  dimensions must match.
- **An in-place leaf-variable error appears** — put the parameter update inside
  `with torch.no_grad():`.
- **`parameter.grad` is `None`** — confirm weights and biases call
  `requires_grad_()` and that `loss.backward()` ran.
- **MNIST download fails or is slow** — the setup cell prints the error; let it
  continue while following the opening slides, and pair with a neighbor if the
  event network blocks one runtime.

## Keep experimenting

Open [EXTENSIONS.md](EXTENSIONS.md) after the workshop to vary epochs, learning
rate, hidden size, individual predictions, batches, GPU execution, weight
pictures, initialization, and the high-level `torch.nn` version.

## License

MIT — see [LICENSE](LICENSE). Use it, remix it, and run it at your own club.
