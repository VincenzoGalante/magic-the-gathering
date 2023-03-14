from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket

# alternative to creating GCP blocks in the UI
# insert your own service_account_file path or service_account_info dictionary from the json file
# IMPORTANT - do not store credentials in a publicly available repository!

your_GCS_bucket_name = ""  # insert your GCS bucket name
GCS_credentials_block_name = "magic-the-gathering"

credentials_block = GcpCredentials(service_account_info={})
credentials_block.save(f"{GCS_credentials_block_name}", overwrite=True)

bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load(f"{GCS_credentials_block_name}"),
    bucket=f"{your_GCS_bucket_name}",
)

bucket_block.save(f"{GCS_credentials_block_name}-bucket", overwrite=True)
