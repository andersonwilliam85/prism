# Experience-First Interface Design: A Practitioner-Oriented Framework
## Decomposing User Interfaces into Experiences, Flows, and Interactions

**Author:** William Christopher Anderson
**Date:** March 2026

---

## Executive Summary

Modern software user interfaces rarely fail because individual interactions are broken. They fail because the accumulation of uncoordinated interactions obscures the user's intent, inflates cognitive load, and prevents the system from expressing coherent purpose.

Experience-First Interface Design addresses this problem by treating user intent — not feature delivery — as the primary organizing force in UI architecture. Rather than decomposing interfaces into screens, components, or endpoints, this framework organizes boundaries around anticipated human purposes and the journeys that fulfill them.

At a practical level, Experience-First Design applies a three-tier decomposition:

- **Experiences** represent complete user journeys — composable, purposeful, and stable over time.
- **Flows** encapsulate the goal-oriented sequences within an experience that accomplish a single discrete outcome.
- **Interactions** are atomic, observable acts — selecting, inputting, observing, confirming.

These tiers are reinforced through shared utility components and validated against a small set of core user journeys. Over time, this approach localizes UI change, reduces unintended coupling between interface layers, and preserves UX integrity even as products and organizations grow.

Experience-First Design is most effective in long-lived products, multi-audience platforms, and systems that must simultaneously serve users with different mental models and goals.

---

## Abstract

User interfaces exist at the intersection of human intent and system capability. Traditional approaches to UI design and implementation frequently conflate these two concerns — embedding navigation logic in components, coupling state management to presentation, and organizing codebases around screens or features rather than user purpose. The result is interfaces that resist change, require widespread modification for localized adjustments, and progressively lose alignment with user intent as products evolve.

Experience-First Interface Design is a decomposition framework that treats human intent as the primary organizing force in UI architecture. It introduces a three-tier hierarchy — Experiences, Flows, and Interactions — and defines explicit boundaries between them, analogous to the component role discipline described in Volatility-Based Decomposition. Shared utility components provide cross-cutting capabilities without embedding domain-specific knowledge. Core user journeys serve as validation mechanisms. This framework provides designers, frontend engineers, and product teams with a practical reference for producing UI architectures that remain coherent as systems scale in complexity, audience, and organizational scope.

---

## 1. Introduction

User interface design has matured significantly as a practice, yet most interface implementations remain architecturally fragile. A minor product decision — adding a new user type, introducing a conditional step, supporting a new locale — can require changes across dozens of components, screens, and state management layers. The cause is rarely poor engineering; it is poor decomposition.

When interfaces are organized around screens, features, or technical implementation details, the user's actual purpose becomes invisible in the codebase. A checkout flow is not a screen. It is a purpose — the user's goal of completing a transaction — and it may span multiple screens, states, and conditional paths depending on context.

Experience-First Interface Design addresses this by inverting the organizing principle. Rather than asking "what screens does this product have?", it asks "what does this user need to accomplish, and how do those accomplishments compose into complete journeys?"

This inversion has a structural implication: the decomposition hierarchy — Experiences, Flows, Interactions — mirrors the volatility decomposition hierarchy in software architecture. Experiences are stable, much like Managers. Flows are moderately volatile, encapsulating goal-specific logic as Engines do. Interactions are volatile at the fine-grained level, touching the actual interface surface as Resource Accessors touch external systems. Utilities are shared and orthogonal to any particular purpose.

---

## 2. Background

### 2.1 The Screen-First Trap

The dominant organizing principle in interface implementation is the screen — or its equivalent: the route, the page, the view. Frameworks reinforce this model by providing routing mechanisms that map URL paths to screen components. Teams naturally organize their codebases this way because screens are visible and bounded.

The limitation is that screens are a technical artifact, not a user artifact. A user pursuing a goal may traverse many screens. A single screen may serve multiple independent goals. When the organization of the codebase mirrors the screen structure rather than the goal structure, every goal-level change requires coordination across multiple units — the same problem that functional decomposition creates in software architecture.

### 2.2 Component Libraries and Their Limits

The response to screen-level fragility has often been component libraries: shared, reusable UI primitives. Component libraries address repetition and consistency. They do not address decomposition. A rich component library can still produce a fragile architecture if the components are assembled without a clear model of purpose.

### 2.3 Flows in Existing Practice

The concept of user flows appears in UX practice as a design artifact — diagrams showing how users move between screens. What is often absent is a corresponding architectural artifact: a unit in the codebase that represents a flow as a first-class concern, owning its own state, validation, and navigation logic, and communicating with components and interactions through well-defined interfaces.

---

## 3. Defining the Decomposition Hierarchy

### 3.1 Interactions

An interaction is the smallest observable unit of user action. It is atomic, meaning it cannot be meaningfully subdivided from the user's perspective. Interactions include:

- Selecting an item from a list
- Entering text into a field
- Checking a checkbox
- Clicking a button
- Observing a status message (passive, but architecturally meaningful)
- Receiving an error or confirmation

Interactions are the leaves of the hierarchy. They are the most volatile tier, changing whenever the interface surface changes — a new field type is added, a label is renamed, a control is replaced. They should be isolated in components that encapsulate only the interaction itself and communicate through stable interfaces.

Interactions produce **events** and receive **state**. They do not make decisions about flow progression.

### 3.2 Flows

A flow is a coherent sequence of interactions that accomplishes a single, well-defined user goal. Flows are bounded by their purpose. Examples:

- **Selecting a configuration profile** — a goal accomplished through browsing, filtering, and confirming a choice
- **Providing personal information** — a goal accomplished through filling, validating, and submitting a set of fields
- **Confirming an installation** — a goal accomplished through reviewing, validating, and committing

A flow owns:
- The sequence of interactions required to accomplish its goal
- The state accumulated across those interactions
- The entry and exit conditions
- The skip logic (when the flow is irrelevant given context)

A flow does not own UI primitives (those are interactions) or the larger journey that contains it (that is an experience).

Flows are moderately volatile. They change when the product changes how a goal is accomplished — a new step added, a step reordered, a validation rule changed. They should not change because a button's label changed (an interaction concern) or because a new user type was introduced (an experience concern).

### 3.3 Experiences

An experience is a complete user journey — the arc from intent to fulfillment. It composes flows (and sometimes other experiences) into a coherent whole. Examples:

- **Developer onboarding** — the complete journey from selecting an environment configuration to having a working development setup
- **Prism authoring** — the complete journey from creating a new configuration scaffold to publishing it for distribution

Experiences are the most stable tier. The high-level intent of developer onboarding — understand your organization's setup, provide your information, get configured — is stable even as the individual flows that fulfill it evolve.

An experience owns:
- The composition of flows that constitute the journey
- The transitions between flows
- The overall progress and state visible to the user at the journey level
- The entry point and the terminal conditions

An experience does not own flow-level logic or interaction primitives.

### 3.4 Utilities

Utilities are cross-cutting capabilities that apply broadly across interactions, flows, and experiences without belonging to any of them. They have no knowledge of user intent. They provide shared infrastructure:

- **Locale rendering** — translating string keys into user-visible text
- **Theme application** — applying visual style from configuration
- **Progress indication** — showing completion state across steps
- **Form validation** — common field validation rules independent of domain meaning
- **Alert and error presentation** — displaying system messages consistently

Utilities are consumed by interactions, flows, and experiences. They must not contain flow progression logic, domain-specific state, or knowledge of user intent. A locale renderer that knows it is rendering an "onboarding" string has violated its utility boundary.

---

## 4. Communication Rules

The decomposition hierarchy implies a set of communication rules analogous to those in Volatility-Based Decomposition:

| From | To | Allowed? |
|---|---|---|
| Experience | Flow | Yes |
| Experience | Experience (as sub-journey) | Yes |
| Flow | Interaction | Yes |
| Flow | Utility | Yes |
| Interaction | Utility | Yes |
| Interaction | Flow (event emission) | Yes — one-way, event-based |
| Flow | Experience (event emission) | Yes — one-way, event-based |
| Interaction | Interaction | No |
| Flow | Flow | No — experience coordinates |
| Utility | Any | No — utilities are consumed, not active |

The key rule: **state and decisions flow downward from experiences to flows to interactions. Events and outputs flow upward through events, not direct calls.**

---

## 5. Application: Prism Installer

The Prism installer provides a concrete demonstration of this framework applied to a real product.

### 5.1 Core User Journeys

Like core use cases in software architecture, core user journeys are deliberately narrow. The Prism installer has three:

1. **Developer Onboarding** — a developer installs their organization's prescribed development environment
2. **Prism Authoring** — a configuration author creates and publishes a new prism
3. **Workspace Discovery** — a developer explores and understands what is installed in their environment

### 5.2 Volatility Analysis

Applying volatility analysis to the Prism UI reveals where change accumulates:

**High volatility (Interaction-level):** The specific fields collected in the user info step change with every prism. The specific tier options differ by organization. Labels, placeholders, and error messages change with locale.

**Medium volatility (Flow-level):** Whether the tier selection step exists at all depends on the prism's `bundled_prisms` structure. The tools step may be skipped entirely. The sequence of the wizard is a flow-level concern.

**Low volatility (Experience-level):** The overall arc — select → configure → confirm → install → done — has been stable since the product was conceived. The intent of the onboarding journey does not change when a new field type is added.

### 5.3 Current Problems

The current `install-ui.py` monolith violates decomposition at every level:

- Experience, flow, interaction, and utility logic are all interleaved in a single 2500-line file
- Flow navigation (`nextStep`, `prevStep`) is coupled to DOM element IDs
- Interactions (`subOrg`, `department`, `team`) were hardcoded based on an old data model, causing the bug fixed in the previous session
- Locale strings are inline; changing any label requires finding and editing a string literal buried in HTML
- The installation API call and the progress display are mixed into a single function

These problems are not caused by poor engineering judgment. They are caused by organizing the code around the screen rather than around purpose.

### 5.4 After Decomposition

After applying Experience-First Design:

**Experiences:** `OnboardingExperience`, `AuthoringExperience`, `DiscoveryExperience`

Each experience is a small JavaScript class or module that composes flows, owns the top-level wizard state, and handles flow transitions.

**Flows:** `PrismSelectionFlow`, `UserInfoFlow`, `TierSelectionFlow`, `ToolSelectionFlow`, `ConfirmationFlow`, `InstallationProgressFlow`, `CompletionFlow`

Each flow owns its own state (selected prism, collected user info, selected tiers). Flows expose `enter()`, `exit()`, and `skip()` methods. They emit `flowComplete(data)` events that the experience handles.

**Interactions:** `PrismCard`, `FormField`, `TierSelect`, `ToolCheckbox`, `SummaryBlock`, `LogLine`, `AlertBanner`

Each interaction is a pure UI component — no flow logic, no state beyond its own display state. Interactions emit DOM events (`change`, `click`) that flows listen to.

**Utilities:** `LocaleRenderer`, `ThemeApplicator`, `StepProgress`, `FormValidator`

---

## 6. Volatility Axes in Interface Design

Applying the volatility axis model to UI architecture reveals four analogous dimensions:

### 6.1 Functional Volatility
Changes in what the user is asked to do — new fields, new steps, new flows. This is localized to flows and interactions when the decomposition is correct.

### 6.2 Structural Volatility
Changes in how flows compose — a new audience type, a new conditional path, a new entry point into a journey. This is localized to experience-level composition logic.

### 6.3 Cross-Cutting Volatility
Changes to locale strings, themes, validation rules, and error presentation. Isolated in utilities.

### 6.4 Environmental Volatility
Changes to API contracts, backend data shapes, and system capabilities. Isolated at the boundary between flows and the API layer — flows consume APIs through thin accessor adapters, not direct fetch calls.

---

## 7. Core User Journey Validation

As in VBD, core user journeys serve as architectural validation mechanisms. If implementing a new flow requires modifying an experience-level module directly, or if adding a new interaction requires changing flow navigation logic, the decomposition has leaked.

The Prism installer's three core journeys provide a validation harness:

1. **Developer Onboarding:** Can a user with no prior context select a prism, fill in their information, choose their team, and complete installation without error? Can adding a new prism-defined field be accomplished without touching navigation logic?

2. **Prism Authoring:** Can a prism author scaffold, validate, and publish without the UI knowing anything about the authoring workflow?

3. **Workspace Discovery:** Can a developer navigate to the docs server and discover all installed tools without requiring a running installer instance?

If any of these journeys breaks due to a change in another journey, or if a change to one flow requires touching another flow, the decomposition is invalid.

---

## 8. Architectural Watchpoints

### Interaction Proliferation
Individual interaction components should remain small and purpose-specific. If an interaction component begins making API calls, managing flow state, or knowing about adjacent interactions, it has absorbed flow responsibility.

### Flow Coupling
Flows should not call other flows. If a flow needs data produced by another flow, that data belongs in the containing experience's shared state, passed downward by the experience.

### Utility Contamination
Utilities that begin to acquire knowledge of specific user journeys or business rules have violated their boundary. A validation utility that knows that the "email" field behaves differently in the "enterprise onboarding" flow is no longer a utility — it is a flow concern.

### Journey Composition Depth
Experiences can contain other experiences, but deep nesting increases coordination cost. When a nested experience requires awareness of its parent experience, the decomposition should be reconsidered.

---

## 9. Relationship to Volatility-Based Decomposition

Experience-First Interface Design is a direct analog of Volatility-Based Decomposition applied to the user interface layer.

| VBD | Experience-First |
|---|---|
| Manager | Experience |
| Engine | Flow |
| Resource Accessor | Interaction (as leaf) / API Accessor (as boundary) |
| Utility | Utility |
| Core Use Case | Core User Journey |
| Communication Rules | Event propagation rules |
| Volatility Axis | Interface volatility axis |

When both frameworks are applied together — VBD to the backend, Experience-First to the frontend — they produce a system where the full stack is organized around a consistent principle: **isolate what changes, stabilize what endures.**

---

## 10. Conclusion

The dominant failures of user interface design are not aesthetic failures or interaction failures. They are architectural failures: the wrong units at the wrong boundaries, accumulating coupling until any meaningful change requires touching half the system.

Experience-First Interface Design provides a decomposition hierarchy that aligns interface architecture with the actual structure of human intent. By treating experiences as stable compositions of volatile flows, and flows as goal-directed sequences of atomic interactions, it produces interfaces that can absorb change at the level where change actually occurs — without propagating that change throughout the system.

The result is an interface architecture with the same properties that Volatility-Based Decomposition produces at the system level: change is localized, intent remains visible, and teams can evolve different parts of the interface independently.

As products grow in complexity, audience diversity, and organizational scope, the frameworks that treat change as a first-class design concern will prove more resilient than those optimized solely for today's feature list.

---

## Appendix A: Glossary

**Experience** — A complete, composable user journey bounded by a human intent, from initiation to fulfillment. Stable over time.

**Flow** — A goal-oriented sequence of interactions that accomplishes a single discrete outcome within an experience. Moderately volatile.

**Interaction** — An atomic, observable act at the interface surface. The most volatile tier.

**Utility** — A cross-cutting interface capability with no knowledge of user intent. Consumed across all tiers.

**Core User Journey** — A high-level human purpose that defines the primary value of the interface. Used as an architectural validation mechanism.

**Volatility Axis (UI)** — A dimension along which interface change is expected: functional, structural, cross-cutting, or environmental.

---

## Appendix B: Decomposition Checklist

Apply Experience-First Design when the interface:

- Serves more than one audience type
- Contains multi-step workflows with conditional paths
- Must support multiple locales
- Is expected to evolve significantly over multiple years
- Requires different visual themes or branding configurations
- Will be maintained by more than one team

---

## References

Anderson, William Christopher. "Volatility-Based Decomposition in Software Architecture." February 2026.

Löwy, Juval. *Righting Software.* Addison-Wesley, 2019.

Cooper, Alan; Reimann, Robert; Cronin, David. *About Face: The Essentials of Interaction Design.* Wiley, 2014.

Nielsen, Jakob. *Usability Engineering.* Morgan Kaufmann, 1993.

Norman, Donald A. *The Design of Everyday Things.* Basic Books, 2013. (Revised and Expanded Edition)

Spool, Jared M. "The $300 Million Button." UIE, 2009.

Gamma, Erich; Helm, Richard; Johnson, Ralph; Vlissides, John. *Design Patterns.* Addison-Wesley, 1994.

---

## Author's Note

This framework is a practitioner-oriented articulation, not a novel invention. The decomposition hierarchy described here draws on decades of UX practice, interaction design theory, and software architecture thought. Its primary contribution is the explicit alignment of interface decomposition principles with architectural decomposition principles — specifically Volatility-Based Decomposition — to produce a unified, coherent design language applicable across the full system stack.

The intent is to provide a durable reference suitable for consistent application, design review, and onboarding within product engineering organizations.

---

## Distribution Note

This document is provided for informational and educational purposes. It may be shared internally within organizations, used as a reference in design and engineering discussions, or adapted for non-commercial educational use with appropriate attribution.
