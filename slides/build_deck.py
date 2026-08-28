#!/usr/bin/env python3
"""Build the PCS Workshop Intro deck.

Authoring source is a flat ODF presentation (`.fodp`, one XML file). LibreOffice
converts it to `.pptx` (for Google Slides import) and `.pdf` (offline copy):

    python3 slides/build_deck.py     # writes .pptx + .pdf into slides/

Visual system is a sibling of the "From Zero to ..." workshop decks: dark canvas,
monospace section labels, bold sans titles, dark bordered cards, an amber warning
callout. Workshop 3's own signature is violet (the learning signal) and the
pixel-grid mark. See docs/slides.md.

The built deck uses Arial (title/body) and DejaVu Sans Mono (code) so the offline
PDF renders true everywhere. In Google Slides, swap titles to Poppins / Montserrat
and code to Roboto Mono if wanted.
"""

import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- palette
BG = "0E1119"       # deep navy-black canvas
PANEL = "0A0C12"    # card / code / terminal fill
BORDER = "272C38"   # hairline
INK = "ECEEF2"      # near-white
BODY = "A7B0BC"     # muted body text
FAINT = "6B7480"    # captions, card numbers, tab
VIOLET = "8B80F9"   # Workshop 3 signature: the learning signal
VIOLET_FILL = "1A1836"
AMBER = "F5B301"    # payoff energy + callout border
AMBER_FILL = "241E0C"
GREEN = "46D07E"    # checkpoints / success only
BLUE = "5A9DFF"     # series breadcrumb + italic accent
RED = "FF6B5E"

SANS = "Arial"
MONO = "DejaVu Sans Mono"

PAGE_W = 25.4
PAGE_H = 14.288
M = 1.75            # left / right margin
TOTAL = 15

_styles: dict[str, str] = {}


def _reg(key, xml):
    _styles.setdefault(key, xml)
    return key


def gstyle(fill=None, stroke=None, stroke_w=0.026, valign="top", pad=0.0, radius=None):
    key = f"g{fill}{stroke}{stroke_w}{valign}{pad}{radius}"
    if key in _styles:
        return key
    p = [
        f'draw:fill="solid" draw:fill-color="#{fill}"' if fill else 'draw:fill="none"',
        (f'draw:stroke="solid" svg:stroke-width="{stroke_w}cm" svg:stroke-color="#{stroke}"'
         if stroke else 'draw:stroke="none"'),
        f'draw:textarea-vertical-align="{valign}"',
        'draw:auto-grow-height="false" draw:auto-grow-width="false"',
        f'fo:padding-top="0cm" fo:padding-bottom="0cm" fo:padding-left="{pad}cm" fo:padding-right="{pad}cm"',
    ]
    if radius:
        p.append(f'draw:corner-radius="{radius}cm"')
    return _reg(key, f'<style:style style:name="{key}" style:family="graphic">'
                     f'<style:graphic-properties {" ".join(p)}/></style:style>')


def tstyle(size, color=INK, bold=False, align="left", font=SANS, spacing=0.0, italic=False,
           tracking=None):
    key = f"t{size}{color}{bold}{align}{font}{spacing}{italic}{tracking}"
    if key in _styles:
        return key
    b = ' fo:font-weight="bold"' if bold else ""
    i = ' fo:font-style="italic"' if italic else ""
    tr = f' fo:letter-spacing="{tracking}cm"' if tracking else ""
    return _reg(key, f'<style:style style:name="{key}" style:family="paragraph">'
                     f'<style:paragraph-properties fo:text-align="{align}" fo:margin-bottom="{spacing}cm"/>'
                     f'<style:text-properties fo:font-size="{size}pt" fo:color="#{color}"{b}{i}{tr} '
                     f'style:font-name="{font}"/></style:style>')


# ---------------------------------------------------------------- primitives
_el: list[str] = []


def _p(item):
    text, st = item if isinstance(item, tuple) else (item, tstyle(15, BODY))
    lead = len(text) - len(text.lstrip("\t"))
    rest = escape(text[lead:]) or " "
    pre = f'<text:s text:c="{lead * 4}"/>' if lead else ""
    return f'<text:p text:style-name="{st}">{pre}{rest}</text:p>'


def txt(x, y, w, h, paras, valign="top"):
    g = gstyle(valign=valign)
    _el.append(f'<draw:frame draw:style-name="{g}" svg:x="{x}cm" svg:y="{y}cm" '
               f'svg:width="{w}cm" svg:height="{h}cm"><draw:text-box>'
               f'{"".join(_p(p) for p in paras)}</draw:text-box></draw:frame>')


def rect(x, y, w, h, fill=None, stroke=None, radius=None, stroke_w=0.026):
    g = gstyle(fill=fill, stroke=stroke, radius=radius, stroke_w=stroke_w)
    _el.append(f'<draw:rect draw:style-name="{g}" svg:x="{x}cm" svg:y="{y}cm" '
               f'svg:width="{w}cm" svg:height="{h}cm"/>')


def ellipse(x, y, d, fill):
    g = gstyle(fill=fill)
    _el.append(f'<draw:ellipse draw:style-name="{g}" svg:x="{x}cm" svg:y="{y}cm" '
               f'svg:width="{d}cm" svg:height="{d}cm"/>')


# ---------------------------------------------------------------- components
def pixel_mark(x, y, cell=0.15, color=VIOLET, gap=0.05):
    pattern = ["110", "111", "011"]
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch == "1":
                rect(x + c * (cell + gap), y + r * (cell + gap), cell, cell, fill=color)


def kicker(text):
    pixel_mark(M, 0.95)
    txt(M + 1.15, 0.86, 20, 0.7,
        [(text.upper(), tstyle(11.5, GREEN, font=MONO, tracking=0.06))], "middle")


def title(text, size=34, w=17.5, y=1.95):
    txt(M, y, w, 2.6, [(text, tstyle(size, INK, bold=True))])


def lead(lines, y=4.5, w=15.5, size=14.5, gap=0.24, color=BODY, x=M):
    txt(x, y, w, len(lines) * 1.4 + 1, [(ln, tstyle(size, color, spacing=gap)) for ln in lines])


def accent(text, y, w=15.5, x=M):
    txt(x, y, w, 0.9, [(text, tstyle(12.5, BLUE, italic=True))])


def note_line(text, y=13.15, x=M, w=22):
    txt(x, y, w, 0.7, [(text, tstyle(10, FAINT, italic=True))])


def tag(n):
    txt(PAGE_W - 4.0, PAGE_H - 0.95, 3.2, 0.55,
        [(f"{n:02d} / {TOTAL}", tstyle(9.5, FAINT, font=MONO, align="right"))])


def card(x, y, w, h, number, big, label, color=VIOLET, big_size=17):
    rect(x, y, w, h, fill=PANEL, stroke=BORDER, radius=0.22)
    if number:
        txt(x + 0.35, y + 0.28, w - 0.6, 0.8, [(number, tstyle(13, FAINT, bold=True, font=MONO))])
    txt(x, y + h * 0.30, w, 1.2, [(big, tstyle(big_size, color, bold=True, font=MONO, align="center"))])
    txt(x, y + h - 1.15, w, 1.0, [(label, tstyle(11.5, INK, align="center"))])


def callout(y, segments, h=1.9):
    rect(M, y, PAGE_W - 2 * M, h, fill=AMBER_FILL, stroke=AMBER, radius=0.24, stroke_w=0.035)
    ellipse(M + 0.55, y + h / 2 - 0.42, 0.84, AMBER)
    txt(M + 0.55, y + h / 2 - 0.42, 0.84, 0.84,
        [("!", tstyle(16, BG, bold=True, align="center"))], "middle")
    txt(M + 1.95, y + 0.3, PAGE_W - 2 * M - 2.5, h - 0.5,
        [(f"{lt}  {rt}", tstyle(12.5, BODY, spacing=0.14)) for lt, rt in segments], "middle")


def terminal(x, y, w, h, lines):
    rect(x, y, w, h, fill=PANEL, stroke=BORDER, radius=0.2)
    for i, col in enumerate((RED, AMBER, GREEN)):
        ellipse(x + 0.45 + i * 0.5, y + 0.42, 0.26, col)
    paras = []
    for item in lines:
        t, kind = item if isinstance(item, tuple) else (item, "out")
        c = {"prompt": GREEN, "out": INK, "dim": FAINT}[kind]
        paras.append((t, tstyle(12.5, c, font=MONO, spacing=0.12)))
    txt(x + 0.55, y + 1.25, w - 1.0, h - 1.5, paras)


def code_panel(lines, x, y, w, h, size=10.5):
    rect(x, y, w, h, fill=PANEL, stroke=BORDER, radius=0.2)
    paras = []
    for ln in lines:
        stripped = ln.lstrip(" ")
        indent = (len(ln) - len(stripped)) // 4
        c = FAINT if stripped.startswith("#") else INK
        paras.append(("\t" * indent + stripped, tstyle(size, c, font=MONO, spacing=0.07)))
    txt(x + 0.5, y + 0.45, w - 1.0, h - 0.8, paras)


def read_card(lines, x, y, w, header="Read it as"):
    h = 1.1 + 0.62 * (len(lines) + 1)
    rect(x, y, w, h, fill=VIOLET_FILL, stroke=VIOLET, radius=0.22, stroke_w=0.03)
    paras = [(header.upper(), tstyle(10.5, VIOLET, bold=True, font=MONO, tracking=0.05, spacing=0.28))]
    paras += [(ln, tstyle(11.5, INK, spacing=0.17)) for ln in lines]
    txt(x + 0.55, y + 0.42, w - 1.1, h - 0.7, paras)


def stat_row(cards, y=5.2, h=4.4):
    n = len(cards)
    gap = 0.7
    w = (PAGE_W - 2 * M - gap * (n - 1)) / n
    x = M
    for value, label in cards:
        rect(x, y, w, h, fill=PANEL, stroke=BORDER, radius=0.22)
        txt(x, y + 0.9, w, 1.9, [(value, tstyle(33, AMBER, bold=True, align="center"))])
        txt(x, y + h - 1.5, w, 1.1, [(label, tstyle(11, BODY, align="center"))])
        x += w + gap


def flow(items, y, h=1.9):
    n = len(items)
    arrow = 0.9
    w = (PAGE_W - 2 * M - arrow * (n - 1)) / n
    x = M
    for i, (head, sub) in enumerate(items):
        rect(x, y, w, h, fill=PANEL, stroke=BORDER, radius=0.2)
        txt(x, y + 0.32, w, 0.8, [(head, tstyle(13, INK, bold=True, align="center"))])
        txt(x, y + h - 0.85, w, 0.7, [(sub, tstyle(9.5, FAINT, align="center"))])
        if i < n - 1:
            txt(x + w, y, arrow, h, [("→", tstyle(16, VIOLET, bold=True, align="center"))], "middle")
        x += w + arrow


def loop_strip(y, checked=0):
    steps = [("Forward", "make a guess"), ("Loss", "measure wrongness"),
             ("Backprop", "find gradients"), ("Update", "change weights"),
             ("Repeat", "try again")]
    arrow, x = 0.7, M
    w = (PAGE_W - 2 * M - arrow * 4) / 5
    for i, (head, sub) in enumerate(steps):
        done = i < checked
        rect(x, y, w, 2.5, fill=(VIOLET_FILL if done else PANEL),
             stroke=(VIOLET if done else BORDER), radius=0.2)
        num = f"{i + 1}"
        txt(x + 0.3, y + 0.25, w - 0.5, 0.6,
            [((num + "  ✓") if done else num, tstyle(11, (VIOLET if done else FAINT), bold=True, font=MONO))])
        txt(x, y + 0.95, w, 0.8, [(head, tstyle(13, INK, bold=True, align="center"))])
        txt(x, y + 1.6, w, 0.7, [(sub, tstyle(9, FAINT, align="center"))])
        if i < 4:
            txt(x + w, y, arrow, 2.5, [("→", tstyle(15, VIOLET, bold=True, align="center"))], "middle")
        x += w + arrow


def checkpoint_banner(text, y=12.15):
    rect(M, y, PAGE_W - 2 * M, 1.15, fill="10241A", stroke=GREEN, radius=0.2, stroke_w=0.028)
    txt(M + 0.6, y, PAGE_W - 2 * M - 1, 1.15,
        [(f"✓   {text}", tstyle(11.5, GREEN, bold=True))], "middle")


DIGIT_3 = ["01111110", "11100111", "00000111", "00011110", "00011110",
           "00000111", "00000111", "11100111", "01111110", "00111100"]
DIGIT_4 = ["00001100", "00011100", "00111100", "01101100", "11001100",
           "11111111", "11111111", "00001100", "00001100", "00001100"]
DIGIT_5 = ["11111110", "11000000", "11000000", "11111100", "00000110",
           "00000011", "00000011", "11000111", "01111110", "00111100"]


def pixel_digit(x, y, bitmap=DIGIT_3, cell=0.62, color=VIOLET):
    for r, row in enumerate(bitmap):
        for c, ch in enumerate(row):
            rect(x + c * cell, y + r * cell, cell - 0.06, cell - 0.06,
                 fill=(color if ch == "1" else "141824"))


# ---------------------------------------------------------------- pages
_pages: list[tuple[str, str]] = []


def page(notes=""):
    content = "".join(_el)
    nx = ""
    if notes:
        ns = tstyle(12, INK, spacing=0.16)
        paras = "".join(f'<text:p text:style-name="{ns}">{escape(l)}</text:p>'
                        for l in notes.strip().split("\n"))
        nx = ('<presentation:notes><draw:frame svg:x="2cm" svg:y="1.2cm" '
              f'svg:width="17cm" svg:height="12cm"><draw:text-box>{paras}'
              '</draw:text-box></draw:frame></presentation:notes>')
    _pages.append((content, nx))
    _el.clear()


# ================================================================ SLIDES
def build():
    # 1 - Hook
    kicker("PCS Workshop Intro  ·  From Zero to AI")
    title("Build a neural network\nthat reads handwriting", size=32, w=13, y=3.1)
    lead(["One Python file. Real MNIST digits.", "A learning loop you can watch."],
         y=7.7, w=12.5, size=15, color=BODY)
    accent("You will write every line that matters -", y=9.6, w=12.5)
    accent("the layers, the loss, the update.", y=10.2, w=12.5)
    pixel_digit(16.7, 2.9, DIGIT_3, cell=0.66)
    txt(16.7, 9.6, 5.3, 0.7, [("what number is this?", tstyle(11, FAINT, italic=True, align="center"))])
    tag(1)
    page("""
Do not say the answer - ask the room; someone says "3".
Ask HOW they know: they cannot fully explain it, and neither will our network.
The promise: one file, built from scratch, that learns to read these.
""")

    # 2 - The idea and the loop
    kicker("The one idea")
    title("Guess. Measure. Change. Repeat.", size=30, w=22)
    lead([
        "A network starts with random weights, so its first guesses are bad - and that",
        "is exactly where learning begins.",
        "",
        "Each round measures how wrong the guess was, finds which weights caused the",
        "error, and nudges every weight a little.",
    ], y=4.6, w=22.5, size=13, gap=0.16)
    loop_strip(8.3, checked=0)
    accent("Every line of code today belongs to one of these five moves.", y=11.5, w=22)
    tag(2)
    page("""
If a student remembers one sentence tomorrow, make it the title of this slide.
The loop strip returns on slide 12 with every step checked - point back here
whenever the code changes.
""")

    # 3 - The input
    kicker("What the computer sees")
    title("A picture is 784 numbers", size=32, w=13.5)
    lead([
        "A 28 x 28 grayscale image: one brightness value per pixel, 0 to 255.",
        "Flatten the square into one row of 784 numbers - no pixel is lost.",
        "Divide by 255 so every value lands between 0 and 1.",
    ], y=4.6, w=13.2, size=13.5)
    code_panel(["x = image.view(-1, 784) / 255.0"], x=M, y=9.6, w=13.2, h=1.5, size=12)
    pixel_digit(16.4, 3.2, DIGIT_3, cell=0.6)
    tag(3)
    page("""
"Grayscale" = one number per pixel. -1 in view() means "however many images there are."
Flattening changes the shape, not the information.
""")

    # 4 - A layer
    kicker("The core move")
    title("Weighted sums, plus a bias", size=32)
    lead([
        "A layer multiplies each input by an adjustable weight, adds the products,",
        "then adds a bias - producing a new set of numbers.",
        "",
        'The key word is "adjustable": learning is nothing more than changing',
        "these weights.",
    ], y=4.3, w=22, size=13.5, gap=0.18)
    code_panel(["(images, 784) @ (784, 128) + (128)  ->  (images, 128)"],
               x=M, y=8.8, w=PAGE_W - 2 * M, h=1.5, size=12)
    callout(10.9, [("The inner dimensions match; the outer ones survive.",
                    "@ runs every multiply-and-add at once.")], h=1.5)
    tag(4)
    page("""
No prior workshop to lean on - build it from "multiply and add".
Trace the shapes with a finger: the 784 on both sides cancels; (images, 128) is left.
""")

    # 5 - Live build Linear
    kicker("Live build  ·  Linear")
    title("Build one learned layer", size=26, w=10.5)
    code_panel([
        "class Linear:",
        "    def __init__(self, in_features, out_features):",
        "        std = (2 / in_features) ** 0.5",
        "        self.weights = torch.randn(",
        "            in_features, out_features) * std",
        "        self.bias = torch.zeros(out_features)",
        "",
        "        self.weights.requires_grad_()",
        "        self.bias.requires_grad_()",
        "",
        "    def forward(self, x):",
        "        return x @ self.weights + self.bias",
        "",
        "    def parameters(self):",
        "        return [self.weights, self.bias]",
    ], x=12.7, y=2.7, w=PAGE_W - M - 12.7, h=8.9, size=9.5)
    read_card([
        "Random weights, zero biases.",
        "Ask PyTorch to track them.",
        "forward() makes the guess.",
        "parameters() = every value",
        "the loop may change.",
    ], x=M, y=5.1, w=10.2)
    checkpoint_banner("Checkpoint 1 - save the file, run the cell.  Expect (3, 784) -> (3, 128).")
    tag(5)
    page("""
Concept: a layer is a learned matrix multiply plus a bias.
Expected: Linear checkpoint passed: (3, 784) -> (3, 128)
Pause: after forward() - "this one line is the guess."
Likely stumble: forgetting requires_grad_() (grads are None later); mismatched @ shapes.
Do not derive the std formula - call it a sensible starting scale.
Recovery: recover(1).
""")

    # 6 - ReLU
    kicker("Live build  ·  ReLU")
    title("Add a bend", size=32, w=10)
    code_panel([
        "class ReLU:",
        "    def forward(self, x):",
        "        return x.clamp(min=0)",
    ], x=12.7, y=2.9, w=PAGE_W - M - 12.7, h=2.9, size=10.5)
    read_card([
        "Below zero becomes zero.",
        "Everything else passes through.",
        "[-2, 0, 3]  ->  [0, 0, 3]",
    ], x=12.7, y=6.4, w=PAGE_W - M - 12.7)
    lead([
        "Stack linear layers with nothing between them and the whole",
        "stack is still just one linear layer.",
        "",
        "Digits are messy; the model needs bends to draw richer",
        "boundaries.",
    ], y=4.5, w=10.4, size=13, gap=0.16)
    tag(6)
    page("""
Concept: the bend that stops stacked layers collapsing into one.
Verified inside Checkpoint 2, no checkpoint of its own.
Likely stumble: x.clamp(0) (that is max), or max(x, 0) on a tensor.
Recovery: recover(2).
""")

    # 7 - NeuralNetwork
    kicker("Live build  ·  Network")
    title("784  ->  128  ->  128  ->  10", size=30)
    txt(M, 3.9, 22, 0.8, [("Linear, ReLU, Linear, ReLU, Linear. The ReLUs change values, not dimensions.",
                           tstyle(12, FAINT, italic=True))])
    code_panel([
        "class NeuralNetwork:",
        "    def __init__(self, input_size, hidden_size, output_size):",
        "        self.layer1 = Linear(input_size, hidden_size)",
        "        self.layer2 = Linear(hidden_size, hidden_size)",
        "        self.layer3 = Linear(hidden_size, output_size)",
        "        self.relu1 = ReLU()",
        "        self.relu2 = ReLU()",
        "",
        "    def forward(self, x):",
        "        x = self.layer1.forward(x)",
        "        x = self.relu1.forward(x)",
        "        x = self.layer2.forward(x)",
        "        x = self.relu2.forward(x)",
        "        x = self.layer3.forward(x)",
        "        return x",
    ], x=9.9, y=4.9, w=PAGE_W - M - 9.9, h=6.8, size=8.5)
    read_card([
        "Six trainable tensors:",
        "three weights,",
        "three biases.",
    ], x=M, y=5.2, w=7.6)
    checkpoint_banner("Checkpoint 2 - four images become ten scores each.  Expect (4, 784) -> (4, 10).")
    tag(7)
    page("""
Concept: the pieces become one object that turns pixels into ten scores.
Expected: Network checkpoint passed: (4, 784) -> (4, 10)
Pause: count the six tensors together before running.
Likely stumble: self.layer1(x) instead of .forward(x); a missing ReLU.
Recovery: recover(2).
""")

    # 8 - Ten outputs
    kicker("Reading the result")
    title("Ten scores, one guess", size=32)
    card(M, 5.2, 6.7, 4.6, "01", "argmax", "largest score = the guess", color=VIOLET, big_size=17)
    card(M + 7.5, 5.2, 6.7, 4.6, "02", "logit", "the name for one raw score", color=VIOLET, big_size=17)
    card(M + 15.0, 5.2, 6.7, 4.6, "03", "softmax", "scores into probabilities", color=VIOLET, big_size=16)
    accent("Same guess with or without softmax - biggest score wins. We never need it to train.", y=10.6, w=22)
    callout(11.4, [("Cross-entropy", "compares all ten scores with the correct digit - that becomes the loss.")], h=1.5)
    tag(8)
    page("""
Show softmax once so "logit" is not a loose end, then set it aside.
Biggest score wins, with or without it.
""")

    # 9 - Data
    kicker("Live build  ·  Data")
    title("Load MNIST", size=32, w=9)
    code_panel([
        "train = torchvision.datasets.MNIST(",
        '    root=\"./data\", train=True, download=True)',
        "test = torchvision.datasets.MNIST(",
        '    root=\"./data\", train=False, download=True)',
        "",
        "x = train.data.float().view(-1, 784) / 255.0",
        "target = train.targets",
        "x_test = test.data.float().view(-1, 784) / 255.0",
        "target_test = test.targets",
    ], x=10.4, y=2.7, w=PAGE_W - M - 10.4, h=7.2, size=9.5)
    read_card([
        "Learn on one set,",
        "test on a separate set.",
        "Flatten to 784,",
        "scale 0-255 to 0-1,",
        "keep each digit as the target.",
    ], x=M, y=4.6, w=8.4)
    tag(9)
    page("""
Concept: the flatten/scale from slide 3, on real data, plus the train/test split.
Pause: "why hold back test data?" - so accuracy measures learning, not memorising.
Likely stumble: forgetting .float() (uint8 breaks the matmul); forgetting / 255.0.
Recovery: the setup cell cached MNIST; re-run this block.
""")

    # 10 - Loss and backward
    kicker("Measure, then walk back")
    title("One number, then every gradient", size=30)
    lead([
        "loss = cross_entropy(prediction, target) is high when the right digit",
        "scores poorly, low when it wins - the single signal learning reduces.",
        "",
        "loss.backward() walks the recorded operations in reverse and reports",
        "how each weight contributed to the error.",
    ], y=4.3, w=22, size=13.5, gap=0.18)
    code_panel(["loss  <-  scores  <-  layers  <-  every weight and bias"],
               x=M, y=8.9, w=PAGE_W - 2 * M, h=1.4, size=12)
    callout(10.7, [("A gradient is a direction:", "changing this value that way would raise the loss.")], h=1.6)
    tag(10)
    page("""
Loss is wrongness, not accuracy. Do not open the calculus - the amber card is the
whole explanation students need today.
""")

    # 11 - Update
    kicker("Live build  ·  Update")
    title("One small step, then clear", size=29, w=10)
    code_panel([
        "loss.backward()",
        "",
        "with torch.no_grad():",
        "    for parameter in model.parameters():",
        "        parameter -= learning_rate * parameter.grad",
        "",
        "for parameter in model.parameters():",
        "    parameter.grad.zero_()",
    ], x=10.4, y=2.7, w=PAGE_W - M - 10.4, h=5.3, size=9.5)
    read_card([
        "Step opposite the gradient, a little.",
        "no_grad(): this is the change itself.",
        "Clear the grads, or the next round",
        "mixes old directions with new.",
    ], x=10.4, y=8.4, w=PAGE_W - M - 10.4)
    lead(["Each gradient points", "toward more error,", "so subtract a little", "of it from each weight."],
         y=4.4, w=8.2, size=12.5, gap=0.16)
    checkpoint_banner("Checkpoint 3 - one manual step makes a fixed problem's loss smaller.")
    tag(11)
    page("""
Concept: gradient descent - step opposite the gradient, a little; then zero the grads.
Expected: Learning checkpoint passed: 1.0247 -> 0.8123 (numbers vary).
Pause: "why minus?" - the gradient points uphill; we want downhill.
Likely stumble: update outside no_grad() -> in-place leaf error; forgetting zero_() -> loss lurches on epoch 2.
Recovery: recover(3).
""")

    # 12 - It is all the loop
    kicker("The code is the loop")
    title("Nothing is hidden", size=32)
    loop_strip(3.9, checked=5)
    code_panel([
        "prediction = model.forward(x)                 # 1 forward",
        "loss = cross_entropy(prediction, target)      # 2 loss",
        "loss.backward()                               # 3 backprop",
        "parameter -= learning_rate * parameter.grad   # 4 update",
        "parameter.grad.zero_()                        # 5 repeat -> next epoch",
    ], x=M, y=7.2, w=PAGE_W - 2 * M, h=4.4, size=9.5)
    tag(12)
    page("""
Have the room name each of the five moves before you run anything.
Then reveal main() and run it.
""")

    # 13 - The payoff
    kicker("Watch it learn")
    title("Ten rounds, then sixty", size=32)
    stat_row([("~2.48", "starting loss"), ("~1.69", "loss after 10 epochs"),
              ("~65%", "test accuracy at 10 epochs")], y=4.6, h=3.8)
    callout(8.9, [("Change epochs 10 -> 60:", "loss ~0.48, test accuracy ~88%. Same network, more rounds.")], h=1.5)
    accent("Blind guessing is 10%. Read the trend, not one exact number: loss down, accuracy up.", y=10.9, w=22)
    note_line("Illustrative seeded output - facilitator, use the numbers you measured on the event machine.")
    tag(13)
    page("""
Anchor on the 10% baseline first, then the numbers. Train and test accuracy both
print - note they track each other here. If the 60-epoch run is still going, keep talking.
""")

    # 14 - Where it gets it wrong
    kicker("Be honest about the model")
    title("It matches pixels - it does not know digits", size=25, w=22)
    rect(M, 4.6, 10.3, 6.1, fill=PANEL, stroke=BORDER, radius=0.22)
    rect(M + 11.0, 4.6, 10.3, 6.1, fill=PANEL, stroke=BORDER, radius=0.22)
    pixel_digit(M + 3.1, 5.1, DIGIT_4, cell=0.44, color=RED)
    pixel_digit(M + 14.1, 5.1, DIGIT_5, cell=0.44, color=RED)
    txt(M, 9.5, 10.3, 0.8, [("guess 9   ·   truth 4", tstyle(13, INK, bold=True, font=MONO, align="center"))])
    txt(M + 11.0, 9.5, 10.3, 0.8, [("guess 3   ·   truth 5", tstyle(13, INK, bold=True, font=MONO, align="center"))])
    accent("It learned pixel patterns that usually work. Draw a 4 like a 9 and it has nothing else to fall back on.",
           y=11.2, w=22)
    tag(14)
    page("""
The memorable slide. Keeps students from over-claiming what they built, and sets up
why bigger models and more data exist. The notebook produces these live.
""")

    # 15 - Your turn
    kicker("Before the runtime disappears")
    title("Keep the file. Change one thing.", size=31)
    lead([
        "1   Download mnist_network.py",
        "2   Pick one experiment",
        "3   Predict what will happen",
        "4   Change one value",
        "5   Run and compare",
    ], y=4.6, w=11.5, size=14, gap=0.32)
    read_card([
        "epochs 10 -> 60",
        "learning rate 0.1 -> 0.01",
        "hidden size 128 -> 32",
        "break the init (std = 1.0)",
        "layer1_weight_grid(model)",
    ], x=13.3, y=4.4, w=PAGE_W - M - 13.3, header="try one")
    accent("You built the layers, the gradients, and the update. The high-level PyTorch tools package the same machinery.",
           y=11.6, w=22)
    tag(15)
    page("""
End on the opening sentence: "Your network made a guess, measured how wrong it was,
changed its weights a little, and repeated. Matrix multiplication became a system
that learns." Then make sure everyone has downloaded the file.
""")


def render():
    build()
    pages = "".join(
        f'<draw:page draw:name="p{i}" draw:master-page-name="Default" '
        f'draw:style-name="dp1">{c}{n}</draw:page>'
        for i, (c, n) in enumerate(_pages, 1))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.presentation">
<office:automatic-styles>
<style:page-layout style:name="PL1"><style:page-layout-properties fo:page-width="{PAGE_W}cm" fo:page-height="{PAGE_H}cm" style:print-orientation="landscape"/></style:page-layout>
<style:style style:name="dp1" style:family="drawing-page"><style:drawing-page-properties draw:fill="solid" draw:fill-color="#{BG}"/></style:style>
{"".join(_styles.values())}
</office:automatic-styles>
<office:master-styles>
<style:master-page style:name="Default" style:page-layout-name="PL1" draw:style-name="dp1"/>
</office:master-styles>
<office:body><office:presentation>
{pages}
</office:presentation></office:body>
</office:document>
"""


def main():
    here = Path(__file__).resolve().parent
    fodp = here / "pcs-workshop-intro.fodp"
    fodp.write_text(render(), encoding="utf-8")
    print(f"wrote {fodp.name}  ({len(_pages)} slides)")
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("LibreOffice not found - convert the .fodp manually.")
        return
    for fmt in ("pptx", "pdf"):
        src = fodp if fmt == "pptx" else here / "pcs-workshop-intro.pptx"
        subprocess.run([soffice, "--headless", "--convert-to", fmt, "--outdir", str(here), str(src)],
                       check=True, capture_output=True)
        print(f"wrote pcs-workshop-intro.{fmt}")


if __name__ == "__main__":
    main()
