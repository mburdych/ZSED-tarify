# Príklady použitia ZSE HDO Live

## 📊 Lovelace Dashboard Examples

### 1. Základná karta s entitami

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
```

### 2. Mushroom Card (odporúčané)

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
```

## 🤖 Automation Examples

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
              - service: switch.turn_on
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
