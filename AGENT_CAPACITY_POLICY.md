# Axiom — Agent Capacity Policy

## Status

**OWNER GOVERNANCE RULE.**

## Purpose

Codex, Grok and other external construction agents may have weekly, monthly or equivalent usage limits.

Their available execution window is a scarce project resource.

The default strategy is therefore:

> **Use the largest safe, completable sprint possible, with the fewest avoidable follow-up calls.**

## 1. Default unit of work

Prefer a **complete vertical sprint**, not isolated microtasks.

A sprint should include, when applicable:
- authority/canonical reading;
- branch/HEAD precheck;
- implementation;
- migrations;
- integration;
- permissions/audit;
- error states;
- tests;
- CI/gates;
- documentation;
- update/validation scripts;
- self-review;
- commits/push;
- final status and real residuals.

## 2. Complete does not mean infinite

Do not send an impossible mega-scope.

A sprint must be:
- large enough to justify the limited agent window;
- bounded enough to be finished end-to-end;
- defined by explicit acceptance criteria.

## 3. Minimize rework

Operational goal:
**ZERO AVOIDABLE ADJUSTMENTS.**

Preferred homologation target:
**0–1 correction round per sprint.**

Avoidable rework includes:
- failing to read existing requirements;
- ignoring canonical UX/rules;
- not testing;
- leaving obvious TODOs;
- implementing only half of a requested flow;
- inventing requirements already defined elsewhere.

## 4. Before calling an agent — Definition of Ready

The order should contain, when applicable:
- repository;
- branch;
- starting HEAD;
- issue/authority;
- objective;
- full in-scope work;
- explicit out-of-scope work;
- required canonical files;
- known owner decisions;
- implementation order;
- tests;
- acceptance criteria;
- deliverables;
- prohibitions;
- commit/push requirements;
- stop conditions.

Do not ask the owner again for information already recorded in the repository.

## 5. Before returning — Definition of Done

The agent should not stop at “code works”.

Expected, when applicable:
- feature complete;
- integration complete;
- migrations complete;
- tests/gates run;
- no avoidable TODO/FIXME;
- no dead buttons or disconnected UI;
- docs updated;
- commits/push complete;
- application/validation instructions ready;
- self-audit complete;
- only real residuals remain.

## 6. Self-audit in the same window

Before handoff, inspect:
- missing requested items;
- partial flows;
- TODO/FIXME;
- duplicated local standards;
- missing persistence;
- missing permission/audit;
- missing tests;
- stale docs;
- unhandled errors.

Fix avoidable findings **before ending the sprint**.

## 7. Batch owner feedback

Do not spend one agent call per cosmetic or small correction.

Group all known homologation feedback for the same surface into one consolidated correction sprint.

## 8. Microtask exceptions

A small isolated call is justified for:
- data-loss/corruption risk;
- security issue;
- blocking regression;
- tiny hotfix that unlocks the whole sprint;
- new owner decision after previous work;
- external dependency change.

Otherwise batch it.

## 9. Codex and Grok

Do not waste both agents duplicating the same audit or implementation without a clear reason.

Prefer:
- one primary implementation agent;
- the other only for complementary value: specialized review, UX, research, diagnosis or a genuinely useful independent check.

## 10. Preserve handoff context

For meaningful sprints, persist:
- branch;
- initial HEAD;
- final HEAD;
- commits;
- tests;
- decisions;
- blockers;
- residuals.

A future Dante/Codex/Grok should be able to resume without repeating the audit.

## 11. Do not stop early

If the assigned sprint still has known in-scope work and the agent can safely finish it, continue to the sprint Definition of Done.

Do not artificially split into many phases just to return partial results.

## 12. Real vs avoidable residuals

A real residual depends on:
- owner decision;
- local environment;
- unavailable credential/source;
- legal research;
- visual homologation;
- external service.

An avoidable residual is work the agent could reasonably complete in the active sprint.

Avoidable residuals should not be deferred.

## 13. Owner authority

Technical green gates do not equal owner homologation.

This policy optimizes scarce agent capacity; it does not transfer product authority to the agent.

## 14. Rule for future chats

When a future Dante prepares work for Codex/Grok:

**Consolidate first. Delegate once. Require end-to-end delivery, tests, self-review and documentation. Minimize corrective calls.**

## Final rule

**Do not spend a scarce agent window today on work that should have been delivered correctly in yesterday's complete sprint.**
