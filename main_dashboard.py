import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Global Budget Analytics Core",
    layout="wide"
)

# ---------------------------------------------------------
# LOAD DATA FROM CSV
# ---------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("Master_Global_Budgets_Historical.csv")
    return df


df = load_data()

st.title("🏛️ Global Government Budget Analytics Core")
st.markdown(
    "An interactive platform exploring public finance shifts, "
    "sector dominance, and predictive trajectories."
)

# ---------------------------------------------------------
# CHECK DATA
# ---------------------------------------------------------

if df.empty:
    st.error("Dataset is empty.")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR COUNTRY FILTER
# ---------------------------------------------------------

if "Country" not in df.columns:
    st.error("The 'Country' column was not found in the dataset.")
    st.stop()

countries = sorted(df["Country"].dropna().unique().tolist())

selected_country = st.sidebar.selectbox(
    "Select a Country to Filter",
    countries
)

country_df = df[df["Country"] == selected_country].copy()

# ---------------------------------------------------------
# FIND IMPORTANT COLUMNS
# ---------------------------------------------------------

budget_column = None

possible_budget_columns = [
    "Total_Budget_Billions_USD",
    "total_budget_billions_usd",
    "Total Budget Billions USD",
    "Total_Budget"
]

for col in possible_budget_columns:
    if col in df.columns:
        budget_column = col
        break

if budget_column is None:
    st.error(
        "Total budget column was not found. "
        "Please check the CSV column names."
    )
    st.stop()

# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------

tab_macro, tab_sectors, tab_anomalies, tab_research_lab = st.tabs([
    "📈 Macro Historical Trends",
    "🍕 Sector Structural Spreads",
    "🔍 Statistical Anomalies",
    "🔬 Macro Economic Research Lab"
])

# =========================================================
# TAB 1 — MACRO HISTORICAL TRENDS
# =========================================================

with tab_macro:

    st.header("Global Spending Growth Pathways")

    df_macro = country_df.copy()

    if "Year" in df_macro.columns:
        df_macro = df_macro.sort_values("Year")

    elif "year" in df_macro.columns:
        df_macro = df_macro.sort_values("year")
        df_macro["Year"] = df_macro["year"]

    else:
        st.error("Year column was not found.")
        st.stop()

    df_macro = df_macro.rename(
        columns={
            budget_column: "total_budget_billions_usd"
        }
    )

    if not df_macro.empty:

        fig = px.line(
            df_macro,
            x="Year",
            y="total_budget_billions_usd",
            title=f"Historical Expenditure Strategy: {selected_country}",
            template="plotly_dark",
            labels={
                "total_budget_billions_usd":
                "Total Budget (Billions USD)"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No records found for the selection.")


# =========================================================
# TAB 2 — SECTOR STRUCTURAL SPREADS
# =========================================================

with tab_sectors:

    st.header("Allocation Distribution Analysis")

    # Identify sector columns automatically
    excluded_columns = [
        "Country",
        "Year",
        "year",
        budget_column
    ]

    sector_columns = [
        col for col in country_df.columns
        if col not in excluded_columns
        and pd.api.types.is_numeric_dtype(country_df[col])
    ]

    if len(sector_columns) == 0:

        st.warning(
            "No sector allocation columns were found in the dataset."
        )

    else:

        sector_df = country_df.copy()

        if "Year" in sector_df.columns:
            year_column = "Year"
        else:
            year_column = "year"

        # Convert sector data into long format
        df_sec = sector_df.melt(
            id_vars=[year_column],
            value_vars=sector_columns,
            var_name="sector_name",
            value_name="allocated_percentage"
        )

        df_sec = df_sec.dropna()

        col_c1, col_c2 = st.columns(2)

        with col_c1:

            fig_area = px.area(
                df_sec,
                x=year_column,
                y="allocated_percentage",
                color="sector_name",
                title="Structural Budget Shifts Over Time",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_area,
                use_container_width=True
            )

        with col_c2:

            fig_box = px.box(
                df_sec,
                x="sector_name",
                y="allocated_percentage",
                color="sector_name",
                title="Variance and Spread Across Sectors",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_box,
                use_container_width=True
            )


# =========================================================
# TAB 3 — STATISTICAL ANOMALIES
# =========================================================

with tab_anomalies:

    st.header("Descriptive Outlier Detection")

    st.markdown(
        "Identifies fiscal years where spending shifted sharply "
        "outside normal historical baselines."
    )

    df_anomaly = country_df.copy()

    if "Year" in df_anomaly.columns:
        year_column = "Year"
    else:
        year_column = "year"

    df_anomaly = df_anomaly[
        [year_column, budget_column]
    ].dropna()

    df_anomaly = df_anomaly.rename(
        columns={
            budget_column: "total_budget_billions_usd"
        }
    )

    if not df_anomaly.empty:

        mean_val = df_anomaly[
            "total_budget_billions_usd"
        ].mean()

        std_val = df_anomaly[
            "total_budget_billions_usd"
        ].std()

        if std_val != 0 and not pd.isna(std_val):

            df_anomaly["z_score"] = (
                df_anomaly["total_budget_billions_usd"]
                - mean_val
            ) / std_val

            anomalies = df_anomaly[
                df_anomaly["z_score"].abs() > 1.96
            ]

            st.write(
                "### Flagged Fiscal Outlier Periods "
                "(Z-Score > 1.96):"
            )

            if not anomalies.empty:

                st.dataframe(
                    anomalies,
                    use_container_width=True
                )

            else:

                st.success(
                    "No extreme statistical outliers discovered."
                )

        else:

            st.info(
                "Standard deviation is zero or unavailable."
            )

    else:

        st.info("No records available for anomaly detection.")


# =========================================================
# TAB 4 — MACRO ECONOMIC RESEARCH LAB
# =========================================================

with tab_research_lab:

    st.header("🔬 Deep Exploratory Research Workspace")

    st.markdown(
        "Advanced analytical modules calculating structural "
        "correlation shifts and spending volatility."
    )

    # -----------------------------------------------------
    # CORRELATION MATRIX
    # -----------------------------------------------------

    st.subheader(
        "Cross-Sector Allocation Correlation Matrix"
    )

    correlation_columns = [
        col for col in sector_columns
        if col in country_df.columns
    ]

    if len(correlation_columns) >= 2:

        corr_matrix = country_df[
            correlation_columns
        ].corr()

        fig_heat = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu",
            labels={
                "color": "Correlation Coefficient"
            },
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )

    else:

        st.info(
            "At least two sector columns are required "
            "for correlation analysis."
        )

    # -----------------------------------------------------
    # VOLATILITY INDEX
    # -----------------------------------------------------

    st.subheader(
        "Volatility Index & Rolling Statistics"
    )

    df_vol = country_df.copy()

    df_vol = df_vol.rename(
        columns={
            budget_column:
            "total_budget_billions_usd"
        }
    )

    df_vol = df_vol[
        [year_column, "total_budget_billions_usd"]
    ].dropna()

    df_vol = df_vol.sort_values(year_column)

    if not df_vol.empty:

        df_vol["rolling_mean"] = (
            df_vol[
                "total_budget_billions_usd"
            ]
            .rolling(window=10)
            .mean()
        )

        df_vol["rolling_std"] = (
            df_vol[
                "total_budget_billions_usd"
            ]
            .rolling(window=10)
            .std()
        )

        df_vol["volatility_index"] = (
            df_vol["rolling_std"]
            / df_vol["rolling_mean"]
        ) * 100

        st.markdown(
            "Rolling 10-year Volatility Index "
            "(Coefficient of Variation)"
        )

        fig_vol = go.Figure()

        fig_vol.add_trace(
            go.Scatter(
                x=df_vol[year_column],
                y=df_vol["volatility_index"],
                mode="lines+markers",
                name="Volatility Index"
            )
        )

        fig_vol.update_layout(
            template="plotly_dark",
            yaxis_title="Volatility Index (%)"
        )

        st.plotly_chart(
            fig_vol,
            use_container_width=True
        )

        st.write(
            "Recent rolling statistics "
            "(non-null rows):"
        )

        st.dataframe(
            df_vol.dropna().tail(10),
            use_container_width=True
        )

    else:

        st.info(
            "Not enough historical data to compute "
            "volatility metrics."
        )

    # -----------------------------------------------------
    # POLYNOMIAL PROJECTION
    # -----------------------------------------------------

    st.subheader(
        "Polynomial Projection (Analytical)"
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:

        proj_degree = st.selectbox(
            "Projection degree",
            [1, 2, 3],
            index=1
        )

        proj_horizon = st.number_input(
            "Forecast horizon year",
            min_value=2025,
            max_value=2050,
            value=2035
        )

    with col_p2:

        apply_scenario = st.checkbox(
            "Apply scenario shock to projection"
        )

        shock_pct = st.slider(
            "Shock %",
            -50,
            100,
            0
        )

    if not df_vol.empty:

        x = df_vol[
            year_column
        ].astype(int).values

        y = df_vol[
            "total_budget_billions_usd"
        ].astype(float).values

        if len(x) > proj_degree:

            coeffs = np.polyfit(
                x,
                y,
                deg=proj_degree
            )

            poly = np.poly1d(coeffs)

            years_future = np.arange(
                int(x.max()) + 1,
                int(proj_horizon) + 1
            )

            proj_vals = poly(years_future)

            if (
                apply_scenario
                and shock_pct != 0
            ):

                proj_vals = proj_vals * (
                    1 + shock_pct / 100.0
                )

            fig_proj = go.Figure()

            fig_proj.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers+lines",
                    name="Historical"
                )
            )

            fig_proj.add_trace(
                go.Scatter(
                    x=years_future,
                    y=proj_vals,
                    mode="lines",
                    name="Projection",
                    line=dict(
                        dash="dash"
                    )
                )
            )

            fig_proj.update_layout(
                title=(
                    f"Polynomial Projection "
                    f"(deg {proj_degree}) "
                    f"for {selected_country}"
                ),
                template="plotly_dark",
                xaxis_title="Year",
                yaxis_title=(
                    "Budget (Billions USD)"
                )
            )

            st.plotly_chart(
                fig_proj,
                use_container_width=True
            )

            df_proj_out = pd.DataFrame({
                "year": years_future,
                "projected_budget": proj_vals
            })

            st.dataframe(
                df_proj_out.style.format(
                    {
                        "projected_budget":
                        "${:,.2f}"
                    }
                ),
                use_container_width=True
            )

        else:

            st.warning(
                "Not enough historical points "
                "for the selected polynomial degree."
            )