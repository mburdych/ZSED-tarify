# Research Summary

**Project:** ZSED Tarify Home Assistant Integracia
**Date:** 2026-04-29

## Domain Snapshot

This project sits in the Home Assistant custom integration ecosystem where users expect stable entities, predictable automation behavior, and low-friction setup via UI config flows. For a community plugin, trust is built mostly through correctness and reliability rather than feature count.

## Key Findings

### Stack

- Async-first runtime is mandatory (`aiohttp`, coordinator-driven refresh, Python 3.13 compatibility).
- Parser robustness should include strict normalization and optional tolerant fallback parsing.
- Tooling baseline should include HA-focused tests plus static quality gates (`pytest-homeassistant-custom-component`, `ruff`, `mypy`).

### Table Stakes

- Stable config flow and entity model for `current tariff`, `next switch`, and schedule visibility.
- Correct tariff-time semantics (weekday/weekend, midnight crossing, timezone).
- Graceful degraded mode with cache fallback when upstream fails.

### Architecture

- Strong boundary: `parser -> coordinator -> entities`.
- `DataUpdateCoordinator` should remain the single source of truth for refresh/caching behavior.
- Entity layer must stay read-only from coordinator cache (no network I/O in entities).

### Watch Outs

- Event-loop blocking and sync I/O in HA integration paths.
- Parser fragility from tight coupling to one HTML/JS shape.
- Retry/polling misconfiguration that causes rate limits and self-inflicted outages.
- Hidden staleness and poor diagnostics that make incidents hard to debug.

## Recommended Delivery Order

1. Establish parser contract and async-safe data path.
2. Harden parser correctness and boundary-time logic with fixtures/tests.
3. Add reliability policy (backoff, fallback, staleness visibility).
4. Improve presentation and operator UX (dashboard-oriented entities and diagnostics).

## Practical Scope Guidance

Prioritize correctness and dashboard clarity over broad feature expansion.
Allow new features only if they do not reduce parser correctness or integration stability.

---
*Research synthesized: 2026-04-29*
