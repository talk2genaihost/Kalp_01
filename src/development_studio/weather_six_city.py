"""Small six-city, six-day weather demo tool."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

DEFAULT_CITIES = ("Delhi", "London", "New York", "Tokyo", "Cairo", "Sydney")

@dataclass(frozen=True)
class WeatherRecord:
    city: str
    country: str
    date: str
    temperature_max_c: float | None
    temperature_min_c: float | None
    precipitation_probability_max_pct: int | None
    weather_code: int | None
    local_time: str
    timezone: str

def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "KALP-weather-demo/1.0"})
    with urlopen(request, timeout=10) as response:
        return json.load(response)

def _geocode(city: str) -> tuple[float, float, str, str, str]:
    url = ("https://geocoding-api.open-meteo.com/v1/search?"
           f"name={quote(city)}&count=1&language=en&format=json")
    results = (_get_json(url).get("results") or [])
    if not results:
        raise ValueError(f"City not found: {city}")
    result = results[0]
    return (float(result["latitude"]), float(result["longitude"]),
            result.get("name", city), result.get("country", ""),
            result.get("timezone", "UTC"))

def fetch_six_city_weather(cities: tuple[str, ...] = DEFAULT_CITIES) -> list[WeatherRecord]:
    """Return six days of forecast records for exactly six cities."""
    if len(cities) != 6:
        raise ValueError("Exactly six cities are required for this demo.")
    records: list[WeatherRecord] = []
    for city in cities:
        latitude, longitude, resolved_city, country, timezone = _geocode(city)
        url = ("https://api.open-meteo.com/v1/forecast?"
               f"latitude={latitude}&longitude={longitude}"
               "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
               "precipitation_probability_max&forecast_days=6&timezone=auto")
        daily = _get_json(url).get("daily", {})
        dates = daily.get("time", [])
        highs = daily.get("temperature_2m_max", [])
        lows = daily.get("temperature_2m_min", [])
        rain = daily.get("precipitation_probability_max", [])
        codes = daily.get("weather_code", [])
        local_time = datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M:%S")
        for index, date in enumerate(dates[:6]):
            records.append(WeatherRecord(
                city=resolved_city, country=country, date=date,
                temperature_max_c=highs[index] if index < len(highs) else None,
                temperature_min_c=lows[index] if index < len(lows) else None,
                precipitation_probability_max_pct=rain[index] if index < len(rain) else None,
                weather_code=codes[index] if index < len(codes) else None,
                local_time=local_time, timezone=timezone))
    return records

def flash_weather(records: list[WeatherRecord]) -> str:
    """Render a compact six-city weather flash with each city's local time."""
    grouped: dict[str, list[WeatherRecord]] = {}
    for record in records:
        grouped.setdefault(record.city, []).append(record)
    lines = ["KALP WEATHER FLASH | 6 CITIES × 6 DAYS"]
    for city, city_records in grouped.items():
        first = city_records[0]
        lines.append(f"\n{city}, {first.country} | LOCAL TIME: {first.local_time} | {first.timezone}")
        for record in city_records:
            high = "—" if record.temperature_max_c is None else f"{record.temperature_max_c:.0f}°C"
            low = "—" if record.temperature_min_c is None else f"{record.temperature_min_c:.0f}°C"
            rain = "—" if record.precipitation_probability_max_pct is None else f"{record.precipitation_probability_max_pct}% rain"
            lines.append(f"  {record.date}: {low}–{high}, {rain}, code {record.weather_code}")
    return "\n".join(lines)

def records_as_json(records: list[WeatherRecord]) -> str:
    return json.dumps([asdict(record) for record in records], indent=2)
