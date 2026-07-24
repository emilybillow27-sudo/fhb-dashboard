import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="FHB Trait Dashboard", layout="wide")
st.title("🌾 FHB Trait Dashboard")
st.write("Explore phenotypic variation, correlations, and genotype profiles interactively.")

# --- Sidebar Upload ---
st.sidebar.header("Upload Phenotype Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# --- Helper: Clean Trait Names ---
def clean_columns(df):
    rename_map = {
        "FHB.incidence.....CO_321.0001149": "INC",
        "FHB.severity.....CO_321.0001440": "SEV",
        "FHB.disease.index.....CO_321.0501030": "DI",
        "FHB.don.....CO_321.0001000": "DON",
        "studyYear": "Year",
        "FHB.grain.incidence.....CO_321.0001155": "FDK",   # training dataset
        "grainIncidence": "FDK",                           # alternate naming
        "FDK": "FDK"                                       # testing dataset
    }
    df = df.rename(columns={col: rename_map.get(col, col) for col in df.columns})
    return df

# --- Helper: Auto-detect genotype column ---
def detect_genotype_column(df):
    candidates = ["uID", "ID", "Genotype", "Line", "Entry", "FullSampleName"]
    for col in df.columns:
        if col in candidates:
            return col
    return None

# --- Main App ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = clean_columns(df)

    # Detect genotype column
    genotype_col = detect_genotype_column(df)
    if genotype_col is None:
        st.warning("⚠ No genotype identifier column found. Please check your CSV.")
    else:
        st.sidebar.success(f"Detected genotype column: **{genotype_col}**")

    # Numeric traits
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # --- Sidebar Controls ---
    st.sidebar.header("Trait Controls")
    trait = st.sidebar.selectbox("Select Trait for Distribution", numeric_cols)

    # --- Trait Distribution ---
    st.subheader(f"Distribution of {trait}")
    fig = px.histogram(
        df, x=trait, nbins=40, marginal="box",
        title=f"{trait} Distribution",
        color_discrete_sequence=["#7BC8A4"]  # mint aesthetic
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Summary Stats ---
    st.subheader("Summary Statistics")
    stats = df[trait].describe().to_frame()
    stats.loc["skewness"] = df[trait].skew()
    st.dataframe(stats)

    # --- Correlation Matrix ---
    st.subheader("Trait Correlation Matrix")
    corr = df[numeric_cols].corr()
    fig_corr = px.imshow(
        corr, text_auto=True, aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Heatmap"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # --- Scatter Explorer ---
    st.subheader("Scatterplot Explorer")
    col1, col2 = st.columns(2)

    # Smart defaults
    default_x = "INC" if "INC" in numeric_cols else numeric_cols[0]
    default_y = "SEV" if "SEV" in numeric_cols else numeric_cols[min(1, len(numeric_cols)-1)]

    with col1:
        x_trait = st.selectbox("X-axis Trait", numeric_cols, index=numeric_cols.index(default_x))
    with col2:
        y_trait = st.selectbox("Y-axis Trait", numeric_cols, index=numeric_cols.index(default_y))

    fig_scatter = px.scatter(
        df, x=x_trait, y=y_trait,
        trendline="ols",
        color_discrete_sequence=["#F4A261"]  # peach aesthetic
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Genotype Viewer ---
    st.subheader("Genotype Detail Viewer")

    if genotype_col:
        selected_genotype = st.selectbox("Choose Genotype", sorted(df[genotype_col].unique()))
        geno_data = df[df[genotype_col] == selected_genotype]

        st.write(f"### Trait Profile for {selected_genotype}")
        st.dataframe(geno_data)
    else:
        st.info("Upload a dataset with a genotype identifier column to enable this viewer.")

else:
    st.info("Upload a CSV file to begin exploring your FHB data.")