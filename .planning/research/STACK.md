# Stack Research

**Domain:** Home Assistant custom integration (web scraping/parsing dependency)
**Researched:** 2026-04-29
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Home Assistant custom integration API | Track latest stable `2025.x` (validate monthly) | Runtime host and integration contract | HA developer docs and quality scale rules move continuously; pinning to an old Core API causes breakage in config flow, coordinator, and entity contracts. |
| Python | `3.13` baseline | Integration runtime compatibility target | HA Core 2025 changelog explicitly references restoring Python `3.13.2` requirement; targeting 3.13 avoids drift and CI mismatches. |
| `aiohttp` | `3.13.5` | Async HTTP client for source fetches | HA quality rule requires async dependency and recommends `aiohttp`/`httpx` with injected HA web session; `aiohttp` is native to common HA patterns. |
| Home Assistant `DataUpdateCoordinator` pattern | Current HA helper APIs (2025 docs) | Poll scheduling, retry behavior, entity freshness | This is the standard HA pattern for polling integrations; it centralizes refresh, backoff, and error handling instead of per-entity network logic. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `beautifulsoup4` | `4.14.3` | HTML fallback parsing when upstream page shape changes | Use only as fallback for resilient extraction; prefer structured extraction first (embedded JS/JSON, stable selectors). |
| `awesomeversion` | latest compatible with HA (indirect via HA ecosystem) | Version parsing for manifest/version checks | Use for release/version validation logic aligned with HA conventions; avoid hand-rolled semantic parsing. |
| `voluptuous` (via HA patterns) | HA-managed | Config flow/schema validation | Use in config flow and options flow validation to surface user errors early (`test-before-configure` expectation). |
| `pytest-homeassistant-custom-component` | `0.13.325` | Integration-focused test harness | Use for config flow, coordinator refresh, and entity state tests against HA-compatible test fixtures updated with Core releases. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `ruff` | `0.15.12` | Fast linting + formatting | Use as single lint/format gate in CI to reduce style-tool drift; replace separate flake8/isort/black stacks unless explicitly required. |
| `mypy` | `1.20.2` | Static type checks | Aligns with HA strict-typing direction; prioritize coordinator payload typing and config entry runtime-data typing. |
| `hassfest` (HA validation tooling) | follow latest HA scripts/docs | Validate manifest + integration metadata quality | Run in CI for manifest and quality-scale sanity; catches common metadata and structure regressions early. |

## Installation

```bash
# Runtime requirement (manifest)
aiohttp==3.13.5

# Optional parser fallback
beautifulsoup4==4.14.3

# Dev/test
pip install -U pytest-homeassistant-custom-component==0.13.325 ruff==0.15.12 mypy==1.20.2
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `aiohttp` | `httpx` | Use `httpx` only if you already standardize your client library on httpx and still inject HA-managed async client/session. |
| `DataUpdateCoordinator` polling | Ad-hoc per-entity fetch logic | Only for trivial one-entity prototypes; not for production community integrations. |
| `beautifulsoup4` fallback | `lxml`-only parser stack | Use `lxml` when performance is critical and HTML is well-formed; for brittle pages BS4 is usually safer to maintain. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `requests` (sync HTTP) in integration runtime | Blocks event loop or forces awkward executor wrappers; conflicts with HA async-first quality direction | `aiohttp` with `async_get_clientsession(hass)` (or HA-supported `httpx` async client). |
| Hard pinning stale requirement floors like `aiohttp>=3.8.0` for long periods | Increases security/regression risk and misses compatibility updates; this project currently shows this drift | Periodically bump and test current stable minor/patch (`aiohttp 3.13.x` at time of research). |
| Parsing only brittle CSS selectors without schema/shape guards | Source-site markup changes can silently corrupt entity state | Hybrid parser strategy: primary structured extraction + explicit validation + fallback parser. |
| Production reliance on unsupported HA Core install method | HA deprecated Core/Supervised support for end users in 2025; support focus moved to OS/Container | Validate primarily on Home Assistant OS/Container environments. |

## Stack Patterns by Variant

**If upstream source remains embedded JS arrays (current ZSED case):**
- Use `aiohttp` fetch + deterministic JS-object extraction + strict normalization into typed schedule model.
- Because this is more stable than DOM scraping and easier to regression-test.

**If upstream source moves to dynamic HTML/content blocks:**
- Add `beautifulsoup4` fallback parser with explicit selector contract tests.
- Because parser resilience matters more than micro-performance for community integrations.

**If project targets higher quality-scale maturity (Silver/Gold+):**
- Add full `pytest-homeassistant-custom-component` coverage for config flow, coordinator failures, and entity behavior.
- Because HA quality expectations increasingly emphasize reliability and typed maintainability.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `aiohttp==3.13.5` | Python `>=3.9` (works with HA Python 3.13 baseline) | Good fit for current HA runtime direction and async session-injection rule. |
| `pytest-homeassistant-custom-component==0.13.325` | Python `>=3.13` | Tracks Home Assistant releases frequently; keep it updated with Core target. |
| `mypy==1.20.2` | Python `>=3.10` | Safe for 3.13 projects; use strict mode incrementally on integration modules. |
| `beautifulsoup4==4.14.3` | Python `>=3.7` | Compatibility is broad; treat as optional fallback dependency, not first-line parser. |

## Recommendation Confidence

| Area | Confidence | Reason |
|------|------------|--------|
| Runtime stack (`aiohttp`, async HA patterns) | HIGH | Backed by HA quality-scale docs (`inject-websession`, async dependency guidance) and current ecosystem usage. |
| Python baseline (3.13) | HIGH | Backed by official HA changelog references in 2025 cycle. |
| Testing stack (`pytest-homeassistant-custom-component`) | HIGH | Package is HA-specific, frequently updated, and explicitly tracks Home Assistant versions. |
| Parser fallback (`beautifulsoup4`) | MEDIUM | Strong ecosystem evidence and current releases, but fallback need depends on future zsed.sk markup changes. |

## Sources

- https://developers.home-assistant.io/docs/creating_integration_manifest
- https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/inject-websession/
- https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/strict-typing/
- https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure
- https://www.home-assistant.io/changelogs/core-2025.5/
- https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems
- https://pypi.org/project/aiohttp/
- https://pypi.org/project/beautifulsoup4/
- https://pypi.org/project/pytest-homeassistant-custom-component/
- https://pypi.org/project/ruff/
- https://pypi.org/project/mypy/

---
*Stack research for: Home Assistant web-scraping custom integration*
*Researched: 2026-04-29*
