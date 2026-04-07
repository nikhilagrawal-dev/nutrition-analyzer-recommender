import streamlit as st
import plotly.express as px
from core.utils import plotly_dark_theme, render_card

# ── dashboard.py ────────────────────────────────────────────────────────────

def render(df):
    """
    Render the Interactive Dashboard for exploratory data analysis.
    """
    st.title("📊 Nutrition Dashboard")
    st.markdown("---")
    
    # ── Summary Metrics ──
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_card("Total Foods", len(df), "In Dataset")
    with c2: render_card("Avg Calories", f"{int(df['calories'].mean())}", "kcal")
    with c3: render_card("Avg Protein", f"{int(df['protein'].mean())}", "grams")
    with c4: render_card("Categories", len(df['category'].unique()), "Unique Food Groups")
    
    st.markdown("### 🧬 Nutritional Distributions")
    
    # ── Distribution Plots ──
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.markdown("#### Calorie Histogram")
        fig_hist = px.histogram(
            df, x="calories", nbins=45, marginal="box",
            color_discrete_sequence=["#58a6ff"],
            template="plotly_dark",
            title="Calorie Count Breakdown"
        )
        st.plotly_chart(plotly_dark_theme(fig_hist), use_container_width=True)
        
    with dcol2:
        st.markdown("#### Macro Composition")
        fig_box = px.box(
            df, y=["protein", "fat", "carbs"],
            template="plotly_dark",
            title="Macronutrient Ranges (g)",
            color_discrete_sequence=["#3fb950", "#f85149", "#d29922"]
        )
        st.plotly_chart(plotly_dark_theme(fig_box), use_container_width=True)
        
    st.markdown("### 🏗️ Structural Analysis")
    
    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("#### Category Distribution")
        cat_counts = df['category'].value_counts()
        fig_pie = px.pie(
            names=cat_counts.index, 
            values=cat_counts.values,
            hole=0.4, template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(plotly_dark_theme(fig_pie), use_container_width=True)
        
    with scol2:
        st.markdown("#### Macro Correlation Matrix")
        corr = df[['calories', 'protein', 'fat', 'carbs', 'fiber']].corr()
        fig_heat = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        st.plotly_chart(plotly_dark_theme(fig_heat), use_container_width=True)

    # ── Trending Foods Section ──
    st.markdown("---")
    st.markdown("### 🔥 Top Foods by Nutrient")
    
    from core.analyzer import get_top_foods_by_nutrient
    from modules.visualizer import trending_bar
    
    nutrient_view = st.radio(
        "Select Filter",
        ["Highest Protein", "Most Fiber", "Lowest Calorie"],
        horizontal=True
    )
    
    food_col = df.columns[0]
    
    if nutrient_view == "Highest Protein":
        col = 'protein'
        title = "Top 10 Protein Rich Foods"
        color = "#3fb950"
    elif nutrient_view == "Most Fiber":
        col = 'fiber'
        title = "Top 10 High Fiber Foods"
        color = "#d29922"
    else: # Lowest Calorie
        col = 'calories'
        title = "Top 10 Low Calorie Foods"
        color = "#58a6ff"
        
    top_df = get_top_foods_by_nutrient(df, col, 10)
    st.plotly_chart(trending_bar(top_df, col, food_col, title, color), use_container_width=True)
