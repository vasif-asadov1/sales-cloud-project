with products as (

    select *
    from {{ ref('stg_products') }}

),

translations as (

    select *
    from {{ ref('stg_product_category_translation') }}

),

final as (

    select

        p.product_id,

        p.product_category_name,

        t.product_category_name_english,

        p.product_photos_qty,

        p.product_weight_g,

        p.product_length_cm,

        p.product_height_cm,

        p.product_width_cm,

        /* Volume */

        p.product_length_cm
        * p.product_height_cm
        * p.product_width_cm
        as product_volume_cm3,

        /* Density */

        case
            when p.product_length_cm
                 * p.product_height_cm
                 * p.product_width_cm = 0
            then null

            else
                p.product_weight_g
                /
                (
                    p.product_length_cm
                    * p.product_height_cm
                    * p.product_width_cm
                )
        end as product_density_g_cm3,

        /* Dimension Category */

        case

            when (
                p.product_length_cm
                * p.product_height_cm
                * p.product_width_cm
            ) < 1000

                then 'Small'

            when (
                p.product_length_cm
                * p.product_height_cm
                * p.product_width_cm
            ) < 10000

                then 'Medium'

            else 'Large'

        end as product_dimension_category,

        /* Weight Category */

        case

            when p.product_weight_g < 500
                then 'Light'

            when p.product_weight_g < 2000
                then 'Medium'

            else 'Heavy'

        end as product_weight_category,

        /* Logistics Class */

        case

            when p.product_weight_g < 500
                 and (
                     p.product_length_cm
                     * p.product_height_cm
                     * p.product_width_cm
                 ) < 1000
                then 'Small Parcel'

            when p.product_weight_g < 2000
                 and (
                     p.product_length_cm
                     * p.product_height_cm
                     * p.product_width_cm
                 ) < 10000
                then 'Medium Parcel'

            when p.product_weight_g < 5000
                then 'Large Parcel'

            else 'Oversized'

        end as shipping_size_class

    from products p

    left join translations t
        on p.product_category_name = t.product_category_name

)

select *
from final