from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket

# This is an alternative to creating GCP blocks in the UI
# (1) insert your own GCS bucket name
# (2) insert your own service_account_file path or service_account_info dictionary from the json file
# IMPORTANT - do not store credentials in a publicly available repository!

your_GCS_bucket_name = ""  # (1) insert your GCS bucket name
GCS_credentials_block_name = "magic-the-gathering"

credentials_block = GcpCredentials(
    service_account_info={}  # (2) enter your credentials info here
)

credentials_block.save(f"{GCS_credentials_block_name}", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load(f"{GCS_credentials_block_name}"),
    bucket=f"{your_GCS_bucket_name}",
)

bucket_block.save(f"{GCS_credentials_block_name}-bucket", overwrite=True)
