import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="FHB Trait Dashboard", layout="wide")

st.title("🌾 FHB Trait Dashboard")
st.write("Explore phenotypic variation, correlations, and genotype profiles interactively.")

# --- File Upload ---
st.sidebar.header("Upload Phenotype Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Sidebar Controls ---
    st.sidebar.header("Controls")
    trait = st.sidebar.selectbox("Select Trait", df.columns)

    # --- Trait Distribution ---
    st.subheader(f"Distribution of {trait}")
    fig = px.histogram(df, x=trait, nbins=40, marginal="box",
                       title=f"{trait} Distribution",
                       color_discrete_sequence=["#7BC8A4"])
    st.plotly_chart(fig, use_container_width=True)

    # --- Summary Stats ---
    st.subheader("Summary Statistics")
    stats = df[trait].describe().to_frame()
    stats.loc["skewness"] = df[trait].skew()
    st.dataframe(stats)

    # --- Correlation Matrix ---
    st.subheader("Trait Correlation Matrix")
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto",
                         color_continuous_scale="RdBu_r",
                         title="Correlation Heatmap")
    st.plotly_chart(fig_corr, use_container_width=True)

    # --- Scatter Explorer ---
    st.subheader("Scatterplot Explorer")
    col1, col2 = st.columns(2)
    with col1:
        x_trait = st.selectbox("X-axis Trait", numeric_df.columns)
    with col2:
        y_trait = st.selectbox("Y-axis Trait", numeric_df.columns)

    fig_scatter = px.scatter(df, x=x_trait, y=y_trait,
                             trendline="ols",
                             color_discrete_sequence=["#F4A261"])
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Genotype Viewer ---
    st.subheader("Genotype Detail Viewer")
    genotype_col = st.selectbox("Select Genotype Column", df.columns)
    genotype = st.selectbox("Choose Genotype", df[genotype_col].unique())

    geno_data = df[df[genotype_col] == genotype]
    st.write(f"### Trait Profile for {genotype}")
    st.dataframe(geno_data)

else:
    st.info("Upload a CSV file to begin exploring your FHB data.")# rebuild
