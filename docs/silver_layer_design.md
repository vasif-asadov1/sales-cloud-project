# Silver Layer Design

## RAW_CUSTOMERS

- customer_id: Unique identifier for each customer. Different for each order even the customers are same. used to build relations with orders. Primary Key. 
- customer_unique_id: unique identifier for each customer. Will be used to find RFM, Retention and so on. 
- customer_zip_code_prefix:  varchar 
- customer_city: varchar
- customer_state: varchar


## RAW_GEOLOCATION

- geolocation_zip_code_prefix: varchar
- geolocation_lat: float
- geolocation_lng: float
- geolocation_city: varchar
- geolocation_state: varchar


## RAW_ORDERS

- order_id: Unique identifier for each order. Primary Key 
- customer_id: Unique identifier for each customer. Foreign Key to RAW_CUSTOMERS
- order_status: varchar
- order_purchase_timestamp: timestamp
- order_approved_at: timestamp
- order_delivered_carrier_date: timestamp
- order_delivered_customer_date: timestamp
- order_estimated_delivery_date: timestamp 


## RAW_ORDER_ITEMS

- order_id: Unique identifier for each order. Foreign Key to RAW_ORDERS
- order_item_id: Unique identifier for each item in an order. Primary Key
- product_id: Unique identifier for each product. Foreign Key to RAW_PRODUCTS
- seller_id: Unique identifier for each seller. Foreign Key to RAW_SELLERS
- shipping_limit_date: timestamp
- price: float
- freight_value: float 


## RAW_ORDER_PAYMENTS

- order_id: Unique identifier for each order. Foreign Key to RAW_ORDERS
- payment_type: varchar
- payment_installments: int
- payment_value: float

## RAW_ORDER_REVIEWS

- REVIEW_ID: Unique identifier for each review. Primary Key
- order_id: Unique identifier for each order. Foreign Key to RAW_ORDERS
- review_score: float
- review_comment_title: varchar
- review_comment_message: varchar
- review_creation_date: timestamp
- review_answer_timestamp: timestamp


## RAW_PRODUCTS

- PRODUCT_ID - Unique identifier for each product. Primary Key
- PRODUCT_CATEGORY_NAME - varchar
- PRODUCT_NAME_LENGHT - drop it 
- PRODUCT_DESCRIPTION_LENGHT - drop it
- PRODUCT_PHOTOS_QTY - int 
- PRODUCT_WEIGHT_G - float
- PRODUCT_LENGTH_CM - float
- PRODUCT_HEIGHT_CM - float
- PRODUCT_WIDTH_CM - float
- PRODUCT_CATEGORY_NAME - varchar
- PRODUCT_CATEGORY_NAME_ENGLISH - varchar


## RAW_SELLERS

- SELLER_ID - Unique identifier for each seller. Primary Key
- SELLER_ZIP_CODE_PREFIX - varchar
- SELLER_CITY - varchar
- SELLER_STATE - varchar