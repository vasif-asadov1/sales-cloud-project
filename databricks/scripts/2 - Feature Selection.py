# Databricks notebook source
# MAGIC %md
# MAGIC # Libraries

# COMMAND ----------

import pandas as pd
import numpy as np

# COMMAND ----------

# MAGIC %md
# MAGIC # Load Data

# COMMAND ----------

sp_df = spark.table("ml_review_prediction_dataset_clean")
df = sp_df.toPandas()

# COMMAND ----------

df.info()

# COMMAND ----------

# MAGIC %md
# MAGIC # Correlation Analysis

# COMMAND ----------

# ==========================================================
# Correlation Analysis
# Pearson & Spearman Correlation with Average Review Score
# ==========================================================

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr

TARGET = "AVERAGE_REVIEW_SCORE"

# Select numerical features
numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

# Remove target from feature list
numeric_cols.remove(TARGET)

results = []

for feature in numeric_cols:
    
    pearson_r, pearson_p = pearsonr(df[feature], df[TARGET])
    spearman_rho, spearman_p = spearmanr(df[feature], df[TARGET])

    results.append({
        "Feature": feature,
        "Pearson_r": pearson_r,
        "Pearson_p": pearson_p,
        "Spearman_rho": spearman_rho,
        "Spearman_p": spearman_p
    })

correlation_results = (
    pd.DataFrame(results)
      .sort_values(by="Spearman_rho", key=np.abs, ascending=False)
      .reset_index(drop=True)
)

correlation_results.round(4)

# COMMAND ----------

# ==========================================================
# Pearson & Spearman Correlation Heatmap
# (Correlation + Statistical Significance)
# ==========================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import pearsonr, spearmanr

TARGET = "AVERAGE_REVIEW_SCORE"

numeric_features = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
numeric_features.remove(TARGET)

results = []

for feature in numeric_features:

    pearson_r, pearson_p = pearsonr(df[feature], df[TARGET])
    spearman_r, spearman_p = spearmanr(df[feature], df[TARGET])

    results.append({
        "Feature": feature,

        "Pearson": pearson_r,
        "Pearson_p": pearson_p,

        "Spearman": spearman_r,
        "Spearman_p": spearman_p
    })

corr_df = pd.DataFrame(results)

# ----------------------------------------------------------
# Sort by strongest monotonic correlation
# ----------------------------------------------------------

corr_df = corr_df.iloc[
    corr_df["Spearman"].abs().sort_values(ascending=False).index
]

# ----------------------------------------------------------
# Heatmap values
# ----------------------------------------------------------

z = corr_df[["Pearson", "Spearman"]].values

# ----------------------------------------------------------
# Significance stars
# ----------------------------------------------------------

def stars(p):

    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""

text = []

for _, row in corr_df.iterrows():

    text.append([
        f"{row['Pearson']:.2f}{stars(row['Pearson_p'])}",
        f"{row['Spearman']:.2f}{stars(row['Spearman_p'])}"
    ])

# ----------------------------------------------------------
# Gray-out insignificant cells
# ----------------------------------------------------------

mask = np.array([
    [
        row["Pearson_p"] >= 0.05,
        row["Spearman_p"] >= 0.05
    ]
    for _, row in corr_df.iterrows()
])

colorscale = [
    [0.00, "#B2182B"],
    [0.50, "#F7F7F7"],
    [1.00, "#2166AC"]
]

fig = go.Figure()

fig.add_trace(

    go.Heatmap(

        z=z,

        x=["Pearson", "Spearman"],

        y=corr_df["Feature"],

        zmin=-1,
        zmax=1,

        colorscale=colorscale,

        colorbar=dict(
            title="Correlation"
        ),

        text=text,

        texttemplate="%{text}",

        hovertemplate=
        "<b>%{y}</b><br>" +
        "Method: %{x}<br>" +
        "Correlation: %{z:.3f}<extra></extra>"
    )
)

# ----------------------------------------------------------
# Draw gray rectangles on insignificant cells
# ----------------------------------------------------------

for i in range(mask.shape[0]):

    for j in range(mask.shape[1]):

        if mask[i, j]:

            fig.add_shape(

                type="rect",

                x0=j-0.5,
                x1=j+0.5,

                y0=i-0.5,
                y1=i+0.5,

                fillcolor="rgba(180,180,180,0.55)",

                line=dict(width=0),

                layer="above"
            )

fig.update_layout(

    title=dict(
        text="<b>Correlation of Numerical Features with Average Review Score</b>",
        x=0.5,
        font=dict(size=22)
    ),

    template="plotly_white",

    width=850,

    height=950,

    font=dict(size=13),

    margin=dict(l=240, r=60, t=80, b=40)
)

fig.update_yaxes(autorange="reversed")

fig.add_annotation(

    x=0,
    y=-0.08,

    xref="paper",
    yref="paper",

    showarrow=False,

    align="left",

    text=(
        "<b>Statistical significance:</b> "
        "*** p < 0.001&nbsp;&nbsp;&nbsp;"
        "** p < 0.01&nbsp;&nbsp;&nbsp;"
        "* p < 0.05"
        "<br>"
        "<span style='color:gray'>Gray cells indicate non-significant correlations (p ≥ 0.05).</span>"
    )
)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Chi Square Test

# COMMAND ----------

# ==========================================================
# Chi-Square Test + Cramer's V
# Categorical Features vs Review Sentiment
# ==========================================================

import numpy as np
import pandas as pd

from scipy.stats import chi2_contingency

import plotly.express as px
import plotly.graph_objects as go

TARGET = "REVIEW_SENTIMENT"

# ----------------------------------------------------------
# Select categorical features
# ----------------------------------------------------------

categorical_features = df.select_dtypes(include="object").columns.tolist()

# Remove identifiers and target
categorical_features.remove("ORDER_ID")
categorical_features.remove("CUSTOMER_ID")
categorical_features.remove(TARGET)

# ----------------------------------------------------------
# Cramer's V interpretation
# ----------------------------------------------------------

def cramers_strength(v):

    if v < 0.10:
        return "Negligible"
    elif v < 0.30:
        return "Weak"
    elif v < 0.50:
        return "Moderate"
    else:
        return "Strong"

# ----------------------------------------------------------
# Chi-Square + Cramer's V
# ----------------------------------------------------------

results = []

for feature in categorical_features:

    contingency = pd.crosstab(df[feature], df[TARGET])

    chi2, p, dof, expected = chi2_contingency(contingency)

    n = contingency.to_numpy().sum()

    phi2 = chi2 / n

    r, k = contingency.shape

    phi2corr = max(
        0,
        phi2 - ((k - 1) * (r - 1)) / (n - 1)
    )

    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)

    cramers_v = np.sqrt(
        phi2corr /
        min(
            (kcorr - 1),
            (rcorr - 1)
        )
    )

    results.append({

        "Feature": feature,
        "Chi2": chi2,
        "P_Value": p,
        "Cramers_V": cramers_v,
        "Association": cramers_strength(cramers_v),
        "Significant": p < 0.05

    })

chi_df = (
    pd.DataFrame(results)
      .sort_values("Cramers_V", ascending=True)
      .reset_index(drop=True)
)

# ----------------------------------------------------------
# Visualization
# ----------------------------------------------------------

color_map = {
    "Negligible": "#D3D3D3",
    "Weak": "#4C78A8",
    "Moderate": "#F2A104",
    "Strong": "#D62728"
}

opacity = np.where(
    chi_df["Significant"],
    1.0,
    0.35
)

fig = go.Figure()

for i in range(len(chi_df)):

    fig.add_trace(

        go.Bar(

            x=[chi_df.loc[i, "Cramers_V"]],

            y=[chi_df.loc[i, "Feature"]],

            orientation="h",

            marker_color=color_map[
                chi_df.loc[i, "Association"]
            ],

            opacity=float(opacity[i]),

            text=[
                f"{chi_df.loc[i,'Cramers_V']:.3f}"
            ],

            textposition="outside",

            hovertemplate=
            "<b>%{y}</b><br>" +
            f"Chi² = {chi_df.loc[i,'Chi2']:.2f}<br>" +
            f"Cramer's V = {chi_df.loc[i,'Cramers_V']:.3f}<br>" +
            f"P-value = {chi_df.loc[i,'P_Value']:.4g}<br>" +
            f"Association = {chi_df.loc[i,'Association']}<br>" +
            f"Significant = {chi_df.loc[i,'Significant']}<extra></extra>",

            showlegend=False

        )
    )

fig.update_layout(

    title=dict(
        text="<b>Chi-Square Association Between Categorical Features and Review Sentiment</b>",
        x=0.5,
        font=dict(size=22)
    ),

    template="plotly_white",

    height=650,

    width=1200,

    xaxis_title="Cramer's V",

    yaxis_title="",

    bargap=0.35,

    font=dict(size=13),

    margin=dict(
        l=220,
        r=80,
        t=80,
        b=80
    )
)

fig.add_annotation(

    x=0,
    y=-0.16,

    xref="paper",
    yref="paper",

    showarrow=False,

    align="left",

    text=(
        "<b>Association Strength</b><br>"
        "Gray = Negligible (<0.10)<br>"
        "Blue = Weak (0.10–0.30)<br>"
        "Orange = Moderate (0.30–0.50)<br>"
        "Red = Strong (≥0.50)<br><br>"
        "<b>Opacity</b><br>"
        "Opaque = Statistically Significant (p < 0.05)<br>"
        "Transparent = Not Significant (p ≥ 0.05)"
    )

)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Anova Test

# COMMAND ----------

# ==========================================================
# ANOVA Feature Importance
# Eta² Lollipop Chart
# ==========================================================

import numpy as np
import plotly.graph_objects as go

# Sort by effect size
anova_plot = anova_df.sort_values("Eta_Squared", ascending=True).copy()

# Color by significance
colors = np.where(
    anova_plot["P_Value"] < 0.05,
    "#2563EB",      # Significant
    "#CFCFCF"       # Not significant
)

fig = go.Figure()

# Lollipop stems
for i in range(len(anova_plot)):

    fig.add_trace(
        go.Scatter(
            x=[0, anova_plot.iloc[i]["Eta_Squared"]],
            y=[anova_plot.iloc[i]["Feature"]]*2,
            mode="lines",
            line=dict(
                color=colors[i],
                width=3
            ),
            hoverinfo="skip",
            showlegend=False
        )
    )

# Lollipop heads
fig.add_trace(

    go.Scatter(

        x=anova_plot["Eta_Squared"],

        y=anova_plot["Feature"],

        mode="markers+text",

        marker=dict(

            size=14,

            color=colors,

            line=dict(
                color="black",
                width=1
            )

        ),

        text=anova_plot["Eta_Squared"].round(3),

        textposition="middle right",

        customdata=np.stack([
            anova_plot["F"],
            anova_plot["P_Value"],
            anova_plot["Effect_Size"]
        ], axis=1),

        hovertemplate=
        "<b>%{y}</b><br><br>" +
        "Eta²: %{x:.3f}<br>" +
        "F Statistic: %{customdata[0]:.2f}<br>" +
        "P-value: %{customdata[1]:.4g}<br>" +
        "Effect Size: %{customdata[2]}<extra></extra>",

        showlegend=False

    )

)

fig.update_layout(

    title=dict(

        text="<b>ANOVA Feature Importance (Eta² Effect Size)</b>",

        x=0.5,

        font=dict(size=22)

    ),

    template="plotly_white",

    width=1100,

    height=550,

    xaxis=dict(

        title="Eta Squared (η²)",

        zeroline=False,

        showgrid=True

    ),

    yaxis=dict(

        title="",

        automargin=True

    ),

    font=dict(size=13),

    margin=dict(

        l=220,

        r=60,

        t=80,

        b=90

    )

)

fig.add_annotation(

    x=0,

    y=-0.20,

    xref="paper",

    yref="paper",

    showarrow=False,

    align="left",

    text=(
        "<b>Interpretation</b><br>"
        "<span style='color:#2563EB'>● Significant (p < 0.05)</span><br>"
        "<span style='color:#CFCFCF'>● Not Significant (p ≥ 0.05)</span><br><br>"
        "Effect Size (η²): "
        "Negligible <0.01 | "
        "Small 0.01–0.06 | "
        "Medium 0.06–0.14 | "
        "Large ≥0.14"
    )

)

fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC # Mutual Information Analysis

# COMMAND ----------

df["REVIEW_SENTIMENT"].value_counts()

# COMMAND ----------

mi_df["MI_Score"].describe()

# COMMAND ----------

