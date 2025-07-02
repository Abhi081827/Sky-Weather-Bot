# tools/openweathermap_query.py
import os
from datetime import datetime, timezone
from typing import Optional, Type

import requests
from pydantic import BaseModel, Field
from requests.adapters import HTTPAdapter, Retry

from langchain.tools import BaseTool

from prompts import CURRENT_TEMPLATE, FUTURE_TEMPLATE

class OpenWeatherMapInput(BaseModel):
    city: str = Field(..., description="City name (e.g. 'London').")
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="Optional country code.")
    state:   Optional[str] = Field(None, min_length=2, max_length=2, description="Optional US state code.")

class OpenWeatherMapQuery(BaseTool):
    name: str = "OpenWeatherMap"
    description: str = "Fetch current + 5-day/3h forecast for a city, optionally with country/state."
    args_schema: Type[OpenWeatherMapInput] = OpenWeatherMapInput
    return_direct: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not self._key:
            raise ValueError("Missing OPENWEATHERMAP_API_KEY")
        sess = requests.Session()
        sess.mount("https://", HTTPAdapter(max_retries=Retry(3, backoff_factor=0.3)))
        self._session = sess

    def _handle(self, resp: requests.Response):
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 401:
            raise RuntimeError("401 Unauthorized: check your API key")
        raise RuntimeError(f"Error {resp.status_code}: {resp.text}")

    def _get_location(self, city, country, state):
        q = ",".join([city] + ([state] if country=="US" and state else []) + ([country] if country else []))
        data = self._handle(self._session.get(
            "http://api.openweathermap.org/geo/1.0/direct",
            params={"q":q,"limit":1,"appid":self._key}, timeout=5
        ))
        if not data:
            raise RuntimeError(f"No location found for '{q}'")
        return data[0]

    def _fmt_ts(self, ts):
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%A %Y-%m-%d %H:%M")

    def _run(self, city: str, country: Optional[str] = None, state: Optional[str] = None, **_):
        loc  = self._get_location(city, country, state)
        lat, lon = loc["lat"], loc["lon"]

        curr = self._handle(self._session.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat":lat,"lon":lon,"units":"metric","appid":self._key}, timeout=5
        ))
        fcst = self._handle(self._session.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"lat":lat,"lon":lon,"units":"metric","appid":self._key}, timeout=5
        ))

        current_str = CURRENT_TEMPLATE.format(
            location=f"{loc['name']}, {loc['country']}",
            time=self._fmt_ts(curr["dt"]),
            temp=curr["main"]["temp"],
            humidity=curr["main"]["humidity"],
            clouds=curr["clouds"]["all"],
            wind_speed=curr["wind"]["speed"],
            weather=curr["weather"][0]["description"],
        )
        forecasts = []
        for entry in fcst["list"][:5]:
            forecasts.append(
                FUTURE_TEMPLATE.format(
                    date=self._fmt_ts(entry["dt"]),
                    temp=entry["main"]["temp"],
                    weather=entry["weather"][0]["description"],
                )
            )
        return current_str + "\n####\n" + "\n####\n".join(forecasts)

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported for this tool")
