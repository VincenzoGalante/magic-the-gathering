import requests
from datetime import datetime


def fetch_api(url: str) -> dict:
    """
    Calls the Scryfall API and returns the updated_at timestamp and the card dictionary as a tuple.
    """
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        return response.content["updated_at"]
    else:
        print(f"[ERROR] {response.status_code}")


if __name__ == "__main__":
    format = "file"  # file or json
    oracle_url = f"https://api.scryfall.com/bulk-data/oracle-cards?format={format}"
    print(fetch_api(oracle_url))
