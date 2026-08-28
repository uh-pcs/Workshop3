# PCS Workshop Intro — Slide Source

Content source of truth for the deck. The built deck lives at
`slides/pcs-workshop-intro.pptx` (offline PDF: `slides/pcs-workshop-intro.pdf`)
and, in the room, as native Google Slides (link in the README). Change a slide
here first, then run `python3 slides/build_deck.py`.

**15 slides** for a 60-minute live-coding session — slides are reference points
between typing, not a lecture. Each of the three notebook checkpoints is a green
strip on its live-build slide, not a slide of its own.

## Visual system

| Token | Value | Use |
|---|---|---|
| canvas | `#FFF9EE` | slide background |
| ink | `#24303A` | all body and title text |
| blue | `#367BF5` | arrows only — never small text on canvas |
| yellow | `#FFD85A` | highlighter cards and fills only — never text |
| green | `#43B581` / mint `#E8F6EF` | checkpoint strips, completed loop steps |
| pale blue | `#EAF2FF` | code panels, shape banners, side notes |

Fonts: design intent is titles **Poppins**, body **Inter**, code **JetBrains
Mono** (all render in Google Slides). The built `.pptx`/`.pdf` use Office-safe
substitutes (Calibri, Consolas) so the offline copy renders identically
everywhere; swap after import if wanted. Format 16:9.

Grammar: warm dot-free canvas; kicker pill top-left; the five-step loop diagram on
slide 2 and again on slide 12 with every step checked; pixel tiles for digits;
light code panels; yellow "read it as" cards; green checkpoint strips; slide tabs
bottom-right.

Every coding slide's speaker notes carry: concept, expected output, pause point,
likely stumble, recovery checkpoint.

---

## 1 — Hook

**Kicker:** PCS Workshop Intro · **Title:** What number is this?
**Visual:** one MNIST digit as a large pixel grid (a messy 3).
**Lines:** Your phone reads it instantly. In one hour you build the thing that can
— one Python file, from scratch.

**Notes:** Do not say the answer; ask the room. Someone says "3". Ask *how* they
know — they can't fully explain it, and neither will our network. The promise:
one file, built from scratch, that learns to read these.

## 2 — The idea and the loop

**Kicker:** The one idea · **Title:** Guess. Measure. Change. Repeat.
- A network starts with random weights, so its first guesses are bad — that is
  where learning begins.
- Each round measures how wrong the guess was, finds which weights caused the
  error, and nudges every weight a little.

**Visual:** the five-step loop — Forward · Loss · Backprop · Update · Repeat.
**Marker:** every line of code today belongs to one of these five moves.

**Notes:** If a student remembers one sentence tomorrow, make it the title. The
loop returns on slide 12 with every step checked — point here whenever the code
changes.

## 3 — The input

**Kicker:** What the computer sees · **Title:** A picture is 784 numbers
**Visual:** pixel digit with 28 / 28 / 784 callouts.
- A 28×28 grayscale image: one brightness value per pixel, 0–255.
- Flatten the square into one row of 784 numbers — no pixel is lost.
- Divide by 255 so every value lands between 0 and 1.

**Code chip:** `x = image.view(-1, 784) / 255.0`

**Notes:** "Grayscale" = one number per pixel. `-1` means "however many images
there are." Flattening changes the shape, not the information.

## 4 — A layer

**Kicker:** The core move · **Title:** Weighted sums, plus a bias
- A layer multiplies each input by an adjustable weight, adds the products, then
  adds a bias — producing a new set of numbers.
- The key word is "adjustable": learning is nothing more than changing these
  weights.

**Shape banner:** `(images, 784) @ (784, 128) + (128) → (images, 128)`
**Yellow:** `@` does every multiply-and-add at once. Inside dims match; outside
dims survive.

**Notes:** No prior workshop to lean on — build it from "multiply and add". Trace
the shapes with a finger: the 784 on both sides cancels; `(images, 128)` is left.

## 5 — Live build: Linear

**Kicker:** Live build · Linear · **Title:** Build one learned layer
**Code panel:** the `Linear` class (`std`, `torch.randn * std`, `torch.zeros`,
`requires_grad_()`, `forward`, `parameters`).
**Side text:** random weights, zero biases; ask PyTorch to track them; `forward()`
makes the guess; `parameters()` hands the loop every value it may change.
**Checkpoint 1 strip:** save the file, run the cell. Expect `(3, 784) → (3, 128)`.

**Notes:**
- *Concept:* a layer is a learned matrix multiply plus a bias.
- *Expected:* `Linear checkpoint passed: (3, 784) → (3, 128)`
- *Pause:* after `forward()` — "this one line is the guess."
- *Stumble:* forgetting `requires_grad_()` (grads are `None` later); mismatched
  `@` shapes.
- Do not derive the `std` formula — call it a sensible starting scale.
- *Recovery:* `recover(1)`.

## 6 — Live build: ReLU

**Kicker:** Live build · ReLU · **Title:** Add a bend
**Code panel:** `class ReLU: def forward(self, x): return x.clamp(min=0)`
- Stack linear layers with nothing between them and the whole stack is still just
  one linear layer.
- Digits are messy; the model needs bends to draw richer boundaries.

**Yellow card:** below zero becomes zero; everything else passes through;
`[-2, 0, 3] → [0, 0, 3]`.

**Notes:**
- *Concept:* the bend that stops stacked layers collapsing into one.
- *Expected:* no checkpoint of its own; verified inside Checkpoint 2.
- *Stumble:* `x.clamp(0)` (that's `max`), or `max(x, 0)` on a tensor.
- *Recovery:* `recover(2)`.

## 7 — Live build: NeuralNetwork

**Kicker:** Live build · Network · **Title:** 784 → 128 → 128 → 10
**Subtitle:** Linear, ReLU, Linear, ReLU, Linear. The ReLUs change values, not
dimensions.
**Code panel:** the `NeuralNetwork` class with the step-by-step `forward` and the
`parameters()` concatenation.
**Side text:** `parameters()` adds up to six tensors — three weights, three
biases.
**Checkpoint 2 strip:** four images become ten scores each. Expect
`(4, 784) → (4, 10)`.

**Notes:**
- *Concept:* the pieces become one object that turns pixels into ten scores.
- *Expected:* `Network checkpoint passed: (4, 784) → (4, 10)`
- *Pause:* count the six tensors together before running.
- *Stumble:* `self.layer1(x)` instead of `.forward(x)`; a missing ReLU.
- *Recovery:* `recover(2)`.

## 8 — Ten outputs

**Kicker:** Reading the result · **Title:** Ten scores → one guess
- Ten numbers out, one per digit. The largest is the model's guess (`argmax`).
- A raw score is called a **logit**.
- `prediction.softmax(dim=1)` turns the ten into probabilities that add to 1 —
  same guess, readable confidence.

**Yellow:** cross-entropy will compare all ten scores with the correct digit.

**Notes:** Show softmax once so "logit" isn't a loose end, then set it aside — we
never need it to train. Biggest score wins, with or without it.

## 9 — Live build: data

**Kicker:** Live build · Data · **Title:** Load MNIST
**Code panel:** the two `torchvision.datasets.MNIST` calls and the
`.data.float().view(-1, 784) / 255.0` / `.targets` lines for train and test.
**Side text:** examples for learning, separate examples for testing; flatten to
784; scale 0–255 down to 0–1; keep each digit as the target.

**Notes:**
- *Concept:* the flatten/scale from slide 3, on real data, plus the train/test
  split.
- *Pause:* "why hold back test data?" — so accuracy measures learning, not
  memorising.
- *Stumble:* forgetting `.float()` (uint8 breaks the matmul); forgetting
  `/ 255.0`.
- *Recovery:* the setup cell cached MNIST; re-run this block.

## 10 — Loss and backward

**Kicker:** Measure, then walk back · **Title:** One number, then every gradient
- `loss = cross_entropy(prediction, target)` is high when the right digit scores
  poorly, low when it wins — the single signal learning reduces.
- `loss.backward()` walks the remembered operations in reverse and reports how
  each weight contributed to the error.

**Banner:** `loss ← scores ← layers ← every weight and bias`
**Yellow:** a gradient is a direction: changing this value that way would raise
the loss.

**Notes:** Loss is wrongness, not accuracy. Do not open the calculus — the yellow
card is the whole explanation students need today.

## 11 — Live build: update

**Kicker:** Live build · Update · **Title:** One small step, then clear
**Code panel:** `loss.backward()`, the `with torch.no_grad()` update loop, the
`parameter.grad.zero_()` loop.
**Side text:** each gradient points toward more error, so subtract a little of it
from each weight.
**Yellow card:** step opposite the gradient, a little; `no_grad()` is the change
itself; clear the grads, or the next round mixes old with new.
**Checkpoint 3 strip:** one manual step makes a fixed problem's loss smaller.

**Notes:**
- *Concept:* gradient descent — step opposite the gradient, a little; then zero
  the grads.
- *Expected:* `Learning checkpoint passed: 1.0247 → 0.8123` (numbers vary).
- *Pause:* "why minus?" — the gradient points uphill; we want downhill.
- *Stumble:* update outside `no_grad()` → in-place leaf error; forgetting
  `zero_()` → loss lurches on epoch 2.
- *Recovery:* `recover(3)`.

## 12 — It's all the loop

**Kicker:** The code is the loop · **Title:** Nothing is hidden
**Visual:** the five-step loop, every step checked, each labelled with its line:
1. `prediction = model.forward(x)`
2. `loss = cross_entropy(prediction, target)`
3. `loss.backward()`
4. `parameter -= learning_rate * parameter.grad`
5. `parameter.grad.zero_()` → next epoch

**Notes:** Have the room name each of the five moves before you run anything. Then
reveal `main()` and run it.

## 13 — The payoff

**Kicker:** Watch it learn · **Title:** Ten rounds, then sixty
**Stat cards:** starting loss ≈ 2.48 · loss after 10 epochs ≈ 1.69 · test accuracy
≈ 65%.
**Banner:** change `epochs` 10 → 60: loss ≈ 0.48, test accuracy ≈ 88%. Same
architecture, more rounds.
**Yellow:** blind guessing is 10%. Read the trend: loss down, accuracy up.

**Notes:** Anchor on the 10% baseline first. Train and test accuracy both print —
note they track each other here. If the 60-epoch run is still going, keep talking.
Replace these numbers with what you measured on the event machine.

## 14 — Where it gets it wrong

**Kicker:** Be honest about the model · **Title:** It matches pixels — it does not
know digits
**Visual:** two misclassified digits (a 4 called 9, a 5 called 3), each labelled
`guess · truth`.
**Line:** it learned pixel patterns that usually work. When a 4 is drawn like a 9,
it has nothing else to fall back on.

**Notes:** The memorable slide. Keeps students from over-claiming what they built,
and sets up why bigger models and more data exist. The notebook's "where it gets
things wrong" cell produces these live.

## 15 — Your turn

**Kicker:** Before the runtime disappears · **Title:** Keep the file. Change one
thing.
1. Download `mnist_network.py`
2. Pick one experiment
3. Predict what will happen
4. Change one value
5. Run and compare

**Yellow card — try one:** epochs 10 → 60 · learning rate 0.1 → 0.01 · hidden size
128 → 32 · break the init (`std = 1.0`) · `layer1_weight_grid(model)`
**Footer:** you built the layers, the gradients, and the update. The high-level
PyTorch tools package the same machinery you now understand.

**Notes:** End on the opening sentence: "Your network made a guess, measured how
wrong it was, changed its weights a little, and repeated. Matrix multiplication
became a system that learns." Then make sure everyone has downloaded the file.
