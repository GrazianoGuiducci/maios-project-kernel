---
name: maios-software-design
description: Design or evolve software responsibilities, interfaces and dependencies so useful behavior stays understandable and changeable. Use for substantive module, adapter or migration decisions, not to turn an open kernel inquiry into a predetermined software architecture.
---

# Design responsibilities that carry useful behavior

Begin with the work a caller or participant needs to accomplish, the behavior that must remain coherent and the effects it must understand. File proximity, name symmetry and anticipated reuse do not by themselves define a useful module.

## Find the responsibility before the interface

Understand which decisions the proposed boundary should own, which state and dependencies it can encapsulate and which errors, progress or effects must remain visible. If every caller still coordinates the internal implementation, a thin wrapper may have changed names without reducing complexity.

Explore another materially different organization when it can expose a missing tradeoff. A command-oriented interface and a result-oriented one, for example, may distribute responsibility differently. Compare the knowledge required of callers, invalid states, recovery, likely change and migration burden. Do not manufacture two designs when the relation is already settled.

## Preserve truthful depth

A useful interface lets callers express their work without inheriting unnecessary storage, framework or transport detail. Keep domain decisions with the owner that understands them. Do not hide a consequential effect behind an apparently harmless operation.

Classify dependencies through their actual behavior. Pure transformation, owned persistent state and an external service create different failure and recovery relationships. A generic port should not erase irreducibly different capabilities just to give every adapter the same shape.

For example, replacing a synchronous file reader with a remote job service can introduce cancellation, progress and result-lifetime questions. Decide which belong to the caller's actual job and which are internal mechanics. A second adapter is not required merely to justify an abstraction; the real sources determine whether a shared responsibility exists.

## Evolve without erasing useful work

Preserve the existing behavior that still serves the context. Where change crosses several consumers, introduce the new relation and migrate the actual dependants in a form that keeps the work recoverable. Compatibility can be temporary, but its reason and eventual successor should remain intelligible.

Do not keep two competing architectures indefinitely only to avoid a decision. Do not remove the old path before understanding what it still carries. A smaller representation is an improvement only when useful behavior, error meaning and continuation survive the transformation.

Use the available evidence appropriate to the selected implementation. This method does not select a test campaign, deployment or broad refactor on its own. When the cause of a failure is still unknown, diagnose that mechanism instead of treating architecture as an explanation.

## Teach the design reason

Record the distinction that made the boundary useful, the alternatives that materially changed the choice and the consequences the receiving work must understand. Update the competence when later use reveals a missing dependency, a leaky interface or an unnecessary abstraction.

When the object is the kernel itself, software design contributes knowledge about mechanisms and interfaces. The kernel's generative competence retains the wider relationship among sources, meaning, competences, organization and learning; a cleaner class diagram does not replace that work.
