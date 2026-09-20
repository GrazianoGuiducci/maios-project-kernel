---
name: maios-software-diagnosis
description: Understand a software failure, regression or integration fault through attributable observations and discriminating explanations, then prepare or perform a cause-directed correction within the selected scope. Use for uncertain technical causes, not as a universal method for conceptual inquiry.
---

# Diagnose the mechanism that changed the result

Connect expected behavior, observed behavior and the conditions of the case. A visible symptom can be far from the mechanism that produced it. Preserve the selected object and distinguish diagnosis from implementation when only understanding was requested.

## Establish the relevant observation

Use the reported trace, source and actual environment. Determine what was observed directly, what was reported by another actor and what remains inferred. A reproduction is useful when it can discriminate the cause or support the confidence needed for a change; do not claim it happened if the required environment is unavailable.

Separate an observation that detects the stated failure from a check that always succeeds. When an executable probe is selected, make it sensitive to the mechanism and run it in an appropriate, authorized environment. A source inspection can also settle a particular relationship without a new test.

## Compare explanations that could change the correction

Consider materially different mechanisms supported by the evidence, rather than generating a fixed number of hypotheses. For a live candidate, know what should be seen if it is right, what would contradict it and which available observation best distinguishes it from alternatives.

Trace the path from the symptom toward the first incorrect transformation. Distinguish the trigger, the causal mechanism, the way the error propagates and conditions that amplify frequency or severity. Removing an amplifier does not necessarily correct the mechanism.

For example, a packaging check can fail because source identity metadata changed after a rebuild. That failure alone does not prove that an old method was delivered. Compare the actual bodies to answer the delivery question, and inspect metadata to answer the source-identity question. The two corrections can be related without being the same.

## Correct where the cause belongs

When implementation is selected, change the owner that produces the incorrect behavior and follow the changed meaning into its consumers. Do not compensate downstream merely because the symptom is easiest to edit. Avoid unrelated cleanup that obscures the causal comparison.

Use temporary instrumentation only when it provides a missing distinction; keep it narrow and remove it when it no longer helps. Preserve important failure, conflict and recovery behavior. Changes involving external data, credentials, production or destructive state require the actual authority and recovery appropriate to those effects.

The existing verification contract may need clarification if it tests the wrong behavior. Explain that distinction rather than weakening an assertion to obtain a green result. Technical checks support the claims they actually cover; they do not establish semantic understanding by an LLM.

## Continue the knowledge

Return the best supported mechanism, its evidence, the correction or proposed owner and material uncertainty. Preserve a reusable diagnostic lesson where later work can use it. If the error came from the way this competence framed the problem, let that correction change its source selection or method too.

A selected software diagnosis can involve a test. The existence of this skill does not authorize new experiments, installation trials or comparisons unrelated to the present task.
