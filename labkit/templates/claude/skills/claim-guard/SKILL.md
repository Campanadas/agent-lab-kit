---
name: claim-guard
description: Use before reporting any statistic, fold change, ratio, percentage or pass/fail verdict, before declaring anything a ceiling or "cannot be tested", and whenever a result looks clean, a control passed, or a number came out exactly 0.0 or 1.0.
---

# Claim guard

```
ASSUME A PASSING CHECK IS UNINFORMATIVE UNTIL YOU HAVE SHOWN IT CAN FAIL.
THE TELL IS EXACTNESS. THE SECOND TELL IS GRANULARITY.
```

Retractions in long agent-run projects share a handful of causes. Run through them before a claim enters the record.

## 1. Can the test fail?
- Compute the control **and compare it**. A control that is computed and never compared is decoration.
- **Delete the mechanism and re-run.** If the result survives without the thing that supposedly produces it, the test was not
  testing it (e.g. a tracking score that stays perfect when the tracker is removed, because the input already carries the answer).
- A wide pass band ("ratio above 1.3", "within an order of magnitude") is a test that cannot fail. Narrow it before the run.
- Ask what a **dead, flat or near-zero** result scores. If it passes, add the floor that excludes it (a survival condition, a
  minimum amplitude, a minimum effect size) and pre-register the floor.
- Exact 0.0 / 1.0 is a tell, not proof. Ask whether the value is forced by construction.

## 2. Is the unit of randomisation the unit of the claim?
- A claim about four named things has about four degrees of freedom, however many measurements each contains.
- A z-score is meaningful only when the null has real spread. With a degenerate null, report the raw effect, the rank and the
  empirical p, not the z.

## 3. Is the effect an artefact of pooling or truncation?
- Pooling a real effect with a null one dilutes it; pooling can also create an effect. Check the effective n.
- A list sorted and sampled at one end is not a property of the whole list.

## 4. Is the label curated or predicted?
- Never build on a predicted label when a curated one exists in the same data. Honour "unknown" as unknown.

## 5. Identity and staleness
- Identify things by their content (members, parameters), never by an integer id that a rebuild can reassign.
- `labkit check FILE` before anything leaves the project: no claim may rest on a dead finding.

## 6. The symmetric failure: do not concede early either
- A "wall", "ceiling" or "cannot be measured" is usually the instrument or the missing build, not the world. Attack it at least
  three distinct ways before writing it down, and record the attacks.
- A false positive looks too good and invites scrutiny; a false negative looks like rigour and invites none.

## Rationalisations to catch

| The thought | What it usually means |
|---|---|
| "The control passed." | Check the control shares little with the thing it controls. |
| "The z is enormous." | Check the null's spread and the unit of the claim. |
| "I'll note the caveat." | A caveat naming a one-answer design is the next experiment, not a footnote. |
| "The script exits 0." | An exit code is not a standing. Read what it printed. |
| "This is a hard limit." | Attack it three ways first. |
| "It reproduces the behaviour, so it's explained." | Reproduction is not explanation; show the mechanism is necessary. |

Constructing a case for why this particular number is the exception is the tell.
