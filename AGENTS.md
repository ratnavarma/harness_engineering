# Training Material Steering

## Purpose

`training/index.html` is the canonical, self-contained learning guide for the
Assembler Harness Engineering Workshop. It must remain accurate to the code and
the learning sequence; it is not a speculative product page.

## Required update on every completed task

When a task completes a workshop milestone, update `training/index.html` in the
same change set before committing:

1. Change the relevant module from planned to built only after its acceptance
   checks pass.
2. Replace the Day 1 status-card text with the newest completed-day summary.
3. Update the relevant layer description if the implemented design differs from
   the curriculum wording.
4. Keep later days visibly planned until their work is actually complete.
5. Verify the page still opens directly in a browser with no build step or
   external dependency.

## Source-of-truth rules

- The implementation and tests decide what is marked complete.
- Preserve the five-day schedule, module titles, and project promise unless the
  workshop owner explicitly changes them.
- Use concise, concrete language that tells a learner what they built and why.
- Do not include API keys, private paths, transcripts containing secrets, or
  vendor credentials in the training material.
