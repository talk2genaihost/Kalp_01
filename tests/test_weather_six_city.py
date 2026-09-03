from development_studio.weather_six_city import WeatherRecord, fetch_six_city_weather, flash_weather


def test_requires_exactly_six_cities():
    try:
        fetch_six_city_weather(("Delhi",))
    except ValueError as exc:
        assert "Exactly six cities" in str(exc)
    else:
        raise AssertionError("Expected six-city validation")


def test_flash_contains_city_and_six_days():
    records = [
        WeatherRecord("Delhi", "India", f"2026-09-0{i}", 35, 25, 20, 1)
        for i in range(1, 7)
    ]
    output = flash_weather(records)
    assert "KALP WEATHER FLASH | 6 CITIES × 6 DAYS" in output
    assert "Delhi, India" in output
    assert output.count("2026-09-0") == 6
