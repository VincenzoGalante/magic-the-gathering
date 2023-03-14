![](images/mtg-logo.png)

<b>TL;DR</b>: This project is analyzing MGT card data. Follow the steps mentioned under `How to make it work?` to set it up.

## What is this about?
If you have never seen the logo above, here a very quick intro: `Magic: The Gathering` (Magic or MGT) is the first collectible card game of its kind, created in 1993. It can be played be two or more players. The exact rules differ a bit by the exact format but in general: players battle against each other with their card decks, trying to defeat the other players by casting spells, artifacts and creatures. Curious? [Learn how to play...](https://magic.wizards.com/en/intro)

## What questions are we trying to answer? 
This project looks at MGT from a meta-perspective and dives into the following:
- How many cards are being released over time?
- What is the color distribution?
- What is the average amount of cards per set?
- Who are the most common illustrators? 
- What are the most expensive cards?

With a growing database, we would be able to further explore the following:
- What is the color distribution over time?
- What is the price development of cards?

## What technologies are being used?
- Cloud: [Google Cloud](https://cloud.google.com)
- Infrastructure: [Terraform](https://www.terraform.io/)
- Orchestration: [Prefect](https://www.prefect.io/)
- Data lake: [Google Cloud Storage](https://cloud.google.com/storage)
- Data transformation: [DBT](https://www.https://getdbt.com/) / [Spark](https://spark.apache.org/)
- Data warehouse: [BigQuery](https://cloud.google.com/bigquery)
- Data visualization: [Google Looker Studio](https://cloud.google.com/looker), former Data Studio

<p align="center">
<a href="https://scryfall.com/"><img src="images/lotus.png"></a>
</p>

## How to make it work?
1. Setup your Google Cloud environment
- Create a [Google Cloud Platform project](https://console.cloud.google.com/cloud-resource-manager)
- Configure Identity and Access Management (IAM) for the service account, giving it the following privileges: BigQuery Admin, Storage Admin and Storage Object Admin
- Download the JSON credentials and save it to `~/.gc/<credentials>`
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
- Download the [Terraform](https://developer.hashicorp.com/terraform/downloads) executable and add it to your `~/bin/`-directory
- Review and adjust the variables mentioned in `magic-the-gathering/terraform/variables.tf`
- To initiate, plan and apply the infrastructure run the following Terraform commands: 
```bash
terraform init
terraform plan -var="project=<your-gcp-project-id>"
terraform apply -var="project=<your-gcp-project-id>"
```
4. 

<p align="center">
<img src="images/mana_black.png">
<img src="images/mana_red.png">
<img src="images/mana_green.png">
<img src="images/mana_blue.png">
<img src="images/mana_white.png">
</p>

# To do

## Setup
- [x] Describe what MTG is
- [x] Clear problem description and clear description of the solution
- [x] Mention Scryfall, [Logo](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/a/a2/Scryfall.jpg/revision/latest/scale-to-width-down/180?cb=20221220021533)
- [x] Mention Magic: The Gathering [lotus](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/e/e6/Site-logo.png/revision/latest?cb=20210621093849) [logo](https://www.google.com/url?sa=i&url=https%3A%2F%2Fde.m.wikipedia.org%2Fwiki%2FDatei%3AMagicthegathering-logo.svg&psig=AOvVaw1ITUEgWPlwcDb6HN93f5dR&ust=1678264036225000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCKiMx--yyf0CFQAAAAAdAAAAABAE)
- [x] instructions on how to run the code
- [x] Setup terraform
- [x] Cloud development
- [x] Save [pictures](https://github.com/jupyter/notebook/issues/3278) to github repository
- [] Readme on Prefect
- [] Test on new account (Anto)

## Data ingestion
- [x] Download data from API
- [x] upload to GCS
- [x] Orcehstration with Prefect
- [x] Saving to parque directly on GCS
- [] Schedule weekly

## Lake to warehouse
- [x] From GCS to BQ

## Transformation
- [] Partitioning and clustering in dbt

## Visaulization
- [] DataStudio Dashboard
- [] How many cards are being released over time?
- [] What is the average amount of cards per set?
- [] Who are the most common illustrators? 
- [] What are the most expensive cards?

Prepare:
- [] What is the color distribution over time?
- [] What is the price development of cards?

## Extra mile
- [] ML on price forecast?
- [] Tests
- [] CI / CD pipeline
