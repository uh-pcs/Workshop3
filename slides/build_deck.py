#!/usr/bin/env python3
"""Build the PCS Workshop Intro deck from the content in docs/slides.md.

Authoring source is a flat ODF presentation (`.fodp`, one XML file). LibreOffice
converts it to `.pptx` (for Google Slides import) and `.pdf` (offline copy):

    python3 slides/build_deck.py     # writes .fodp + .pptx + .pdf into slides/

The visual system (palette, fonts, grammar) is documented in docs/slides.md.
Built decks use Office-safe fonts; restyle to Poppins / Inter in Google Slides if
wanted.
"""

import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- design tokens
CANVAS = "FFF9EE"
INK = "24303A"
BLUE = "367BF5"
YELLOW = "FFD85A"
GREEN = "43B581"
PALE = "EAF2FF"
MINT = "E8F6EF"
MUTED = "77808C"

TITLE_FONT = "Calibri"
BODY_FONT = "Calibri"
CODE_FONT = "Consolas"

PAGE_W = 25.4
PAGE_H = 14.288
MARGIN = 1.6
TOTAL = 15

_styles: dict[str, str] = {}


def _reg(key: str, xml: str) -> str:
    _styles.setdefault(key, xml)
    return key


def gstyle(fill=None, stroke=None, stroke_color=INK, valign="top", pad=0.25):
    key = f"g_{fill}_{stroke}_{stroke_color}_{valign}_{pad}"
    if key in _styles:
        return key
    props = [
        f'draw:fill="solid" draw:fill-color="#{fill}"' if fill else 'draw:fill="none"',
        (
            f'draw:stroke="solid" svg:stroke-width="0.03cm" svg:stroke-color="#{stroke_color}"'
            if stroke
            else 'draw:stroke="none"'
        ),
        f'draw:textarea-vertical-align="{valign}"',
        'draw:auto-grow-height="false" draw:auto-grow-width="false"',
        'fo:padding-top="0.04cm" fo:padding-bottom="0.04cm"',
        f'fo:padding-left="{pad}cm" fo:padding-right="{pad}cm"',
    ]
    xml = (
        f'<style:style style:name="{key}" style:family="graphic">'
        f'<style:graphic-properties {" ".join(props)}/></style:style>'
    )
    return _reg(key, xml)


def pstyle(size, color=INK, bold=False, align="left", font=BODY_FONT, spacing=0.0):
    key = f"p_{size}_{color}_{bold}_{align}_{font}_{spacing}"
    if key in _styles:
        return key
    weight = ' fo:font-weight="bold"' if bold else ""
    xml = (
        f'<style:style style:name="{key}" style:family="paragraph">'
        f'<style:paragraph-properties fo:text-align="{align}" fo:margin-bottom="{spacing}cm"/>'
        f'<style:text-properties fo:font-size="{size}pt" fo:color="#{color}"{weight} '
        f'style:font-name="{font}"/></style:style>'
    )
    return _reg(key, xml)


# ---------------------------------------------------------------- elements
_elements: list[str] = []


def _para(item):
    text, ps = item if isinstance(item, tuple) else (item, pstyle(16))
    lead = len(text) - len(text.lstrip("\t"))
    rest = escape(text[lead:]) or " "
    prefix = f'<text:s text:c="{lead * 4}"/>' if lead else ""
    return f'<text:p text:style-name="{ps}">{prefix}{rest}</text:p>'


def box(x, y, w, h, paras, valign="top"):
    g = gstyle(valign=valign)
    body_xml = "".join(_para(p) for p in paras)
    _elements.append(
        f'<draw:frame draw:style-name="{g}" svg:x="{x}cm" svg:y="{y}cm" '
        f'svg:width="{w}cm" svg:height="{h}cm">'
        f"<draw:text-box>{body_xml}</draw:text-box></draw:frame>"
    )


def rect(x, y, w, h, fill, stroke=None, stroke_color=INK):
    g = gstyle(fill=fill, stroke=stroke, stroke_color=stroke_color)
    _elements.append(
        f'<draw:rect draw:style-name="{g}" svg:x="{x}cm" svg:y="{y}cm" '
        f'svg:width="{w}cm" svg:height="{h}cm"/>'
    )


def banner(y, text, fill, size=13, color=INK, bold=True, x=MARGIN, w=22.2, h=1.4):
    rect(x, y, w, h, fill)
    box(x, y, w, h, [(text, pstyle(size, color, bold=bold, align="center"))], "middle")


def kicker(text):
    w = min(11.0, 0.95 + 0.212 * len(text))
    rect(MARGIN, 0.95, w, 0.78, PALE)
    box(MARGIN, 0.95, w, 0.78, [(text.upper(), pstyle(9.5, INK, bold=True))], "middle")


def title(text, size=32, w=22.4):
    box(MARGIN, 2.15, w, 1.9, [(text, pstyle(size, INK, bold=True, font=TITLE_FONT))])


def body(lines, x=MARGIN, y=4.6, w=22.0, size=15.5, gap=0.34):
    paras = [(f"•  {ln}", pstyle(size, INK, spacing=gap)) for ln in lines]
    box(x, y, w, PAGE_H - y - 1.2, paras)


def plain(lines, x=MARGIN, y=4.6, w=22.0, size=14, gap=0.18, color=INK, bold=False,
          font=BODY_FONT, h=None):
    paras = [(ln, pstyle(size, color, bold=bold, font=font, spacing=gap)) for ln in lines]
    box(x, y, w, h if h is not None else PAGE_H - y - 1.0, paras)


def tabnum(n):
    box(PAGE_W - 3.7, PAGE_H - 1.05, 2.9, 0.6,
        [(f"{n:02d} / {TOTAL}", pstyle(9.5, MUTED, align="right"))])


def checkpoint_strip(text, y=12.0):
    rect(MARGIN, y, 22.2, 1.2, MINT)
    box(MARGIN, y, 22.2, 1.2, [(text, pstyle(12, INK, bold=True, align="center"))], "middle")


# ---------------------------------------------------------------- composites
def loop_diagram(y, checked=0):
    steps = [
        ("1", "Forward", "make a guess"),
        ("2", "Loss", "measure wrongness"),
        ("3", "Backprop", "find gradients"),
        ("4", "Update", "change weights"),
        ("5", "Repeat", "try again"),
    ]
    w, gap, x = 4.0, 0.55, MARGIN
    for i, (n, head, sub) in enumerate(steps):
        done = i < checked
        rect(x, y, w, 2.5, MINT if done else PALE)
        mark = f"{n}  {head}  ✓" if done else f"{n}  {head}"
        box(x, y + 0.3, w, 0.9, [(mark, pstyle(13, INK, bold=True, align="center"))], "middle")
        box(x, y + 1.3, w, 0.9, [(sub, pstyle(10, MUTED, align="center"))], "middle")
        if i < 4:
            box(x + w, y, gap, 2.5, [("→", pstyle(15, BLUE, bold=True, align="center"))], "middle")
        x += w + gap


def stat_cards(cards, y=5.4, h=4.6):
    w, gap, x = 6.87, 0.8, MARGIN
    for big, label in cards:
        rect(x, y, w, h, PALE)
        box(x, y + 0.7, w, 1.7, [(big, pstyle(32, INK, bold=True, align="center"))], "middle")
        box(x, y + h - 1.7, w, 1.3, [(label, pstyle(12, MUTED, align="center"))], "middle")
        x += w + gap


def code_panel(lines, x, y=4.4, w=None, h=None, size=10):
    w = w if w is not None else (PAGE_W - MARGIN - x)
    h = h if h is not None else (PAGE_H - y - 1.3)
    rect(x, y, w, h, PALE)
    paras = []
    for ln in lines:
        stripped = ln.lstrip(" ")
        indent = (len(ln) - len(stripped)) // 4
        paras.append(("\t" * indent + stripped, pstyle(size, INK, font=CODE_FONT, spacing=0.06)))
    box(x + 0.35, y + 0.3, w - 0.7, h - 0.6, paras)


def read_card(lines, x, y, w, header="Read it as"):
    h = 0.95 + 0.6 * (len(lines) + 1)
    rect(x, y, w, h, YELLOW)
    paras = [(header, pstyle(11.5, INK, bold=True, spacing=0.22))]
    paras += [(ln, pstyle(11.5, INK, spacing=0.16)) for ln in lines]
    box(x + 0.4, y + 0.3, w - 0.8, h - 0.5, paras)


DIGIT_3 = [
    " ####### ",
    "#########",
    "     ####",
    "    ###  ",
    "  ####   ",
    "    ###  ",
    "      ###",
    "#     ###",
    "#########",
    " ####### ",
]
DIGIT_4 = [
    "     ##  ",
    "    ###  ",
    "   ####  ",
    "  ## ##  ",
    " ##  ##  ",
    "######## ",
    "#########",
    "     ##  ",
    "     ##  ",
    "     ##  ",
]
DIGIT_5 = [
    "######## ",
    "##       ",
    "##       ",
    "#######  ",
    "      ## ",
    "       ##",
    "       ##",
    "##     ##",
    " ####### ",
    "  #####  ",
]


def pixel_digit(x, y, bitmap=DIGIT_3, cell=0.66):
    for r, row in enumerate(bitmap):
        for c, ch in enumerate(row):
            g = gstyle(fill=(INK if ch == "#" else CANVAS), stroke=True, stroke_color="ECE1CD")
            _elements.append(
                f'<draw:rect draw:style-name="{g}" svg:x="{x + c * cell}cm" '
                f'svg:y="{y + r * cell}cm" svg:width="{cell}cm" svg:height="{cell}cm"/>'
            )


# ---------------------------------------------------------------- pages
_pages: list[tuple[str, str]] = []


def page(notes=""):
    content = "".join(_elements)
    notes_xml = ""
    if notes:
        ns = pstyle(12, INK, spacing=0.15)
        paras = "".join(
            f'<text:p text:style-name="{ns}">{escape(line)}</text:p>'
            for line in notes.strip().split("\n")
        )
        notes_xml = (
            "<presentation:notes>"
            '<draw:frame svg:x="2cm" svg:y="1.2cm" svg:width="17cm" svg:height="12cm">'
            f"<draw:text-box>{paras}</draw:text-box></draw:frame>"
            "</presentation:notes>"
        )
    _pages.append((content, notes_xml))
    _elements.clear()


# ================================================================ SLIDES
def build():
    # 1 - Hook
    kicker("PCS Workshop Intro")
    title("What number is this?", size=36, w=13.6)
    pixel_digit(16.3, 3.1)
    plain([
        "Your phone reads it instantly.",
        "In one hour you build the thing",
        "that can - one Python file, from scratch.",
    ], y=7.4, w=13.6, size=16, gap=0.3, bold=True)
    tabnum(1)
    page("""
Do not say the answer. Ask the room; someone says "3".
Ask HOW they know - they cannot fully explain it, and neither will our network.
The promise: one file, built from scratch, that learns to read these.
""")

    # 2 - The idea and the loop
    kicker("The one idea")
    title("Guess. Measure. Change. Repeat.")
    body([
        "A network starts with random weights, so its first guesses are bad - that is where learning begins.",
        "Each round measures how wrong the guess was, finds which weights caused the error, and nudges every weight a little.",
    ], y=4.4, size=15)
    loop_diagram(7.7, checked=0)
    plain(["Every line of code today belongs to one of these five moves."], y=11.1, size=13, bold=True)
    tabnum(2)
    page("""
If a student remembers one sentence tomorrow, make it the title of this slide.
The loop diagram returns at the end with every step checked - point here whenever
the code changes.
""")

    # 3 - The input
    kicker("What the computer sees")
    title("A picture is 784 numbers", size=30, w=13.5)
    pixel_digit(16.8, 4.5, cell=0.58)
    body([
        "A 28 x 28 grayscale image: one brightness value per pixel, 0 to 255.",
        "Flatten the square into one row of 784 numbers - no pixel is lost.",
        "Divide by 255 so every value lands between 0 and 1.",
    ], y=4.8, w=13.5, size=14)
    banner(10.6, "x = image.view(-1, 784) / 255.0", PALE, size=14, bold=False, w=13.5, x=MARGIN)
    tabnum(3)
    page("""
"Grayscale" = one number per pixel. -1 in view() means "however many images there are."
Flattening changes the shape, not the information.
""")

    # 4 - A layer
    kicker("The core move")
    title("Weighted sums, plus a bias", size=28)
    body([
        "A layer multiplies each input by an adjustable weight, adds the products, then adds a bias - producing a new set of numbers.",
        'The key word is "adjustable": learning is nothing more than changing these weights.',
    ], y=4.6, size=15)
    banner(8.6, "(images, 784) @ (784, 128) + (128)   ->   (images, 128)", PALE, size=15, bold=False)
    banner(10.8, "@ does every multiply-and-add at once. Inside dims match; outside dims survive.", YELLOW)
    tabnum(4)
    page("""
No prior workshop to lean on. Build it from "multiply and add".
Trace the shapes with a finger: the 784 on both sides cancels; (images, 128) is left.
""")

    # 5 - Live build Linear
    kicker("Live build - Linear")
    title("Build one learned layer", size=30, w=10.6)
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
    ], x=12.9, y=2.9, h=8.6, size=9.5)
    plain([
        "Random weights, zero biases.",
        "Ask PyTorch to track them.",
        "",
        "forward() makes the guess.",
        "parameters() hands the loop",
        "every value it may change.",
    ], y=4.6, w=10.6, size=13, gap=0.22)
    checkpoint_strip("Checkpoint 1  -  save the file, run the cell.  Expect (3, 784)  ->  (3, 128).")
    tabnum(5)
    page("""
Concept: a layer is a learned matrix multiply plus a bias.
Expected: Linear checkpoint passed: (3, 784) -> (3, 128)
Pause: after forward() - "this one line is the guess."
Likely stumble: forgetting requires_grad_() (grads are None later); mismatched @ shapes.
Do not derive the std formula - call it a sensible starting scale.
Recovery: recover(1).
""")

    # 6 - Live build ReLU
    kicker("Live build - ReLU")
    title("Add a bend", size=32, w=10.0)
    code_panel([
        "class ReLU:",
        "    def forward(self, x):",
        "        return x.clamp(min=0)",
    ], x=12.9, y=3.0, h=3.0, size=11)
    read_card([
        "Below zero becomes zero.",
        "Everything else passes through.",
        "[-2, 0, 3]  ->  [0, 0, 3]",
    ], x=12.9, y=6.6, w=10.9, header="Read it as")
    body([
        "Stack linear layers with nothing between them and the whole stack is still just one linear layer.",
        "Digits are messy; the model needs bends to draw richer boundaries.",
    ], y=4.6, w=10.6, size=13)
    tabnum(6)
    page("""
Concept: the bend that stops stacked layers collapsing into one.
Verified inside Checkpoint 2, no checkpoint of its own.
Likely stumble: x.clamp(0) (that is max), or max(x, 0) on a tensor.
Recovery: recover(2).
""")

    # 7 - Stack and build the network
    kicker("Live build - Network")
    title("784  ->  128  ->  128  ->  10", size=30)
    plain(["Linear, ReLU, Linear, ReLU, Linear.  The ReLUs change values, not dimensions."],
          y=4.0, size=12.5, color=MUTED)
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
    ], x=10.3, y=4.7, h=6.7, size=9)
    plain([
        "parameters() adds up",
        "to six tensors:",
        "three weights,",
        "three biases.",
    ], y=5.2, w=8.0, size=12.5, gap=0.22)
    checkpoint_strip("Checkpoint 2  -  four images become ten scores each.  Expect (4, 784)  ->  (4, 10).")
    tabnum(7)
    page("""
Concept: the pieces become one object that turns pixels into ten scores.
Expected: Network checkpoint passed: (4, 784) -> (4, 10)
Pause: count the six tensors together before running.
Likely stumble: self.layer1(x) instead of .forward(x); a missing ReLU.
Recovery: recover(2).
""")

    # 8 - Ten outputs
    kicker("Reading the result")
    title("Ten scores  ->  one guess")
    body([
        "Ten numbers out, one per digit. The largest is the model's guess (argmax).",
        "A raw score is called a logit.",
        "prediction.softmax(dim=1) turns the ten into probabilities that add to 1 - same guess, readable confidence.",
    ], y=4.7, size=15)
    banner(10.0, "Cross-entropy will compare all ten scores with the correct digit.", YELLOW)
    tabnum(8)
    page("""
Show softmax once so "logit" is not a loose end, then set it aside - we never need
it to train. Biggest score wins, with or without it.
""")

    # 9 - Live build data
    kicker("Live build - Data")
    title("Load MNIST", size=32, w=9.0)
    code_panel([
        "train = torchvision.datasets.MNIST(",
        '    root="./data", train=True, download=True)',
        "test = torchvision.datasets.MNIST(",
        '    root="./data", train=False, download=True)',
        "",
        "x = train.data.float().view(-1, 784) / 255.0",
        "target = train.targets",
        "x_test = test.data.float().view(-1, 784) / 255.0",
        "target_test = test.targets",
    ], x=10.6, y=2.9, h=7.0, size=9.5)
    plain([
        "Examples for learning,",
        "separate examples for testing.",
        "",
        "Flatten to 784.",
        "Scale 0-255 down to 0-1.",
        "Keep each digit as the target.",
    ], y=4.6, w=8.6, size=12.5, gap=0.22)
    tabnum(9)
    page("""
Concept: the flatten/scale from slide 3, on real data, plus the train/test split.
Pause: "why hold back test data?" - so accuracy measures learning, not memorising.
Likely stumble: forgetting .float() (uint8 breaks the matmul); forgetting / 255.0.
Recovery: the setup cell cached MNIST; re-run this block.
""")

    # 10 - Loss and backward
    kicker("Measure, then walk back")
    title("One number, then every gradient", size=30)
    body([
        "loss = cross_entropy(prediction, target) is high when the right digit scores poorly, low when it wins - the single signal learning reduces.",
        "loss.backward() walks the remembered operations in reverse and reports how each weight contributed to the error.",
    ], y=4.5, size=14.5)
    banner(9.4, "loss  <-  scores  <-  layers  <-  every weight and bias", PALE, size=14, bold=False)
    banner(11.4, "A gradient is a direction: changing this value that way would raise the loss.", YELLOW)
    tabnum(10)
    page("""
Loss is wrongness, not accuracy. Do not open the calculus - the yellow card is the
whole explanation students need today.
""")

    # 11 - Live build update
    kicker("Live build - Update")
    title("One small step, then clear", size=28, w=9.8)
    code_panel([
        "loss.backward()",
        "",
        "with torch.no_grad():",
        "    for parameter in model.parameters():",
        "        parameter -= learning_rate * parameter.grad",
        "",
        "for parameter in model.parameters():",
        "    parameter.grad.zero_()",
    ], x=10.6, y=2.9, h=5.2, size=9.5)
    read_card([
        "Step opposite the gradient, a little.",
        "no_grad(): this is the change itself.",
        "Clear the grads, or the next round mixes old with new.",
    ], x=10.6, y=8.3, w=13.2, header="Read it as")
    plain([
        "Each gradient points",
        "toward more error,",
        "so subtract a little",
        "of it from each weight.",
    ], y=4.6, w=8.4, size=12.5, gap=0.22)
    checkpoint_strip("Checkpoint 3  -  one manual step makes a fixed problem's loss smaller.")
    tabnum(11)
    page("""
Concept: gradient descent - step opposite the gradient, a little; then zero the grads.
Expected: Learning checkpoint passed: 1.0247 -> 0.8123 (numbers vary).
Pause: "why minus?" the gradient points uphill; we want downhill.
Likely stumble: update outside no_grad() -> in-place leaf error; forgetting zero_() -> loss lurches on epoch 2.
Recovery: recover(3).
""")

    # 12 - It is all the loop
    kicker("The code is the loop")
    title("Nothing is hidden")
    loop_diagram(4.5, checked=5)
    plain([
        "1   prediction = model.forward(x)",
        "2   loss = cross_entropy(prediction, target)",
        "3   loss.backward()",
        "4   parameter -= learning_rate * parameter.grad",
        "5   parameter.grad.zero_()   ->   next epoch",
    ], y=7.8, size=12, gap=0.2, font=CODE_FONT)
    tabnum(12)
    page("""
Have the room name each of the five moves before you run anything. Then reveal
main() and run it.
""")

    # 13 - The payoff
    kicker("Watch it learn")
    title("Ten rounds, then sixty")
    stat_cards([("~2.48", "starting loss"), ("~1.69", "loss after 10 epochs"), ("~65%", "test accuracy, 10 epochs")], y=4.8, h=3.8)
    banner(9.0, "Change epochs 10 -> 60:  loss ~0.48,  test accuracy ~88%.  Same architecture, more rounds.",
           PALE, size=12.5)
    banner(10.9, "Blind guessing is 10%. Read the trend: loss down, accuracy up.", YELLOW)
    plain(["Illustrative seeded output; facilitator, use the numbers you measured on the event machine."],
          y=12.7, size=9.5, color=MUTED, h=0.6)
    tabnum(13)
    page("""
Anchor on the 10% baseline first. Train and test accuracy both print - note they
track each other here. If the 60-epoch run is still going, keep talking.
""")

    # 14 - Where it gets it wrong
    kicker("Be honest about the model")
    title("It matches pixels - it does not know digits", size=27)
    pixel_digit(3.0, 4.9, bitmap=DIGIT_4, cell=0.5)
    pixel_digit(14.4, 4.9, bitmap=DIGIT_5, cell=0.5)
    box(3.0, 10.1, 8.5, 0.9, [("guess 9   ·   truth 4", pstyle(14, INK, bold=True, font=CODE_FONT))], "middle")
    box(14.4, 10.1, 8.5, 0.9, [("guess 3   ·   truth 5", pstyle(14, INK, bold=True, font=CODE_FONT))], "middle")
    plain(["It learned pixel patterns that usually work. When a 4 is drawn like a 9, it has nothing else to fall back on."],
          y=11.4, size=13)
    tabnum(14)
    page("""
The memorable slide. Keeps students from over-claiming what they built, and sets up
why bigger models and more data exist. The notebook produces these live.
""")

    # 15 - Your turn
    kicker("Before the runtime disappears")
    title("Keep the file. Change one thing.")
    plain([
        "1   Download mnist_network.py",
        "2   Pick one experiment",
        "3   Predict what will happen",
        "4   Change one value",
        "5   Run and compare",
    ], y=4.8, w=12.0, size=14, gap=0.3)
    rect(14.6, 4.6, 9.2, 7.0, YELLOW)
    plain([
        "Try one:",
        "epochs 10 -> 60",
        "learning rate 0.1 -> 0.01",
        "hidden size 128 -> 32",
        "break the init (std = 1.0)",
        "layer1_weight_grid(model)",
    ], x=15.1, y=4.9, w=8.2, size=12, gap=0.2)
    plain(["You built the layers, the gradients, and the update. The high-level PyTorch tools package the same machinery."],
          y=12.2, size=10.5, color=MUTED)
    tabnum(15)
    page("""
End on the opening sentence: "Your network made a guess, measured how wrong it was,
changed its weights a little, and repeated. Matrix multiplication became a system
that learns." Then make sure everyone has downloaded the file.
""")


def render() -> str:
    build()
    pages_xml = "".join(
        f'<draw:page draw:name="page{i}" draw:master-page-name="Default" '
        f'draw:style-name="dp1">{content}{notes}</draw:page>'
        for i, (content, notes) in enumerate(_pages, 1)
    )
    styles_xml = "".join(_styles.values())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.3" office:mimetype="application/vnd.oasis.opendocument.presentation">
<office:automatic-styles>
<style:page-layout style:name="PL1"><style:page-layout-properties fo:page-width="{PAGE_W}cm" fo:page-height="{PAGE_H}cm" style:print-orientation="landscape"/></style:page-layout>
<style:style style:name="dp1" style:family="drawing-page"><style:drawing-page-properties draw:fill="solid" draw:fill-color="#{CANVAS}"/></style:style>
{styles_xml}
</office:automatic-styles>
<office:master-styles>
<style:master-page style:name="Default" style:page-layout-name="PL1" draw:style-name="dp1"/>
</office:master-styles>
<office:body><office:presentation>
{pages_xml}
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
        print("LibreOffice not found - convert pcs-workshop-intro.fodp manually.")
        return
    for fmt in ("pptx", "pdf"):
        src = fodp if fmt == "pptx" else here / "pcs-workshop-intro.pptx"
        subprocess.run(
            [soffice, "--headless", "--convert-to", fmt, "--outdir", str(here), str(src)],
            check=True, capture_output=True,
        )
        print(f"wrote pcs-workshop-intro.{fmt}")


if __name__ == "__main__":
    main()
