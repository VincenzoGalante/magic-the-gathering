{#
    This macro returns the color category in line with one of the following groups: Black, White, Blue, Red, Green, Mixed, Colorless
#}

{% macro get_color_category(color_identity) -%}

    case {{ color_identity }}
        when 'B' then 'Black'
        when 'U' then 'Blue'
        when 'W' then 'White'
        when 'G' then 'Green'
        when 'R' then 'Red'
        when '' then 'Colorless'
        else 'Mixed'
    end
{%- endmacro%}