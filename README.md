# ZSE HDO Live Integration pre Home Assistant

🇸🇰 **Slovenská integrácia pre sledovanie HDO taríf ZSE v reálnom čase!**

## 🎯 Funkcie

- ✅ **Dynamické načítanie** všetkých HDO čísel priamo z www.zsdis.sk
- ✅ **Live parsing** - vždy aktuálne dáta z webu (podobne ako waste_collection_schedule)
- ✅ **Binary sensor** - aktuálna tarifa (ON = nízka, OFF = vysoká)
- ✅ **Sensor** - čas najbližšieho prepnutia
- ✅ **Sensor** - dnešný rozvrh nízkych taríf
- ✅ **Podpora všetkých 44 HDO** čísel (domácnosti aj firmy)
- ✅ **Automatické rozlíšenie** víkend/pracovný deň

## 📦 Inštalácia

### Cez HACS (odporúčané)

1. Otvorte HACS v Home Assistant
2. Kliknite na "Integrations"
3. Kliknite na "..." v pravom hornom rohu
4. Vyberte "Custom repositories"
5. Pridajte URL: `https://github.com/mburdych/zse-hdo-live`
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
  - `last_updated`: Čas poslednej aktualizácie

### 2. Sensor - Ďalšie prepnutie
- **Entity ID**: `sensor.zse_hdo_XXX_next_switch`
- **Stav**: ISO datetime najbližšieho prepnutia
- **Atribúty**:
  - `time`: Čas prepnutia (HH:MM)
  - `to_tariff`: low/high
  - `to_tariff_name`: Nízka/Vysoká
  - `meaning`: Účel (napr. "Ohrev teplej úžitkovej vody")
  - `for_rate`: Typ tarify (napr. "D3 Aktiv")

### 3. Sensor - Dnešný rozvrh
- **Entity ID**: `sensor.zse_hdo_XXX_today_schedule`
- **Stav**: Počet období nízkej tarify dnes
- **Atribúty**:
  - `day_type`: Pracovný deň/Víkend
  - `periods`: Zoznam všetkých období
  - `period_count`: Počet období

## 🔄 Automatická aktualizácia

- Integrácia **automaticky sťahuje** aktuálne dáta z www.zsdis.sk
- **Interval**: Každých 5 minút
- **Zmeny na webe** sa automaticky prejavia v Home Assistant

## 💡 Príklady použitia

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

**Páči sa vám táto integrácia? Dajte ⭐ na GitHube!**

alebo mi pošlite na kavej https://buymeacoffee.com/mburdych
