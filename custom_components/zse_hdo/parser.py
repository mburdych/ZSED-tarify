"""
ZSE HDO Live Parser
===================

Dynamicky sťahuje a parsuje HDO dáta priamo zo ZSE webovej stránky.
"""

import re
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, time

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

# URL pre HDO dáta
ZSE_HDO_URL = "https://www.zsdis.sk/Uvod/Online-sluzby/Casy-prepinania-nizkej-a-vysokej-tarify"

# Timeout pre HTTP požiadavky
REQUEST_TIMEOUT = 30


class ZSEHDOLiveParser:
    """Parser pre live ZSE HDO dáta z webu."""

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        Initialize parser.
        
        Args:
            session: Aiohttp session (ak None, vytvorí sa nová)
        """
        self._session = session
        self._own_session = session is None
        
    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()
    
    async def fetch_page(self) -> str:
        """
        Stiahne HTML stránku zo ZSE webu.
        
        Returns:
            HTML content as string
            
        Raises:
            aiohttp.ClientError: Ak zlyhá sťahovanie
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "sk,en;q=0.5",
        }
        
        _LOGGER.debug(f"Fetching HDO data from {ZSE_HDO_URL}")
        
        if not self._session:
            self._session = aiohttp.ClientSession()
            self._own_session = True
        
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                async with self._session.get(ZSE_HDO_URL, headers=headers) as response:
                    response.raise_for_status()
                    html = await response.text()
                    _LOGGER.debug(f"Successfully fetched {len(html)} bytes")
                    return html
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to fetch HDO data: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error fetching HDO data: {err}")
            raise
    
    def _extract_javascript_array(self, html: str, var_name: str) -> List[Dict]:
        """
        Extrahuje JavaScript array z HTML (napr. var household_rates = [...];)
        
        Args:
            html: HTML content
            var_name: Názov JavaScript premennej (napr. "household_rates")
            
        Returns:
            List of dictionaries parsed from JavaScript
        """
        # Pattern pre nájdenie JavaScript array
        # Stratégia: Nájdi "var variable_name = [", potom spočítaj zátvorky
        pattern = rf"var\s+{var_name}\s*=\s*\["
        
        match = re.search(pattern, html)
        if not match:
            _LOGGER.warning(f"JavaScript variable '{var_name}' not found in HTML")
            return []
        
        # Začiatok array
        start_pos = match.end() - 1  # Pozícia prvej '['
        
        # Nájdi koniec array spočítaním zátvoriek (ale ignoruj zátvorky v stringoch)
        bracket_count = 0
        in_string = False
        string_char = None
        escaped = False
        end_pos = start_pos
        
        for i in range(start_pos, len(html)):
            char = html[i]
            
            # Handle escape sequences
            if escaped:
                escaped = False
                continue
            
            if char == '\\':
                escaped = True
                continue
            
            # Handle string boundaries
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            # Count brackets only outside strings
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break
        
        if bracket_count != 0:
            _LOGGER.error(f"Unmatched brackets in '{var_name}'")
            return []
        
        # Extrahuj array
        js_array = html[start_pos:end_pos]
        
        # Konvertovať JavaScript objekt na JSON
        result = js_array
        
        # 1. Replace single quotes with double quotes
        result = result.replace("'", '"')
        
        # 2. Quote unquoted object keys (but preserve already quoted)
        result = re.sub(r'(?<!")(\b\w+)(?=\s*:)', r'"\1"', result)
        
        # 3. Fix boolean values
        result = result.replace('true', 'true')
        result = result.replace('false', 'false')
        
        # 4. Remove trailing commas before } or ]
        result = re.sub(r',(\s*[}\]])', r'\1', result)
        
        try:
            data = json.loads(result)
            _LOGGER.debug(f"Successfully parsed {len(data)} items from '{var_name}'")
            return data
        except json.JSONDecodeError as err:
            _LOGGER.error(f"Failed to parse JavaScript array '{var_name}': {err}")
            return []
    
    def _parse_time(self, time_str: str) -> time:
        """
        Konvertuje string času na datetime.time objekt.
        
        Args:
            time_str: Čas vo formáte "HH:MM" alebo "H:MM"
            
        Returns:
            datetime.time object
        """
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)
    
    def _normalize_schedule(self, intervals: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Normalizuje rozvrh do formátu použiteľného v HA.
        
        Args:
            intervals: Raw intervals zo ZSE
            
        Returns:
            Dict with 'workday' and 'weekend' keys
        """
        schedule = {
            "workday": [],
            "weekend": []
        }
        
        for interval in intervals:
            if interval.get("t_type") != "nt":
                continue  # Preskočiť vysokú tarifu
            
            period = {
                "start": interval["t_from"],
                "end": interval["t_to"],
                "tariff": "low",
                "meaning": interval.get("meaning", ""),
                "for_rate": interval.get("for_rate", "")
            }
            
            if interval.get("weekday"):
                schedule["workday"].append(period)
            
            if interval.get("weekend"):
                schedule["weekend"].append(period)
        
        return schedule
    
    async def get_all_hdo_numbers(self) -> List[int]:
        """
        Získa zoznam všetkých dostupných HDO čísel.
        
        Returns:
            List of HDO codes (integers)
        """
        html = await self.fetch_page()
        
        household = self._extract_javascript_array(html, "household_rates")
        business = self._extract_javascript_array(html, "business_rates")
        
        all_codes = []
        all_codes.extend([item["code"] for item in household])
        all_codes.extend([item["code"] for item in business])
        
        return sorted(list(set(all_codes)))
    
    async def get_schedule(self, hdo_number: int) -> Optional[Dict]:
        """
        Získa rozvrh pre konkrétne HDO číslo.
        
        Args:
            hdo_number: HDO kód (napr. 145)
            
        Returns:
            Dict s rozvrhom alebo None ak HDO neexistuje
        """
        html = await self.fetch_page()
        
        household = self._extract_javascript_array(html, "household_rates")
        business = self._extract_javascript_array(html, "business_rates")
        
        all_rates = household + business
        
        # Debug logging
        _LOGGER.debug(f"Searching for HDO {hdo_number} (type: {type(hdo_number).__name__})")
        _LOGGER.debug(f"Available codes: {[rate['code'] for rate in all_rates[:3]]}")
        
        for rate in all_rates:
            # Convert both to int for comparison (JSON might have strings)
            rate_code = int(rate["code"]) if isinstance(rate["code"], str) else rate["code"]
            hdo_num = int(hdo_number)
            
            if rate_code == hdo_num:
                schedule = self._normalize_schedule(rate["intervals"])
                
                return {
                    "hdo_number": hdo_number,
                    "name": f"HDO {hdo_number}",
                    "category": "household" if rate in household else "business",
                    "rate_type": rate.get("for_rate", "Unknown"),  # Sadzba/tarifikácia
                    "workday": schedule["workday"],
                    "weekend": schedule["weekend"],
                    "last_updated": datetime.now().isoformat(),
                    "source": ZSE_HDO_URL
                }
        
        _LOGGER.warning(f"HDO {hdo_number} not found")
        return None
    
    async def get_all_schedules(self) -> Dict[int, Dict]:
        """
        Získa všetky HDO rozvrhy.
        
        Returns:
            Dict s HDO číslom ako kľúčom a rozvrhom ako hodnotou
        """
        html = await self.fetch_page()
        
        household = self._extract_javascript_array(html, "household_rates")
        business = self._extract_javascript_array(html, "business_rates")
        
        all_schedules = {}
        
        for rate in household + business:
            hdo_number = rate["code"]
            schedule = self._normalize_schedule(rate["intervals"])
            
            all_schedules[hdo_number] = {
                "hdo_number": hdo_number,
                "name": f"HDO {hdo_number}",
                "category": "household" if rate in household else "business",
                "workday": schedule["workday"],
                "weekend": schedule["weekend"]
            }
        
        return all_schedules
    
    async def is_low_tariff_now(self, hdo_number: int) -> Optional[bool]:
        """
        Kontroluje či je práve teraz nízka tarifa.
        
        Args:
            hdo_number: HDO kód
            
        Returns:
            True = nízka tarifa, False = vysoká tarifa, None = neznáme HDO
        """
        schedule = await self.get_schedule(hdo_number)
        if not schedule:
            return None
        
        now = datetime.now()
        current_time = now.time()
        is_weekend = now.weekday() >= 5  # 5=sobota, 6=nedeľa
        
        periods = schedule["weekend"] if is_weekend else schedule["workday"]
        
        for period in periods:
            start = self._parse_time(period["start"])
            end = self._parse_time(period["end"])
            
            # Handle midnight crossover
            if end < start:
                if current_time >= start or current_time < end:
                    return True
            else:
                if start <= current_time < end:
                    return True
        
        return False


# ==============================================
# PRÍKLAD POUŽITIA
# ==============================================

async def main():
    """Príklad použitia parsera."""
    import asyncio
    
    logging.basicConfig(level=logging.DEBUG)
    
    async with ZSEHDOLiveParser() as parser:
        print("=" * 60)
        print("🔄 LIVE ZSE HDO PARSER")
        print("=" * 60)
        
        # Získať všetky HDO čísla
        print("\n📋 Získavam zoznam všetkých HDO čísel...")
        all_hdo = await parser.get_all_hdo_numbers()
        print(f"✅ Našiel som {len(all_hdo)} HDO čísel:")
        print(f"   {all_hdo}")
        
        # Získať rozvrh pre HDO 145
        print("\n⏰ Získavam rozvrh pre HDO 145...")
        schedule = await parser.get_schedule(145)
        if schedule:
            print(f"✅ HDO 145 - {schedule['category']}")
            print(f"   Pracovné dni: {len(schedule['workday'])} periód")
            print(f"   Víkend: {len(schedule['weekend'])} periód")
            
            print("\n   Pracovné dni:")
            for period in schedule['workday']:
                print(f"      🕐 {period['start']} - {period['end']}")
        
        # Skontrolovať aktuálny stav
        print("\n🔍 Kontrolujem aktuálny stav tarify...")
        is_low = await parser.is_low_tariff_now(145)
        if is_low is not None:
            tariff_name = "NÍZKA ⚡" if is_low else "VYSOKÁ 🔴"
            print(f"   Aktuálna tarifa: {tariff_name}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
