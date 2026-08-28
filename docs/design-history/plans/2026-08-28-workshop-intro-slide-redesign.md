# Workshop Intro Slide Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recast the neural-network workshop as the first PCS workshop and replace its Workshop2-derived deck with an original 24-slide interactive digital-classroom presentation.

**Architecture:** Keep the repository and public URLs named `Workshop3`, but change visible workshop copy to **PCS Workshop Intro**. Treat the local PPTX as the verified authoring source, rebuild it from a blank presentation using `@oai/artifact-tool`, then import the verified result into Google Slides and validate the native output.

**Tech Stack:** Markdown, Jupyter Notebook JSON, Python/pytest, JavaScript ES modules, `@oai/artifact-tool`, Google Slides/Drive connector tools

**Spec:** `docs/superpowers/specs/2026-08-28-workshop-intro-redesign-design.md`

## Global Constraints

- Keep the public repository and Colab URLs at `daryl-888/Workshop3`.
- Use **PCS Workshop Intro** as the visible identity.
- Do not mention Workshop1, Workshop2, a prior blur lab, or assumed previous matrix-multiplication instruction.
- Preserve the 60-minute workshop, one-file build, manual layers, manual parameter update, and five-step learning loop.
- Rebuild all 24 slides using the interactive digital-classroom visual system from the spec.
- Preserve complete presenter notes on every coding slide.
- Do not modify Workshop1 or Workshop2.

---

### Task 1: Make the repository copy standalone

**Files:**
- Modify: `README.md`
- Modify: `FACILITATOR.md`
- Modify: `mnist_workshop.ipynb`
- Create: `tests/test_first_workshop_copy.py`

**Interfaces:**
- Consumes: Existing workshop code and `Workshop3` URLs.
- Produces: Standalone student-facing copy with unchanged repository links.

- [ ] **Step 1: Write the failing copy test**

```python
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def visible_copy():
    notebook = json.loads((ROOT / "mnist_workshop.ipynb").read_text())
    notebook_text = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "markdown"
    )
    return "\n".join([
        (ROOT / "README.md").read_text(),
        (ROOT / "FACILITATOR.md").read_text(),
        notebook_text,
    ])


def test_workshop_is_presented_as_the_intro():
    text = visible_copy()
    assert "PCS Workshop Intro" in text
    for forbidden in ("Workshop 1", "Workshop 2", "Workshop 3", "Workshop1", "Workshop2"):
        assert forbidden not in text


def test_repository_urls_remain_workshop3():
    readme = (ROOT / "README.md").read_text()
    assert "github.com/daryl-888/Workshop3" in readme
    assert "github/daryl-888/Workshop3/blob/main/mnist_workshop.ipynb" in readme
```

- [ ] **Step 2: Run the copy test and verify it fails**

Run: `python3 -m pytest tests/test_first_workshop_copy.py -q`

Expected: FAIL because the existing title and facilitator copy still describe Workshop 3 and prior-workshop callbacks.

- [ ] **Step 3: Rewrite the visible copy**

Update the three artifacts so their title is **PCS Workshop Intro — Build a Neural Network That Reads Handwriting**. Replace the matrix-multiplication callback with this standalone explanation:

```text
A layer takes every input number, combines it with adjustable weights, adds a bias, and produces a new set of numbers. The @ symbol asks PyTorch to perform those multiply-and-add operations together.
```

Keep `https://github.com/daryl-888/Workshop3` and its Colab URL unchanged.

- [ ] **Step 4: Run repository tests**

Run: `python3 -m pytest -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the standalone narrative**

```bash
git add README.md FACILITATOR.md mnist_workshop.ipynb tests/test_first_workshop_copy.py
git commit -m "Recast workshop as PCS introduction"
```

---

### Task 2: Build the original digital-classroom deck

**Files:**
- Replace: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/work/workshop-intro-slides/build-deck.mjs`
- Create: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/work/workshop-intro-slides/design-notes.txt`
- Replace: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/workshop-intro-neural-network.pptx`

**Interfaces:**
- Consumes: The 24-slide narrative and speaker-note requirements in the spec.
- Produces: A blank-source PPTX with 24 independently designed slides and notes.

- [ ] **Step 1: Record the design tokens and slide map**

Write `design-notes.txt` with these exact tokens:

```text
canvas #FFF9EE
ink #24303A
blue #367BF5
coral #FF6B5E
yellow #FFD85A
green #43B581
pale-blue #EAF2FF
titles Aptos Display Semibold
body Aptos
code Aptos Mono
format 16:9
```

List slides 1–24 using the narrative roles in the spec and assign each one a dominant visual: pixel digit, promise card, loop diagram, pixel grid, flattening animation frame, weighted connections, matrix operation board, code editor, checkpoint card, ReLU number cards, network map, score race, dataset board, loss meter, backprop arrows, update equation, gradient eraser, complete loop, training chart, or experiment card.

- [ ] **Step 2: Mark the presentation edit operation once**

Run from the Presentations skill directory:

```bash
node container_tools/mark_artifact_operation_started.mjs --operation-kind edit --expected-output-count 1 --output-format pptx
```

Expected: the operation marker completes successfully.

- [ ] **Step 3: Implement the deck from a blank presentation**

Create `build-deck.mjs` using `@oai/artifact-tool`. Start with a blank 16:9 presentation rather than importing or duplicating Workshop2 slides. Implement shared helpers with these interfaces:

```javascript
function addCanvas(slide, slideNumber, sectionLabel) {}
function addTitle(slide, kicker, title, subtitle = "") {}
function addStickyNote(slide, x, y, w, h, text, color) {}
function addCodePanel(slide, x, y, w, h, code, highlights = []) {}
function addPixelDigit(slide, x, y, cellSize, bitmap, color) {}
function addLoop(slide, activeStep) {}
function addSpeakerNotes(slide, notes) {}
```

Use the palette and typography from `design-notes.txt`. Use light code panels, marker arrows, sticky-note checkpoints, and pixel imagery. Give every coding slide notes containing the concept, exact code, expected output, pause point, likely stumble, and recovery checkpoint.

- [ ] **Step 4: Export the PPTX**

Run the module with the bundled Node.js executable and runtime module paths. Export exactly:

```text
/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/workshop-intro-neural-network.pptx
```

Expected: one 24-slide PPTX with speaker notes and no source-slide imports.

---

### Task 3: Validate and repair every slide

**Files:**
- Inspect: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/workshop-intro-neural-network.pptx`
- Create: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/work/workshop-intro-slides/renders/`
- Create: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/work/workshop-intro-slides/contact-sheet.png`

**Interfaces:**
- Consumes: Task 2 PPTX.
- Produces: A visually verified, overflow-free PPTX ready for import.

- [ ] **Step 1: Render all slides**

Run `render_slides.py` with the bundled Python and Node runtime variables, then run `create_montage.py` against the render directory.

Expected: 24 PNG renders and one contact sheet.

- [ ] **Step 2: Inspect each render at full size**

Check all 24 PNGs individually for clipping, overlap, awkward wrapping, illegible code, stretched pixel imagery, inconsistent page tabs, and missing learning-loop state. Record concrete defects in `qa-ledger.txt`.

- [ ] **Step 3: Run automated overflow detection**

Run:

```bash
slides_test.py /home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/workshop-intro-neural-network.pptx
```

Expected: `Test passed. No overflow detected.`

- [ ] **Step 4: Repair all recorded defects in one pass**

Edit `build-deck.mjs`, regenerate the deck, rerender all 24 slides, and inspect the repaired output. Do not preserve any Workshop2 color, background, footer, or layout treatment.

- [ ] **Step 5: Confirm narrative and notes**

Extract slide text and notes. Assert there are 24 slides, no visible `Workshop 3`, `Workshop1`, `Workshop2`, or blur callback, and complete recovery guidance on coding slides 9, 12, 14, 19, 20, and 21.

---

### Task 4: Replace the native Google Slides deck

**Files:**
- Source: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/workshop-intro-neural-network.pptx`
- Destination presentation: `15u64H2RkaHIWpErKeOLNS99TGJjibNAxYQkEH4V18us`

**Interfaces:**
- Consumes: Task 3 verified PPTX.
- Produces: A native 24-slide Google Slides deck in the connected Drive account.

- [ ] **Step 1: Import the verified PPTX as a native Google Slides presentation**

Use the Google Drive/Slides connector import path and title the result:

```text
PCS Workshop Intro — Build a Neural Network That Reads Handwriting
```

If the connector cannot replace the existing presentation in place, create a new native presentation and update the repository's Slides URL to the new presentation ID.

- [ ] **Step 2: Read the complete native presentation**

Save the unmodified connector response to `raw-output.json`, parse it with `parse_template_design_system.mjs`, and confirm exactly 24 delivered slides.

- [ ] **Step 3: Run native issue detection**

Run `check_output_issues.mjs` against `raw-output.json`.

Expected: zero errors for undersized narrative text, placeholders, blank slides, typed bullets, and empty bullets.

- [ ] **Step 4: Render and inspect the native deck**

Export once to PDF, render all 24 pages, and visually compare the native contact sheet and full-size renders with the verified PPTX. Repair any import-only defects in a consolidated pass.

- [ ] **Step 5: Verify sharing and link behavior**

Open the final presentation URL without relying on editor state and confirm the intended audience can view it. Confirm the repository README points to the final native presentation.

---

### Task 5: Final verification and publication

**Files:**
- Modify if needed: `README.md`
- Regenerate: `/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/Workshop3.zip`

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: A clean repository commit, public workshop entry points, and final distributable files.

- [ ] **Step 1: Run all repository verification**

Run:

```bash
python3 -m pytest -q
python3 -m compileall -q starter solution facilitator/checkpoints
git diff --check
```

Expected: all tests pass, compilation succeeds, and no whitespace errors are reported.

- [ ] **Step 2: Verify forbidden-copy scan**

Run a targeted search across README, facilitator guide, notebook markdown, and extracted slide text. Repository URLs containing `Workshop3` are allowed; visible titles and teaching copy containing `Workshop 3`, Workshop1, Workshop2, or blur callbacks are not.

- [ ] **Step 3: Commit and push**

```bash
git add README.md FACILITATOR.md mnist_workshop.ipynb tests/test_first_workshop_copy.py docs/superpowers/specs docs/superpowers/plans
git commit -m "Redesign PCS workshop introduction"
git push origin main
```

Expected: `main` is clean and synchronized with `origin/main`.

- [ ] **Step 4: Regenerate the repository archive**

Run:

```bash
git archive --format=zip --output=/home/daryl/Documents/Codex/2026-08-27/files-pasted-by-the-user-i/outputs/Workshop3.zip HEAD
```

Expected: the archive contains tracked workshop files and excludes `.git`, datasets, caches, and scratch slide assets.

- [ ] **Step 5: Perform final entry-point checks**

Confirm the GitHub README, raw notebook, Colab link, native Google Slides link, local PPTX, and repository archive all resolve and match the final content.
