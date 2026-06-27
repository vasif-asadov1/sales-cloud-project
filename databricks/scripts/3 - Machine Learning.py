# Databricks notebook source
# MAGIC %pip install category_encoders xgboost lightgbm catboost

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC # Load Data

# COMMAND ----------

sp_df = spark.table("workspace.default.ml_review_prediction_dataset_clean")
df = sp_df.toPandas()

# COMMAND ----------

df.head()

# COMMAND ----------

df.info()

# COMMAND ----------

# ============================================================
# 1. Remove identifier, datetime and leakage columns
# ============================================================

columns_to_drop = [
    # Identifiers
    "ORDER_ID",
    "CUSTOMER_ID",

    # Raw datetime columns
    "ORDER_PURCHASE_TIMESTAMP",
    "ORDER_APPROVED_AT",
    "ORDER_DELIVERED_CARRIER_DATE",
    "ORDER_DELIVERED_CUSTOMER_DATE",
    "ORDER_ESTIMATED_DELIVERY_DATE",

    # Target leakage
    "AVERAGE_REVIEW_SCORE"
]

df = df.drop(columns=columns_to_drop)

print(f"Dataset shape after column removal: {df.shape}")

# COMMAND ----------

from sklearn.model_selection import train_test_split

# ============================================================
# 2. Define Features and Target
# ============================================================

X = df.drop(columns=["REVIEW_SENTIMENT"])
y = df["REVIEW_SENTIMENT"]

# ============================================================
# 3. Train / Test Split
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("=" * 60)
print("Train/Test Split Completed")
print("=" * 60)
print(f"X_train: {X_train.shape}")
print(f"X_test : {X_test.shape}")
print(f"y_train: {y_train.shape}")
print(f"y_test : {y_test.shape}")

# COMMAND ----------

from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()

y_train = label_encoder.fit_transform(y_train)
y_test = label_encoder.transform(y_test)

print(label_encoder.classes_)

# COMMAND ----------

# Categorical columns
categorical_cols = X_train.select_dtypes(include=["object"]).columns.tolist()

print("Categorical Features:")
print(categorical_cols)

# COMMAND ----------

# High-cardinality feature
high_cardinality = ["CUSTOMER_CITY"]

# Low-cardinality features
low_cardinality = [
    col for col in categorical_cols
    if col not in high_cardinality
]

print("Low Cardinality Features:")
print(low_cardinality)

print("\nHigh Cardinality Features:")
print(high_cardinality)

# COMMAND ----------

from sklearn.preprocessing import OneHotEncoder

ohe = OneHotEncoder(
    handle_unknown="ignore",
    sparse_output=False
)

X_train_low = ohe.fit_transform(X_train[low_cardinality])
X_test_low = ohe.transform(X_test[low_cardinality])

print("One-Hot Encoding Completed")
print(X_train_low.shape)
print(X_test_low.shape)

# COMMAND ----------

from category_encoders import CatBoostEncoder

city_encoder = CatBoostEncoder()

X_train_city = city_encoder.fit_transform(
    X_train[high_cardinality],
    y_train
)

X_test_city = city_encoder.transform(
    X_test[high_cardinality]
)

print("City Encoding Completed")
print(X_train_city.shape)
print(X_test_city.shape)

# COMMAND ----------

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

# COMMAND ----------

# Keep only numerical columns
X_train_num = X_train.select_dtypes(exclude=["object"]).reset_index(drop=True)
X_test_num = X_test.select_dtypes(exclude=["object"]).reset_index(drop=True)

print(X_train_num.shape)
print(X_test_num.shape)

# COMMAND ----------

import pandas as pd

ohe_feature_names = ohe.get_feature_names_out(low_cardinality)

X_train_low = pd.DataFrame(
    X_train_low,
    columns=ohe_feature_names
).reset_index(drop=True)

X_test_low = pd.DataFrame(
    X_test_low,
    columns=ohe_feature_names
).reset_index(drop=True)

# COMMAND ----------

X_train_city = X_train_city.reset_index(drop=True)
X_test_city = X_test_city.reset_index(drop=True)

# COMMAND ----------

X_train_processed = pd.concat(
    [X_train_num, X_train_low, X_train_city],
    axis=1
)

X_test_processed = pd.concat(
    [X_test_num, X_test_low, X_test_city],
    axis=1
)

print("=" * 60)
print("Processed Dataset")
print("=" * 60)

print(X_train_processed.shape)
print(X_test_processed.shape)

# COMMAND ----------

print(X_train_processed.isnull().sum().sum())
print(X_test_processed.isnull().sum().sum())

# COMMAND ----------

print(X_train_processed.info())
print(X_train_processed.head())

# COMMAND ----------

from sklearn.preprocessing import StandardScaler

# ============================================================
# Standard Scaling (For Logistic Regression Only)
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train_processed)
X_test_scaled = scaler.transform(X_test_processed)

print("=" * 60)
print("Standard Scaling Completed")
print("=" * 60)

print(f"X_train_scaled shape: {X_train_scaled.shape}")
print(f"X_test_scaled shape : {X_test_scaled.shape}")

# COMMAND ----------

import pandas as pd

scaled_df = pd.DataFrame(
    X_train_scaled,
    columns=X_train_processed.columns
)

print(scaled_df.describe().loc[["mean", "std"]].round(2))

# COMMAND ----------

import joblib

joblib.dump(scaler, "standard_scaler.pkl")

# COMMAND ----------

import mlflow
import mlflow.sklearn

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

# COMMAND ----------

# ============================================================
# MLflow Experiment
# ============================================================

mlflow.set_experiment("/Shared/Olist_Review_Sentiment_Prediction")

print("MLflow Experiment Set Successfully.")

# COMMAND ----------

# ============================================================
# Logistic Regression - MLflow
# ============================================================

import mlflow
import mlflow.sklearn

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# Close any active run
if mlflow.active_run():
    mlflow.end_run()

with mlflow.start_run(run_name="Logistic Regression"):

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        solver="lbfgs",
        multi_class="multinomial"
    )

    model.fit(X_train_scaled, y_train)

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted"
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted"
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted"
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob,
        multi_class="ovr",
        average="weighted"
    )

    gini = (2 * roc_auc) - 1

    # --------------------------------------------------------
    # Log Parameters
    # --------------------------------------------------------

    mlflow.log_param("Model", "Logistic Regression")
    mlflow.log_param("Solver", "lbfgs")
    mlflow.log_param("Max Iterations", 1000)
    mlflow.log_param("Random State", 42)

    # --------------------------------------------------------
    # Log Metrics
    # --------------------------------------------------------

    mlflow.log_metric("Accuracy", accuracy)
    mlflow.log_metric("Precision", precision)
    mlflow.log_metric("Recall", recall)
    mlflow.log_metric("F1 Score", f1)
    mlflow.log_metric("ROC AUC", roc_auc)
    mlflow.log_metric("Gini", gini)

    # --------------------------------------------------------
    # Log Model
    # --------------------------------------------------------

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model"
    )

    print("=" * 60)
    print("Logistic Regression Training Completed")
    print("=" * 60)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC AUC  : {roc_auc:.4f}")
    print(f"Gini     : {gini:.4f}")

# COMMAND ----------

# ============================================================
# Confusion Matrix
# ============================================================

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=model.classes_,
    yticklabels=model.classes_
)

plt.title("Logistic Regression - Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")

plt.tight_layout()

plt.savefig("confusion_matrix.png", dpi=300)

mlflow.log_artifact("confusion_matrix.png")

plt.show()

# COMMAND ----------

# ============================================================
# Classification Report
# ============================================================

report = classification_report(y_test, y_pred)

print(report)

with open("classification_report.txt", "w") as f:
    f.write(report)

mlflow.log_artifact("classification_report.txt")

# COMMAND ----------

# ============================================================
# Feature Importance
# ============================================================

feature_importance = (
    pd.DataFrame({
        "Feature": X_train_processed.columns,
        "Importance": np.mean(np.abs(model.coef_), axis=0)
    })
    .sort_values("Importance", ascending=False)
)

top20 = feature_importance.head(20)

plt.figure(figsize=(10, 8))

sns.barplot(
    data=top20,
    x="Importance",
    y="Feature",
    orient="h"
)

plt.title("Top 20 Important Features\n(Logistic Regression)")

plt.tight_layout()

plt.savefig("feature_importance.png", dpi=300)

mlflow.log_artifact("feature_importance.png")

plt.show()

# COMMAND ----------

# ============================================================
# Save Feature Importance Table
# ============================================================

feature_importance.to_csv(
    "feature_importance.csv",
    index=False
)

mlflow.log_artifact("feature_importance.csv")

feature_importance.head(20)

# COMMAND ----------

# MAGIC %md
# MAGIC # Tree Models

# COMMAND ----------

import mlflow
import mlflow.sklearn

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

def train_tree_model(model, model_name):

    # Close previous run if necessary
    if mlflow.active_run():
        mlflow.end_run()

    with mlflow.start_run(run_name=model_name):

        # -----------------------------
        # Train
        # -----------------------------
        model.fit(X_train_processed, y_train)

        # -----------------------------
        # Prediction
        # -----------------------------
        y_pred = model.predict(X_test_processed)
        y_prob = model.predict_proba(X_test_processed)

        # -----------------------------
        # Metrics
        # -----------------------------
        accuracy = accuracy_score(y_test, y_pred)

        precision = precision_score(
            y_test,
            y_pred,
            average="weighted"
        )

        recall = recall_score(
            y_test,
            y_pred,
            average="weighted"
        )

        f1 = f1_score(
            y_test,
            y_pred,
            average="weighted"
        )

        roc_auc = roc_auc_score(
            y_test,
            y_prob,
            multi_class="ovr",
            average="weighted"
        )

        gini = (2 * roc_auc) - 1

        # -----------------------------
        # MLflow
        # -----------------------------
        mlflow.log_params(model.get_params())

        mlflow.log_metric("Accuracy", accuracy)
        mlflow.log_metric("Precision", precision)
        mlflow.log_metric("Recall", recall)
        mlflow.log_metric("F1 Score", f1)
        mlflow.log_metric("ROC AUC", roc_auc)
        mlflow.log_metric("Gini", gini)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model"
        )

        print("=" * 60)
        print(model_name)
        print("=" * 60)

        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print(f"ROC AUC  : {roc_auc:.4f}")
        print(f"Gini     : {gini:.4f}")

    return model

# COMMAND ----------

from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

rf = train_tree_model(
    rf,
    "Random Forest"
)

# COMMAND ----------

from xgboost import XGBClassifier

xgb = XGBClassifier(
    objective="multi:softprob",
    num_class=3,
    random_state=42,
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss"
)

xgb = train_tree_model(
    xgb,
    "XGBoost"
)

# COMMAND ----------

from lightgbm import LGBMClassifier

lgbm = LGBMClassifier(
    random_state=42,
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6
)

lgbm = train_tree_model(
    lgbm,
    "LightGBM"
)

# COMMAND ----------

from catboost import CatBoostClassifier

cat = CatBoostClassifier(
    iterations=300,
    learning_rate=0.1,
    depth=6,
    random_seed=42,
    verbose=False
)

cat = train_tree_model(
    cat,
    "CatBoost"
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Results

# COMMAND ----------

import mlflow

results = mlflow.search_runs(
    experiment_names=["/Shared/Olist_Review_Sentiment_Prediction"]
)

metrics = results[[
    "tags.mlflow.runName",
    "metrics.Accuracy",
    "metrics.Precision",
    "metrics.Recall",
    "metrics.F1 Score",
    "metrics.ROC AUC",
    "metrics.Gini"
]]

metrics = metrics.rename(columns={
    "tags.mlflow.runName":"Model",
    "metrics.Accuracy":"Accuracy",
    "metrics.Precision":"Precision",
    "metrics.Recall":"Recall",
    "metrics.F1 Score":"F1",
    "metrics.ROC AUC":"ROC AUC",
    "metrics.Gini":"Gini"
})

metrics

# COMMAND ----------

results = mlflow.search_runs(
    experiment_names=["/Shared/Olist_Review_Sentiment_Prediction"]
)

results = results.dropna(
    subset=["metrics.Accuracy"]
)

# COMMAND ----------

import matplotlib.pyplot as plt

metrics = metrics.sort_values("Accuracy", ascending=False)

plt.figure(figsize=(8,5))

plt.bar(metrics["Model"], metrics["Accuracy"])

plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")

plt.xticks(rotation=20)

plt.show()

# COMMAND ----------

import matplotlib.pyplot as plt

metrics = metrics.sort_values("Accuracy", ascending=False)

plt.figure(figsize=(8,5))

plt.bar(metrics["Model"], metrics["Accuracy"])

plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")

plt.xticks(rotation=20)

plt.show()

# COMMAND ----------

metrics = metrics.sort_values("Gini", ascending=False)

plt.figure(figsize=(8,5))

plt.bar(metrics["Model"], metrics["Gini"])

plt.ylabel("Gini")
plt.title("Model Gini Comparison")

plt.xticks(rotation=20)

plt.show()

# COMMAND ----------

metrics = metrics.sort_values("ROC AUC", ascending=False)

plt.figure(figsize=(8,5))

plt.bar(metrics["Model"], metrics["ROC AUC"])

plt.ylabel("ROC AUC")
plt.title("Model ROC AUC Comparison")

plt.xticks(rotation=20)

plt.show()

# COMMAND ----------

metrics.sort_values(
    "F1",
    ascending=False
).reset_index(drop=True)

# COMMAND ----------

print(xgb.n_estimators)

print(lgbm.n_estimators)

print(cat.get_params())

# COMMAND ----------

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# CatBoost Confusion Matrix
# ============================================================

y_pred = cat.predict(X_test_processed)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
)

plt.title("CatBoost - Confusion Matrix", fontsize=15)
plt.xlabel("Predicted Label", fontsize=12)
plt.ylabel("True Label", fontsize=12)

plt.tight_layout()
plt.show()

# COMMAND ----------

from sklearn.metrics import confusion_matrix
import numpy as np

# ============================================================
# Normalized Confusion Matrix
# ============================================================

cm = confusion_matrix(y_test, y_pred)

cm_percent = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

plt.figure(figsize=(8,6))

sns.heatmap(
    cm_percent,
    annot=True,
    fmt=".2%",
    cmap="Greens",
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
)

plt.title("CatBoost - Normalized Confusion Matrix", fontsize=15)
plt.xlabel("Predicted Label", fontsize=12)
plt.ylabel("True Label", fontsize=12)

plt.tight_layout()
plt.show()

# COMMAND ----------

plt.savefig("catboost_confusion_matrix.png", dpi=300)

mlflow.log_artifact("catboost_confusion_matrix.png")

# COMMAND ----------

from sklearn.metrics import classification_report

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Handling Class Imbalance

# COMMAND ----------

from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Compute balanced class weights
classes = np.unique(y_train)

weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=y_train
)

class_weights = dict(zip(classes, weights))

print(class_weights)

# COMMAND ----------

model = LogisticRegression(
    random_state=42,
    max_iter=1000,
    solver="lbfgs",
    multi_class="multinomial",
    class_weight="balanced"
)

# COMMAND ----------

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

# COMMAND ----------

cat = CatBoostClassifier(
    iterations=300,
    learning_rate=0.1,
    depth=6,
    random_seed=42,
    verbose=False,
    class_weights=[
        class_weights[0],
        class_weights[1],
        class_weights[2]
    ]
)

# COMMAND ----------

sample_weights = np.array(
    [class_weights[label] for label in y_train]
)

# COMMAND ----------

xgb.fit(
    X_train_processed,
    y_train,
    sample_weight=sample_weights
)

# COMMAND ----------

sample_weights = np.array(
    [class_weights[label] for label in y_train]
)

lgbm.fit(
    X_train_processed,
    y_train,
    sample_weight=sample_weights
)

# COMMAND ----------

import mlflow
import pandas as pd

results = mlflow.search_runs(
    experiment_names=["/Shared/Olist_Review_Sentiment_Prediction"]
)

results = results.dropna(subset=["metrics.Accuracy"])

# COMMAND ----------

results = (
    results.sort_values("start_time", ascending=False)
           .drop_duplicates(
                subset="tags.mlflow.runName",
                keep="first"
           )
)

# COMMAND ----------

comparison = results[[
    "tags.mlflow.runName",
    "metrics.Accuracy",
    "metrics.Precision",
    "metrics.Recall",
    "metrics.F1 Score",
    "metrics.ROC AUC",
    "metrics.Gini"
]]

comparison.columns = [
    "Model",
    "Accuracy",
    "Precision",
    "Recall",
    "Weighted F1",
    "ROC AUC",
    "Gini"
]

comparison

# COMMAND ----------

import matplotlib.pyplot as plt

comparison = comparison.sort_values("Weighted F1")

plt.figure(figsize=(12,6))

plt.barh(
    comparison["Model"],
    comparison["Weighted F1"]
)

plt.xlabel("Weighted F1 Score")
plt.title("Baseline vs Balanced Models")

plt.grid(axis="x", alpha=0.3)

plt.show()

# COMMAND ----------

