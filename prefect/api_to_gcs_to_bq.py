import os
import requests
import pandas as pd
import datetime as dt
from glom import glom
from pathlib import Path
from prefect import task, flow
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket

gcp_cloud = GcsBucket.load("magic-the-gathering-bucket")


@task(log_prints=True, name="Fetch Cards", retries=3)
def fetch_cards(url: str) -> pd.DataFrame:
    """Fetches the API and returns the latest card data as a pandas dataframe"""
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        json = response.json()["download_uri"]
        update = response.json()["updated_at"]
        update = update[0:10]
        df = pd.read_json(json).fillna("")
        print("Successfully fetched data from API.")
        return df, update
    else:
        print(f"[ERROR] {response.status_code}")


@task(log_prints=True, name="Write to Google Cloud Storage in parquet-format")
def write_to_gcs(df: pd.DataFrame, update: str, dataset: str) -> None:
    """Writes the dataframe to a GCS bucket as a parquet file"""
    df = df.astype(str)
    gcp_cloud.upload_from_dataframe(
        df=df,
        to_path=f"pq/{dataset}_{update}.parquet",
        serialization_format="parquet_snappy",
    )
    return


@task(log_prints=True, name="Get parquet from Google Cloud Storage")
def get_df_from_gcs(update: str, dataset: str) -> None:
    """Gets the parquet file from GCS and returns the path to the file"""
    parent_path = Path(__file__).parent.parent
    from_file_path = f"pq/{dataset}_{update}.parquet.snappy"
    folder_path = f"{parent_path}"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    to_file_path = f"{parent_path}/pq/{dataset}_{update}.parquet.snappy"
    gcp_cloud.get_directory(from_path=from_file_path, local_path=folder_path)
    return Path(to_file_path)


def concatenate(string: str) -> str:
    """Converts a string to a comma separated string"""
    try:
        code = eval(string)
        code = ", ".join(code)
        return code
    except (NameError, SyntaxError):
        return string


@task(log_prints=True, name="Select columns and enforce data type")
def transform_df(path: str, update_ts: str) -> pd.DataFrame:
    """Selects the columns we want to keep and enforces the correct data types"""

    df = pd.read_parquet(path)

    df["id"] = df["id"].astype("string")
    df["name"] = df["name"].astype("string")
    df["released_at"] = pd.to_datetime(df["released_at"])

    df["colors"] = df["colors"].apply(concatenate)
    df["color_identity"] = df["color_identity"].apply(concatenate)

    df["set_name"] = df["set_name"].astype("string")
    df["artist"] = df["artist"].astype("string")

    euro_prices = df["prices"].apply(lambda row: glom(row, "eur", default=None))
    df["prices"] = euro_prices.astype(float)

    year = int(update_ts[0:4])
    month = int(update_ts[5:7])
    day = int(update_ts[8:10])
    date = dt.date(year, month, day)
    df["data_update"] = date

    df = df[
        [
            "id",
            "name",
            "released_at",
            "colors",
            "color_identity",
            "set_name",
            "artist",
            "prices",
            "data_update",
        ]
    ]
    print("Successfully selected columns and enforced data types.")
    return df


def write_to_bq(df: pd.DataFrame) -> None:
    """Writes the dataframe to a BigQuery table"""
    gcp_credentials_block = GcpCredentials.load("magic-the-gathering")

    df.to_gbq(
        destination_table="mtg_card_data.default_cards",
        project_id="dtc-mtg-final-project",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=10000,
        if_exists="append",
    )
    print("Successfully uploaded data to BigQuery.")
    return


@flow(log_prints=True, name="[Magic: The Gathering] API to Cloud Storage")
def api_to_gcs_orchestration(dataset: str, first_time: bool = False) -> None:
    """Orchestrates the flow of the API to Google Cloud Storage Bucket pipeline"""

    api = f"https://api.scryfall.com/bulk-data/{dataset}"
    api_df, update_ts = fetch_cards(api)
    write_to_gcs(api_df, update_ts, dataset)
    print(f"Uploaded {len(api_df)} rows to GCS.")

    gcs_df = get_df_from_gcs(update_ts, dataset)
    transformed_df = transform_df(gcs_df, update_ts)

    if first_time == True:
        transformed_df.to_parquet("../pq/sample_for_bq.parquet")
        print(
            "Created sample parquet to be used in BigQuery table creation as a source."
        )
    else:
        write_to_bq(transformed_df)
        print(f"Uploaded {len(transformed_df)} rows to BigQuery.")


if __name__ == "__main__":
    oracle_dataset = "oracle_cards"  # one entry in db per card, multiple printings of the same card are unified
    default_dataset = "default_cards"  # one entry in db per printed card
    first_time = False  # if set to true, a sample parquet file will be created for BigQuery table creation
    api_to_gcs_orchestration(default_dataset, first_time)
