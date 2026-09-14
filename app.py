import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


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
# FIND GDP.CSV
# =========================================================

# Get the folder where app.py is located
BASE_DIR = Path(__file__).resolve().parent

# Look for GDP.csv in the same folder as app.py
DATA_FILE = BASE_DIR / "GDP.csv"


# =========================================================
# CHECK IF FILE EXISTS
# =========================================================

if not DATA_FILE.exists():

    st.error("GDP.csv could not be found.")

    st.write(
        "Please make sure your files are arranged like this:"
    )

    st.code(
        """
World-GDP-Analysis/
│
├── app.py
├── GDP.csv
└── requirements.txt
        """
    )

    st.write(
        f"Streamlit is currently looking here:"
    )

    st.code(str(DATA_FILE))

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(file_path):

    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )

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
    # Clean GDP per Capita
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


# Load the CSV
try:

    df = load_data(DATA_FILE)

except Exception as e:

    st.error(
        f"An error occurred while reading GDP.csv: {e}"
    )

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
        "Your GDP.csv file is missing the following columns:"
    )

    for column in missing_columns:
        st.write(f"- {column}")

    st.write("Columns found in your file:")

    st.write(list(df.columns))

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Dashboard Filters")


# =========================================================
# COUNTRY FILTER
# =========================================================

countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(
        df["Country"]
        .dropna()
        .unique()
    ),
    default=[]
)


# =========================================================
# GDP GROWTH FILTER
# =========================================================

growth_values = df["GDP Growth"].dropna()


growth_min = float(growth_values.min())
growth_max = float(growth_values.max())


growth_range = st.sidebar.slider(
    "GDP Growth Range (%)",
    min_value=growth_min,
    max_value=growth_max,
    value=(growth_min, growth_max)
)


# =========================================================
# GDP PER CAPITA FILTER
# =========================================================

income_values = df["GDP per capita"].dropna()


income_min = float(income_values.min())
income_max = float(income_values.max())


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


if countries:

    filtered_df = filtered_df[
        filtered_df["Country"].isin(countries)
    ]


filtered_df = filtered_df[
    (filtered_df["GDP Growth"] >= growth_range[0])
    &
    (filtered_df["GDP Growth"] <= growth_range[1])
]


filtered_df = filtered_df[
    (filtered_df["GDP per capita"] >= income_range[0])
    &
    (filtered_df["GDP per capita"] <= income_range[1])
]


# =========================================================
# CHECK FILTERED DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "No countries match the selected filters. "
        "Please change the filters."
    )

    st.stop()


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("Key Performance Indicators")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Countries",
        f"{len(filtered_df):,}"
    )


with col2:

    total_gdp = filtered_df[
        "GDP (nominal, 2023)"
    ].sum()

    st.metric(
        "Total GDP",
        f"${total_gdp / 1e12:.2f}T"
    )


with col3:

    average_gdp_per_capita = filtered_df[
        "GDP per capita"
    ].mean()

    st.metric(
        "Average GDP per Capita",
        f"${average_gdp_per_capita:,.0f}"
    )


with col4:

    average_growth = filtered_df[
        "GDP Growth"
    ].mean()

    st.metric(
        "Average GDP Growth",
        f"{average_growth:.2f}%"
    )


# =========================================================
# DATA PREVIEW
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


scatter_df = filtered_df.dropna(
    subset=[
        "GDP (nominal, 2023)",
        "GDP per capita",
        "Population 2023"
    ]
)


fig_scatter = px.scatter(
    scatter_df,
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


population_df = filtered_df.dropna(
    subset=[
        "Population 2023",
        "GDP (nominal, 2023)",
        "GDP per capita"
    ]
)


fig_population = px.scatter(
    population_df,
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
    .dropna(subset=["Share of World GDP"])
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


growth_capita_df = filtered_df.dropna(
    subset=[
        "GDP per capita",
        "GDP Growth",
        "GDP (nominal, 2023)"
    ]
)


if len(growth_capita_df) >= 3:

    fig_growth_capita = px.scatter(
        growth_capita_df,
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
        growth_capita_df,
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