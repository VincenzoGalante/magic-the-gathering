{{ config(materialized='table') }}

with default_cards as (
    select *
    from {{ source('staging','default_cards')}}
    where id is not null
)

select
    cast(id as str) as id,
    cast(name as str) as name,
    cast(released_at as timestamp) as released_at,
    cast(color_identity as str) as color_identity,
    cast(set_name as str) as set_name,
    cast(artist as str) as artist,
    cast(prices as integer) as price,
    cast(data_update as timestamp) as data_update,
    {{get_color_category('color_identity')}} as color_category
from default_cards

-- dbt build --m dbt_mtg.sql --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}