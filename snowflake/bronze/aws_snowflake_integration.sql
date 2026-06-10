CREATE WAREHOUSE IF NOT EXISTS olist_wh
WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;


USE WAREHOUSE olist_wh;

USE DATABASE olist_db;

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

SELECT CURRENT_ACCOUNT();
SELECT CURRENT_REGION();
SHOW ORGANIZATION ACCOUNTS;




CREATE OR REPLACE STORAGE INTEGRATION olist_s3_int
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = S3
ENABLED = TRUE
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::538620445611:role/SnowflakeOlistRole'
STORAGE_ALLOWED_LOCATIONS = (
    's3://olist-dataset-vasifasadov/'
);


DESC INTEGRATION olist_s3_int;

DESC INTEGRATION olist_s3_int;

USE ROLE ACCOUNTADMIN;
USE DATABASE olist_db;
USE SCHEMA bronze;

CREATE OR REPLACE STAGE olist_stage
URL = 's3://olist-dataset-vasifasadov/'
STORAGE_INTEGRATION = olist_s3_int;


LIST @olist_stage;


CREATE OR REPLACE FILE FORMAT csv_format
TYPE = CSV
FIELD_DELIMITER = ','
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
NULL_IF = ('NULL', 'null', '')
EMPTY_FIELD_AS_NULL = TRUE;


SELECT
    $1,
    $2,
    $3,
    $4
FROM @olist_stage/olist_customers_dataset.csv
(FILE_FORMAT => csv_format)
LIMIT 5;



SELECT *
FROM TABLE(
    INFER_SCHEMA(
        LOCATION => '@olist_stage',
        FILE_FORMAT => 'csv_format'
    )
);




CREATE OR REPLACE TABLE raw_customers (
    customer_id VARCHAR,
    customer_unique_id VARCHAR,
    customer_zip_code_prefix VARCHAR,
    customer_city VARCHAR,
    customer_state VARCHAR
);


COPY INTO raw_customers
FROM (
    SELECT
        $1,
        $2,
        $3,
        $4,
        $5
    FROM @olist_stage/olist_customers_dataset.csv
)
FILE_FORMAT = (
    FORMAT_NAME = csv_format
);

SELECT COUNT(*)
FROM raw_customers;


SELECT $1,$2,$3,$4,$5,$6,$7,$8,$9
FROM @olist_stage/olist_products_dataset.csv
(FILE_FORMAT => csv_format)
LIMIT 3;
