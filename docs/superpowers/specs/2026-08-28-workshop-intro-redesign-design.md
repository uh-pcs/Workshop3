# Workshop Intro Rename and Deck Redesign

## Goal

Reposition the neural-network workshop as the first PCS workshop rather than a sequel. Keep the public repository named `Workshop3` for now, remove prior-workshop dependencies from the student experience, and replace the current Workshop2-derived slide styling with an original digital-classroom visual system.

## Naming and URLs

- GitHub repository remains `daryl-888/Workshop3` until the owner renames it later.
- Workshop title: **Build a Neural Network That Reads Handwriting**
- Short label: **PCS Workshop Intro**
- Colab URL remains `https://colab.research.google.com/github/daryl-888/Workshop3/blob/main/mnist_workshop.ipynb`.
- Local repository directory remains `Workshop3`.
- README, notebook, facilitator guide, and slides use **PCS Workshop Intro** as the visible workshop identity without changing repository URLs.

## First-Workshop Narrative

The workshop must stand completely on its own. It will not refer to Workshop1, Workshop2, an earlier blur lab, or a previous matrix-multiplication lesson.

The teaching sequence becomes:

1. A computer sees a handwritten digit as a grid of numbers.
2. Flattening changes the grid's shape, not its information.
3. A layer combines each input with adjustable weights and a bias.
4. `x @ weights + bias` is introduced visually as many multiply-and-add operations performed together.
5. Three layers create ten scores, one for each digit.
6. Loss measures how wrong the scores are.
7. Backpropagation tells every parameter how it contributed to the mistake.
8. The update nudges the parameters in a better direction.
9. Repetition turns this code into a learning system.

The central loop remains:

**Forward Pass → Loss → Backpropagation → Update Weights → Repeat**

## Visual Direction: Interactive Digital Classroom

The deck will use a bright, welcoming classroom system rather than Workshop2's dark code-forward theme.

### Palette

- Warm white canvas: `#FFF9EE`
- Ink charcoal: `#24303A`
- Classroom blue: `#367BF5`
- Coral marker: `#FF6B5E`
- Highlighter yellow: `#FFD85A`
- Learning green: `#43B581`
- Pale blue panel: `#EAF2FF`

### Typography

- Clean rounded sans serif for titles and instructional text.
- Monospace only inside code/editor panels.
- Handwritten-style annotations are used sparingly for arrows, labels, predictions, and checkmarks; they are accents, not body copy.

### Visual Grammar

- Whiteboard canvases with subtle dot-grid or graph-paper structure.
- Sticky-note questions and checkpoint cards.
- Pixel tiles for MNIST imagery and tensor representations.
- Clean, light code-editor panels rather than terminal-heavy dark slides.
- Hand-drawn arrows and marker underlines to show causality.
- The persistent learning loop gains a visible checkmark as each concept is implemented.
- Slide numbers appear as small classroom-tab labels.

## Slide Structure

The deck remains 24 slides, but its narrative and visuals are rebuilt:

1. Hook: can this computer read the digit?
2. Promise: build one Python file and watch it learn.
3. What "learning" means: guess, measure, adjust, repeat.
4. The persistent five-step loop.
5. A 28×28 image is a grid of 784 brightness values.
6. Flatten the grid without losing the pixels.
7. A layer mixes inputs using adjustable weights.
8. Visual introduction to `x @ weights + bias` with no prior-knowledge callback.
9. Live-code `Linear`.
10. Checkpoint 1 and visible shape result.
11. Why the network needs a bend.
12. Live-code `ReLU` with before/after number cards.
13. Stack `784 → 128 → 128 → 10`.
14. Live-code `NeuralNetwork` and collect six tensors.
15. Interpret ten scores as digit guesses.
16. Load, flatten, and normalize MNIST.
17. Cross-entropy measures wrongness.
18. `loss.backward()` sends responsibility backward.
19. Update parameters inside `torch.no_grad()`.
20. Clear gradients before the next repetition.
21. Assemble the five-part training loop.
22. First payoff: run ten epochs and read the trend.
23. Change ten to sixty and compare accuracy.
24. Close: the class built a learning system; optional experiment.

## Speaker Notes

Every coding slide will preserve the existing teaching support:

- concept to land;
- exact code chunk;
- expected output;
- pause point;
- likely typo or misconception;
- recovery checkpoint.

Presenter language must assume no prior PCS workshop experience. Terms such as tensor, matrix multiplication, logits, gradient, and epoch are introduced in plain language when first needed.

## Repository Changes

- Keep the GitHub repository, local directory, clone URL, and Colab URL unchanged.
- Update README, notebook, and facilitator-guide display titles to **PCS Workshop Intro**.
- Update facilitator-guide naming and remove prior-workshop callback language.
- Update any tests that assert old URLs or labels.
- Keep the existing repository archive naming until the owner renames the repository.
- Replace the local PPTX output and native Google Slides presentation with the redesigned deck.

## Verification

- Repository, raw notebook, and Colab source continue to resolve from `Workshop3/main`.
- Search finds no visible workshop title "Workshop 3," Workshop1, Workshop2, blur callback, or prior-workshop dependency language. Repository URLs may retain `Workshop3`.
- All Python and notebook tests pass.
- All 24 slides render without overflow, clipping, unresolved placeholders, or illegible code.
- Every slide is visually inspected at full size.
- Native Google Slides contains 24 slides and matches the verified local deck.
- Slides are accessible in the intended sharing mode.

## Non-Goals

- The neural-network implementation and 60-minute scope do not change.
- Workshop1 and Workshop2 remain untouched.
- Calculus derivations, GPU setup, optimizers, and production abstractions remain outside the core workshop.
