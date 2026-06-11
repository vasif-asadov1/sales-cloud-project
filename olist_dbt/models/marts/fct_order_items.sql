with source as (

    select *
    from {{ ref('stg_order_items') }}

),

final as (

    select

        order_id,

        order_item_id,

        product_id,

        seller_id,

        shipping_limit_date,

        price,

        freight_value,

        price + freight_value
            as item_total_value,

        case
            when price = 0 then null
            else round((freight_value / price) * 100, 2)
        end as freight_percentage,

        case
            when freight_value = 0 then true
            else false
        end as is_free_shipping,

        case

            when freight_value < 10
                then 'Low'

            when freight_value < 25
                then 'Medium'

            else 'High'

        end as shipping_cost_category

    from source

)

select *
from final