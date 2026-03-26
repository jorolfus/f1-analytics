import functools
from typing import TypedDict
import asyncio
from app.database.models import Driver


import httpx

base_url = "https://api.openf1.org/v1"


def with_async_client(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with httpx.AsyncClient() as client:
            return await func(*args, _client=client, **kwargs)

    return wrapper


async def safe_get(_client: httpx.AsyncClient, url: str, params=None):
    while True:
        response = await _client.get(url, params=params)

        if response.status_code == 429:
            print("Zu viele Anfragen → warte 1 Sekunde...")
            await asyncio.sleep(1)
            continue

        response.raise_for_status()
        return response


@with_async_client
async def get_session(
    year: int, country_name: str, _client: httpx.AsyncClient
) -> int | None:

    response = await safe_get(
        _client,
        f"{base_url}/sessions",
        params={"year": year},
    )

    sessions = response.json()

    def norm(s: str) -> str:
        return s.lower().strip()

    for s in sessions:
        # DEBUG
        print("SESSION:", s)

        if (
            norm(s.get("country_name", "")) == norm(country_name)
            and norm(s.get("session_name", "")) == "race"
        ):
            return int(s["session_key"])

    return None


@with_async_client
async def get_drivers(
    session_key: int, _client: httpx.AsyncClient
) -> dict[str, dict[int, list[str, str]] | dict[str, list[int, str]]]:
    response = await safe_get(
        _client,
        f"{base_url}/drivers",
        params={"session_key": session_key},
    )
    response.raise_for_status()

    drivers = response.json()

    driver_values_after_number: dict[int, list[str, str]] = {}
    driver_values_after_name: dict[str, list[int, str]] = {}

    for d in drivers:
        driver_list_for_number_dict: list[str, str] = []
        driver_list_for_name_dict: list[int, str] = []
        driver_name = d["full_name"]
        driver_number = int(d["driver_number"])
        team_name = d["team_name"]

        driver_list_for_number_dict.append(driver_name)
        driver_list_for_number_dict.append(team_name)
        driver_list_for_name_dict.append(driver_number)
        driver_list_for_name_dict.append(team_name)

        driver_values_after_number[driver_number] = driver_list_for_number_dict
        driver_values_after_name[driver_name.lower()] = driver_list_for_name_dict

    return {
        "number": driver_values_after_number,
        "name": driver_values_after_name,
    }


@with_async_client
async def get_lap_times_from_driver(
    year: int, country_name: str, driver_name: str, _client: httpx.AsyncClient
) -> Driver:
    session_key = await get_session(year, country_name)
    if session_key is None:
        raise ValueError("Keine passende Session gefunden.")

    drivers_in_session = await get_drivers(session_key)

    name_to_number = drivers_in_session["name"]

    driver_name_key = driver_name.lower()
    if driver_name_key not in name_to_number:
        raise ValueError(f"Fahrer '{driver_name}' nicht in der Session gefunden.")

    driver_number = name_to_number[driver_name_key][0]
    team_name = name_to_number[driver_name_key][1]

    response = await safe_get(
        _client,
        f"{base_url}/laps",
        params={"session_key": session_key, "driver_number": driver_number},
    )
    response.raise_for_status()

    laps = {}
    for lap in response.json():
        time = lap["lap_duration"]
        if time is None:
            continue
        lap_time = format_lap_time(time)
        laps[lap["lap_number"]] = lap_time

    driver = Driver(
        name=driver_name_key,
        team=team_name,
        laps=laps,
        year=year,
        country_name=country_name,
    )

    return driver


def format_lap_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"
