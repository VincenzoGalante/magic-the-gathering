import requests
import pandas as pd
from glom import glom
from pathlib import Path
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket


@task(log_prints=True, name="Fetch Cards", retries=3)
def fetch_cards(url: str) -> pd.DataFrame:
    """Fetches the API and returns the latest card data as a pandas dataframe"""
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        json = response.json()["download_uri"]
        update = response.json()["updated_at"]
        df = pd.read_json(json)
        print("Successfully fetched data from API.")
        return df, update
    else:
        print(f"[ERROR] {response.status_code}")


@task(log_prints=True, name="Select columns and enforce data type")
def enforce_col_types(df: pd.DataFrame) -> pd.DataFrame:
    """Selects the columns we want to keep and enforces the correct data types"""
    df["name"] = df["name"].astype("string")
    df["released_at"] = pd.to_datetime(df["released_at"])

    df["colors"] = df["colors"].astype("string")
    # df["colors"] = df["colors"].apply(", ".join)

    df["color_identity"] = df["color_identity"].astype("string")
    df["set_name"] = df["set_name"].astype("string")
    df["artist"] = df["artist"].astype("string")

    euro_prices = df["prices"].apply(lambda row: glom(row, "eur", default=None))
    df["prices"] = euro_prices.astype(float)

    df = df[
        [
            "name",
            "released_at",
            "colors",
            "color_identity",
            "set_name",
            "artist",
            "prices",
        ]
    ]
    print("Successfully selected columns and enforced data types.")
    return df


@task(log_prints=True, name="Write to local parquet")
def write_to_local_parquet(df: pd.DataFrame, update: str) -> Path:
    """Writes the dataframe to a local parquet file"""
    path = Path(__file__).parent.parent
    local_path = Path(f"{path}/pq/oracle_{update}.parquet")
    df.to_parquet(local_path, compression="gzip")
    print(f"Successfully wrote to local parquet: {local_path}")
    return local_path


def write_to_gcs(local_path: str, update: str) -> None:
    """Writes a local parquet file to GCS"""
    gcs_path = Path(f"pq/oracle_{update}.parquet")
    gcp_cloud = GcsBucket.load("magic-the-gathering-bucket")
    gcp_cloud.upload_from_path(from_path=local_path, to_path=gcs_path)
    return


@flow(log_prints=True, name="[Magic: The Gathering] API to Cloud Storage")
def api_to_gcs_orchestration() -> None:
    """Orchestrates the flow of the API to Google Cloud Storage Bucket pipeline"""

    oracle_url = f"https://api.scryfall.com/bulk-data/oracle-cards"
    json, update = fetch_cards(oracle_url)
    selected_columns = enforce_col_types(json)
    parquet = write_to_local_parquet(selected_columns, update)
    write_to_gcs(parquet, update)


if __name__ == "__main__":
    api_to_gcs_orchestration()
