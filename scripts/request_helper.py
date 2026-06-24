import requests, json, os, time
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

token = os.getenv("API_KEY")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

_api_cache = {}
_CACHE_TTL_SECONDS = 30


def _normaliseEndpoint(endpoint):
    return endpoint.strip().strip("/")


def _safeJSON(response):
    try:
        return response.json()
    except ValueError:
        return {}


def getData(endpoint, useCache=True, forceRefresh=False, ttl=_CACHE_TTL_SECONDS):
    key = _normaliseEndpoint(endpoint)
    now = time.time()

    if useCache and not forceRefresh:
        cached = _api_cache.get(key)
        if cached and (now - cached["timestamp"]) < ttl:
            return cached["response"]

    r = requests.get(
        f"http://localhost:8000/api/v1/{endpoint}",
        headers = headers
    )

    if useCache:
        _api_cache[key] = {
            "response": r,
            "timestamp": now,
        }

    return r


def invalidateCache(*endpoints):
    for endpoint in endpoints:
        _api_cache.pop(_normaliseEndpoint(endpoint), None)


def postData(endpoint, data, invalidateAfter=None):
    p = requests.post(
        f"http://localhost:8000/api/v1/{endpoint}",
        headers = headers,
        data = json.dumps(data)
    )

    try:
        p.raise_for_status()
    except requests.HTTPError:
        print(f"[{'\033[31m'}FAIL{'\033[0m'}]: Failed to create object with status {p.status_code}.")
        print(_safeJSON(p), "\n")

        return p

    payload = _safeJSON(p)
    if payload.get("status") == "error":
        print(f"[{'\033[31m'}FAIL{'\033[0m'}]: Failed to create object with status {p.status_code}.")
        print(payload, "\n")
    else:
        print(f"[{'\033[32m'}OK{'\033[0m'}]: Created object with status {p.status_code}.\n")

    if invalidateAfter:
        invalidateCache(*invalidateAfter)

    return p


def patchData(endpoint, assetID, data, invalidateAfter=None):
    p = requests.patch(
        f"http://localhost:8000/api/v1/{endpoint}/{assetID}",
        headers = headers,
        data = json.dumps(data)
    )

    try:
        p.raise_for_status()
    except requests.HTTPError:
        print(f"[{'\033[31m'}FAIL{'\033[0m'}]: Failed to update object with status {p.status_code}.")
        print(_safeJSON(p), "\n")

        return p

    payload = _safeJSON(p)
    if payload.get("status") == "error":
        print(f"[{'\033[31m'}FAIL{'\033[0m'}]: Failed to update object with status {p.status_code}.")
        print(payload, "\n")
    else:
        print(f"[{'\033[32m'}OK{'\033[0m'}]: Updated object with status {p.status_code}.\n")

    if invalidateAfter:
        invalidateCache(*invalidateAfter)

    return p