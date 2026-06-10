USE DATABASE olist_db;
USE SCHEMA bronze;

COPY INTO raw_customers
FROM (
SELECT $1,$2,$3,$4,$5
FROM @olist_stage/olist_customers_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_geolocation
FROM (
SELECT $1,$2,$3,$4,$5
FROM @olist_stage/olist_geolocation_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_orders
FROM (
SELECT $1,$2,$3,$4,$5,$6,$7,$8
FROM @olist_stage/olist_orders_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_order_items
FROM (
SELECT $1,$2,$3,$4,$5,$6,$7
FROM @olist_stage/olist_order_items_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_order_payments
FROM (
SELECT $1,$2,$3,$4,$5
FROM @olist_stage/olist_order_payments_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_order_reviews
FROM (
SELECT $1,$2,$3,$4,$5,$6,$7
FROM @olist_stage/olist_order_reviews_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_products
FROM (
SELECT $1,$2,$3,$4,$5,$6,$7,$8,$9
FROM @olist_stage/olist_products_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_sellers
FROM (
SELECT $1,$2,$3,$4
FROM @olist_stage/olist_sellers_dataset.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);

COPY INTO raw_product_category_translation
FROM (
SELECT $1,$2
FROM @olist_stage/product_category_name_translation.csv
)
FILE_FORMAT=(FORMAT_NAME=csv_format);
