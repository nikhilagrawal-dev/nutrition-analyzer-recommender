import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
from scipy import stats
from core.utils import plotly_dark_theme, csv_download

# ── outlier_detection.py ───────────────────────────────────────────────────

def render(df):
    """
    Render Hybrid Outlier Detection (IQR + Z-Score + Isolation Forest).
    """
    st.title("🔍 Nutritional Anomaly Detection")
    st.markdown("Identifies extreme nutritional profiles using statistical and machine learning techniques.")
    
    nutrient = st.sidebar.selectbox("Nutrient for Analysis", ["calories", "protein", "fat", "carbs", "fiber"], key="out_nut")
    
    # ── 1. IQR Method ──
    Q1 = df[nutrient].quantile(0.25)
    Q3 = df[nutrient].quantile(0.75)
    IQR = Q3 - Q1
    iqr_outliers = df[(df[nutrient] < (Q1 - 1.5 * IQR)) | (df[nutrient] > (Q3 + 1.5 * IQR))].index.tolist()
    
    # ── 2. Z-Score Method ──
    z_scores = np.abs(stats.zscore(df[nutrient]))
    z_outliers = df[z_scores > 3].index.tolist()
    
    # ── 3. Isolation Forest (ML) ──
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso_preds = iso.fit_predict(df[[nutrient]])
    iso_outliers = df[iso_preds == -1].index.tolist()
    
    # ── Comparison Matrix ──
    all_outliers = sorted(list(set(iqr_outliers + z_outliers + iso_outliers)))
    results = []
    for idx in all_outliers:
        row = df.loc[idx]
        results.append({
            "Food": row[df.columns[0]],
            "Method": ", ".join([m for m, o in [("IQR", iqr_outliers), ("Z-Score", z_outliers), ("IsoForest", iso_outliers)] if idx in o]),
            "Value": row[nutrient],
            "Category": row['category']
        })
    results_df = pd.DataFrame(results)
    
    # ── Visual Highlights ──
    st.markdown("### 🧬 Global Anomaly Map (Blue: Normal | Red: Outlier)")
    df_plot = df.copy().reset_index(drop=True)
    df_plot['is_anomaly'] = df_plot.index.isin(all_outliers)
    df_plot['Status'] = df_plot['is_anomaly'].map({True: 'Anomaly', False: 'Normal'})
    df_plot['index'] = df_plot.index

    fig_scatter = px.scatter(
        df_plot, x='index', y=nutrient,
        color='Status',
        hover_name=df_plot.columns[0],
        color_discrete_map={'Anomaly': '#f85149', 'Normal': '#58a6ff'},
        template="plotly_dark",
        title=f"Anomaly Highlight: {nutrient.capitalize()} (hover for food name)",
        labels={'index': 'Food Index'}
    )
    st.plotly_chart(plotly_dark_theme(fig_scatter), use_container_width=True)
    
    # ── Box Plots ──
    st.markdown("### 📊 Distribution & Variance")
    fig_box = px.box(
        df, y=nutrient, points="outliers",
        color_discrete_sequence=["#58a6ff"],
        template="plotly_dark",
        title=f"{nutrient.capitalize()} Box Plot (IQR Highlight)"
    )
    st.plotly_chart(plotly_dark_theme(fig_box), use_container_width=True)
    
    # ── Data Table ──
    st.markdown("### 📋 Detected Anomalies Table")
    st.dataframe(results_df, use_container_width=True)
    csv_download(results_df, "⬇️ Download Anomaly Report", "anomalies.csv")
