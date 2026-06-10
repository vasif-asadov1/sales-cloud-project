select
    product_category_name,
    product_category_name_english
    
from {{ source('bronze', 'raw_product_category_translation') }}