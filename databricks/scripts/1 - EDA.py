# Databricks notebook source
# MAGIC %md
# MAGIC # Import Data



# We will use Databricks Connect to connect to the Databricks cluster and run Spark code from this local script. Make sure you have set up Databricks Connect properly before running this script.

# COMMAND ----------

# COMMAND ----------

from databricks.connect import DatabricksSession

# This securely connects local script to the cloud cluster
spark = DatabricksSession.builder.getOrCreate()


# Import necessary libraries

# COMMAND ----------
import math 
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# COMMAND ----------

# MAGIC %md
# MAGIC We will use spark table and pandas dataframes:

# COMMAND ----------

sp_df = spark.table("ml_review_prediction_dataset")
df = sp_df.toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC Check the data types of columns:

# COMMAND ----------

data_types = {
    "Feature" : df.columns, 
    "Data Type" : df.dtypes.values
}

data_types = pd.DataFrame(data_types, index=None)
data_types

# COMMAND ----------

# MAGIC %md
# MAGIC Data types are correct.

# COMMAND ----------

# MAGIC %md
# MAGIC # Check Missing Values

# COMMAND ----------

missing_pct = (df.isnull().sum() / len(df) * 100)
missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)

plt.figure(figsize=(12, 6))
sns.barplot(
    x=missing_pct.values,
    y=missing_pct.index
)

plt.title("Missing Values Percentage by Feature")
plt.xlabel("Missing Percentage (%)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("../eda_results/missing_values_percentage.png", dpi=300)
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Remove rows with missing target values:

# COMMAND ----------

df = df.dropna(subset=["AVERAGE_REVIEW_SCORE"])

# COMMAND ----------

# MAGIC %md
# MAGIC Check:  if we drop all null - nan values completely, how much data we will lose:

# COMMAND ----------

rows_before = len(df)

df_clean = df.dropna()

rows_after = len(df_clean)

print(f"Rows removed: {rows_before - rows_after}")
print(f"Percentage removed: {(rows_before - rows_after)/rows_before*100:.2f}%")

# COMMAND ----------

# MAGIC %md
# MAGIC If we remove all rows with null values, we will lose only about 5% of the data which is negligible. Therefore, drop all missing values and continue with the clean data.

# COMMAND ----------

df = df.dropna().reset_index(drop=True)
print(df.shape)

# COMMAND ----------

df.head(1)

# COMMAND ----------

# MAGIC %md
# MAGIC # Duplicate Values

# COMMAND ----------

df.duplicated().sum()

# COMMAND ----------

# MAGIC %md
# MAGIC There is not any duplicated values in the dataset.

# COMMAND ----------

# MAGIC %md
# MAGIC # Distribution of Numerical Features

# COMMAND ----------

numerical_cols = df.select_dtypes(include=[np.number]).columns

n_cols = 4
n_rows = int(np.ceil(len(numerical_cols) / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 4))
axes = axes.flatten()

for i, col in enumerate(numerical_cols):
    sns.boxplot(
        x=df[col],
        ax=axes[i]
    )
    axes[i].set_title(col, fontsize=10)
    axes[i].set_xlabel("")

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Distribution for Categorical Features

# COMMAND ----------

categorical_cols = [
    col for col in df.select_dtypes(include=["object"]).columns
    if col not in ["ORDER_ID", "CUSTOMER_ID"]
]

n_cols = 2
n_rows = math.ceil(len(categorical_cols) / n_cols)

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5 * n_rows))
axes = axes.flatten()

for i, col in enumerate(categorical_cols):

    top_categories = (
    df[col]
    .value_counts(normalize=True)
    .head(10)
    .mul(100)
    )

    sns.barplot(
        x=top_categories.values,
        y=top_categories.index,
        ax=axes[i]
    )

    axes[i].set_title(f"Top 10 Categories - {col}")
    axes[i].set_xlabel("Percentage (%)")
    axes[i].set_ylabel("")

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig("../eda_results/categorical_features_distribution.png", dpi=300)
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Target Feature Distribution

# COMMAND ----------

review_dist = (
    df["AVERAGE_REVIEW_SCORE"]
    .value_counts(normalize=True)
    .sort_index()
    .mul(100)
)

plt.figure(figsize=(8, 5))

ax = sns.barplot(
    x=review_dist.index,
    y=review_dist.values
)

for i, v in enumerate(review_dist.values):
    ax.text(i, v + 0.3, f"{v:.1f}%", ha="center")

plt.title("Distribution of Average Review Score")
plt.xlabel("Review Score")
plt.ylabel("Percentage (%)")
plt.tight_layout()
plt.savefig("../eda_results/target_feature_distribution.png", dpi=300)
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC There are some values (1.5, 2.5, 3.33 and etc) that are not whole numbers. We should eliminate them and make them 1,2,3,4,5 by rounding:

# COMMAND ----------

df["AVERAGE_REVIEW_SCORE"] = (
    df["AVERAGE_REVIEW_SCORE"]
    .round()
    .astype(int)
)

# COMMAND ----------

df["AVERAGE_REVIEW_SCORE"].value_counts().sort_index()

# COMMAND ----------

# MAGIC %md
# MAGIC This is highly imbalanced dataset. We will deal with imbalance further. Currently, these review scores are `integer` type. This is good because in the Feature Selection part, we will be able to apply Correlation Analysis (Pearson and Anova Tests). However, for prediction, it is better to have categories - groups: So, I will group scores 1 and 2 into **negative**, 3 into **neutral**; and 4 and 5 into **positive** groups. This feature will be `review_score_sentiment`. We will also be able to apply Chi Square test with categorical features. 

# COMMAND ----------

df["REVIEW_SENTIMENT"] = df["AVERAGE_REVIEW_SCORE"].map({
    1: "Negative",
    2: "Negative",
    3: "Neutral",
    4: "Positive",
    5: "Positive"
})

# COMMAND ----------

# MAGIC %md
# MAGIC Check distribution for new target feature:

# COMMAND ----------

(
    df["REVIEW_SENTIMENT"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Business Questions

# COMMAND ----------


delivery_review = (
    df.groupby("IS_LATE_ORDER")["AVERAGE_REVIEW_SCORE"]
    .agg(["mean", "count"])
    .reset_index()
)

delivery_review["Delivery Status"] = delivery_review["IS_LATE_ORDER"].map({
    0: "On Time",
    1: "Delayed"
})

fig = px.bar(
    delivery_review,
    x="Delivery Status",
    y="mean",
    color="Delivery Status",
    text=delivery_review["mean"].round(2),
    hover_data={"count": True, "mean": ":.2f"},
    title="Impact of Delivery Delays on Customer Review Scores"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    xaxis_title="Delivery Status",
    yaxis_title="Average Review Score",
    title_x=0.5,
    showlegend=False,
    template="plotly_white",
    height=600
)
fig.write_image("../eda_results/delivery_review_scores.png", scale=2)
fig.show()

# COMMAND ----------

import plotly.express as px

fig = px.box(
    df,
    x=df["IS_LATE_ORDER"].map({0: "On Time", 1: "Delayed"}),
    y="AVERAGE_REVIEW_SCORE",
    color=df["IS_LATE_ORDER"].map({0: "On Time", 1: "Delayed"}),
    points=False,
    title="Distribution of Review Scores by Delivery Status"
)

fig.update_layout(
    xaxis_title="Delivery Status",
    yaxis_title="Review Score",
    title_x=0.5,
    template="plotly_white",
    showlegend=False,
    height=600
)

fig.show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Q2. Does shipping cost affect customer satisfaction?

# COMMAND ----------

import pandas as pd
import plotly.express as px

shipping_analysis = (
    df.groupby(pd.qcut(df["ORDER_SHIPPING_COST"], q=5))
      .agg(
          Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
          Avg_Shipping_Cost=("ORDER_SHIPPING_COST", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index(drop=True)
)

shipping_analysis["Shipping Cost Group"] = [
    "Very Low",
    "Low",
    "Medium",
    "High",
    "Very High"
]

fig = px.line(
    shipping_analysis,
    x="Shipping Cost Group",
    y="Avg_Review_Score",
    markers=True,
    text=shipping_analysis["Avg_Review_Score"].round(2),
    title="Does Shipping Cost Affect Customer Satisfaction?"
)

fig.update_traces(
    textposition="top center",
    line_width=4,
    marker_size=12
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Shipping Cost Segment",
    yaxis_title="Average Review Score",
    height=600
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q3. Do expensive orders receive higher ratings?

# COMMAND ----------

import pandas as pd
import plotly.express as px

order_value_analysis = (
    df.groupby(pd.qcut(df["TOTAL_ORDER_VALUE"], q=5))
      .agg(
          Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
          Avg_Order_Value=("TOTAL_ORDER_VALUE", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index(drop=True)
)

order_value_analysis["Order Value Segment"] = [
    "Very Low",
    "Low",
    "Medium",
    "High",
    "Very High"
]

fig = px.bar(
    order_value_analysis,
    x="Order Value Segment",
    y="Avg_Review_Score",
    color="Avg_Order_Value",
    text=order_value_analysis["Avg_Review_Score"].round(2),
    title="Do Expensive Orders Receive Higher Ratings?"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Order Value Segment",
    yaxis_title="Average Review Score",
    coloraxis_colorbar_title="Avg Order Value",
    height=600
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q4. Do heavier products tend to have more shipping cost? Also check customer satisfaction on heavy products and others? 

# COMMAND ----------

import pandas as pd
import plotly.express as px

weight_shipping = (
    df.groupby(pd.qcut(df["AVG_PRODUCT_WEIGHT_G"], q=5))
      .agg(
          Avg_Product_Weight=("AVG_PRODUCT_WEIGHT_G", "mean"),
          Avg_Shipping_Cost=("ORDER_SHIPPING_COST", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index(drop=True)
)

weight_shipping["Weight Segment"] = [
    "Very Light",
    "Light",
    "Medium",
    "Heavy",
    "Very Heavy"
]

fig = px.bar(
    weight_shipping,
    x="Weight Segment",
    y="Avg_Shipping_Cost",
    color="Avg_Shipping_Cost",
    text=weight_shipping["Avg_Shipping_Cost"].round(2),
    title="Do Heavier Products Generate Higher Shipping Costs?"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Product Weight Segment",
    yaxis_title="Average Shipping Cost",
    coloraxis_colorbar_title="Shipping Cost",
    height=650
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Do certain product categories receive better reviews?

# COMMAND ----------

import pandas as pd
import plotly.express as px

top_categories = (
    df["DOMINANT_PRODUCT_CATEGORY_ENGLISH"]
    .value_counts()
    .head(15)
    .index
)

category_review = (
    df[df["DOMINANT_PRODUCT_CATEGORY_ENGLISH"].isin(top_categories)]
    .groupby("DOMINANT_PRODUCT_CATEGORY_ENGLISH")
    .agg(
        Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
        Orders=("ORDER_ID", "count")
    )
    .reset_index()
    .sort_values("Avg_Review_Score", ascending=False)
)

fig = px.bar(
    category_review,
    x="Avg_Review_Score",
    y="DOMINANT_PRODUCT_CATEGORY_ENGLISH",
    color="Avg_Review_Score",
    text=category_review["Avg_Review_Score"].round(2),
    hover_data=["Orders"],
    orientation="h",
    title="Average Review Score by Product Category (Top 15 Categories)"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Average Review Score",
    yaxis_title="Product Category",
    coloraxis_colorbar_title="Review Score",
    height=800
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Do some states consistently give lower ratings? 

# COMMAND ----------

import pandas as pd
import plotly.express as px

state_review = (
    df.groupby("CUSTOMER_STATE")
      .agg(
          Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index()
)

# Keep only meaningful states with enough observations
state_review = state_review[state_review["Orders"] >= 100]

state_review = state_review.sort_values(
    "Avg_Review_Score",
    ascending=True
)

fig = px.bar(
    state_review,
    x="Avg_Review_Score",
    y="CUSTOMER_STATE",
    color="Avg_Review_Score",
    text=state_review["Avg_Review_Score"].round(2),
    hover_data=["Orders"],
    orientation="h",
    title="Average Review Score by Customer State"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Average Review Score",
    yaxis_title="State",
    coloraxis_colorbar_title="Review Score",
    height=900
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q7. Does Payment Type affect review score?

# COMMAND ----------

import pandas as pd
import plotly.express as px

payment_review = (
    df.groupby("PAYMENT_TYPE")
      .agg(
          Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index()
      .sort_values("Avg_Review_Score", ascending=False)
)

fig = px.bar(
    payment_review,
    x="PAYMENT_TYPE",
    y="Avg_Review_Score",
    color="Avg_Review_Score",
    text=payment_review["Avg_Review_Score"].round(2),
    hover_data=["Orders"],
    title="Average Review Score by Payment Type"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Payment Type",
    yaxis_title="Average Review Score",
    coloraxis_colorbar_title="Review Score",
    height=650
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q8. Basket Size Analysis. Basket Size effect on review score. 

# COMMAND ----------

import pandas as pd
import plotly.express as px

basket_review = (
    df.groupby("TOTAL_PRODUCTS")
      .agg(
          Avg_Review_Score=("AVERAGE_REVIEW_SCORE", "mean"),
          Orders=("ORDER_ID", "count")
      )
      .reset_index()
)

# Keep basket sizes with sufficient observations
basket_review = basket_review[basket_review["Orders"] >= 50]

fig = px.line(
    basket_review,
    x="TOTAL_PRODUCTS",
    y="Avg_Review_Score",
    markers=True,
    text=basket_review["Avg_Review_Score"].round(2),
    title="Basket Size Effect on Customer Review Score"
)

fig.update_traces(
    mode="lines+markers+text",
    textposition="top center",
    line=dict(width=4),
    marker=dict(size=10)
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Number of Products in Order",
    yaxis_title="Average Review Score",
    height=650
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q9. Do customers receiving orders late write more negative reviews?

# COMMAND ----------

import pandas as pd
import plotly.express as px

sentiment_order = ["Negative", "Neutral", "Positive"]

late_review = (
    df.groupby(["IS_LATE_ORDER", "REVIEW_SENTIMENT"])
      .size()
      .reset_index(name="Count")
)

late_review["Delivery Status"] = late_review["IS_LATE_ORDER"].map({
    0: "On Time",
    1: "Delayed"
})

late_review["REVIEW_SENTIMENT"] = pd.Categorical(
    late_review["REVIEW_SENTIMENT"],
    categories=sentiment_order,
    ordered=True
)

fig = px.histogram(
    late_review,
    x="Delivery Status",
    y="Count",
    color="REVIEW_SENTIMENT",
    barnorm="percent",
    barmode="stack",
    category_orders={"REVIEW_SENTIMENT": sentiment_order},
    color_discrete_map={
        "Negative": "#d62728",
        "Neutral": "#ffbf00",
        "Positive": "#2ca02c"
    },
    title="Customer Sentiment by Delivery Status"
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Delivery Status",
    yaxis_title="Percentage of Reviews (%)",
    legend_title="Review Sentiment",
    height=650
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q10. Which feature appear most associated with customer satisfaction? 

# COMMAND ----------

from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import plotly.express as px

features = [
    "DELIVERY_DELAYED_DAYS",
    "ORDER_SHIPPING_COST",
    "TOTAL_ORDER_VALUE",
    "TOTAL_PRODUCTS",
    "AVG_PRODUCT_WEIGHT_G"
]

X = df[features]
y = df["AVERAGE_REVIEW_SCORE"]

rf = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

rf.fit(X, y)

importance = (
    pd.DataFrame({
        "Operational Factor": [
            "Delivery Delay",
            "Shipping Cost",
            "Order Value",
            "Basket Size",
            "Product Weight"
        ],
        "Importance": rf.feature_importances_
    })
    .sort_values("Importance", ascending=True)
)

fig = px.bar(
    importance,
    x="Importance",
    y="Operational Factor",
    orientation="h",
    color="Importance",
    text=importance["Importance"].round(3),
    color_continuous_scale="Viridis",
    title="Which Operational Factors Have the Greatest Impact on Customer Satisfaction?"
)

fig.update_traces(textposition="outside")

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_title="Relative Importance",
    yaxis_title="",
    height=650
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Convert the dataset into csv file.

# COMMAND ----------

spark_df = spark.createDataFrame(df)

spark_df.write \
    .mode("overwrite") \
    .saveAsTable("ml_review_prediction_dataset_clean")

# COMMAND ----------

df_clean = spark.table("ml_review_prediction_dataset_clean")
display(df_clean.limit(5))

# COMMAND ----------

dd = df_clean.toPandas()
dd.shape

# COMMAND ----------

