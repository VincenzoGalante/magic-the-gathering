![](images/mtg-logo.png)

<b>TL;DR</b>: This project is analyzing MTG card data. Follow the steps mentioned under `How to make it work?` to set it up.

## What is this about?
If you have never seen the logo above, here a very quick intro: `Magic: The Gathering` (Magic or MTG) is the first collectible card game of its kind, created in 1993. It can be played by two or more players. The exact rules differ a bit by the format played but in general: players battle against each other with their card decks, trying to defeat the other players by casting spells, artifacts and creatures. Curious? [Learn how to play...](https://magic.wizards.com/en/intro)

<p align="center">
<img src="images/magic_cards.png" width="400">
</p>

With this project I aim to built an end-to-end orchestrated data pipeline. I am calling the [Scryfall API](https://scryfall.com/) to get a complete export of the latest card information available, and save the data to my Google Cloud Storage. Afterwards, I filter the data on the needed columns, enforce a data type and push it to BigQuery. In there, I use DBT to derive new columns and make sure that only the most up-to-date dataset is used for visualization in the dashboard.

## What questions am I trying to answer? 
As this project looks at MTG from a meta-perspective we are diving into the following:
1. How many cards are being released over time?
2. What is the color distribution?
3. Which set has the highest count of cards?
4. Who are the most common artists? 
5. What are the most expensive cards?

## What technologies are being used?
- Cloud: `Google Cloud`
- Infrastructure: `Terraform`
- Orchestration: `Prefect`
- Data lake: `Google Cloud Storage`
- Data transformation: `DBT`
- Data warehouse: `BigQuery`
- Data visualization: `Google Looker Studio`

## Dashboard example
[Click here](https://lookerstudio.google.com/u/0/reporting/ebdf68e1-27f7-435b-8add-a4018681f801/page/BkBJD) to see my Looker dashboard.

<p align="left">
<img src="images/looker_dashboard_example.gif" width="600">
<img src="images/full_wizard.png" height="400">
</p>

## What is the structure of the production table?
| Column | Description | 
|--------|-------------|
| primary_key | Unique surrogate key from card_id and released_at data points |
| card_id | Card ID in database, IDs can be repeated due to reprintings |
| name | The name of this card |
| released_at | The date this card was first released |
| color_identity | This card’s color identity |
| color_category | Based on the color_identity: Black, Blue, White, Green, Red, Colorless or Mixed |
| set_name | This card’s full set name |
| artist | The name of the illustrator of this card face |
| price | Price information of this card in US Dollar |
| data_update | Timestamp when the data was updated in the database |

- Here the dbt lineage graph <img src="images/dbt_lineage.png" width="400">
- Partitioned on the `released_at` column - in favor of question 1 and 3 - assuming that in most cases, cards with the same release date are from the same set
- Clustered on the `color_category` column - in favor of question 2 - assuming that within one set the number of colors is lower than the numbers of unique prices and artists

<p align="center">
<img src="images/lotus.png">
</p>

## How to make it work?
1. Setup your Google Cloud environment
- Create a [Google Cloud Platform project](https://console.cloud.google.com/cloud-resource-manager)
- Configure Identity and Access Management (IAM) for the service account, giving it the following privileges: BigQuery Admin, Storage Admin and Storage Object Admin
- Download the JSON credentials and save it, e.g. to `~/.gc/<credentials>`
- Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk)
- Let the [environment variable point to your GCP key](https://cloud.google.com/docs/authentication/application-default-credentials#GAC), authenticate it and refresh the session token
```bash
export GOOGLE_APPLICATION_CREDENTIALS=<path_to_your_credentials>.json
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default login
```
2. Install all required dependencies into your environment
```bash
pip install -r requirements.txt
```
3. Setup your infrastructure
- Assuming you are using Linux AMD64 run the following commands to install Terraform - if you are using a different OS please choose the correct version [here](https://developer.hashicorp.com/terraform/downloads) and exchange the download link and zip file name

```bash
sudo apt-get install unzip
cd ~/bin
wget https://releases.hashicorp.com/terraform/1.4.1/terraform_1.4.1_linux_amd64.zip
unzip terraform_1.4.1_linux_amd64.zip
rm terraform_1.4.1_linux_amd64.zip
```
- To initiate, plan and apply the infrastructure, adjust and run the following Terraform commands
```bash
cd terraform/
terraform init
terraform plan -var="project=<your-gcp-project-id>"
terraform apply -var="project=<your-gcp-project-id>"
```
4. Setup your orchestration
- If you do not have a prefect workspace, sign-up for the prefect cloud and create a workspace [here](https://app.prefect.cloud/auth/login)
- Create the [prefect blocks](https://docs.prefect.io/concepts/blocks/) via the cloud UI or adjust the variables in `/prefect/prefect_blocks.py` and run
```bash
python magic-the-gathering/prefect/prefect_blocks.py
```
- Adjust the keyfile location at `dbt/profiles.yml` to the path of your Google Cloud credentials JSON
- To execute the flow, run the following commands in two different CL terminals
```bash
prefect agent start -q 'default'
```
```bash
python prefect/api_to_gcs_to_bq.py
```
5. Data deep dive
- The data will be available in BigQuery at `mtg_card_data_dbt.dbt_mtg_latest_data` 
- Query the data in-place or build a dashboard

<p align="center">
<img src="images/mana_black.png">
<img src="images/mana_red.png">
<img src="images/mana_green.png">
<img src="images/mana_blue.png">
<img src="images/mana_white.png">
</p>

## Potential next steps
With a growing database, I would be able to further explore the following:
- What is the color distribution over time?
- What is the price development of specific cards / colors / sets over time?

<p align="center">
<img src="images/black_wizard.png" height="300">
</p>
