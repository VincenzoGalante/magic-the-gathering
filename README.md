![](https://upload.wikimedia.org/wikipedia/commons/3/3f/Magicthegathering-logo.svg)

## What is this about?
In case you have never seen the logo display above, here a very quick intro: Magic: The Gathering (Magic or MGT) is the first collecteble card game of its kind, created in 1993. It can be played be two or more players. The rules differ by the exact played format but in general mostly players battle against each other with their card decks, trying to defeat the other players by casting spells, ar tefacts and creatures. 

## What problem are we trying to solve?
This project takes a deeper look at MGT and tries to answer some fundamental questions every player and collector might encounter at a certain point in her / his career, when trying to understand more about the game from a meta perspective. 

Question of these kind are tricky to answer as most (online) information available are focused on individual cards or decks only. This project should support understanding of, but not limited to, the following:

- What is the (average) price development of MGT cards?
- What is the color distribution over time?

## How to make the project work?
1. Create a [Google Cloud Platform project](https://console.cloud.google.com/cloud-resource-manager) 
2. Configure Identity and Access Management (IAM) for the service account, giving it the following privileges: BigQuery Admin and Storage Object Admin
3. Download the JSON credentials and save it to `~/.gc/<credentials>`
4. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk), let the [environment variable point to your GCP key](https://cloud.google.com/docs/authentication/application-default-credentials#GAC), and refresh the session token by logging in to GCP.
5. 

<center><a href="https://scryfall.com/"><img src="https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/e/e6/Site-logo.png/revision/latest?cb=20210621093849"></a></center>

## To do
- [x] Describe what MTG is
- [X] Clear problem description and clear description of the solution
- [x] Mention Scryfall, [Logo](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/a/a2/Scryfall.jpg/revision/latest/scale-to-width-down/180?cb=20221220021533)
- [x] Mention Magic: The Gathering [lotus](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/e/e6/Site-logo.png/revision/latest?cb=20210621093849) [logo](https://www.google.com/url?sa=i&url=https%3A%2F%2Fde.m.wikipedia.org%2Fwiki%2FDatei%3AMagicthegathering-logo.svg&psig=AOvVaw1ITUEgWPlwcDb6HN93f5dR&ust=1678264036225000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCKiMx--yyf0CFQAAAAAdAAAAABAE)

- [] Setup terraform
- [] Cloud development

- [] Data ingestion orchestration with Prefect
- [] Uploading data to GCS
- [] Pull data weekly

- [] From GCS to BQ
- [] BigQuery: Partitioning and clustering 

- [] DBT or Spark for transforming data

- [] DataStudio Dashboard
- [] Price development of top 10 most expensive cards of color / deck choosen by user
- [] Color distribution of all cards
- [] amount of cards per color / overall over time

- [] instructions on how to run the code

## Extra mile to do
- [] ML on price forecast?
- [] Tests
- [] CI / CD pipeline