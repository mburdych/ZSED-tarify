# Feature Research

**Domain:** Home Assistant energy/tariff custom integration (DSO web-scraped schedules)
**Researched:** 2026-04-29
**Confidence:** MEDIUM-HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = plugin is quickly replaced.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| UI config flow with selectable tariff/code | HACS users expect setup in `Settings > Devices & Services` without YAML editing | LOW | Must prevent duplicates via unique ID and validate source connectivity during setup |
| Core entities for "current tariff", "next switch", and "today schedule" | Users automate appliances and dashboards from these three primitives | LOW | Binary + timestamp + daily periods is the minimum practical set |
| Reliable refresh with graceful degradation | Internet/source outages are common; users expect entities not to break permanently | MEDIUM | Coordinator cache + controlled retry + clear availability behavior |
| Correct time semantics (weekday/weekend + midnight crossing + timezone) | Tariff data is time-bound; wrong boundaries immediately break automations | MEDIUM | Highest correctness risk; needs explicit edge-case handling |
| Energy Dashboard compatibility metadata | Users expect price/tariff sensors to be usable in Energy dashboard workflows | MEDIUM | Correct classes/units/attributes are required for HA long-term statistics and dashboard usage |
| Automation-ready attributes and stable entity IDs | Community users build automations from attributes and do not tolerate frequent breaking changes | LOW | Include machine-friendly values (`low/high`) plus human labels |
| Update frequency/options tuning from UI | Different users prefer low traffic vs fresh state; no one wants code edits for this | LOW | Options Flow is now baseline expectation for maintained integrations |

### Differentiators (Competitive Advantage)

Features that make users choose this integration over generic template-based setups.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Dynamic discovery of all valid ZSE(HDO) codes from source | No manual lookup or hardcoded lists; onboarding stays future-proof as utility changes | MEDIUM | Strong local-market advantage versus generic TOU templates |
| Rich tariff intelligence sensors (next low window, remaining low duration, "cheap-now" boolean) | Turns raw schedules into direct automation decisions | MEDIUM | Similar to "cheapest hours" community add-ons, but localized for fixed HDO logic |
| Built-in fallback status/diagnostics entity | Users can see "schedule age", "last fetch", and parser health without log digging | MEDIUM | Reduces support burden and increases trust during source outages |
| "Action packs" (optional blueprint examples) for boiler/EV/water-heater control | Faster time-to-value for non-technical users | LOW-MEDIUM | Documentation + blueprints often outperform adding many extra sensors |
| Schedule-change detection notifications | Alerts users when utility modifies switching patterns | MEDIUM | Useful where users optimize high-load devices around known windows |
| Multi-entry household/business comparison view | Power users can compare multiple HDO codes/properties in one install | MEDIUM | Helpful for mixed properties and planning scenarios |

### Anti-Features (Commonly Requested, Often Problematic)

Features that look attractive but usually damage reliability/scope.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Minute-level forced polling of source website | Users want "real-time" confidence | Increases breakage/rate-limit risk and provides little value for mostly static schedules | Scheduled refresh + local real-time tariff evaluation from cached schedule |
| Huge sensor explosion for every derived metric | "More entities = more power" perception | UI clutter, maintenance burden, and brittle backwards compatibility | Keep core entities lean; provide advanced metrics as opt-in |
| Scraping multiple unofficial mirrors by default | Seen as uptime protection | Inconsistent schema and legal/maintenance risk | Single canonical source + explicit "stale data" diagnostics |
| Full in-app charting subsystem | Users want turnkey visuals | Reinvents HA dashboard ecosystem and expands scope heavily | Provide Lovelace snippets/examples, not custom chart engine |
| Auto-control of appliances by integration itself | "One-click savings" appeal | Safety/liability and overreach beyond data integration scope | Expose high-quality signals and optional blueprints for user-owned automations |

## Feature Dependencies

```text
[Source parser correctness]
    └──requires──> [Time semantics correctness]
                       └──requires──> [Timezone + DST handling]

[Core entities]
    └──requires──> [Source parser correctness]

[Energy dashboard compatibility]
    └──requires──> [Correct units/classes/metadata]

[Rich tariff intelligence sensors]
    └──enhances──> [Core entities]

[Diagnostics + stale-data visibility]
    └──enhances──> [Reliable refresh with graceful degradation]

[Auto-control of appliances]
    └──conflicts──> [Data-only integration boundary]
```

### Dependency Notes

- **Core entities require parser + time correctness:** if parsing/time logic is wrong, every downstream automation is wrong.
- **Differentiator sensors should layer on top of stable primitives:** build intelligence only after core entities are trustworthy.
- **Diagnostics amplifies reliability features:** outage handling without visible status still feels broken to users.
- **Embedded appliance control conflicts with integration scope:** this should stay in user automations/blueprints.

## MVP Definition

### Launch With (v1)

Minimum viable product for community trust.

- [ ] Config flow + unique entry validation + selectable HDO code
- [ ] Three core entities: current tariff, next switch, today schedule
- [ ] Correct weekend/weekday and midnight-crossing logic
- [ ] Coordinator refresh with cached fallback and clear availability handling
- [ ] Stable IDs/attributes for automation use

### Add After Validation (v1.x)

Features to add once core reliability is proven.

- [ ] Options flow refinements (frequency presets, advanced fetch strategy)
- [ ] Diagnostics/staleness entity and troubleshooting-first docs
- [ ] Rich tariff intelligence helpers (remaining low window, upcoming slots)
- [ ] Blueprint pack for common loads (boiler/EV/water heating)

### Future Consideration (v2+)

Defer until adoption and feedback justify complexity.

- [ ] Multi-code comparative analytics dashboards
- [ ] Change-detection alerts with user-configurable thresholds
- [ ] Optional integration with price feeds (if scope expands from schedule-only to cost optimization)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Core entities + parser/time correctness | HIGH | MEDIUM | P1 |
| Reliable refresh + outage behavior | HIGH | MEDIUM | P1 |
| Config/options flow UX polish | HIGH | LOW | P1 |
| Diagnostics + stale data transparency | MEDIUM-HIGH | MEDIUM | P2 |
| Rich tariff intelligence helpers | MEDIUM-HIGH | MEDIUM | P2 |
| Blueprint/action packs | MEDIUM | LOW-MEDIUM | P2 |
| Multi-code comparative analytics | MEDIUM | MEDIUM-HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have after stable launch
- P3: Nice to have, later

## Competitor Feature Analysis

| Feature | Competitor A (HA Nord Pool official) | Competitor B (community cheapest-hours tools) | Our Approach |
|---------|--------------------------------------|-----------------------------------------------|--------------|
| Core tariff/price entities | Strong baseline sensors + attributes + actions | Often binary "cheapest now" oriented | Keep strong core entities first |
| Tomorrow/future planning | Supports fetching dates/actions and templates | Primary focus of many community tools | Provide future switch context for fixed HDO schedules |
| Reliability visibility | Includes diagnostic patterns in HA ecosystem | Varies by project quality | Add explicit staleness/health visibility early |
| Local-market specialization | Generic energy-market integration | Usually tied to Nord Pool spot prices | Differentiate with Slovak ZSE HDO-specific UX and code discovery |

## Sources

- Home Assistant Utility Meter docs: https://www.home-assistant.io/integrations/utility_meter/ (HIGH)
- Home Assistant Nord Pool docs: https://www.home-assistant.io/integrations/nordpool/ (HIGH)
- Home Assistant Integration Quality Scale: https://developers.home-assistant.io/docs/core/integration-quality-scale/ (HIGH)
- Home Assistant Options Flow docs: https://developers.home-assistant.io/docs/core/integration/options_flow/ (HIGH)
- Home Assistant Diagnostics docs: https://developers.home-assistant.io/docs/core/integration/diagnostics (HIGH)
- Community benchmark (Tibber advanced price integration): https://github.com/jpawlowski/hass.tibber_prices (MEDIUM)
- Community benchmark (cheapest-hours patterns): https://www.creatingsmarthome.com/index.php/2024/07/27/home-assistant-nord-pool-cheapest-hours-with-aio-energy-management/ (MEDIUM)

---
*Feature research for: Home Assistant ZSE tariff integrations*
*Researched: 2026-04-29*
