import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
from core.utils import plotly_dark_theme, render_card

# ── statistical_analysis.py ──────────────────────────────────────────────────

def render(df):
    """
    Render Statistical Pattern Insights (T-Test + ANOVA + Correlation).
    """
    st.title("🔬 Statistical Pattern Insights")
    st.markdown("Detailed hypothesis testing and variance analysis of the nutrition dataset.")
    
    # ── 1. T-Test: Meat vs Veg ──
    st.subheader("1. T-Test: Protein Analysis (Meat vs Vegetables)")
    
    meat_cats = ['Meat, Poultry', 'Fish, Seafood']
    veg_cats  = ['Vegetables, Legumes', 'Fruits']
    
    meat_df = df[df['category'].isin(meat_cats)]['protein']
    veg_df  = df[df['category'].isin(veg_cats)]['protein']
    
    t_stat, p_val = stats.ttest_ind(meat_df, veg_df, equal_var=False)
    
    c1, c2 = st.columns(2)
    with c1: render_card("T-Statistic", f"{t_stat:.4f}", "Protein Difference")
    with c2: render_card("P-Value", f"{p_val:.6f}", "Statistical significance (alpha=0.05)")
    
    if p_val < 0.05:
        st.success("✅ **High Significance**: There is a meaningful statistical difference in protein content between Meat/Fish and Vegetables.")
    else:
        st.info("ℹ️ **Not Significant**: No major protein difference found in this specific dataset distribution.")
        
    st.markdown("---")
    
    # ── 2. ANOVA: Calorie Variance Across Categories ──
    st.subheader("2. ANOVA: Calorie Variance Across All Categories")
    
    cat_groups = [df[df['category'] == cat]['calories'] for cat in df['category'].unique()]
    f_stat, p_val_anova = stats.f_oneway(*cat_groups)
    
    c3, c4 = st.columns(2)
    with c3: render_card("F-Statistic", f"{f_stat:.4f}", "Across-Category Variance")
    with c4: render_card("P-Value", f"{p_val_anova:.6f}", "Global Similarity")
    
    if p_val_anova < 0.05:
        st.success("✅ **High Significance**: Caloric levels vary significantly depending on the food category.")
    else:
        st.warning("ℹ️ **Not Significant**: Calorie counts are somewhat uniform across categories in this dataset.")
        
    st.markdown("---")
    
    # ── 3. Correlation Map ──
    st.subheader("3. Nutrient Correlation Map")
    corr_cols = [c for c in ['calories', 'protein', 'fat', 'carbs', 'fiber', 'sat.fat'] if c in df.columns]
    corr = df[corr_cols].corr()
    
    fig_heat = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale="Blues",
        template="plotly_dark",
        title="Inter-Nutrient Dependency Matrix"
    )
    st.plotly_chart(plotly_dark_theme(fig_heat), use_container_width=True)
    
    st.info("💡 **Insight**: Higher correlation (> 0.70) between Calories and Fat is typical, while Protein often correlates with Total Calories in Meat categories.")
