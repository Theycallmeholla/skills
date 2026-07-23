# Spec Mode: Auditing a Written Flow or Screenshots

You have a description of the flow rather than the running thing: a PRD, a written step list, a Figma export, a set of screenshots, or the user explaining it in chat. You audit what's described — and, crucially, you flag what the artifact leaves *unspecified*, because a gap in the spec is usually a gap in the real product.

## Step 1: Establish what you've actually got

- **Written description / PRD** — prose or a step list. Rich on intent, often silent on edge cases and microcopy.
- **Screenshots / mockups** — show the real layout and copy but only the frames someone chose to capture; the unhappy paths are usually missing.
- **Figma / design export** — may include multiple frames and states; check whether error/empty/loading frames exist.
- **Chat explanation** — the user narrates the flow. Mirror it back as a step list and confirm before auditing, so you're not auditing your own misreading.

State which you have and its inherent blind spots in the report.

## Step 2: Reconstruct the flow map

Build the Phase 1 step map from the artifact. For each step capture: what the user sees, what they're asked to do, and what happens next. Number it. Then read it back to the user if anything was inferred rather than stated — confirming the map prevents auditing a flow that doesn't exist.

## Step 3: Audit what's present

Run the standard phases against what the artifact actually shows: comprehension, flow logic, copy clarity (you can read the exact copy in screenshots/Figma), and visible feedback/error states. Screenshots are strong evidence for first-impression, hierarchy, copy, and mobile-layout findings.

## Step 4: Audit what's absent — the highest-value part of spec mode

The most useful spec-mode findings are the questions the artifact can't answer. Systematically check for missing specification of:

- **Error states** — what happens on invalid input, failed payment, network error? If the spec/mocks don't show them, that's a finding: "Error states unspecified — likely unhandled."
- **Empty / loading / first-run states.**
- **Validation rules and timing** — what's required, what formats, when errors appear.
- **Branches** — logged-out vs in, returning user, no-results, expired link.
- **Back / refresh / resume behavior** — is progress preserved?
- **Confirmation & feedback** — does each meaningful action confirm?
- **Microcopy at decision points** — are button labels and helper text specified, or just "button here"?
- **Mobile layout** — is responsive behavior specified or only desktop shown?

Frame each gap as: "The spec doesn't define X. If the implementation also doesn't, users will hit [consequence]. Confirm against the build, or specify it."

## Step 5: Offer to go deeper

Spec mode is inherently partial. Close the report by noting that a code-mode or browser-mode pass against the real implementation would confirm the inferred behaviors and surface the branches the artifact omitted. Offer it.

## Evidence format for spec mode

- Screenshots: reference by filename/frame and describe the specific element ("Onboarding frame 2: the only label is the grey placeholder 'Name'").
- Written spec: quote the minimal relevant line or paraphrase the step. Keep quotes short.
- Inferred gaps: clearly mark as inferred, not observed — "not specified" rather than "broken."
