with orders as (

    select *
    from {{ ref('stg_orders') }}

),

customers as (

    select *
    from {{ ref('dim_customers') }}

),

order_items_agg as (

    select

        order_id,

        count(*) as total_order_volume,

        count(distinct product_id) as total_products,

        sum(price) as total_order_value,

        sum(freight_value) as order_shipping_cost,

        sum(item_total_value) as total_order_revenue,

        avg(price) as average_item_value

    from {{ ref('fct_order_items') }}

    group by order_id

),

payments_agg as (

    select

        order_id,

        sum(payment_value) as total_payment_value,

        sum(payment_installments) as total_payment_installments,

        count(*) as payment_count

    from {{ ref('stg_order_payments') }}

    group by order_id

),

reviews_agg as (

    select

        order_id,

        count(*) as total_reviews,

        avg(review_score) as average_review_score,

        max(
            case
                when review_comment_message is not null
                     and trim(review_comment_message) <> ''
                then 1
                else 0
            end
        ) as is_comment_written,

        avg(
            datediff(
                day,
                review_creation_date,
                review_answer_timestamp
            )
        ) as average_review_response_days

    from {{ ref('stg_order_reviews') }}

    group by order_id

),

final as (

    select

        o.order_id,

        o.customer_id,

        o.order_status,

        o.order_purchase_timestamp,

        o.order_approved_at,

        o.order_delivered_carrier_date,

        o.order_delivered_customer_date,

        o.order_estimated_delivery_date,

        /* Delivery KPIs */

        datediff(
            day,
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date
        ) as total_shipping_days,

        datediff(
            day,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) as total_delivery_days,

        datediff(
            day,
            o.order_purchase_timestamp,
            o.order_approved_at
        ) as approval_efficiency_days,

        datediff(
            day,
            o.order_approved_at,
            o.order_delivered_customer_date
        ) as delivery_efficiency_days,

        /* Order Item Metrics */

        oi.total_products,

        oi.total_order_volume,

        oi.total_order_value,

        oi.order_shipping_cost,

        oi.total_order_revenue,

        oi.average_item_value,

        /* Payment Metrics */

        p.total_payment_value,

        p.total_payment_installments,

        p.payment_count,

        /* Review Metrics */

        r.total_reviews,

        round(r.average_review_score, 2) as average_review_score,

        r.is_comment_written,

        round(r.average_review_response_days, 2)
            as average_review_response_days,

        /* Customer Attributes */

        c.customer_city,

        c.customer_state

    from orders o

    left join order_items_agg oi
        on o.order_id = oi.order_id

    left join payments_agg p
        on o.order_id = p.order_id

    left join reviews_agg r
        on o.order_id = r.order_id

    left join customers c
        on o.customer_id = c.customer_id

)

select *
from final