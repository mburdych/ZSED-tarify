# Coding Conventions

**Analysis Date:** 2026-04-12

## Naming Patterns

**Files:**
- Snake_case module names: `config_flow.py`, `coordinator.py`, `const.py`
- Dunder entry: `__init__.py` serves as integration setup

**Classes:**
- PascalCase with full domain prefix: `ZSEHDOLiveParser`, `ZSEHDOCoordinator`, `ZSEHDOTariffSensor`, `ZSEHDOOptionsFlowHandler`
- Sensor classes follow pattern `ZSEHDO{Feature}Sensor`

**Functions and Methods:**
- Snake_case for all functions and methods
- HA async convention: all public integration methods prefixed with `async_`: `async_setup_entry`, `async_unload_entry`, `async_step_user`, `async_step_init`
- Internal async helpers (e.g., scheduler callbacks) defined as local closures inside methods
- Private methods prefixed with underscore: `_extract_javascript_array`, `_parse_time`, `_normalize_schedule`, `_calculate_current_tariff`, `_calculate_next_update`, `_schedule_next_update`, `_get_next_switch`

**Variables:**
- Snake_case throughout
- Module-level logger always named `_LOGGER`:
  ```python
  _LOGGER = logging.getLogger(__name__)
  ```
- Private instance attributes prefixed with `_`: `self._session`, `self._own_session`, `self._hdo_numbers`, `self._errors`, `self._entry`, `self._hdo_number`
- HA entity attributes use `_attr_` prefix (HA convention): `self._attr_unique_id`, `self._attr_name`, `self._attr_device_class`, `self._attr_icon`

**Constants:**
- SCREAMING_SNAKE_CASE in `custom_components/zse_hdo/const.py`
- Grouped by concern with inline comments
- String keys for dicts use lowercase with underscores: `"workday"`, `"weekend"`, `"low"`, `"high"`

## Code Style

**Formatting:**
- No formatter config file detected (no `.prettierrc`, `pyproject.toml`, or `ruff.toml` in repo)
- Indentation: 4 spaces consistently
- Blank lines: one blank line between methods within a class, two between top-level definitions

**Linting:**
- No linting config file detected

**Type Hints:**
- Used consistently on all public and private method signatures
- Imports from `typing`: `Dict`, `List`, `Optional`, `Any`
- Return types annotated on all methods
- Constructor parameters typed
- Example from `custom_components/zse_hdo/parser.py`:
  ```python
  def _normalize_schedule(self, intervals: List[Dict]) -> Dict[str, List[Dict]]:
  ```

## Import Organization

**Order observed:**
1. Standard library (`re`, `json`, `logging`, `datetime`, `typing`)
2. Third-party (`aiohttp`, `async_timeout`, `voluptuous`)
3. Home Assistant framework (`homeassistant.*`)
4. Local relative imports (`.parser`, `.coordinator`, `.const`)

**Path Aliases:**
- Relative imports used for intra-package references: `from .parser import ZSEHDOLiveParser`
- HA imports grouped under `homeassistant.*` namespace

## Error Handling

**Strategy:** Log-and-raise at boundaries; return `None` or `[]` for missing data in pure parsing code.

**Patterns:**
- HTTP errors in `custom_components/zse_hdo/parser.py` — catch `aiohttp.ClientError` specifically, then catch broad `Exception` as fallback, both log with `_LOGGER.error` and re-raise:
  ```python
  except aiohttp.ClientError as err:
      _LOGGER.error(f"Failed to fetch HDO data: {err}")
      raise
  except Exception as err:
      _LOGGER.error(f"Unexpected error fetching HDO data: {err}")
      raise
  ```
- Coordinator wraps all fetch errors into `UpdateFailed` (HA standard) in `custom_components/zse_hdo/coordinator.py`:
  ```python
  except Exception as err:
      _LOGGER.error(f"Error fetching HDO data for {self.hdo_number}: {err}")
      raise UpdateFailed(f"Error fetching HDO data: {err}")
  ```
- Parse failures (JSON decode, missing JS variable) return empty list `[]` and log warning/error — do not raise
- Config flow catches connection errors and sets `self._errors["base"] = "cannot_connect"` (HA convention)
- Sensor properties guard with `if not self.coordinator.data: return {}` / `return False` — never raise in property accessors

## Logging

**Framework:** Python standard `logging` via `_LOGGER = logging.getLogger(__name__)`

**Patterns:**
- `_LOGGER.debug` for successful data operations and fetch details
- `_LOGGER.info` for lifecycle events (setup, scheduling, update counts)
- `_LOGGER.warning` for expected missing data (HDO not found, JS variable absent)
- `_LOGGER.error` for network failures and parse failures
- F-strings used throughout for log message formatting (not `%s` style)

## Comments

**Language:** Mixed — docstrings in English, inline comments in Slovak (developer's native language)

**Inline comments:** Slovak, describing intent:
```python
# Vytvorenie parsera
# Prvotné načítanie dát
# Uloženie do hass.data
```

**Docstrings:**
- Module-level docstrings present in all files with author/license block
- Class docstrings: single-line Slovak descriptions
- Method docstrings: English or Slovak summary, with `Args:` and `Returns:` sections in some methods (inconsistent — present in `parser.py`, absent in `sensor.py` and `coordinator.py`)

## Function Design

**Size:** Methods are focused and short (10-40 lines); `_extract_javascript_array` in `parser.py` is the longest at ~60 lines due to character-by-character parsing logic

**Parameters:** Positional required first, keyword with defaults after; `Optional[...]` typing used for nullable params

**Return Values:**
- `Optional[Dict]` / `Optional[bool]` returned from parser methods when data may not exist
- Sensor `@property` accessors return typed values or safe defaults
- Parser internal helpers return empty collections (`[]`, `{}`) on failure rather than raising

## Module Design

**Exports:** No `__all__` defined; public API is implicit
**Barrel Files:** Not used; each module imported directly by name

## Home Assistant Specific Conventions

**Entry setup:**
- `async_setup_entry` stores coordinator in `hass.data[DOMAIN][entry.entry_id]` as a dict with keys `"coordinator"`, `"parser"`, `"hdo_number"`
- `async_unload_entry` removes from `hass.data[DOMAIN]` on success

**Entities:**
- Extend `CoordinatorEntity` and the appropriate HA entity base (`BinarySensorEntity`, `SensorEntity`)
- Use `_attr_*` properties for static attributes (HA pattern)
- Use `@property` for dynamic attributes computed from `self.coordinator.data`
- `extra_state_attributes` returns `{}` when coordinator has no data

**Constants:**
- All domain-wide constants in `custom_components/zse_hdo/const.py`
- Configuration keys as string constants (`CONF_HDO_NUMBER`, `CONF_UPDATE_FREQUENCY`)

---

*Convention analysis: 2026-04-12*
