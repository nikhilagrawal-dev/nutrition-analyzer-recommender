import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from core.utils import plotly_dark_theme, csv_download

# ── similarity_engine.py ──────────────────────────────────────────────────────

def render(df):
    """
    Render Similar Food Recommendation Engine (Vector Similarity).
    """
    st.title("🔍 Nutritional Substitutes")
    st.markdown("Finds nutritionally similar alternatives to any food item using **Cosine Vector Similarity**.")
    
    food_col = df.columns[0]
    food_list = df[food_col].tolist()
    
    selected_food = st.selectbox("Search Base Food", food_list)
    
    # ── Similarity Logic ──
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Calculate Similarity
    sim_matrix = cosine_similarity(X_scaled)
    
    # Find matching index
    idx = df[df[food_col] == selected_food].index[0]
    # Positional index in matrix
    pos_idx = df.index.get_loc(idx)
    
    sim_scores = list(enumerate(sim_matrix[pos_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Top 5 alternatives (skip index 0 which is self)
    top_5_indices = [df.index[i] for i, score in sim_scores[1:6]]
    similar_df = df.loc[top_5_indices].copy()
    
    st.markdown(f"### 📋 Top 5 Substitutes for **{selected_food}**")
    
    # ── Radar Chart Comparison ──
    # Normalize features for radar chart display
    base_data = df.loc[idx][features]
    max_val = base_data.max() if base_data.max() > 0 else 1.0 # Scalar check
    
    fig_radar = go.Figure()
    
    # Add Base Food
    fig_radar.add_trace(go.Scatterpolar(
        r=base_data.values / max_val,
        theta=features,
        fill='toself',
        name=f"Base: {selected_food}",
        line_color="#58a6ff"
    ))
    
    # Add Top 1 Substitute
    sub_row = similar_df.iloc[0][features]
    sub_max = sub_row.max() if sub_row.max() > 0 else 1.0
    fig_radar.add_trace(go.Scatterpolar(
        r=sub_row.values / sub_max,
        theta=features,
        fill='toself',
        name=f"Sub: {similar_df.iloc[0][food_col]}",
        line_color="#3fb950"
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.5], gridcolor="#30363d"),
            bgcolor="#0d1117"
        ),
        showlegend=True,
        title="Nutritional Blueprint Comparison (Normalized)"
    )
    st.plotly_chart(plotly_dark_theme(fig_radar), use_container_width=True)
    
    # ── Comparison Table ──
    st.dataframe(similar_df[[food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]], use_container_width=True)
    csv_download(similar_df, "⬇️ Download Similar Foods", "substitutes.csv")
