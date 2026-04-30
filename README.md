# ZSE HDO Live Integration pre Home Assistant

🇸🇰 **Slovenská integrácia pre sledovanie HDO taríf ZSE v reálnom čase!**

## 🎯 Funkcie

- ✅ **Dynamické načítanie** všetkých HDO čísel priamo z www.zsdis.sk
- ✅ **Live parsing** - vždy aktuálne dáta z webu (podobne ako waste_collection_schedule)
- ✅ **Binary sensor** - aktuálna tarifa (ON = nízka, OFF = vysoká)
- ✅ **Sensor** - čas najbližšieho prepnutia
- ✅ **Sensor** - dnešný rozvrh nízkych taríf
- ✅ **Helper sensor** - zostávajúce minúty aktuálnej nízkej tarify
- ✅ **Podpora všetkých 44 HDO** čísel (domácnosti aj firmy)
- ✅ **Automatické rozlíšenie** víkend/pracovný deň

## ☕ Podporte vývoj

Páči sa vám táto integrácia? Pomôžte mi pokračovať vo vývoji!

<a href="https://buymeacoffee.com/mburdych" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

**Každá káva ma motivuje vytvárať lepšie integrácie pre Home Assistant komunitu!** 🚀

## 📦 Inštalácia

### Cez HACS (odporúčané)

1. Otvorte HACS v Home Assistant
2. Kliknite na "Integrations"
3. Kliknite na "..." v pravom hornom rohu
4. Vyberte "Custom repositories"
5. Pridajte URL: `(https://github.com/mburdych/ZSED-tarify)`
6. Kategória: `Integration`
7. Kliknite "Add"
8. Vyhľadajte "ZSE HDO Live" a nainštalujte

### Manuálna inštalácia

1. Skopírujte `custom_components/zse_hdo` do vášho `config/custom_components/`
2. Reštartujte Home Assistant

## ⚙️ Konfigurácia

1. Prejdite do **Nastavenia** → **Zariadenia a služby**
2. Kliknite **+ Pridať integráciu**
3. Vyhľadajte **"ZSE HDO Live"**
4. Vyberte **vaše HDO číslo** zo zoznamu (automaticky načítaný z webu!)
5. Kliknite **Odoslať**

Hotovo! 🎉

## 📊 Entity

Po konfigurácii sa vytvoria nasledujúce entity:

### 1. Binary Sensor - Aktuálna tarifa
- **Entity ID**: `binary_sensor.zse_hdo_XXX_tariff`
- **Stav**: 
  - `ON` = Nízka tarifa ⚡
  - `OFF` = Vysoká tarifa 🔴
- **Atribúty**:
  - `hdo_number`: Vaše HDO číslo
  - `current_tariff`: low/high
  - `tariff_name`: Nízka/Vysoká
  - `category`: household/business
  - `rate_type`: Typ sadzby (napr. `D3 Aktiv (DD3*)`)
  - `last_updated`: Čas poslednej aktualizácie
  - `is_stale`: `true/false` či sa používajú fallback cache dáta
  - `stale_for_s`: Vek dát v sekundách počas degraded režimu
  - `consecutive_failures`: Počet po sebe idúcich neúspešných refreshov
  - `last_success_at`: Čas posledného úspešného refreshu
  - `last_error_at`: Čas poslednej chyby (ak existuje)
  - `next_retry_at`: Čas najbližšieho retry pokusu (ak je naplánovaný)
  - `schedule_changed`: `true/false` či posledný úspešný refresh zistil zmenu harmonogramu
  - `schedule_change_at`: Čas detekcie poslednej zmeny harmonogramu (ak existuje)

### 2. Sensor - Ďalšie prepnutie
- **Entity ID**: `sensor.zse_hdo_XXX_next_switch`
- **Stav**: ISO datetime najbližšieho prepnutia
- **Atribúty**:
  - `time`: Čas prepnutia (HH:MM)
  - `to_tariff`: low/high
  - `to_tariff_name`: Nízka/Vysoká
  - `rate_type`: Typ tarify (napr. "D3 Aktiv")
  - `is_stale`, `stale_for_s`, `consecutive_failures`, `last_success_at`, `last_error_at`, `next_retry_at`, `schedule_changed`, `schedule_change_at`

### 3. Sensor - Dnešný rozvrh
- **Entity ID**: `sensor.zse_hdo_XXX_today_schedule`
- **Stav**: Počet období nízkej tarify dnes
- **Atribúty**:
  - `day_type`: Pracovný deň/Víkend
  - `periods`: Zoznam všetkých období
  - `period_count`: Počet období
  - `rate_type`: Typ tarify
  - `category`: household/business
  - `is_stale`, `stale_for_s`, `consecutive_failures`, `last_success_at`, `last_error_at`, `next_retry_at`, `schedule_changed`, `schedule_change_at`

### 4. Helper Sensor - Zostávajúca nízka tarifa
- **Entity ID**: `sensor.zse_hdo_XXX_low_remaining`
- **Stav**: Zostávajúce minúty v aktuálnom low-tariff okne (`0` mimo nízkej tarify)
- **Atribúty**:
  - `remaining_minutes`: Rovnaká hodnota ako stav (minúty)
  - `period_end`: ISO datetime konca aktuálneho low okna (alebo `null`)
  - `is_low_tariff_now`: `true/false` či je práve aktívna nízka tarifa
  - `rate_type`: Typ tarify
  - `category`: household/business
  - `is_stale`, `stale_for_s`, `consecutive_failures`, `last_success_at`, `last_error_at`, `next_retry_at`, `schedule_changed`, `schedule_change_at`

## 🔄 Automatická aktualizácia

- Integrácia **automaticky sťahuje** aktuálne dáta z www.zsdis.sk
- **Interval**: konfigurovateľný (5 min / 1 h / 1 deň / 1 týždeň / 1 mesiac)
- **Zmeny na webe** sa automaticky prejavia v Home Assistant

## 🚀 Release Workflow

Pred každým ďalším release postupujeme cez opakovateľný checklist:

- planning checklist: `.planning/RELEASE-CHECKLIST.md`
- automated gate: `py -m pytest -q tests`
- manual HA smoke gate: baseline entity card + diagnostics/schedule-change marker check

## 🧩 Blueprint balíček (v1.2.1)

Repo obsahuje pripravené Home Assistant blueprinty:

- `blueprints/automation/zse_hdo_live/notify_low_tariff_on.yaml`
- `blueprints/automation/zse_hdo_live/boiler_by_tariff.yaml`
- `blueprints/automation/zse_hdo_live/reminder_before_switch.yaml`

Import v HA:
1. Settings -> Automations & Scenes -> Blueprints
2. Import blueprint
3. Vyber súbor z uvedeného priečinka

## 💡 Príklady použitia

### Odporúčaný baseline bez custom kariet

Základná prezentácia je plne podporovaná cez vstavanú Home Assistant kartu `type: entities`.
Nepotrebujete `Mushroom` ani `card-mod`.

```yaml
type: entities
title: "⚡ ZSE HDO 145 (baseline)"
entities:
  - entity: binary_sensor.zse_hdo_145_tariff
  - entity: sensor.zse_hdo_145_next_switch
  - entity: sensor.zse_hdo_145_today_schedule
  - entity: sensor.zse_hdo_145_low_remaining
```

Pokročilé vizuály (Mushroom/card-mod) sú voliteľné a sú uvedené v `EXAMPLES.md`.

### Automation - Notifikácia pri prepnutí na nízku tarifu

```yaml
automation:
  - alias: "HDO - Nízka tarifa ON"
    trigger:
      - platform: state
        entity_id: binary_sensor.zse_hdo_145_tariff
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "⚡ Nízka tarifa"
          message: "Zapnula sa nízka tarifa! Teraz je čas zapnúť spotrebiče."
```

### Automation - Automatické zapnutie bojlera

```yaml
automation:
  - alias: "Bojler - Zapnúť pri nízkej tarife"
    trigger:
      - platform: state
        entity_id: binary_sensor.zse_hdo_145_tariff
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.bojler
```

### Lovelace Card

```yaml
type: entities
title: ZSE HDO 145
entities:
  - entity: binary_sensor.zse_hdo_145_tariff
    name: Aktuálna tarifa
  - entity: sensor.zse_hdo_145_next_switch
    name: Ďalšie prepnutie
  - entity: sensor.zse_hdo_145_today_schedule
    name: Dnes období
  - entity: sensor.zse_hdo_145_low_remaining
    name: Zostáva nízka tarifa (min)
```

## 🏷️ Podporované HDO čísla

Integrácia podporuje **všetkých 44 HDO čísel**:

**Domácnosti (32):**
145, 146, 149, 150, 151, 152, 153, 154, 158, 159, 160, 161, 162, 168, 169, 179, 184, 185, 190, 202, 203, 206, 208, 217, 246, 259, 262, 346, 359, 459, 559, 659

**Firmy (12):**
101, 102, 103, 105, 109, 111, 125, 136, 139, 200, 201, 207

## 🐛 Riešenie problémov

### Integrácia sa nepodarilo pridať
- Skontrolujte pripojenie k internetu
- Overte, že máte funkčný prístup na www.zsdis.sk
- Pozrite do logov: `Nastavenia → Systém → Logy`

### Entity sa nezobrazujú
- Reštartujte Home Assistant
- Skontrolujte, či je integrácia aktivovaná v `Zariadenia a služby`

### Nesprávne dáta
- Integrácia automaticky sťahuje dáta z webu ZSE
- Ak sa rozvrh zmenil, počkajte 5 minút na automatickú aktualizáciu
- Môžete manuálne vyžiadať aktualizáciu cez Developer Tools

## 📝 Changelog

### v1.2.0 (2026-04-30)
**Operability + value-add release:**
- ✅ CONF-03: explicit diagnostic separation (`fetch` / `parse` / `tariff_logic`) with stable marker attributes
- ✅ VADD-01: new helper sensor `sensor.zse_hdo_XXX_low_remaining` (remaining low-tariff minutes)
- ✅ VADD-03: schedule-change hooks (`schedule_changed`, `schedule_change_at`) for notification automations
- ✅ Release workflow codified in `.planning/RELEASE-CHECKLIST.md`

### v1.1.0 (2026-04-29)
**Reliability + test hardening release:**
- ✅ Unified tariff/time semantics refactor and HA timezone consistency (`dt_util`)
- ✅ Parser fixture test suite (`pytest` + `pytest-asyncio`, deterministic offline fixtures)
- ✅ Coordinator retry/backoff + explicit stale metadata in existing entities
- ✅ Recovery behavior: stale fields auto-reset after first successful refresh
- ✅ Entity contract/documentation refresh for dashboard usage

### v1.0.8 (2026-01-13)
**Critical Bugfix:**
- 🐛 OPRAVA: `current_tariff` atribút teraz správne vracia "low"/"high"
- Predtým: Zobrazovalo `null` pretože parser nepočítal aktuálnu tarifu
- Teraz: Nová metóda `_calculate_current_tariff()` vypočíta tarifu z rozvrhu
- Rieši prechodenie cez polnoc (napr. 23:45-05:45)
- Rozlišuje pracovný deň vs víkend

### v1.0.7 (2026-01-13)
**Bugfix:**
- 🐛 OPRAVA: `rate_type` teraz správne extrahuje "D3 Aktiv (DD3*)" z intervalov
- Predtým: Zobrazovalo "Unknown" namiesto skutočnej sadzby
- Teraz: Správne zobrazuje sadzbu zo ZSE dát (z prvého intervalu)

### v1.0.6 (2026-01-12)
**Oprava scheduled updates:**
- 🐛 OPRAVA: 1day/1week/1month updaty teraz **skutočne** o 03:00
- 🐛 Predtým: updaty "po N sekundách" od pridania
- ✅ Teraz: presné naplánované časy (každý deň/pondelok/1. v mesiaci o 03:00)

### v1.0.5 (2026-01-12)
**Backend vylepšenia:**
- ✅ Konfigurovateľná frekvencia aktualizácie (5min/1h/1deň/1týždeň/1mesiac)
- ✅ Options Flow - zmena frekvencie bez znovu pridávania
- ✅ Pridaný `rate_type` atribút (sadzba/tarifikácia)
- ✅ Zdieľaný coordinator pre lepšiu efektivitu
- ✅ Zoradenie HDO čísel vzostupne v dropdowne
- ✅ Autor: Miroslav Burdych

### v1.0.4 (2026-01-11)
**Opravy:**
- 🐛 Type fix - HDO číslo ako integer namiesto string
- 🐛 Oprava aiohttp session importu

### v1.0.0 (2026-01-11)
**Prvé vydanie:**
- 🎉 Dynamické načítanie HDO dát zo ZSE webu
- 🎉 3 entity: tarifa, ďalšie prepnutie, dnešný rozvrh
- 🎉 Podpora 44 HDO čísel (32 domácností, 12 podnikateľov)
- 🎉 Config flow s UI konfiguráciou
- ✨ Prvá verzia
- ✅ Live parsing zo ZSE webu
- ✅ Podpora všetkých 44 HDO čísel
- ✅ Binary sensor pre tarifu
- ✅ Sensor pre najbližšie prepnutie
- ✅ Sensor pre dnešný rozvrh

## 🤝 Príspevky

Príspevky sú vítané! Vytvorte PR na GitHub.

## 📄 Licencia

MIT License

## 👨‍💻 Autor

**Miroslav Burdych** - [@mburdych](https://github.com/mburdych)

> 🤖 Tento balík bol vytvorený v spolupráci s **Claude Sonnet 4.5** (Anthropic)
> Kombinácia ľudského know-how a AI asistenta pre efektívny vývoj.

---

## 💖 Ďakujem za podporu!

**Páči sa vám táto integrácia?**
- ⭐ Dajte hviezdičku na GitHube
- ☕ [Kúpte mi kávu](https://buymeacoffee.com/mburdych)

Vaša podpora ma motivuje pokračovať vo vývoji a udržiavaní tejto integrácie!
