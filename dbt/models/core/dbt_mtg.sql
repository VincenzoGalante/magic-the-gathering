{{ config(materialized='table') }}

with default_cards as (
    select *
    from {{ source('staging','default_cards')}}
    where card_id is not null
)

select
    {{ dbt_utils.surrogate_key(['card_id', 'released_at']) }} as primary_key,
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

-- dbt build --m dbt_mtg.sql --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}