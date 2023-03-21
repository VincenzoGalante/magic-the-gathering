import os
import requests
import pandas as pd
import datetime as dt
from pathlib import Path
from prefect import task, flow
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_dbt.cli import DbtCoreOperation, DbtCliProfile


@task(log_prints=True, name="Fetch Cards", retries=3)
def fetch_cards(url: str) -> pd.DataFrame:
    """Fetches the API and returns the latest card data as a pandas dataframe"""
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        json = response.json()["download_uri"]
        update_ts = response.json()["updated_at"]
        update_ts = update_ts[0:10]
        df = pd.read_json(json).fillna("")
        print("Successfully fetched data from API.")
        return df, update_ts
    else:
        print(f"[ERROR] {response.status_code}.")


@task(log_prints=True, name="Write to Google Cloud Storage in parquet-format")
def write_to_gcs(
    df: pd.DataFrame, update: str, dataset: str, gcp_cloud: object
) -> None:
    """Writes the dataframe to a GCS bucket as a parquet file"""
    df = df.astype(str)
    gcp_cloud.upload_from_dataframe(
        df=df,
        to_path=f"pq/{dataset}_{update}.parquet",
        serialization_format="parquet_snappy",
    )
    return


@task(log_prints=True, name="Get parquet from Google Cloud Storage")
def get_df_from_gcs(update: str, dataset: str, gcp_cloud: object) -> None:
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


def select_currency(string: str) -> str:
    """Selects the usd price from the prices column"""
    try:
        code = eval(string)
        code = code["usd"]
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
    df["color_identity"] = df["color_identity"].apply(concatenate)
    df["set_name"] = df["set_name"].astype("string")
    df["artist"] = df["artist"].astype("string")
    euro_prices = df["prices"].apply(select_currency)
    df["prices"] = euro_prices.astype(float)

    year = int(update_ts[0:4])
    month = int(update_ts[5:7])
    day = int(update_ts[8:10])
    date = dt.datetime(year, month, day)
    df["data_update"] = date

    df = df[
        [
            "id",
            "name",
            "released_at",
            "color_identity",
            "set_name",
            "artist",
            "prices",
            "data_update",
        ]
    ]

    df.rename(columns={"id": "card_id", "prices": "price"}, inplace=True)

    print("Successfully selected columns and enforced data types.")
    return df


@task(log_prints=True, name="Write to BigQuery")
def write_to_bq(df: pd.DataFrame) -> None:
    """Writes the dataframe to a BigQuery table"""
    gcp_credentials_block = GcpCredentials.load("magic-the-gathering")

    df.to_gbq(
        destination_table="mtg_card_data_raw.default_cards",
        project_id="dtc-mtg-final-project",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=10000,
        if_exists="append",
    )
    print("Successfully uploaded data to BigQuery.")
    return


@task(log_prints=True, name="Runs dbt to transform the data and derive columns")
def trigger_dbt_flow() -> object:
    """Triggers the dbt dependency and build commands"""

    dbt_cli_profile = DbtCliProfile.load("mtg-dbt-cli-profile")

    with DbtCoreOperation(
        commands=["dbt deps", "dbt build --var 'is_test_run: false'"],
        project_dir="~/magic-the-gathering/dbt/",
        profiles_dir="~/magic-the-gathering/dbt/",
        # dbt_cli_profile=dbt_cli_profile, # comment out if dbt asks for a dbt_cli_profile
    ) as dbt_operation:
        dbt_process = dbt_operation.trigger()
        dbt_process.wait_for_completion()
        result = dbt_process.fetch_result()
    return result


@flow(log_prints=True, name="[Magic: The Gathering] API to BigQuery")
def api_to_bq_orchestration(
    dataset: str, download_parquet: bool = False, update_prod_table: bool = True
) -> None:
    """Orchestrates the flow of the API to BigQuery via Google Cloud Storage"""

    gcp_cloud = GcsBucket.load("magic-the-gathering-bucket")
    api = f"https://api.scryfall.com/bulk-data/{dataset}"

    api_df, update_ts = fetch_cards(api)
    write_to_gcs(api_df, update_ts, dataset, gcp_cloud)
    print(f"Uploaded {len(api_df)} rows to GCS.")

    try:
        gcs_df = get_df_from_gcs(update_ts, dataset, gcp_cloud)
        transformed_df = transform_df(gcs_df, update_ts)

        if download_parquet == True:
            transformed_df.to_parquet("magic-the-gathering/pq/sample_for_bq.parquet")
            print(f"Downloaded {len(transformed_df)} rows and saved into a parquet.")
        else:
            write_to_bq(transformed_df)
            print(f"Uploaded {len(transformed_df)} rows to BigQuery.")
            if update_prod_table == True:
                trigger_dbt_flow()
                print("Successfully updated the production table.")
    except FileNotFoundError:
        print("[ERROR] Parquet file for transformation not found in GCS.")
    except (SyntaxError, NameError):
        print("[ERROR] Invalid code syntax and/or variable not found.")


if __name__ == "__main__":
    oracle_dataset = "oracle_cards"  # one entry in db per card, multiple printings of the same card are unified
    default_dataset = "default_cards"  # one entry in db per printed card
    download_parquet = False  # if set to true, a sample parquet file will be downloaded to the local pq directory
    update_prod_table = True  # if set to true, the production table will be updated
    api_to_bq_orchestration(default_dataset, download_parquet, update_prod_table)
