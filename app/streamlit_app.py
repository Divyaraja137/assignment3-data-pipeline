from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats


st.set_page_config(page_title="Assignment 4 - Crypto Statistical Analysis", layout="wide")

DATA_FILE = Path("data/gold/final_assignment4_dataset.csv")


@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_FILE}. Run transform/create_gold_assignment4.py first."
        )

    df = pd.read_csv(DATA_FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_cols = [
        "btc_open",
        "btc_high",
        "btc_low",
        "btc_close",
        "btc_volume",
        "fear_greed_value",
        "btc_daily_return",
        "positive_return",
        "holiday_flag",
        "high_volatility_flag",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def safe_two_sample_groups(df, value_col, group_col, group_a=0, group_b=1):
    group1 = df.loc[df[group_col] == group_a, value_col].dropna()
    group2 = df.loc[df[group_col] == group_b, value_col].dropna()
    return group1, group2


def interpretation_pvalue(p):
    if p < 0.05:
        return "The result is statistically significant at the 5% level."
    return "The result is not statistically significant at the 5% level."


st.title("Assignment 4: Interactive Statistical Analysis App")
st.subheader("Crypto & Sentiment Extended with Holiday Calendar Data")

df = load_data()

st.sidebar.header("Filters")

min_date = df["date"].min()
max_date = df["date"].max()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date.date(), max_date.date()

filtered_df = df[
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
].copy()

if "day_type" in filtered_df.columns:
    day_type_filter = st.sidebar.multiselect(
        "Day type",
        options=sorted(filtered_df["day_type"].dropna().unique().tolist()),
        default=sorted(filtered_df["day_type"].dropna().unique().tolist())
    )
    filtered_df = filtered_df[filtered_df["day_type"].isin(day_type_filter)]

st.header("1. Project Overview / Data Story")
st.write(
    """
    This project continues the Assignment 3 crypto and sentiment pipeline.
    The original Gold dataset combines Bitcoin daily market data from Binance
    with the Fear & Greed Index data.

    For Assignment 4, a new external source was added: a Canadian public holiday calendar.
    This new source was joined using the `date` column and created a new grouping variable
    called `holiday_flag`.

    Main question:
    Do Bitcoin returns, trading volume, and sentiment-related behavior differ
    between holidays and non-holidays?
    """
)

st.header("2. Data Preview")
st.write("Preview of the final Assignment 4 analysis-ready dataset:")
st.dataframe(filtered_df.head(10), use_container_width=True)

summary_cols = [col for col in [
    "btc_open", "btc_high", "btc_low", "btc_close",
    "btc_volume", "fear_greed_value", "btc_daily_return"
] if col in filtered_df.columns]

if summary_cols:
    st.subheader("Summary Statistics")
    st.dataframe(filtered_df[summary_cols].describe().T, use_container_width=True)

st.subheader("Important Derived Variables")
st.markdown(
    """
    - `holiday_flag`: 1 = holiday, 0 = non-holiday  
    - `day_type`: Holiday or Non-Holiday  
    - `return_category`: Positive, Negative, or Flat  
    - `high_volatility_flag`: 1 if the absolute daily return is above the median absolute return  
    """
)

st.header("3. Visual Storytelling")

col1, col2 = st.columns(2)

with col1:
    if "btc_daily_return" in filtered_df.columns:
        fig1 = px.line(
            filtered_df.sort_values("date"),
            x="date",
            y="btc_daily_return",
            title="Bitcoin Daily Return Over Time"
        )
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    if "btc_volume" in filtered_df.columns:
        fig2 = px.line(
            filtered_df.sort_values("date"),
            x="date",
            y="btc_volume",
            title="Bitcoin Trading Volume Over Time"
        )
        st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    if "day_type" in filtered_df.columns and "btc_daily_return" in filtered_df.columns:
        fig3 = px.box(
            filtered_df,
            x="day_type",
            y="btc_daily_return",
            color="day_type",
            title="BTC Daily Return by Holiday vs Non-Holiday"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    if "positive_return" in filtered_df.columns and "day_type" in filtered_df.columns:
        temp_counts = (
            filtered_df.groupby(["day_type", "positive_return"])
            .size()
            .reset_index(name="count")
        )
        fig4 = px.bar(
            temp_counts,
            x="day_type",
            y="count",
            color="positive_return",
            barmode="group",
            title="Positive Return Counts by Holiday Status"
        )
        st.plotly_chart(fig4, use_container_width=True)

if "fear_greed_value" in filtered_df.columns and "btc_volume" in filtered_df.columns:
    fig5 = px.scatter(
        filtered_df,
        x="fear_greed_value",
        y="btc_volume",
        trendline="ols",
        title="Fear & Greed Value vs BTC Volume"
    )
    st.plotly_chart(fig5, use_container_width=True)

st.header("4. Hypothesis Testing")

analysis_choice = st.selectbox(
    "Choose an analysis",
    [
        "One-Sample T-Test: Mean BTC Return vs 0",
        "Two-Sample T-Test: Holiday vs Non-Holiday Returns",
        "Chi-Square Test: Positive Return vs Holiday Flag",
        "Variance Comparison: Return Variance by Holiday Flag",
        "Correlation: Fear & Greed Value vs BTC Volume",
    ]
)

if analysis_choice == "One-Sample T-Test: Mean BTC Return vs 0":
    st.subheader("One-Sample T-Test")
    st.write("**Null hypothesis (H0):** Mean BTC daily return = 0")
    st.write("**Alternative hypothesis (H1):** Mean BTC daily return ≠ 0")

    series = filtered_df["btc_daily_return"].dropna()
    t_stat, p_value = stats.ttest_1samp(series, popmean=0)

    st.write(f"Sample size: **{len(series)}**")
    st.write(f"Sample mean: **{series.mean():.6f}**")
    st.write(f"T-statistic: **{t_stat:.4f}**")
    st.write(f"P-value: **{p_value:.6f}**")

    st.info("This test is appropriate because BTC daily return is a continuous variable and we are comparing its mean against 0.")
    st.warning("Limitation: financial return data may contain outliers and may not be perfectly normal.")
    st.success(interpretation_pvalue(p_value))

elif analysis_choice == "Two-Sample T-Test: Holiday vs Non-Holiday Returns":
    st.subheader("Two-Sample T-Test")
    st.write("**Null hypothesis (H0):** Mean BTC daily return is the same on holidays and non-holidays")
    st.write("**Alternative hypothesis (H1):** Mean BTC daily return is different on holidays and non-holidays")

    holiday_returns, non_holiday_returns = safe_two_sample_groups(
        filtered_df, "btc_daily_return", "holiday_flag", 1, 0
    )

    if len(holiday_returns) < 2 or len(non_holiday_returns) < 2:
        st.error("Not enough data to run this test.")
    else:
        t_stat, p_value = stats.ttest_ind(
            holiday_returns, non_holiday_returns, equal_var=False, nan_policy="omit"
        )

        st.write(f"Holiday sample size: **{len(holiday_returns)}**")
        st.write(f"Non-holiday sample size: **{len(non_holiday_returns)}**")
        st.write(f"Holiday mean return: **{holiday_returns.mean():.6f}**")
        st.write(f"Non-holiday mean return: **{non_holiday_returns.mean():.6f}**")
        st.write(f"T-statistic: **{t_stat:.4f}**")
        st.write(f"P-value: **{p_value:.6f}**")

        st.info("This test is appropriate because it compares the mean of a continuous variable across two groups.")
        st.warning("Limitation: holiday days may be much fewer than non-holiday days.")
        st.success(interpretation_pvalue(p_value))

elif analysis_choice == "Chi-Square Test: Positive Return vs Holiday Flag":
    st.subheader("Chi-Square Test of Independence")
    st.write("**Null hypothesis (H0):** Positive return is independent of holiday status")
    st.write("**Alternative hypothesis (H1):** Positive return is associated with holiday status")

    temp_df = filtered_df.dropna(subset=["positive_return", "holiday_flag"]).copy()
    temp_df["positive_return"] = temp_df["positive_return"].astype(int)
    temp_df["holiday_flag"] = temp_df["holiday_flag"].astype(int)

    contingency = pd.crosstab(temp_df["positive_return"], temp_df["holiday_flag"])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    st.write("Observed contingency table:")
    st.dataframe(contingency, use_container_width=True)

    st.write(f"Chi-square statistic: **{chi2:.4f}**")
    st.write(f"Degrees of freedom: **{dof}**")
    st.write(f"P-value: **{p_value:.6f}**")

    st.info("This test is appropriate because both variables are categorical.")
    st.warning("Limitation: if holiday rows are very few, expected counts may be small.")
    st.success(interpretation_pvalue(p_value))

elif analysis_choice == "Variance Comparison: Return Variance by Holiday Flag":
    st.subheader("Variance Comparison (F-Test)")
    st.write("**Null hypothesis (H0):** Return variance is the same for holidays and non-holidays")
    st.write("**Alternative hypothesis (H1):** Return variance is different for holidays and non-holidays")

    holiday_returns, non_holiday_returns = safe_two_sample_groups(
        filtered_df, "btc_daily_return", "holiday_flag", 1, 0
    )

    if len(holiday_returns) < 2 or len(non_holiday_returns) < 2:
        st.error("Not enough data to run this test.")
    else:
        var1 = np.var(holiday_returns, ddof=1)
        var2 = np.var(non_holiday_returns, ddof=1)

        if var1 >= var2:
            f_stat = var1 / var2 if var2 != 0 else np.inf
            dfn = len(holiday_returns) - 1
            dfd = len(non_holiday_returns) - 1
        else:
            f_stat = var2 / var1 if var1 != 0 else np.inf
            dfn = len(non_holiday_returns) - 1
            dfd = len(holiday_returns) - 1

        if np.isfinite(f_stat):
            p_one_tail = 1 - stats.f.cdf(f_stat, dfn, dfd)
            p_value = min(2 * min(p_one_tail, 1 - p_one_tail), 1.0)
        else:
            p_value = 0.0

        st.write(f"Holiday return variance: **{var1:.8f}**")
        st.write(f"Non-holiday return variance: **{var2:.8f}**")
        st.write(f"F-statistic: **{f_stat:.4f}**")
        st.write(f"P-value: **{p_value:.6f}**")

        st.info("This test is appropriate because the question is about difference in variability across two groups.")
        st.warning("Limitation: the F-test is sensitive to outliers and non-normality.")
        st.success(interpretation_pvalue(p_value))

elif analysis_choice == "Correlation: Fear & Greed Value vs BTC Volume":
    st.subheader("Correlation Analysis")
    method = st.radio("Choose correlation method", ["pearson", "spearman"], horizontal=True)

    st.write("**Null hypothesis (H0):** No association exists between Fear & Greed value and BTC volume")
    st.write("**Alternative hypothesis (H1):** An association exists between Fear & Greed value and BTC volume")

    temp = filtered_df[["fear_greed_value", "btc_volume"]].dropna()

    if len(temp) < 3:
        st.error("Not enough data to run correlation.")
    else:
        if method == "pearson":
            corr, p_value = stats.pearsonr(temp["fear_greed_value"], temp["btc_volume"])
        else:
            corr, p_value = stats.spearmanr(temp["fear_greed_value"], temp["btc_volume"])

        st.write(f"Method: **{method.title()}**")
        st.write(f"Sample size: **{len(temp)}**")
        st.write(f"Correlation coefficient: **{corr:.4f}**")
        st.write(f"P-value: **{p_value:.6f}**")

        st.info("This test is appropriate because both variables are quantitative.")
        st.warning("Limitation: correlation does not prove causation.")
        st.success(interpretation_pvalue(p_value))

st.header("5. Reflection / Limitations")
st.markdown(
    """
    - This analysis extends the original crypto and sentiment dataset with a holiday calendar.
    - The join key is `date`, which is simple and easy to explain.
    - Holiday days are fewer than non-holiday days, so some comparisons may be imbalanced.
    - Statistical significance does not automatically mean practical importance.
    - These results show association, not causation.
    """
)