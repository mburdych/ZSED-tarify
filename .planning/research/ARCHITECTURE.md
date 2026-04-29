# Architecture Research

**Domain:** Home Assistant custom integration (web-data parser, polling source)
**Researched:** 2026-04-29
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Home Assistant Runtime Layer                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌─────────────────┐   ┌─────────────────────┐  │
│  │ config_flow  │   │   __init__.py   │   │  options / reload   │  │
│  │ (user setup) │──▶│ setup/unload +  │──▶│   config handling   │  │
│  └──────────────┘   │ platform wiring │   └─────────────────────┘  │
│                     └────────┬────────┘                             │
├──────────────────────────────┼──────────────────────────────────────┤
│                    Integration Domain Layer                         │
├──────────────────────────────┼──────────────────────────────────────┤
│  ┌───────────────────────────▼───────────────────────────────────┐  │
│  │ DataUpdateCoordinator (refresh scheduling + error strategy)   │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                              │ raw/normalized schedule data         │
│  ┌───────────────────────────▼───────────────────────────────────┐  │
│  │ Parser/Client (HTTP fetch, HTML/JS extract, normalize model) │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
├──────────────────────────────┼──────────────────────────────────────┤
│                     Entity/Presentation Layer                        │
├──────────────────────────────┼──────────────────────────────────────┤
│  ┌───────────────────────────▼───────────────────────────────────┐  │
│  │ Sensor entities (read coordinator cache, compute state, attrs)│  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                              │ state writes                         │
│  ┌───────────────────────────▼───────────────────────────────────┐  │
│  │ Home Assistant state machine / dashboard / automations        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `manifest.json` + integration package | Declares integration metadata, dependencies, config flow support, version | HA custom component manifest + package under `custom_components/<domain>/` |
| `config_flow.py` | Collects validated user input, sets unique ID, creates/upgrades config entries | `ConfigFlow` with `async_step_user`, optional reconfigure/options |
| `__init__.py` (domain bootstrap) | Creates API/parser client and coordinator per config entry; stores in `hass.data`; forwards platforms | `async_setup_entry` / `async_unload_entry` orchestration |
| `parser.py` (data access + normalization) | Fetches remote page/API and converts unstable source payload into stable internal schema | Async HTTP client + extraction/parsing + normalization + typed dictionary model |
| `coordinator.py` | Owns refresh cadence, retry/fallback behavior, and one canonical in-memory dataset | `DataUpdateCoordinator` subclass with `_async_update_data` |
| `sensor.py` / platform files | Exposes user-visible entities using cached coordinator data; no network I/O inside properties | `CoordinatorEntity` subclasses returning state/attributes from memory |
| `const.py` + `translations/` | Central constants and user-facing localized strings | Immutable constants + HA translation files |

## Recommended Project Structure

```
custom_components/zse_hdo/
├── __init__.py             # Config-entry lifecycle, dependency wiring
├── manifest.json           # HA metadata (domain, version, config_flow, requirements)
├── const.py                # Domain constants, keys, update frequencies
├── config_flow.py          # User setup + unique_id + options/reconfigure
├── coordinator.py          # DataUpdateCoordinator and refresh policy
├── parser.py               # Web fetch + parse + normalize into stable schema
├── sensor.py               # Entity layer (state derivation for HA)
└── translations/
    └── *.json              # User-facing config/entity strings
```

### Structure Rationale

- **`parser.py` separated from entities:** source parsing is volatile; isolate breakage from user-facing state logic.
- **single `coordinator.py`:** one fetch path and one cache for all entities prevents duplicate requests and keeps behavior deterministic.
- **entity modules remain pure-read:** entity properties only read memory and compute presentation state, matching HA guidance.
- **config-flow isolated:** setup/reconfigure concerns should not leak into runtime poll/update logic.

## Architectural Patterns

### Pattern 1: Coordinator-Centric Polling

**What:** One coordinator fetches all upstream data and pushes updates to dependent entities.
**When to use:** Upstream provides schedule/table payload used by multiple entities (exactly this domain).
**Trade-offs:** Simpler consistency and lower traffic; requires careful cache/error strategy because one fetch affects all entities.

**Example:**
```python
coordinator = ZSEHDOCoordinator(hass, parser, hdo_number, update_frequency)
await coordinator.async_config_entry_first_refresh()
async_add_entities([TariffSensor(coordinator), NextSwitchSensor(coordinator)])
```

### Pattern 2: Parse-to-Stable-Domain-Model Boundary

**What:** Convert brittle HTML/embedded-JS format into strict internal schema before any entity consumes data.
**When to use:** Source format is unofficial and can change without notice.
**Trade-offs:** Extra normalization code now, far less downstream coupling and easier incident fixes later.

**Example:**
```python
raw_page = await parser.fetch_page()
raw_rates = parser.extract_rates(raw_page)
normalized = parser.normalize_schedule(raw_rates, hdo_number)
return normalized  # coordinator/entites only see normalized shape
```

### Pattern 3: Derived State in Entities (No I/O)

**What:** Entities derive current tariff / next switch from cached schedule + current time, without remote calls.
**When to use:** Display state changes more frequently than source data refreshes.
**Trade-offs:** Slightly duplicated time-window logic; enables accurate live state changes even with slow upstream polling.

## Data Flow

### Runtime Flow (explicit direction)

```
User adds integration in UI
    ↓
config_flow validates input + sets unique_id
    ↓
ConfigEntry created
    ↓
__init__.py async_setup_entry()
    ↓
Create parser client
    ↓
Create coordinator (refresh policy + cache)
    ↓
coordinator first refresh → parser fetches zsed.sk → parser normalizes data
    ↓
coordinator stores normalized cache
    ↓
sensor entities read coordinator.data and compute current state/attributes
    ↓
Entity state written to HA state machine
    ↓
Dashboard/automations consume entity states
```

### Boundary Contract (who talks to whom)

| Boundary | Allowed Communication | Why |
|----------|------------------------|-----|
| `config_flow.py` → `__init__.py` | Via config entry data only | Keeps setup declarative and restart-safe |
| `__init__.py` → `coordinator.py` / `parser.py` | Constructor injection | Explicit dependency graph per entry |
| `coordinator.py` → `parser.py` | Direct method calls for fetch/normalize | Single data ingress point |
| `sensor.py` → `coordinator.py` | Read-only access to `coordinator.data` + refresh hooks | Prevents entity-originated network calls |
| entities → Home Assistant core | State write callbacks only | Aligns with HA entity lifecycle expectations |

### Failure/Data-Quality Flow

```
Fetch/parsing error
    ↓
coordinator catches exception
    ↓
if previous cache exists: return last known good data
else: raise UpdateFailed (entry setup/retry path)
```

## Suggested Build Order (for roadmap dependencies)

1. **Domain contract + constants**
   - Define normalized schedule schema and keys in `const.py`.
   - Dependency: none.

2. **Parser/client boundary**
   - Implement fetch, extraction, normalization with clear error taxonomy.
   - Dependency: step 1 schema.

3. **Coordinator and refresh policy**
   - Add `DataUpdateCoordinator`, initial refresh, cache fallback, scheduling.
   - Dependency: parser stable output.

4. **Entity layer**
   - Implement tariff/next-switch/today-summary entities from coordinator cache.
   - Dependency: coordinator availability and data model.

5. **Config flow + options/reconfigure**
   - Create user setup and update-frequency editing without runtime coupling.
   - Dependency: coordinator constructor signature and constants.

6. **UX polish and hardening**
   - Translations, logging quality, edge-case handling (midnight crossing, weekend logic), migration hooks.
   - Dependency: all runtime components integrated.

**Build-order implication:** `parser -> coordinator -> entities` is the critical path; config flow can start early but should finalize after constructor/option contracts stabilize.

## Anti-Patterns

### Anti-Pattern 1: Entity Performs Network I/O

**What people do:** call `fetch_page()` directly from entity properties or frequent update methods.
**Why it's wrong:** blocks state writes, causes duplicated requests, and violates HA entity guidance.
**Do this instead:** centralize all remote I/O in coordinator/parser and expose memory-only entity properties.

### Anti-Pattern 2: Letting Raw Source Format Leak Past Parser

**What people do:** pass raw HTML/JS blobs into coordinator/entities.
**Why it's wrong:** any upstream markup change breaks multiple modules simultaneously.
**Do this instead:** parser returns a strict normalized object; all other layers depend only on that schema.

### Anti-Pattern 3: Mixing Setup and Runtime Concerns

**What people do:** handle reconfigure/options logic directly in coordinator or entity code.
**Why it's wrong:** creates hidden side effects and makes reload/migration behavior fragile.
**Do this instead:** keep setup in config flow + `__init__.py`, runtime in coordinator/entities.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| `https://www.zsdis.sk/...` tariff page | Async HTTP fetch + parser normalization boundary | Treat as unstable source; design for parser resilience |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `config_flow.py` ↔ config entry store | HA flow API | unique ID required to prevent duplicates |
| `__init__.py` ↔ platforms | `async_forward_entry_setups` | lifecycle and unloading centralized |
| `coordinator.py` ↔ `sensor.py` | `CoordinatorEntity` listener + shared cache | one source of truth for entity updates |

## Sources

- https://developers.home-assistant.io/docs/creating_component_index/ (integration scaffolding and package structure)
- https://developers.home-assistant.io/docs/integration_fetching_data/ (DataUpdateCoordinator, push/poll patterns, update model)
- https://developers.home-assistant.io/docs/config_entries_config_flow_handler/ (config-entry, unique ID, reconfigure/reauth boundaries)
- https://developers.home-assistant.io/docs/core/entity/ (entity contract: memory-only properties, polling/subscription behavior)

---
*Architecture research for: Home Assistant web-data parser integration (`zsed.sk` source)*
*Researched: 2026-04-29*
