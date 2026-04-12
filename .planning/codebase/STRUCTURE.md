# Codebase Structure

**Analysis Date:** 2026-04-12

## Directory Layout

```
ZSED-tarify/                          # Repository root
├── custom_components/
│   └── zse_hdo/                      # HA integration package
│       ├── __init__.py               # Entry setup/unload, wires all layers
│       ├── config_flow.py            # ConfigFlow + OptionsFlow UI handlers
│       ├── const.py                  # Domain, config keys, frequency registry
│       ├── coordinator.py            # DataUpdateCoordinator + scheduler
│       ├── manifest.json             # HA integration manifest
│       ├── parser.py                 # HTTP scraper + JS-array extractor
│       ├── sensor.py                 # All three entity classes
│       └── translations/
│           ├── en.json               # English UI strings
│           └── sk.json               # Slovak UI strings
├── .planning/
│   └── codebase/                     # GSD analysis documents
├── .claude/
│   └── settings.local.json           # Claude Code local settings
├── CLAUDE.md                         # Claude Code project instructions
├── EXAMPLES.md                       # Usage examples
├── INSTALLATION.md                   # Manual installation guide
├── README.md                         # Project overview and documentation
├── LICENSE                           # MIT license
└── hacs.json                         # HACS repository metadata
```

## Directory Purposes

**`custom_components/zse_hdo/`:**
- Purpose: The entire HA integration lives here — this is the only deployable artifact
- Contains: All Python source files and JSON manifests that HA loads
- Key files: `__init__.py` (bootstrap), `coordinator.py` (data layer), `sensor.py` (entities)

**`custom_components/zse_hdo/translations/`:**
- Purpose: Localised strings for config flow and options flow UI
- Contains: One JSON file per supported language (`en.json`, `sk.json`)
- Keys mirror HA translations schema: `config.step.*`, `config.error.*`, `config.abort.*`, `options.step.*`, `selector.*`

**`.planning/codebase/`:**
- Purpose: GSD architecture/analysis documents consumed by planning and execution agents
- Generated: Yes (by GSD mapping agents)
- Committed: Yes

## Key File Locations

**Entry Points:**
- `custom_components/zse_hdo/__init__.py`: Integration load/unload — start here for any lifecycle change
- `custom_components/zse_hdo/sensor.py`: Platform setup and all entity definitions — start here for entity changes

**Configuration:**
- `custom_components/zse_hdo/manifest.json`: Integration identity, version, requirements, iot_class
- `custom_components/zse_hdo/const.py`: All constants — domain name, config keys, update frequency definitions
- `custom_components/zse_hdo/config_flow.py`: UI setup wizard and options editing
- `custom_components/zse_hdo/translations/en.json`: English UI strings
- `custom_components/zse_hdo/translations/sk.json`: Slovak UI strings

**Core Logic:**
- `custom_components/zse_hdo/parser.py`: `ZSEHDOLiveParser` — HTTP fetch, JS extraction, schedule normalisation, tariff calculation
- `custom_components/zse_hdo/coordinator.py`: `ZSEHDOCoordinator` — scheduling modes, refresh orchestration

**Testing:**
- No test directory exists. There are no automated tests.

## Naming Conventions

**Files:**
- Snake_case Python modules: `config_flow.py`, `const.py`, `coordinator.py`
- HA-mandated names for `__init__.py`, `manifest.json`, `config_flow.py`, `sensor.py`

**Classes:**
- PascalCase with `ZSEHDO` prefix for all integration classes: `ZSEHDOLiveParser`, `ZSEHDOCoordinator`, `ZSEHDOConfigFlow`, `ZSEHDOTariffSensor`
- Sensor entity names follow: `ZSEHDO` + feature description + `Sensor`

**Entity unique IDs:**
- Pattern: `zse_hdo_{hdo_number}_{feature}`
- Examples: `zse_hdo_145_tariff`, `zse_hdo_145_next_switch`, `zse_hdo_145_today_schedule`

**Entity display names:**
- Pattern: `ZSE HDO {hdo_number} {Slovak label}`
- Examples: `ZSE HDO 145 Tarifa`, `ZSE HDO 145 Ďalšie prepnutie`, `ZSE HDO 145 Dnešný rozvrh`

**Constants:**
- UPPER_SNAKE_CASE for all constants in `const.py`
- Config key strings match their Python constant name in lower snake_case: `CONF_HDO_NUMBER = "hdo_number"`

**Translation keys:**
- Frequency selector option keys match `UPDATE_FREQUENCIES` dict keys exactly: `"5min"`, `"1hour"`, `"1day"`, `"1week"`, `"1month"`

## Where to Add New Code

**New entity type:**
- Implementation: `custom_components/zse_hdo/sensor.py` — add new class extending `CoordinatorEntity` + `BinarySensorEntity` or `SensorEntity`
- Register: Add instance to the `entities` list in `sensor.py:async_setup_entry`
- No new files needed unless the entity type requires a new platform (e.g., `binary_sensor.py` if separating platforms)

**New configuration option:**
- Add constant to `custom_components/zse_hdo/const.py`
- Add field to the `vol.Schema` in `custom_components/zse_hdo/config_flow.py`
- Add UI strings to both `custom_components/zse_hdo/translations/en.json` and `custom_components/zse_hdo/translations/sk.json`
- Read new option in `custom_components/zse_hdo/__init__.py:async_setup_entry`

**New update frequency option:**
- Add entry to `UPDATE_FREQUENCIES` dict in `custom_components/zse_hdo/const.py`
- If `type` is `"scheduled"`, add handling branch in `coordinator.py:_calculate_next_update`
- Add label to translation files under `selector.update_frequency.options`

**Parser changes (new data fields):**
- Modify `ZSEHDOLiveParser._normalize_schedule` or `get_schedule` in `custom_components/zse_hdo/parser.py`
- New fields are automatically available in `coordinator.data` and can be read in entity `extra_state_attributes`

**Utilities / shared helpers:**
- No `utils.py` exists. Small helpers belong in the module that uses them (e.g., `_parse_time` is defined in both `parser.py` and `sensor.py` independently — a shared utility module could consolidate this).

## Special Directories

**`custom_components/`:**
- Purpose: HA standard location for custom integrations
- Generated: No
- Committed: Yes — this is the deployable source

**`.planning/`:**
- Purpose: GSD agent analysis documents
- Generated: Yes (by GSD commands)
- Committed: Yes

**`.claude/`:**
- Purpose: Claude Code local configuration
- Generated: Yes
- Committed: Partial (settings.local.json is project-specific but may be gitignored)

---

*Structure analysis: 2026-04-12*
