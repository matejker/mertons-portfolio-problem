import httpx
import configparser
import pandas as pd

from typing import Optional, TypedDict

ALPHAVANTAGE_URL = "https://www.alphavantage.co"


__all__ = [
    "AlphaVantageException",
    "AuthenticationError",
    "MissingDataError",
    "AlphaVantageResponse",
    "AlphaVantage",
    "ALPHAVANTAGE_URL",
]


class AlphaVantageException(Exception):
    pass


class AuthenticationError(AlphaVantageException):
    pass


class MissingDataError(AlphaVantageException):
    pass


class AlphaVantageResponse(TypedDict):
    pass


class AlphaVantage:
    def __init__(self, url: str = ALPHAVANTAGE_URL, token: Optional[str] = None) -> None:
        if token:
            self.token: str = token.upper()
        else:
            config = configparser.ConfigParser()
            config.read("config.ini")
            self.token = config.get("alphavantage", "access_token").upper()

        self.url: str = url.rstrip("/")

    @staticmethod
    def raise_for_status(resp: httpx.Response) -> None:
        if resp.status_code == 403:
            raise AuthenticationError(403, "Authentication failed to the AlphaVantage service", resp.text)
        elif resp.status_code == 404:
            raise MissingDataError(404, "Failed to get Strava data", resp.text)
        if resp.status_code >= 400:
            raise AlphaVantageException(resp.status_code, "Failed to get AlphaVantage data", resp.text)

    @staticmethod
    def convert_to_pandas(resp: httpx.Response, header: bool = True):
        rows = resp.text.rstrip("\r\n").split("\r\n")
        if header:
            return pd.DataFrame([sub.split(",") for sub in rows[1:]], columns=rows[0].split(","))
        else:
            return pd.DataFrame([sub.split(",") for sub in rows])

    async def get_time_series_daily(
        self, symbol: str, full: bool = False, csv_format: bool = False
    ) -> AlphaVantageResponse:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": "full" if full else "compact",
            "datatype": "csv" if csv_format else "json",
            "apikey": self.token,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/query", params=params)

        self.raise_for_status(resp)

        return self.convert_to_pandas(resp) if csv_format else resp.json()

    async def get_crypto_time_series_daily(
        self, symbol: str, full: bool = False, csv_format: bool = False, market: str = "GBP"
    ) -> AlphaVantageResponse:
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol.upper(),
            "market": market.upper(),
            "outputsize": "full" if full else "compact",
            "datatype": "csv" if csv_format else "json",
            "apikey": self.token,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/query", params=params)

        self.raise_for_status(resp)

        return self.convert_to_pandas(resp) if csv_format else resp.json()
