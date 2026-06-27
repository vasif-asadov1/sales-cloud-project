# Completed Steps

I have completed the following steps in the project.

**AWS S3 and Snowflake Integration:**

1. Created S3 bucket `olist-dataset-vasifasadov` in AWS Console.
2. Created IAM role `SnowflakeOlistRole` with the least privilege principle and attached that policy `SnowflakeOlistReadOnlyPolicy` to the role.
3. Created a Snowflake stage `olist_stage` that points to the S3 bucket `olist-dataset-vasifasadov`. 
4. Created a Snowflake Warehouse `olist_wh` with minimum size and auto-suspend enabled to optimize costs.
5. Created a Snowflake database `olist_db` and medallion architecture with `Bronze`, `Silver`, and `Gold` layers - schemas to organize the data.
6. Adjusted Trust Relationship of the IAM role `SnowflakeOlistRole` to allow Snowflake to assume the role.
7. Retrieved the ARN of the IAM role `SnowflakeOlistRole` and used it to create an external stage in Snowflake.
8. Copied the External ID and AWS User ARN from the Snowflake stage creation output and used them to configure the IAM role trust relationship.
9. Tested the connection between Snowflake and S3 by executing a simple query to list files in the S3 bucket using the Snowflake stage.
10. Verified that the Snowflake stage can access the S3 bucket and read files by executing a `LIST` command in Snowflake.
11. Created a file format in Snowflake to define the structure of the data files stored in S3. As we will store the files in Bronze layer, all columns are stored as `VARCHAR` to accommodate any data type and avoid schema evolution issues.
12. Created Snowflake tables in the Bronze layer to store the raw data from S3. The table schema matches the file format defined earlier.
13. Loaded all tables from the S3 bucket into the corresponding Bronze layer tables in Snowflake using the `COPY INTO` command.
14. Verified that the data has been successfully loaded into the Bronze layer tables by executing `SELECT` queries on each table and checking the row counts and sample data.
15. Eventually, data is successfully loaded into the Bronze layer tables in Snowflake, and the integration between AWS S3 and Snowflake is complete.

**Snowflake Medallion Archictecture Implementation with dbt:**

1. Installed dbt-core and dbt-snowflake packages in the local environment. 
2. Created profiles.yml file in the `~/.dbt` directory to configure the connection to Snowflake using the credentials and connection details.
3. I created a new dbt project - folder `olist-dbt` inside the main project directory. In that folder, I initialized a new dbt project using the `dbt init` command and set up the project structure.
4. Inside the `olist-dbt` folder, I created the necessary directories and files for the dbt project, including the `models`, `macros`, `seeds` and `tests` directories.
5. I created `dbt_project.yml` file to define the project configuration, including the project name, version, and model configurations. This file also specifies the default schema for the models and the materialization strategy (e.g., table, view, incremental). As a data engineer, I have chosen to use the `table` materialization strategy for the Bronze layer models, `view` materialization strategy for the Silver layer models, and `table` materialization strategy for the Gold layer models to optimize performance and storage. 
6. The `models/staging` directory contains the SQL files that define the staging models for each table in the Bronze layer. These models are responsible for transforming the raw data from the Bronze layer into a more structured format suitable for analysis. It clears the data, renames columns, and applies any necessary transformations to prepare the data for further processing in the Silver layer. The resulted staging models are materialized as views and then sent to the Silver layer in Snowflake.
7. The `models/marts` directory contains the SQL files that define the mart models for each table in the Silver layer. These models are responsible for aggregating and summarizing the data from the staging models into a more analytical format suitable for reporting and analysis. The resulted mart models are materialized as tables and then sent to the Gold layer in Snowflake. These tables will be a single source of truth for the business users and will be used for reporting and analysis.
8. In both the staging and mart models,  I created dbt tests to validate the data quality and integrity of the models. These tests check the relations, uniqueness, and nullability of the columns in the models to ensure that the data is accurate and reliable. 
9. Besides the Medallion architecture implementation, I also created ML schema. I created the aggregated mart dataset which will be used for machine learning purposes. The dataset is created by joining the necessary tables from the Silver layer and applying any necessary transformations to prepare the data for machine learning. The resulted dataset is materialized as a table in the Gold layer in Snowflake, which will be used for training and testing machine learning models.
10. At the end, I ran the dbt models using the `dbt run` command to execute the transformations and load the data into the Silver and Gold layers in Snowflake. I also ran the dbt tests using the `dbt test` command to validate the data quality and integrity of the models. The dbt run and test commands were executed successfully, and the data was transformed and loaded into the Silver and Gold layers in Snowflake with high quality and integrity.
11. Finally, by using `dbt docs generate` and `dbt docs serve` commands, I generated and served the dbt documentation for the project. The documentation provides a comprehensive overview of the dbt models, their relationships, and the data lineage, making it easier for stakeholders to understand the data transformations and dependencies in the project. You can access the dbt documentation and see the data lineage and model relationships by visiting the following link: [dbt Documentation](http://localhost:8080) (Note: This link is accessible only when the dbt docs server is running locally).


**EDA, Data Analysis and Machine Learning in Databricks**

1. I directly created a Serverless Databricks workspace.  
2. I created a folder in the Databricks workspace to organize the project files and notebooks. The folder is named `olist_project` and contains subfolders for data, notebooks, and results. `Olist Cloud Project` is the main folder that contains all the project files and notebooks. Inside that folder, I created 3 notebooks: `01_EDA`, `02_Feature_Selection`, and `03_Machine_Learning`. Each notebook is dedicated to a specific task in the project, allowing for better organization and separation of concerns.
3. In the `01_EDA` notebook, I performed exploratory data analysis (EDA) on the dataset to understand its structure, quality, and characteristics. I used various visualization techniques and statistical methods to analyze the data and identify any patterns, trends, or anomalies. The EDA process helped me gain insights into the dataset and informed the subsequent steps in the project. I also answered the following business questions during the EDA process:
   - Do delayed deliveries reduce review scores?
   - Does shipping cost affect customer satisfaction?
   - Do expensive orders receive higher ratings?
   - Do heavier products receive lower ratings?
   - Do certain product categories receive better reviews?
   - Do some states consistently give lower ratings?
   - Does payment type affect review score?
   - Does order size affect review score?
   - Do customers receiving orders late write more negative reviews?
   - Which features appear most associated with customer satisfaction?

    Besides these, I dropped unnecessary columns, handled missing values, and performed data cleaning and preprocessing to prepare the dataset for further analysis and modeling. I stored the cleaned dataset in the Databricks catalog with the name `ml_review_prediction_dataset_clean`. 

4. In the `02_Feature_Selection` notebook, I performed Hypothesis Testing and Feature Selection to identify the most relevant features for predicting customer review scores. I used statistical tests and feature importance techniques to evaluate the significance of each feature and its impact on the target variable. Based on the results, I selected the most important features for building the machine learning model.  In order to apply all tests, I created a new column which groups the review scores into three categories: negative (1-2), neutral (3), and positive (4-5). This new column is used as the target variable for the machine learning model. For correlation analysis, I used `average_review_score` as the target variable, which is a continuous variable. For the other tests, I used the newly created categorical column as the target variable. The selected features are then used to train and evaluate the machine learning models in the next step.
5. In the `03_Machine_Learning` notebook, I built and evaluated machine learning models to predict customer review scores based on the selected features. In the EDA stage, I grouped the review scores into three categories: negative (1-2), neutral (3), and positive (4-5) to simplify the prediction task. I used various classification algorithms, including Logistic Regression, Random Forest, and XGBoost, LightGBM and CatBoost, to train the models on the cleaned dataset. I evaluated the models using metrics such as accuracy, precision, recall, and F1-score to determine their performance. After comparing the results, I selected the best-performing model for deployment and further analysis. In order to track the results of the machine learning experiments, I used MLflow to log the model parameters, metrics, and artifacts. This allowed me to keep track of the different models and their performance, making it easier to compare and select the best model for deployment. The final selected model is then saved and registered in the Databricks Model Registry for future use and deployment.


# What Next? 

I completed the above steps in Databricks inside the Browser. However, I don't like the Browser interface of Databricks. I want to use VS Code for Databricks development. From now on, if I want to do project in Databricks, I want to use VS Code or other editors instead of the Databricks browser interface. Because the browser interface is not user-friendly and is quite slow and laggy. I want to use VS Code for Databricks development because it provides a better user experience, faster performance, and more advanced features for coding and debugging. I will set up the necessary extensions and configurations in VS Code to connect to my Databricks workspace and work on the project seamlessly. This will allow me to write code, run notebooks, and manage my Databricks resources directly from VS Code, improving my productivity and workflow. I will replace the Databricks part of the project with VS Code and continue my work in a more efficient and effective manner. I want to do the following steps to set up VS Code for Databricks development:

1. Install the Databricks extension for VS Code from the Visual Studio Code Marketplace. This extension provides features such as code completion, syntax highlighting, and integration with Databricks clusters and notebooks.
2. Configure the Databricks extension in VS Code by providing the necessary authentication details, such as the Databricks workspace URL and personal access token. This will allow VS Code to connect to the Databricks workspace and access the resources.
3. I want to re-do the EDA, Feature Selection, and Machine Learning steps in VS Code using the Databricks extension. I will create new notebooks in VS Code and replicate the analysis and modeling steps that I performed in the Databricks browser interface. This will allow me to leverage the features of VS Code for a better development experience.
4. I want to do ML part from scratch in VS Code, including EDA, Feature Selection, and Machine Learning. I will use the same dataset, but this time I want to write all steps in python scripts instead of notebooks. I will create separate python scripts for each step, such as `eda.py`, `feature_selection.py`, and `machine_learning.py`. This will allow me to have a more organized and modular codebase, making it easier to maintain and update the code in the future. 

My request from you is: 

- guide me on how to set up VS Code for Databricks development, including the installation of the Databricks extension, configuration of authentication details, and any additional settings or extensions that may enhance the development experience.
- provide a step-by-step guide on how to replicate the EDA, Feature Selection, and Machine Learning steps in VS Code using the Databricks extension. Include instructions on how to create new notebooks, run code, and manage Databricks resources from VS Code.
- I want my scripts to be modular and organized. Provide guidance on how to structure the project in VS Code, including the creation of separate python scripts for each step (EDA, Feature Selection, Machine Learning) and how to manage dependencies and imports between the scripts.
- I want my scripts deploying to the Databricks cluster. Provide instructions on how to set up the deployment process, including any necessary configurations or settings in VS Code and Databricks. Include guidance on how to run the scripts on the Databricks cluster and monitor their execution.
- Provide best practices for version control and collaboration when working on the project in VS Code, including the use of Git for source control, branching strategies, and code review processes. Include guidance on how to set up a Git repository for the project and how to manage changes and updates to the codebase effectively. Currently, my project folder is initialized as a Git repository, and is connected to a remote repository on GitHub. That Github repo is on the following link: https://github.com/vasif-asadov1/sales-cloud-project


You should consider the following points while providing the guidance:
- Ensure that the guidance is clear, concise, and easy to follow, with step-by-step instructions.
- I MUST NOT EXCEED the free tier limits of Databricks while running the scripts. Provide guidance on how to optimize resource usage and avoid exceeding the free tier limits.
- In my notebooks, in the browser interface, I already had codes for EDA, Feature Selection, and Machine Learning. You can use those codes as a reference to replicate the steps in VS Code. However, you should also consider optimizing the code for better performance and resource usage to stay within the free tier limits of Databricks. I will tell you the steps, what should be done in each step, and you will provide clean instructions on how to do that in VS Code. You should also provide any necessary code snippets if I ask you.
- You should teach me how to set up the Databricks environment in any project without exceeding the free tier limits. From now on, on the all new projects, I want to make this setup by myself. Therefore, you should not only provide instructions for the current project, but also teach me how to set up the Databricks environment in any new project without exceeding the free tier limits. This includes guidance on cluster configuration, resource allocation, and best practices for optimizing performance and cost-efficiency in Databricks.
- Do your best to provide clean, professional and guided instructions for the entire process, ensuring that I can successfully set up and use VS Code for Databricks development while adhering to the free tier limits and best practices.
- In the below, I will note down the folder structure of my project in VS Code. You should consider this structure while providing guidance on how to organize the project and manage dependencies between the scripts.

Folder structure of the project in VS Code:


```bash
sales_cloud_project on  main [?] via 🐍 v3.12.3 (.venv) 
❯ tree
.
├── AI Prompt.md
├── databricks
│   └── scripts
│       ├── 1 - EDA.py
│       ├── 2 - Feature Selection.py
│       └── 3 - Machine Learning.py
├── docs
│   └── silver_layer_design.md
├── logs
│   └── dbt.log
├── olist_dbt
│   ├── analyses
│   ├── dbt_packages
│   ├── dbt_project.yml
│   ├── logs
│   │   └── dbt.log
│   ├── macros
│   │   └── generate_schema_name.sql
│   ├── models
│   │   ├── marts
│   │   │   ├── dim_customers.sql
│   │   │   ├── dim_date.sql
│   │   │   ├── dim_products.sql
│   │   │   ├── dim_sellers.sql
│   │   │   ├── fct_order_items.sql
│   │   │   ├── fct_orders.sql
│   │   │   └── marts.yml
│   │   └── staging
│   │       ├── sources.yml
│   │       ├── staging.yml
│   │       ├── stg_customers.sql
│   │       ├── stg_geolocation.sql
│   │       ├── stg_order_items.sql
│   │       ├── stg_order_payments.sql
│   │       ├── stg_order_reviews.sql
│   │       ├── stg_orders.sql
│   │       ├── stg_product_category_translation.sql
│   │       ├── stg_products.sql
│   │       └── stg_sellers.sql
│   ├── README.md
│   ├── seeds
│   ├── snapshots
│   ├── target
│   │   ├── catalog.json
│   │   ├── compiled
│   │   │   └── olist_dbt
│   │   │       └── models
│   │   │           ├── marts
│   │   │           │   ├── dim_customers.sql
│   │   │           │   ├── dim_date.sql
│   │   │           │   ├── dim_products.sql
│   │   │           │   ├── dim_sellers.sql
│   │   │           │   ├── fct_order_items.sql
│   │   │           │   ├── fct_orders.sql
│   │   │           │   └── marts.yml
│   │   │           │       ├── not_null_dim_customers_customer_id.sql
│   │   │           │       ├── not_null_dim_date_date_id.sql
│   │   │           │       ├── not_null_dim_date_date.sql
│   │   │           │       ├── not_null_dim_products_product_id.sql
│   │   │           │       ├── not_null_dim_sellers_seller_id.sql
│   │   │           │       ├── not_null_fct_order_items_order_id.sql
│   │   │           │       ├── not_null_fct_order_items_order_item_id.sql
│   │   │           │       ├── not_null_fct_order_items_product_id.sql
│   │   │           │       ├── not_null_fct_order_items_seller_id.sql
│   │   │           │       ├── not_null_fct_orders_customer_id.sql
│   │   │           │       ├── not_null_fct_orders_order_id.sql
│   │   │           │       ├── relationships_fct_order_items_6605ef9332585c82f278ac817835eb79.sql
│   │   │           │       ├── relationships_fct_orders_0c6c6d9e6f30dfb9b653557ebf38e47c.sql
│   │   │           │       ├── unique_dim_customers_customer_id.sql
│   │   │           │       ├── unique_dim_date_date_id.sql
│   │   │           │       ├── unique_dim_date_date.sql
│   │   │           │       ├── unique_dim_products_product_id.sql
│   │   │           │       ├── unique_dim_sellers_seller_id.sql
│   │   │           │       └── unique_fct_orders_order_id.sql
│   │   │           └── staging
│   │   │               ├── staging.yml
│   │   │               │   ├── not_null_stg_customers_customer_id.sql
│   │   │               │   ├── not_null_stg_order_items_order_id.sql
│   │   │               │   ├── not_null_stg_order_items_product_id.sql
│   │   │               │   ├── not_null_stg_order_items_seller_id.sql
│   │   │               │   ├── not_null_stg_orders_customer_id.sql
│   │   │               │   ├── not_null_stg_orders_order_id.sql
│   │   │               │   ├── not_null_stg_products_product_id.sql
│   │   │               │   ├── not_null_stg_sellers_seller_id.sql
│   │   │               │   ├── relationships_stg_order_items_7e2e810dab2dfa777551ed7db1b8bb77.sql
│   │   │               │   ├── relationships_stg_order_items_85fcc371bcae46211ede4a7fca07283f.sql
│   │   │               │   ├── relationships_stg_order_items_b3d7cdbd08ebfad01e3226c01c10bba0.sql
│   │   │               │   ├── relationships_stg_orders_96411fe0c89b49c3f4da955dfd358ba0.sql
│   │   │               │   ├── unique_stg_customers_customer_id.sql
│   │   │               │   ├── unique_stg_orders_order_id.sql
│   │   │               │   ├── unique_stg_products_product_id.sql
│   │   │               │   └── unique_stg_sellers_seller_id.sql
│   │   │               ├── stg_customers.sql
│   │   │               ├── stg_geolocation.sql
│   │   │               ├── stg_order_items.sql
│   │   │               ├── stg_order_payments.sql
│   │   │               ├── stg_order_reviews.sql
│   │   │               ├── stg_orders.sql
│   │   │               ├── stg_product_category_translation.sql
│   │   │               ├── stg_products.sql
│   │   │               └── stg_sellers.sql
│   │   ├── graph.gpickle
│   │   ├── graph_summary.json
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── partial_parse.msgpack
│   │   ├── run_results.json
│   │   └── semantic_manifest.json
│   └── tests
├── README.md
├── requirements.txt
├── scripts
│   ├── create_s3_bucket.py
│   └── import_data.py
└── snowflake
    └── bronze
        ├── aws_snowflake_integration.sql
        ├── create_bronze_tables.sql
        └── load_bronze_tables.sql

27 directories, 93 files

sales_cloud_project on  main [?] via 🐍 v3.12.3 (.venv) 
❯ 
```

I have set the .venv virtual environment for the project. I have installed all the necessary packages in the virtual environment, including `dbt-core`, `dbt-snowflake`, and any other dependencies required for the project. The `requirements.txt` file contains a list of all the packages and their versions that are installed in the virtual environment. This allows for easy replication of the environment on other machines or by other team members.

Below, I will send the `ml_review_prediction_dataset`. This is stored inside the Gold layer in Snowflake. However, I downloaded it in my local, it is also available in Databricks catelog as `ml_review_prediction_dataset`. We should do EDA, cleaning, feature selection, and machine learning on this dataset. After EDA and cleaning, we will store the cleaned dataset in Databricks catalog as `ml_review_prediction_dataset_clean`. This cleaned dataset will be used for feature selection and machine learning. The dataset contains the following columns and data types:

```
#   Column                                   Non-Null Count  Dtype         
---  ------                                   --------------  -----         
 0   ORDER_ID                                 99441 non-null  object        
 1   CUSTOMER_ID                              99441 non-null  object        
 2   ORDER_STATUS                             99441 non-null  object        
 3   ORDER_PURCHASE_TIMESTAMP                 99441 non-null  datetime64[ns]
 4   ORDER_APPROVED_AT                        99281 non-null  datetime64[ns]
 5   ORDER_DELIVERED_CARRIER_DATE             97658 non-null  datetime64[ns]
 6   ORDER_DELIVERED_CUSTOMER_DATE            96476 non-null  datetime64[ns]
 7   ORDER_ESTIMATED_DELIVERY_DATE            99441 non-null  datetime64[ns]
 8   IS_LATE_ORDER                            99441 non-null  int64         
 9   ORDER_APPROVAL_EFFICIENCY_HOURS          99281 non-null  float64       
 10  ORDER_DELIVERY_EFFICIENCY_DAYS           96462 non-null  float64       
 11  ORDER_SHIPPING_DAYS                      96475 non-null  float64       
 12  DELIVERY_DELAYED_DAYS                    96476 non-null  float64       
 13  CUSTOMER_CITY                            99441 non-null  object        
 14  CUSTOMER_STATE                           99441 non-null  object        
 15  CUSTOMER_LAT                             99123 non-null  float64       
 16  CUSTOMER_LNG                             99123 non-null  float64       
 17  TOTAL_PRODUCTS                           98666 non-null  float64       
 18  TOTAL_ORDER_VOLUME                       98666 non-null  float64       
 19  TOTAL_SELLERS                            98666 non-null  float64       
 20  TOTAL_ORDER_VALUE                        98666 non-null  float64       
 21  ORDER_SHIPPING_COST                      98666 non-null  float64       
 22  TOTAL_ORDER_REVENUE                      98666 non-null  float64       
 23  AVERAGE_ITEM_VALUE                       98666 non-null  float64       
 24  PAYMENT_COUNT                            99440 non-null  float64       
 25  TOTAL_PAYMENT_INSTALLMENTS               99440 non-null  float64       
 26  PAYMENT_TYPE                             99440 non-null  object        
 27  TOTAL_PAYMENT_VALUE                      99440 non-null  float64       
 28  PAYMENT_DIFFERENCE                       98665 non-null  float64       
 29  DISTINCT_PRODUCT_CATEGORIES              98666 non-null  float64       
 30  DOMINANT_PRODUCT_CATEGORY_ENGLISH        97252 non-null  object        
 31  MOST_EXPENSIVE_PRODUCT_CATEGORY_ENGLISH  97234 non-null  object        
 32  AVG_PRODUCT_WEIGHT_G                     98650 non-null  float64       
 33  MAX_PRODUCT_WEIGHT_G                     98650 non-null  float64       
 34  AVG_PRODUCT_VOLUME_CM3                   98650 non-null  float64       
 35  MAX_PRODUCT_VOLUME_CM3                   98650 non-null  float64       
 36  AVG_PRODUCT_DENSITY_G_CM3                98650 non-null  float64       
 37  AVG_PRODUCT_PHOTOS_QTY                   97277 non-null  float64       
 38  MAX_PRODUCT_PHOTOS_QTY                   97277 non-null  float64       
 39  HEAVY_PRODUCT_RATIO                      98666 non-null  float64       
 40  LARGE_PRODUCT_RATIO                      98666 non-null  float64       
 41  OVERSIZED_PRODUCT_RATIO                  98666 non-null  float64       
 42  ORDER_YEAR                               99441 non-null  int64         
 43  ORDER_SEMESTER                           99441 non-null  int64         
 44  ORDER_QUARTER                            99441 non-null  int64         
 45  ORDER_MONTH_NUMBER                       99441 non-null  int64         
 46  ORDER_SEASON                             99441 non-null  object        
 47  ORDER_DAY_OF_WEEK                        99441 non-null  int64         
 48  ORDER_DAY_OF_MONTH                       99441 non-null  int64         
 49  ORDER_DAY_OF_YEAR                        99441 non-null  int64         
 50  AVERAGE_REVIEW_SCORE                     98673 non-null  float64       
dtypes: datetime64[ns](5), float64(29), int64(8), object(9)
memory usage: 38.7+ MB
```

