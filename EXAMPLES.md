# Príklady použitia ZSE HDO Live

## 📊 Lovelace Dashboard Examples

### 1. Základná karta s entitami (baseline bez custom kariet)

```yaml
type: entities
title: "⚡ ZSE HDO 145"
entities:
  - entity: binary_sensor.zse_hdo_145_tariff
    name: "Aktuálna tarifa"
    icon: mdi:flash
  - entity: sensor.zse_hdo_145_next_switch
    name: "Ďalšie prepnutie"
  - entity: sensor.zse_hdo_145_today_schedule
    name: "Počet období dnes"
  - entity: sensor.zse_hdo_145_low_remaining
    name: "Zostáva nízka tarifa (min)"
```

### 2. Mushroom Card (odporúčané)

> Voliteľné: táto karta vyžaduje HACS doplnok Mushroom.

```yaml
type: custom:mushroom-chips-card
chips:
  - type: entity
    entity: binary_sensor.zse_hdo_145_tariff
    icon_color: |
      {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
        green
      {% else %}
        red
      {% endif %}
    name: |
      {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
        Nízka ⚡
      {% else %}
        Vysoká 🔴
      {% endif %}
```

### 3. Prehľadná karta s viac informáciami

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-entity-card
    entity: binary_sensor.zse_hdo_145_tariff
    name: HDO 145
    icon_color: |
      {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
        green
      {% else %}
        red
      {% endif %}
    secondary_info: |
      {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'tariff_name') }}

  - type: custom:mushroom-template-card
    primary: "Ďalšie prepnutie"
    secondary: |
      {{ state_attr('sensor.zse_hdo_145_next_switch', 'time') }}
      → {{ state_attr('sensor.zse_hdo_145_next_switch', 'to_tariff_name') }}
    icon: mdi:clock-outline
    icon_color: blue

  - type: custom:mushroom-template-card
    primary: "Dnes období"
    secondary: |
      {{ states('sensor.zse_hdo_145_today_schedule') }} období
      ({{ state_attr('sensor.zse_hdo_145_today_schedule', 'day_type') }})
    icon: mdi:calendar-today
    icon_color: orange

  - type: custom:mushroom-template-card
    primary: "Zostávajúca nízka tarifa"
    secondary: |
      {{ states('sensor.zse_hdo_145_low_remaining') }} min
      (do: {{ state_attr('sensor.zse_hdo_145_low_remaining', 'period_end') }})
    icon: mdi:timer-sand
    icon_color: teal
```

### 4. Pokročilá karta s dynamickým timeline (Advanced)

**Požiadavky:**
- `custom:mushroom-template-card` (HACS: Mushroom)
- `card-mod` (HACS: card-mod)

> Voliteľné: používajte iba ak máte nainštalované oba doplnky. Baseline zostáva karta v sekcii 1.

**Features:**
- 📊 Dynamický timeline zobrazujúci tarify počas celého dňa
- 🎯 Animovaná šípka ukazujúca aktuálny čas
- 🎨 Farebné pozadie podľa aktuálnej tarify
- 🔄 Automatické spracovanie prechodov cez polnoc

```yaml
type: custom:mushroom-template-card
primary: ⚡ ZSE HDO 145
secondary: |
  Tarifa: {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'tariff_name') }}
  Nasledujúce prepnutie: {{ states('sensor.zse_hdo_145_next_switch') }}
icon: |
  {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
    mdi:flash
  {% else %}
    mdi:flash-off
  {% endif %}
icon_color: |
  {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
    green
  {% else %}
    red
  {% endif %}
tap_action:
  action: more-info
  entity: binary_sensor.zse_hdo_145_tariff
multiline_secondary: true
card_mod:
  style: |
    ha-card {
      position: relative;
      padding-bottom: 38px !important;
      /* FIX: Add isolation to contain z-index within this card */
      isolation: isolate;
      {% if is_state('binary_sensor.zse_hdo_145_tariff', 'on') %}
        background: rgba(76, 175, 80, 0.1);
        border-left: 5px solid #4CAF50;
      {% else %}
        background: rgba(244, 67, 54, 0.1);
        border-left: 5px solid #F44336;
      {% endif %}
    }
    .secondary {
      white-space: pre-line !important;
      line-height: 1.5 !important;
    }
    /* DYNAMICKÝ TIMELINE BAR */
    ha-card:after {
      {% set rozvrh = state_attr('sensor.zse_hdo_145_today_schedule', 'periods') %}
      {% if rozvrh and rozvrh | length > 0 %}
        {% set ns = namespace(parts=[], segments=[]) %}
        {% for period in rozvrh %}
          {% set start_parts = period.start.split(':') %}
          {% set end_parts = period.end.split(':') %}
          {% set start_h = start_parts[0] | int %}
          {% set start_m = start_parts[1] | int %}
          {% set end_h = end_parts[0] | int %}
          {% set end_m = end_parts[1] | int %}
          {% if start_h > end_h %}
            {% set end_pct = ((end_h + end_m/60) / 24 * 100) | round(2) %}
            {% set ns.segments = ns.segments + [{'start': 0, 'end': end_pct}] %}
            {% set start_pct = ((start_h + start_m/60) / 24 * 100) | round(2) %}
            {% set ns.segments = ns.segments + [{'start': start_pct, 'end': 100}] %}
          {% else %}
            {% set start_pct = ((start_h + start_m/60) / 24 * 100) | round(2) %}
            {% set end_pct = ((end_h + end_m/60) / 24 * 100) | round(2) %}
            {% set ns.segments = ns.segments + [{'start': start_pct, 'end': end_pct}] %}
          {% endif %}
        {% endfor %}
        {% set ns.segments = ns.segments | sort(attribute='start') %}
        {% set ns.last_end = 0 %}
        {% for segment in ns.segments %}
          {% if segment.start > ns.last_end %}
            {% set ns.parts = ns.parts + ['#f44336 ' ~ ns.last_end ~ '%', '#f44336 ' ~ segment.start ~ '%'] %}
          {% endif %}
          {% set ns.parts = ns.parts + ['#4caf50 ' ~ segment.start ~ '%', '#4caf50 ' ~ segment.end ~ '%'] %}
          {% set ns.last_end = segment.end %}
        {% endfor %}
        {% if ns.last_end < 100 %}
          {% set ns.parts = ns.parts + ['#f44336 ' ~ ns.last_end ~ '%', '#f44336 100%'] %}
        {% endif %}
        content: "";
        position: absolute;
        bottom: 8px;
        left: 16px;
        right: 16px;
        height: 12px;
        background: linear-gradient(90deg, {{ ns.parts | join(', ') }});
        border-radius: 6px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        z-index: 0;
      {% else %}
        content: "";
        position: absolute;
        bottom: 8px;
        left: 16px;
        right: 16px;
        height: 12px;
        background: #cccccc;
        border-radius: 6px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        z-index: 0;
      {% endif %}
    }
    /* ŠÍPKA ČASU */
    ha-card:before {
      {% set now_h = now().hour + now().minute / 60.0 %}
      {% set pct = (now_h / 24.0 * 100.0) | round(2) %}
      content: "▼";
      position: absolute;
      bottom: 20px;
      left: 0;
      margin-left: calc(16px + (100% - 32px) * {{ pct }} / 100);
      transform: translateX(-50%);
      color: orange;
      font-size: 18px;
      font-weight: bold;
      text-shadow: 0 0 8px rgba(0,0,0,0.9), 0 0 3px rgba(255,152,0,0.8);
      z-index: 1;
      animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }
```

**Poznámka k entitám:**
Táto karta používa entity `binary_sensor.zse_hdo_145_tariff`, `sensor.zse_hdo_145_next_switch` a `sensor.zse_hdo_145_today_schedule`. Ak máte iné ID (napr. vlastné prefixy), upravte ich podľa vašej konfigurácie.
Odporúčaná baseline teraz zahŕňa aj `sensor.zse_hdo_145_low_remaining`.

**Poznámka k času prepnutia (od v1.2.2):**
Integrácia sama aktualizuje `next_switch` na každej tarifnej hranici. Pre vlastné template senzory (napr. „Ďalšia lacná“) odporúčame počítať relatívny čas živo:

```yaml
{% set ts = as_timestamp(states('sensor.zse_hdo_145_next_switch')) %}
{% set diff = ts - as_timestamp(now()) %}
{{ state_attr('sensor.zse_hdo_145_next_switch', 'time') }}
{% if diff > 0 %}(o {{ (diff // 3600) | int }}h {{ ((diff % 3600) // 60) | int }}min){% endif %}
```

## 🤖 Automation Examples

### Blueprint pack (odporúčané pre rýchly štart)

Použi pripravené blueprinty:
- `blueprints/automation/zse_hdo_live/notify_low_tariff_on.yaml`
- `blueprints/automation/zse_hdo_live/boiler_by_tariff.yaml`
- `blueprints/automation/zse_hdo_live/reminder_before_switch.yaml`

V HA ich importuj cez **Settings -> Automations & Scenes -> Blueprints**.

### 1. Notifikácia pri prepnutí na nízku tarifu

```yaml
automation:
  - id: hdo_nizka_tarifa_on
    alias: "HDO - Nízka tarifa zapnutá"
    description: "Pošle notifikáciu keď sa zapne nízka tarifa"
    
    trigger:
      - platform: state
        entity_id: binary_sensor.zse_hdo_145_tariff
        from: "off"
        to: "on"
    
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚡ Nízka tarifa"
          message: "Zapnula sa nízka tarifa! Teraz je vhodný čas zapnúť spotrebiče."
          data:
            importance: high
            channel: HDO
            notification_icon: mdi:flash
```

### 2. Automatické zapnutie bojlera

```yaml
automation:
  - id: bojler_auto_hdo
    alias: "Bojler - Automatické riadenie HDO"
    description: "Zapína/vypína bojler podľa HDO tarify"
    
    trigger:
      - platform: state
        entity_id: binary_sensor.zse_hdo_145_tariff
    
    action:
      - choose:
          # Zapnúť pri nízkej tarife
          - conditions:
              - condition: state
                entity_id: binary_sensor.zse_hdo_145_tariff
                state: "on"
            sequence:
              - service: switch.turn_off
                target:
                  entity_id: switch.bojler
              - service: notify.persistent_notification.create
                data:
                  title: "🔥 Bojler"
                  message: "Bojler zapnutý - nízka tarifa"
          
          # Vypnúť pri vysokej tarife
          - conditions:
              - condition: state
                entity_id: binary_sensor.zse_hdo_145_tariff
                state: "off"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.bojler
              - service: notify.persistent_notification.create
                data:
                  title: "❄️ Bojler"
                  message: "Bojler vypnutý - vysoká tarifa"
```

### 3. Nabíjanie elektromobilu počas nízkej tarify

```yaml
automation:
  - id: ev_charging_hdo
    alias: "EV - Nabíjanie počas nízkej tarify"
    description: "Zapne nabíjanie elektromobilu iba počas nízkej tarify"
    
    trigger:
      - platform: state
        entity_id: binary_sensor.zse_hdo_145_tariff
        to: "on"
      
      # Overenie či je auto pripojené
      - platform: state
        entity_id: binary_sensor.ev_charger_connected
        to: "on"
    
    condition:
      - condition: and
        conditions:
          # Nízka tarifa
          - condition: state
            entity_id: binary_sensor.zse_hdo_145_tariff
            state: "on"
          
          # Auto pripojené
          - condition: state
            entity_id: binary_sensor.ev_charger_connected
            state: "on"
          
          # Batéria nie je plná
          - condition: numeric_state
            entity_id: sensor.ev_battery_level
            below: 95
    
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
      
      - service: notify.mobile_app_your_phone
        data:
          title: "🚗⚡ Nabíjanie EV"
          message: "Začalo nabíjanie počas nízkej tarify HDO"
```

### 4. Predhrev domu pred nízkou tarifou

```yaml
automation:
  - id: preheat_before_low_tariff
    alias: "Kúrenie - Predhrev 30 min pred nízkou tarifou"
    description: "Zvýši teplotu 30 minút pred zapnutím nízkej tarify"
    
    trigger:
      - platform: template
        value_template: >
          {% set next_switch = as_timestamp(states('sensor.zse_hdo_145_next_switch')) %}
          {% set now = as_timestamp(now()) %}
          {% set diff = (next_switch - now) / 60 %}
          {{ diff <= 30 and diff > 29 and 
             state_attr('sensor.zse_hdo_145_next_switch', 'to_tariff') == 'low' }}
    
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.termostat_obyvacka
        data:
          temperature: 22
      
      - service: notify.mobile_app_your_phone
        data:
          title: "🏠🔥 Predhrev"
          message: "Začal predhrev domu pred nízkou tarifou"
```

### 5. Upozornenie 15 minút pred prepnutím

```yaml
automation:
  - id: hdo_reminder_before_switch
    alias: "HDO - Upozornenie 15 min pred prepnutím"
    description: "Pripomienka 15 minút pred zmenou tarify"
    
    trigger:
      - platform: template
        value_template: >
          {% set next_switch = as_timestamp(states('sensor.zse_hdo_145_next_switch')) %}
          {% set now = as_timestamp(now()) %}
          {% set diff = (next_switch - now) / 60 %}
          {{ diff <= 15 and diff > 14 }}
    
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⏰ HDO Upozornenie"
          message: >
            O 15 minút prepnutie na 
            {{ state_attr('sensor.zse_hdo_145_next_switch', 'to_tariff_name') }} tarifu 
            ({{ state_attr('sensor.zse_hdo_145_next_switch', 'time') }})
```

### 6. Notifikácia pri zmene harmonogramu

```yaml
automation:
  - id: hdo_schedule_changed
    alias: "HDO - Zmena harmonogramu"
    description: "Upozorní keď integrácia deteguje zmenu harmonogramu na zdroji"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'schedule_changed') == true }}
    condition:
      - condition: template
        value_template: >
          {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'schedule_change_at') is not none }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🗓️ Zmena HDO harmonogramu"
          message: >
            Detegovaná zmena harmonogramu o
            {{ state_attr('binary_sensor.zse_hdo_145_tariff', 'schedule_change_at') }}
```

## 📈 Template Sensors

### 1. Čas zostávajúci do prepnutia

```yaml
template:
  - sensor:
      - name: "HDO čas do prepnutia"
        unique_id: hdo_time_until_switch
        state: >
          {% set next_switch = as_timestamp(states('sensor.zse_hdo_145_next_switch')) %}
          {% set now = as_timestamp(now()) %}
          {% set diff = (next_switch - now) / 60 %}
          {% if diff < 60 %}
            {{ diff | int }} minút
          {% else %}
            {{ (diff / 60) | round(1) }} hodín
          {% endif %}
        icon: mdi:timer-outline
```

### 2. Celkový čas nízkej tarify dnes

```yaml
template:
  - sensor:
      - name: "HDO celkový čas nízkej tarify dnes"
        unique_id: hdo_total_low_today
        unit_of_measurement: "h"
        state: >
          {% set periods = state_attr('sensor.zse_hdo_145_today_schedule', 'periods') %}
          {% set total = namespace(minutes=0) %}
          {% for period in periods %}
            {% set start_parts = period.start.split(':') %}
            {% set end_parts = period.end.split(':') %}
            {% set start_minutes = start_parts[0]|int * 60 + start_parts[1]|int %}
            {% set end_minutes = end_parts[0]|int * 60 + end_parts[1]|int %}
            {% if end_minutes < start_minutes %}
              {% set end_minutes = end_minutes + 1440 %}
            {% endif %}
            {% set total.minutes = total.minutes + (end_minutes - start_minutes) %}
          {% endfor %}
          {{ (total.minutes / 60) | round(1) }}
        icon: mdi:clock-time-eight
```

## 🎨 Conditional Cards

### Zobraz upozornenie iba počas vysokej tarify

```yaml
type: conditional
conditions:
  - entity: binary_sensor.zse_hdo_145_tariff
    state: "off"
card:
  type: markdown
  content: |
    ### 🔴 Vysoká tarifa
    
    Aktuálne je **vysoká tarifa**.
    
    Ďalšie prepnutie na nízku: 
    **{{ state_attr('sensor.zse_hdo_145_next_switch', 'time') }}**
```

## 💾 Node-RED Example

```json
[
    {
        "id": "hdo_monitor",
        "type": "server-state-changed",
        "name": "HDO Tarifa Changed",
        "server": "home_assistant",
        "entityidfilter": "binary_sensor.zse_hdo_145_tariff",
        "outputinitially": false,
        "state_type": "str",
        "wires": [["check_tariff"]]
    },
    {
        "id": "check_tariff",
        "type": "switch",
        "name": "Check Tariff",
        "property": "payload",
        "rules": [
            {
                "t": "eq",
                "v": "on",
                "vt": "str"
            },
            {
                "t": "eq",
                "v": "off",
                "vt": "str"
            }
        ],
        "wires": [["low_tariff_action"], ["high_tariff_action"]]
    }
]
```

---

**Páči sa vám táto integrácia? Dajte ⭐ na GitHube!**
