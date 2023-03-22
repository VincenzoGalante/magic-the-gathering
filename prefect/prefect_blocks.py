from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation

# This is an alternative to creating GCP blocks in the UI
# (1) insert your own GCS bucket name
# (2) insert your own service_account_file path or service_account_info dictionary from the json file
# IMPORTANT - do not store credentials in a publicly available repository!

your_GCS_bucket_name = ""  # (1) insert your GCS bucket name
gcs_credentials_block_name = "magic-the-gathering"

credentials_block = GcpCredentials(
    service_account_info={}  # (2) enter your credentials info here
)

credentials_block.save(f"{gcs_credentials_block_name}", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load(f"{gcs_credentials_block_name}"),
    bucket=f"{your_GCS_bucket_name}",
)

bucket_block.save(f"{gcs_credentials_block_name}-bucket", overwrite=True)


credentials = GcpCredentials.load(gcs_credentials_block_name)
target_configs = BigQueryTargetConfigs(
    schema="mtg_card_data_dbt",
    credentials=credentials,
)
target_configs.save("mtg-dbt-target-config", overwrite=True)

dbt_cli_profile = DbtCliProfile(
    name="mtg-dbt-cli-profile",
    target="dev",
    target_configs=target_configs,
)
dbt_cli_profile.save("mtg-dbt-cli-profile", overwrite=True)
