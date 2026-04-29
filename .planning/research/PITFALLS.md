# Pitfalls Research

**Domain:** Home Assistant custom integration scraping/parsing tariff data from external website (`zsed.sk`)
**Researched:** 2026-04-29
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Blocking I/O inside Home Assistant event loop

**What goes wrong:**
Integration performs synchronous HTTP/file work (`requests`, `urllib`, blocking parser steps) in async paths, causing HA stalls, watchdog warnings, or random setup/update timeouts.

**Why it happens:**
Scraping code is often prototyped as standalone Python first, then copied into HA without converting all call paths to async-safe execution.

**How to avoid:**
Use `aiohttp`/`httpx` async clients for network calls; if a dependency remains blocking, isolate it behind `hass.async_add_executor_job`. Add explicit timeouts and never use blocking `sleep`.

**Warning signs:**
- Logs show "Detected blocking call ..." warnings.
- UI lag or delayed automations during refresh windows.
- Coordinator update duration spikes when source website is slow.

**Phase to address:**
Phase 1 - Data access layer + async safety baseline.

---

### Pitfall 2: Fragile parser coupled to one HTML/JS shape

**What goes wrong:**
Minor source-site markup/script changes break extraction logic, resulting in empty schedules, wrong tariff windows, or crash loops.

**Why it happens:**
Parser is written as exact string/regex match against current page output without resilient extraction boundaries and schema normalization.

**How to avoid:**
Design parser with layered strategy: (1) locate stable anchors, (2) tolerant extraction, (3) strict normalization/validation, (4) fail-soft fallback to last known good data. Add fixture tests from multiple historical page variants.

**Warning signs:**
- Parse success drops to zero immediately after site deploy.
- Sudden rise in "key not found"/JSON decode errors.
- Entity availability flaps despite network being healthy.

**Phase to address:**
Phase 2 - Parser hardening and schema validation.

---

### Pitfall 3: No graceful degradation when upstream fails

**What goes wrong:**
Temporary upstream downtime/rate-limit makes all entities unavailable; users lose automations and dashboard trust.

**Why it happens:**
Coordinator treats every fetch failure as fatal and does not keep or expose last successful snapshot + timestamp.

**How to avoid:**
Keep last known good payload in coordinator, return cached data for transient failures, expose staleness attributes (`last_success`, `data_age_minutes`), and surface warnings instead of hard failure.

**Warning signs:**
- Entities become `unavailable` on single timeout.
- No metadata showing data freshness.
- Error bursts correlate with external 429/5xx but recovery is poor.

**Phase to address:**
Phase 3 - Reliability and degraded-mode behavior.

---

### Pitfall 4: Bad polling/backoff strategy (hammering source or self-DOS)

**What goes wrong:**
Integration over-polls a low-change page, triggers rate limits/blocks, and wastes HA resources; or retries aggressively and amplifies outages.

**Why it happens:**
Teams optimize for "freshness" without domain-aware cadence; retries are implemented as immediate loops without `Retry-After`/exponential backoff.

**How to avoid:**
Use domain-driven refresh cadence (e.g., scheduled daily/weekly for tariff calendars), bounded retry policy with exponential backoff + jitter, and honor `Retry-After` semantics for 429/503-style responses.

**Warning signs:**
- Frequent 429/503 responses from source.
- Refresh task runs almost continuously after errors.
- CPU/network usage rises while data freshness does not improve.

**Phase to address:**
Phase 3 - Coordinator scheduling, retry and rate-limit policy.

---

### Pitfall 5: Timezone/day-boundary logic errors in tariff state

**What goes wrong:**
Current tariff and next-switch sensors are wrong around midnight, DST transitions, or weekend/weekday boundaries.

**Why it happens:**
Business-time logic is duplicated across parser/sensors and uses naive datetimes or inconsistent day classification.

**How to avoid:**
Centralize tariff-evaluation engine in one module, use timezone-aware HA utilities, and add boundary tests: `23:59->00:00`, DST shift day, weekend crossover, overnight intervals.

**Warning signs:**
- User reports mismatch between utility schedule and HA state around midnight.
- Bug fixes in one sensor regress another.
- "Next switch" jumps backward/forward unexpectedly.

**Phase to address:**
Phase 2 - Domain rules engine + boundary test suite.

---

### Pitfall 6: Poor observability for parser/coordinator health

**What goes wrong:**
Failures are hard to diagnose; maintainers cannot quickly separate upstream website changes from local code regressions.

**Why it happens:**
Logs are either too sparse ("update failed") or too noisy; no structured counters for fetch/parse/cache/degraded states.

**How to avoid:**
Add structured, redacted logging around fetch/parse/normalize phases; expose diagnostics attributes (source status, parse version, payload hash, last success). Define alert thresholds for repeated parse failures.

**Warning signs:**
- Issue reports cannot be reproduced from logs.
- Same bug reopens after "fixes" due to missing telemetry.
- MTTR is high for source-format breakages.

**Phase to address:**
Phase 4 - Observability and supportability hardening.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Parsing with one brittle regex | Fast first delivery | Breaks on minor site changes | Only throwaway spike |
| Refreshing every few minutes "just in case" | Looks real-time | Rate-limit risk + HA load | Never for tariff schedules |
| Duplicating tariff-time logic per entity | Quick implementation | Inconsistent behavior and regressions | Never |
| Swallowing parse errors and returning empty data | Avoids crashes | Silent wrong state | Never |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| External website scraping (`zsed.sk`) | Assume stable HTML/JS contract | Treat source as unstable; normalize + validate every refresh |
| Home Assistant coordinator | Fail setup/update on first transient network issue | Use cached fallback + controlled `UpdateFailed` behavior |
| Rate-limited upstream | Retry instantly on 429/503 | Exponential backoff, jitter, honor `Retry-After` |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Per-entity independent fetches | Duplicate requests, slow updates | Single `DataUpdateCoordinator` per config entry | As soon as users add multiple entities |
| Parsing full page for each sensor read | CPU spikes, laggy state updates | Parse once per refresh, sensors read cached normalized model | Moderate installations with frequent state writes |
| Aggressive retry storms | Constant network churn | Retry budget + circuit-breaker cooldown | During upstream outage windows |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging full response body from scraped page | Potential leakage of unexpected PII/tokens in logs | Log metadata only; redact payload samples |
| Trusting remote content without bounds | Memory/CPU abuse from oversized/hostile payloads | Enforce response size/time limits and parse guards |
| Following redirects blindly | SSRF-like fetch behavior to untrusted hosts | Pin allowed hostnames and validate final URL |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing stale data as if live | Wrong automation decisions | Expose freshness/staleness attributes clearly |
| Generic error state without context | Users cannot self-diagnose | Add human-readable reason (`upstream timeout`, `parse changed`) |
| "Unavailable" toggling on transient errors | Dashboard noise and distrust | Keep last known good state + degraded status signal |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Parser robustness:** Works on one live sample but not on archived variants - verify fixture set across multiple page versions.
- [ ] **Coordinator reliability:** Happy-path updates pass - verify behavior under timeout, 429, invalid payload, and partial parse.
- [ ] **Tariff correctness:** Typical daytime intervals pass - verify midnight-crossing, weekend, and DST boundaries.
- [ ] **User-facing status:** Entities update - verify staleness and degraded-mode are visible in attributes/logs.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Source format changed | MEDIUM | Hotfix extractor with fallback path, ship fixture from failed payload, release patch |
| Rate-limited/blocked upstream | LOW-MEDIUM | Reduce polling cadence, enable backoff/jitter, add cooldown before next refresh |
| Wrong tariff around boundary time | HIGH | Disable affected automation path, patch central evaluator, add regression tests for boundary case |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Blocking I/O in event loop | Phase 1 (Async-safe data access) | No HA blocking-call warnings under debug mode |
| Fragile parser coupling | Phase 2 (Parser hardening) | Fixture suite passes across historical and mutated samples |
| No degraded mode | Phase 3 (Reliability) | Timeout/429 chaos test keeps entities available with stale marker |
| Bad polling/backoff | Phase 3 (Scheduling + retry policy) | Load test shows bounded retry behavior and no request storm |
| Time boundary bugs | Phase 2 (Domain rules engine) | Boundary regression tests pass (midnight, DST, weekend) |
| Poor observability | Phase 4 (Telemetry + diagnostics) | Incident triage possible from logs/attributes without reproducing locally |

## Sources

- Home Assistant developer docs - Fetching data: https://developers.home-assistant.io/docs/integration_fetching_data/ (HIGH)
- Home Assistant developer docs - Blocking operations with asyncio: https://developers.home-assistant.io/docs/asyncio_blocking_operations (HIGH)
- urllib3 Retry reference (backoff + `Retry-After` handling): https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.retry.Retry (HIGH)
- Home Assistant core issue context on coordinator/config entry migration: https://github.com/home-assistant/core/issues/128077 (MEDIUM)
- Home Assistant blog on coordinator unnecessary updates (`always_update=False`): https://developers.home-assistant.io/blog/2023/07/27/avoiding-unnecessary-callbacks-with-dataupdatecoordinator/ (HIGH)

---
*Pitfalls research for: Home Assistant scraping integration (`zsed.sk`)*
*Researched: 2026-04-29*
