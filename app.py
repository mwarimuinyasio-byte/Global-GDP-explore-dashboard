import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="World GDP Data Analysis",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("World GDP Data Analysis Dashboard")

st.write(
    "Interactive analysis of GDP, GDP growth, population, "
    "GDP per capita, and share of world GDP."
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("GDP.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # -----------------------------------------------------
    # Clean GDP
    # -----------------------------------------------------

    if "GDP (nominal, 2023)" in df.columns:

        df["GDP (nominal, 2023)"] = (
            df["GDP (nominal, 2023)"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace("−", "-", regex=False)
            .str.strip()
        )

        df["GDP (nominal, 2023)"] = pd.to_numeric(
            df["GDP (nominal, 2023)"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean GDP per capita
    # -----------------------------------------------------

    if "GDP per capita" in df.columns:

        df["GDP per capita"] = (
            df["GDP per capita"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace("−", "-", regex=False)
            .str.strip()
        )

        df["GDP per capita"] = pd.to_numeric(
            df["GDP per capita"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean GDP Growth
    # -----------------------------------------------------

    if "GDP Growth" in df.columns:

        df["GDP Growth"] = (
            df["GDP Growth"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace("−", "-", regex=False)
            .str.strip()
        )

        df["GDP Growth"] = pd.to_numeric(
            df["GDP Growth"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean Share of World GDP
    # -----------------------------------------------------

    if "Share of World GDP" in df.columns:

        df["Share of World GDP"] = (
            df["Share of World GDP"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace("−", "-", regex=False)
            .str.strip()
        )

        df["Share of World GDP"] = pd.to_numeric(
            df["Share of World GDP"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean Population
    # -----------------------------------------------------

    if "Population 2023" in df.columns:

        df["Population 2023"] = (
            df["Population 2023"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("−", "-", regex=False)
            .str.strip()
        )

        df["Population 2023"] = pd.to_numeric(
            df["Population 2023"],
            errors="coerce"
        )

    return df


# Load dataset
try:
    df = load_data()

except FileNotFoundError:

    st.error(
        "GDP.csv was not found. Make sure GDP.csv is in the same "
        "folder as app.py."
    )

    st.stop()

except Exception as e:

    st.error(f"Error loading the dataset: {e}")

    st.stop()


# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "Country",
    "GDP (nominal, 2023)",
    "GDP Growth",
    "Population 2023",
    "GDP per capita",
    "Share of World GDP"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing from GDP.csv:"
    )

    for column in missing_columns:
        st.write(f"- {column}")

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Dashboard Filters")


# ---------------------------------------------------------
# Country Filter
# ---------------------------------------------------------

countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(
        df["Country"]
        .dropna()
        .unique()
    ),
    default=[]
)


# ---------------------------------------------------------
# GDP Growth Filter
# ---------------------------------------------------------

growth_min = float(
    df["GDP Growth"]
    .dropna()
    .min()
)

growth_max = float(
    df["GDP Growth"]
    .dropna()
    .max()
)

growth_range = st.sidebar.slider(
    "GDP Growth Range (%)",
    min_value=growth_min,
    max_value=growth_max,
    value=(growth_min, growth_max)
)


# ---------------------------------------------------------
# GDP Per Capita Filter
# ---------------------------------------------------------

income_min = float(
    df["GDP per capita"]
    .dropna()
    .min()
)

income_max = float(
    df["GDP per capita"]
    .dropna()
    .max()
)

income_range = st.sidebar.slider(
    "GDP per Capita Range ($)",
    min_value=income_min,
    max_value=income_max,
    value=(income_min, income_max)
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


# Country filter
if countries:

    filtered_df = filtered_df[
        filtered_df["Country"].isin(countries)
    ]


# GDP Growth filter
filtered_df = filtered_df[
    (filtered_df["GDP Growth"] >= growth_range[0])
    &
    (filtered_df["GDP Growth"] <= growth_range[1])
]


# GDP per capita filter
filtered_df = filtered_df[
    (filtered_df["GDP per capita"] >= income_range[0])
    &
    (filtered_df["GDP per capita"] <= income_range[1])
]


# =========================================================
# CHECK IF FILTER RETURNED DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "No countries match the selected filters. "
        "Please adjust the filters in the sidebar."
    )

    st.stop()


# =========================================================
# KEY PERFORMANCE INDICATORS
# =========================================================

st.subheader("Key Performance Indicators")


col1, col2, col3, col4 = st.columns(4)


# ---------------------------------------------------------
# Number of Countries
# ---------------------------------------------------------

with col1:

    st.metric(
        "Countries",
        f"{len(filtered_df):,}"
    )


# ---------------------------------------------------------
# Total GDP
# ---------------------------------------------------------

with col2:

    total_gdp = filtered_df[
        "GDP (nominal, 2023)"
    ].sum()

    st.metric(
        "Total GDP",
        f"${total_gdp / 1e12:.2f}T"
    )


# ---------------------------------------------------------
# Average GDP Per Capita
# ---------------------------------------------------------

with col3:

    avg_gdp_per_capita = filtered_df[
        "GDP per capita"
    ].mean()

    st.metric(
        "Average GDP per Capita",
        f"${avg_gdp_per_capita:,.0f}"
    )


# ---------------------------------------------------------
# Average GDP Growth
# ---------------------------------------------------------

with col4:

    avg_growth = filtered_df[
        "GDP Growth"
    ].mean()

    st.metric(
        "Average GDP Growth",
        f"{avg_growth:.2f}%"
    )


# =========================================================
# DATASET PREVIEW
# =========================================================

st.subheader("Dataset Preview")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# =========================================================
# DATASET INFORMATION
# =========================================================

st.subheader("Dataset Information")


info_col1, info_col2, info_col3 = st.columns(3)


with info_col1:

    st.write("Number of Rows")

    st.write(
        f"{filtered_df.shape[0]:,}"
    )


with info_col2:

    st.write("Number of Columns")

    st.write(
        filtered_df.shape[1]
    )


with info_col3:

    st.write("Missing Values")

    st.write(
        f"{filtered_df.isnull().sum().sum():,}"
    )


# =========================================================
# TOP COUNTRIES BY GDP
# =========================================================

st.subheader("Top Countries by GDP")


top_gdp = (
    filtered_df
    .sort_values(
        by="GDP (nominal, 2023)",
        ascending=False
    )
    .head(15)
)


fig_gdp = px.bar(
    top_gdp,
    x="Country",
    y="GDP (nominal, 2023)",
    title="Top 15 Countries by Nominal GDP",
    labels={
        "GDP (nominal, 2023)": "GDP ($)"
    },
    text_auto=".2s"
)


fig_gdp.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45
)


st.plotly_chart(
    fig_gdp,
    use_container_width=True
)


# =========================================================
# TOP COUNTRIES BY GDP PER CAPITA
# =========================================================

st.subheader("GDP per Capita Analysis")


top_per_capita = (
    filtered_df
    .sort_values(
        by="GDP per capita",
        ascending=False
    )
    .head(15)
)


fig_per_capita = px.bar(
    top_per_capita,
    x="Country",
    y="GDP per capita",
    title="Top 15 Countries by GDP per Capita",
    labels={
        "GDP per capita": "GDP per Capita ($)"
    },
    text_auto=".2s"
)


fig_per_capita.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45
)


st.plotly_chart(
    fig_per_capita,
    use_container_width=True
)


# =========================================================
# GDP GROWTH
# =========================================================

st.subheader("GDP Growth Analysis")


growth_df = (
    filtered_df
    .sort_values(
        by="GDP Growth",
        ascending=False
    )
    .head(15)
)


fig_growth = px.bar(
    growth_df,
    x="Country",
    y="GDP Growth",
    title="Top 15 Countries by GDP Growth",
    labels={
        "GDP Growth": "GDP Growth (%)"
    },
    text="GDP Growth"
)


fig_growth.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)


fig_growth.update_layout(
    template="plotly_white",
    xaxis_tickangle=-45
)


st.plotly_chart(
    fig_growth,
    use_container_width=True
)


# =========================================================
# GDP DISTRIBUTION
# =========================================================

st.subheader("GDP Distribution")


fig_hist = px.histogram(
    filtered_df,
    x="GDP (nominal, 2023)",
    nbins=30,
    title="Distribution of Nominal GDP",
    labels={
        "GDP (nominal, 2023)": "GDP ($)"
    }
)


fig_hist.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_hist,
    use_container_width=True
)


# =========================================================
# GDP PER CAPITA DISTRIBUTION
# =========================================================

st.subheader("GDP per Capita Distribution")


fig_hist_capita = px.histogram(
    filtered_df,
    x="GDP per capita",
    nbins=30,
    title="Distribution of GDP per Capita",
    labels={
        "GDP per capita": "GDP per Capita ($)"
    }
)


fig_hist_capita.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_hist_capita,
    use_container_width=True
)


# =========================================================
# GDP GROWTH DISTRIBUTION
# =========================================================

st.subheader("GDP Growth Distribution")


fig_growth_hist = px.histogram(
    filtered_df,
    x="GDP Growth",
    nbins=30,
    title="Distribution of GDP Growth",
    labels={
        "GDP Growth": "GDP Growth (%)"
    }
)


fig_growth_hist.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_growth_hist,
    use_container_width=True
)


# =========================================================
# GDP VS GDP PER CAPITA
# =========================================================

st.subheader("GDP vs GDP per Capita")


fig_scatter = px.scatter(
    filtered_df,
    x="GDP (nominal, 2023)",
    y="GDP per capita",
    size="Population 2023",
    hover_name="Country",
    hover_data=[
        "GDP Growth",
        "Share of World GDP"
    ],
    title="Nominal GDP vs GDP per Capita",
    labels={
        "GDP (nominal, 2023)": "GDP ($)",
        "GDP per capita": "GDP per Capita ($)",
        "Population 2023": "Population"
    }
)


fig_scatter.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# =========================================================
# POPULATION VS GDP
# =========================================================

st.subheader("Population vs GDP")


fig_population = px.scatter(
    filtered_df,
    x="Population 2023",
    y="GDP (nominal, 2023)",
    size="GDP per capita",
    hover_name="Country",
    hover_data=[
        "GDP Growth",
        "Share of World GDP"
    ],
    title="Population vs Nominal GDP",
    labels={
        "Population 2023": "Population",
        "GDP (nominal, 2023)": "GDP ($)"
    }
)


fig_population.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_population,
    use_container_width=True
)


# =========================================================
# SHARE OF WORLD GDP
# =========================================================

st.subheader("Share of World GDP")


world_share = (
    filtered_df
    .sort_values(
        by="Share of World GDP",
        ascending=False
    )
    .head(10)
)


fig_world_share = px.pie(
    world_share,
    names="Country",
    values="Share of World GDP",
    title="Top 10 Countries by Share of World GDP"
)


fig_world_share.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_world_share,
    use_container_width=True
)


# =========================================================
# GDP GROWTH VS GDP PER CAPITA
# =========================================================

st.subheader("GDP Growth vs GDP per Capita")


# Only use trendline when enough valid rows exist
trend_df = filtered_df[
    [
        "GDP per capita",
        "GDP Growth",
        "GDP (nominal, 2023)",
        "Population 2023",
        "Share of World GDP",
        "Country"
    ]
].dropna()


if len(trend_df) >= 3:

    fig_growth_capita = px.scatter(
        trend_df,
        x="GDP per capita",
        y="GDP Growth",
        size="GDP (nominal, 2023)",
        hover_name="Country",
        hover_data=[
            "Population 2023",
            "Share of World GDP"
        ],
        title="GDP Growth vs GDP per Capita",
        labels={
            "GDP per capita": "GDP per Capita ($)",
            "GDP Growth": "GDP Growth (%)"
        },
        trendline="ols"
    )

else:

    fig_growth_capita = px.scatter(
        trend_df,
        x="GDP per capita",
        y="GDP Growth",
        hover_name="Country",
        title="GDP Growth vs GDP per Capita"
    )


fig_growth_capita.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_growth_capita,
    use_container_width=True
)


# =========================================================
# CORRELATION ANALYSIS
# =========================================================

st.subheader("Correlation Analysis")


numeric_columns = [
    "GDP (nominal, 2023)",
    "GDP Growth",
    "Population 2023",
    "GDP per capita",
    "Share of World GDP"
]


correlation = filtered_df[
    numeric_columns
].corr()


fig_corr = px.imshow(
    correlation,
    text_auto=".2f",
    title="Correlation Heatmap",
    aspect="auto"
)


fig_corr.update_layout(
    template="plotly_white"
)


st.plotly_chart(
    fig_corr,
    use_container_width=True
)


# =========================================================
# DESCRIPTIVE STATISTICS
# =========================================================

st.subheader("Descriptive Statistics")


st.dataframe(
    filtered_df[
        numeric_columns
    ].describe(),
    use_container_width=True
)


# =========================================================
# SORTING TABLE
# =========================================================

st.subheader("Sort Countries")


sort_column = st.selectbox(
    "Select column to sort by",
    options=filtered_df.columns
)


sort_order = st.radio(
    "Sort Order",
    ["Ascending", "Descending"],
    horizontal=True
)


sorted_df = filtered_df.sort_values(
    by=sort_column,
    ascending=(sort_order == "Ascending")
)


st.dataframe(
    sorted_df,
    use_container_width=True
)


# =========================================================
# COUNTRY SEARCH
# =========================================================

st.subheader("Search for a Country")


search_country = st.text_input(
    "Enter country name"
)


if search_country:

    search_result = df[
        df["Country"].str.contains(
            search_country,
            case=False,
            na=False
        )
    ]

    if not search_result.empty:

        st.dataframe(
            search_result,
            use_container_width=True
        )

    else:

        st.warning(
            "No country found."
        )


# =========================================================
# DOWNLOAD DATA
# =========================================================

st.subheader("Download Data")


csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_gdp_dataset.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.write(
    "World GDP Data Analysis Dashboard"
)