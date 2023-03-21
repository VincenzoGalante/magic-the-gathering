{{ 
    config(
        materialized='table',
        unique_key="primary_key",
        partition_by={
            "field": "released_at",
            "data_type": "timestamp",
            "granularity": "day",
        },
        cluster_by="color_category",
    ) 
}}

with default_cards as (
    select *
    from {{ source('staging','default_cards')}}
    where card_id is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['card_id', 'released_at', 'data_update']) }} as primary_key,
    cast(card_id as string) as card_id,
    cast(name as string) as name,
    cast(released_at as timestamp) as released_at,
    cast(color_identity as string) as color_identity,
    {{get_color_category('color_identity')}} as color_category,
    cast(set_name as string) as set_name,
    cast(artist as string) as artist,
    cast(price as integer) as price,
    cast(data_update as timestamp) as data_update
from default_cards
where data_update = (
    select distinct data_update
    from default_cards
    order by data_update DESC
    limit 1
)

-- dbt build --select dbt_mtg_latest_data.sql --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}