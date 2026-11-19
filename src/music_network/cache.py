"""
Jack K
This module implements API caching
"""

import requests
import json
from pathlib import Path
from typing import Any


def make_cached_call(
    url: str, arg: str, token: str, params: dict[str, str] = {}
) -> dict[str, Any]:
    """
    Takes in a url, a formatting argument for the url, and an auth token
    as strings. Can additionally recieve additional params. Returns either
    JSON from a GET request to a given URL, or a local cached copy.
    """
    url = url.format(arg)

    qstr = ""

    for param in params.keys():
        value = params[param]
        qstr += f"{param}{value}"

    cache_path = Path(f"cache/{url.split("v1/")[1]}{qstr}.json")

    headers = {"Authorization": f"Bearer {token}"}

    if cache_path.exists():
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w+") as f:
            print(f"Loading {url} from Spotify!")
            resp = requests.get(url=url, headers=headers, params=params)

            if resp.status_code != 200:
                print(f"Error {resp.status_code}: {resp.reason} on {url}")
                return {
                    "Status Code": resp.status_code,
                    "Reason": resp.reason,
                    "URL": url,
                }

            data = resp.json()
            json.dump(data, f)

            return data
