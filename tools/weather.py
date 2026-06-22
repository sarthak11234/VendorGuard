"""
VendorGuard - Weather Risk Tool
Integrates with OpenWeatherMap API to fetch forecasts and calculate weather-related risk scores.
"""

import httpx
from typing import Any, Dict


async def get_weather_risk(city: str, api_key: str) -> Dict[str, Any]:
    """Fetches weather forecast for a city and calculates a risk score (0-30).

    If API key is missing or request fails, falls back gracefully.
    """
    # 1. Graceful Fallback if API key is not configured
    if not api_key:
        # Pre-seeded mock risks for test vendors
        if city.lower() == "raipur":
            return {
                "score": 28.0,
                "evidence": f"Mock Weather Alert: Heavy monsoon warning and potential flooding in {city} (Pre-seeded fallback).",
                "url": "https://openweathermap.org/city/1258980",
            }
        elif city.lower() == "hubli":
            return {
                "score": 25.0,
                "evidence": f"Mock Weather Alert: Heavy monsoon and severe waterlogging forecast in {city} (Pre-seeded fallback).",
                "url": "https://openweathermap.org/city/1270101",
            }
        elif city.lower() == "nagpur":
            return {
                "score": 18.0,
                "evidence": f"Mock Weather Alert: Moderate to heavy rain causing transport delays in {city} (Pre-seeded fallback).",
                "url": "https://openweathermap.org/city/1262180",
            }
        return {
            "score": 5.0,
            "evidence": f"No severe weather warnings for {city} (Mock fallback).",
            "url": "https://openweathermap.org",
        }

    # 2. Call OpenWeatherMap API
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": f"{city},IN",
        "appid": api_key,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"Weather Tool Warning: API returned status {response.status_code} for {city}. Using mock fallback.")
                return await get_weather_risk(city, "")

            data = response.json()
            
            # Weather risk scoring logic:
            # We look through the list of 3-hour forecasts (up to 40 items = 5 days)
            # Find the most severe condition and weight by proximity (earlier forecast = higher risk)
            max_score = 5.0
            evidence = f"No severe weather forecast for {city} over the next 5 days."
            citation_url = f"https://openweathermap.org/city/{data.get('city', {}).get('id', '')}"

            for idx, forecast in enumerate(data.get("list", [])):
                weather_info = forecast.get("weather", [{}])[0]
                weather_id = weather_info.get("id", 800)
                main_desc = weather_info.get("main", "").lower()
                desc = weather_info.get("description", "").lower()
                dt_txt = forecast.get("dt_txt", "")

                # Score based on Weather Condition Code (OpenWeatherMap standard IDs)
                # 2xx: Thunderstorm
                # 5xx: Rain (502-504 are heavy/extreme rain, 522-524 are heavy shower rain)
                # 7xx: Atmosphere (781 is tornado)
                # 9xx: Extreme (900-906 severe weather, cyclone, hurricane)
                base_score = 0
                condition = ""
                
                if weather_id == 781 or (900 <= weather_id <= 906):
                    base_score = 30.0
                    condition = "Tornado/Cyclone warning"
                elif weather_id in [502, 503, 504, 522, 524]:
                    base_score = 25.0
                    condition = "Severe/Heavy rainfall forecast"
                elif 200 <= weather_id < 300:
                    base_score = 20.0
                    condition = "Thunderstorm alert"
                elif 500 <= weather_id < 600:
                    base_score = 15.0
                    condition = "Moderate rain forecast"
                elif main_desc == "clouds" or main_desc == "clear":
                    base_score = 5.0
                    condition = "Clear/Overcast skies"

                # Apply proximity discount multiplier:
                # First 24 hours (first 8 forecasts): multiplier = 1.0
                # Next 48 hours (next 16 forecasts): multiplier = 0.7
                # Remaining 48 hours (next 16 forecasts): multiplier = 0.4
                if idx < 8:
                    multiplier = 1.0
                elif idx < 24:
                    multiplier = 0.7
                else:
                    multiplier = 0.4

                weighted_score = base_score * multiplier
                if weighted_score > max_score:
                    max_score = weighted_score
                    evidence = f"{condition} ({desc}) forecast for {dt_txt} in {city}."

            return {
                "score": round(max_score, 1),
                "evidence": evidence,
                "url": citation_url,
            }

    except Exception as e:
        print(f"Weather Tool Warning: Failed to fetch weather for {city} due to exception: {e}. Using mock fallback.")
        return await get_weather_risk(city, "")
