import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.utils import plotly_dark_theme, csv_download, render_card

# ── nutrition_score.py ───────────────────────────────────────────────────────

def render(df):
    """
    Render Nutrition Score System.
    """
    st.title("🏆 Smart Nutrition Score")
    st.markdown("Calculates a 0-100 score based on nutrient density. Reward: **Protein & Fiber**. Penalty: **Sat.Fat & Calories**.")
    
    # ── Scoring Formula ──
    df = df.copy()
    sat_fat = df['sat.fat'] if 'sat.fat' in df.columns else 0
    score = (df['protein'] * 2) + (df['fiber'] * 2) - (df['fat'] * 0.5) - (sat_fat * 2) - (df['calories'] / 50)
    
    # Percentile-based 0-100 scaling
    min_s, max_s = score.min(), score.max()
    df['health_score'] = ((score - min_s) / (max_s - min_s)) * 100
    df = df.sort_values("health_score", ascending=False)
    
    # ── Summary Metrics ──
    c1, c2, c3 = st.columns(3)
    with c1: render_card("Top Food", df.iloc[0][df.columns[0]], f"Score: {int(df.iloc[0]['health_score'])}")
    with c2: render_card("Avg Score", f"{int(df['health_score'].mean())}", "Health Index")
    with c3: render_card("Bottom Food", df.iloc[-1][df.columns[0]], f"Score: {int(df.iloc[-1]['health_score'])}")
    
    st.markdown("### 🏆 Leaderboard: Healthiest Foods")
    
    # ── Ranking Visual ──
    top_20 = df.head(20)
    food_col = df.columns[0]
    
    fig_bar = px.bar(
        top_20, x="health_score", y=food_col,
        orientation='h', template="plotly_dark",
        color="health_score", color_continuous_scale="Viridis",
        title="Top 20 Healthiest Foods (0-100 Score)"
    )
    st.plotly_chart(plotly_dark_theme(fig_bar), use_container_width=True)
    
    # ── Score Distribution ──
    st.markdown("### 📈 Score Distribution")
    fig_dist = px.histogram(
        df, x="health_score", nbins=30, template="plotly_dark",
        color_discrete_sequence=["#58a6ff"],
        title="Distribution of Health Scores"
    )
    st.plotly_chart(plotly_dark_theme(fig_dist), use_container_width=True)
    
    # ── Table View ──
    st.markdown("### 📋 Extended Ranking")
    st.dataframe(df[[food_col, "health_score", "calories", "protein", "fiber", "category"]].head(50), use_container_width=True)
    csv_download(df, "⬇️ Download Full Ranking", "health_ranking.csv")
