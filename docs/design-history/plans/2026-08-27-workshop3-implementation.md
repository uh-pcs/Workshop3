# PCS Workshop 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent, beginner-friendly, 60-minute PCS workshop in which students manually implement and train a neural network on MNIST.

**Architecture:** A native Google Slides deck drives the lesson while a thin Colab notebook prepares a temporary workspace, runs isolated checkpoints, and downloads the student's file. Students progressively edit one Python file; a tested solution and facilitator-only recovery snapshots support the live room.

**Tech Stack:** Python 3, PyTorch, torchvision, Google Colab, Jupyter notebook JSON, Google Slides.

**Spec:** Approved user plan in the Codex task dated 2026-08-27.

## Global Constraints

- Workshop1 and Workshop2 are read-only references and must remain unchanged.
- Do not use `torch.nn.Linear`, `torch.nn.Sequential`, or `torch.optim`.
- Use a standard Colab CPU runtime and full-batch gradient descent.
- Keep the conceptual loop visible: Forward Pass → Loss → Backpropagation → Update Weights → Repeat.
- Student work is one progressively built `mnist_network.py` file, not fill-in-the-blank code.
- The default first run is 10 epochs; the payoff experiment changes it to 60 epochs.

---

### Task 1: Manual neural-network artifact

**Files:**
- Create: `tests/test_solution.py`
- Create: `solution/mnist_network.py`
- Create: `starter/mnist_network.py`
- Create: `facilitator/checkpoints/*.py`

**Interfaces:**
- Produces `Linear.forward`, `Linear.parameters`, `ReLU.forward`, `NeuralNetwork.forward`, `NeuralNetwork.parameters`, `load_data`, `accuracy`, and `main`.

- [ ] Write tests for tensor shapes, parameter enumeration, gradients, forbidden abstractions, training improvement, and checkpoint importability.
- [ ] Run the tests and confirm they fail because the implementation files do not exist.
- [ ] Implement the smallest complete teaching solution and staged recovery files.
- [ ] Run the test suite and confirm it passes.

### Task 2: Colab workbench

**Files:**
- Create: `tests/test_notebook.py`
- Create: `mnist_workshop.ipynb`

**Interfaces:**
- Consumes the starter file and facilitator checkpoints.
- Produces setup, isolated subprocess checkpoints, final execution, recovery, and file-download cells.

- [ ] Write structural tests for required cells and commands.
- [ ] Run the tests and confirm the notebook is missing.
- [ ] Create the notebook as valid Jupyter JSON.
- [ ] Run structural tests and execute non-network checkpoint commands locally.

### Task 3: Student and facilitator documentation

**Files:**
- Create: `README.md`
- Create: `FACILITATOR.md`
- Create: `EXTENSIONS.md`
- Create: `LICENSE`
- Create: `.gitignore`

**Interfaces:**
- Documents the Colab workflow, 60-minute timing, code reveals, recovery actions, expected outputs, setup risks, and optional experiments.

- [ ] Write documentation checks for required links, timing, presenter lines, and recovery guidance.
- [ ] Run checks and confirm the documents are missing.
- [ ] Write the student and facilitator materials.
- [ ] Run documentation checks and inspect links and commands.

### Task 4: Google Slides deck

**Files:**
- Create build sources and renders in a temporary directory.
- Create final build artifact: `outputs/workshop3-neural-network.pptx`.
- Import the verified PPTX as a native Google Slides presentation.

**Interfaces:**
- Produces a 24-slide, dark, code-forward deck with speaker notes on coding slides.

- [ ] Build the deck from the approved outline using the presentation runtime.
- [ ] Render all slides and inspect each slide for fit, hierarchy, and consistency.
- [ ] Run overflow and content checks; repair any defects.
- [ ] Import as native Google Slides and record the resulting URL in `README.md`.

### Task 5: End-to-end verification and repository initialization

**Files:**
- Verify all created artifacts.
- Initialize `.git` in `Workshop3` and create the initial local commit.

- [ ] Run the full automated test suite.
- [ ] Execute the solution for 10 and 60 epochs using cached MNIST data.
- [ ] Confirm loss decreases, accuracy rises, and runtime/accuracy targets are met.
- [ ] Validate notebook JSON and slide render output.
- [ ] Confirm no files in Workshop1 or Workshop2 changed.
- [ ] Initialize the independent repository and commit the verified workshop.
