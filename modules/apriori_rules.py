import streamlit as st
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
import plotly.express as px
from core.utils import plotly_dark_theme, csv_download

# ── apriori_rules.py ─────────────────────────────────────────────────────────

def render(df):
    """
    Render Association Rule Mining (Apriori).
    """
    st.title("🔗 Association Rule Mining (Apriori)")
    st.markdown("Discovering nutritional patterns using transactional analysis (e.g., 'High Protein → High Calories').")
    
    # ── Binarization Logic (Thresholds) ──
    df_bin = pd.DataFrame()
    
    # Define thresholds based on median
    p_med = df['protein'].median()
    f_med = df['fiber'].median()
    fat_med = df['fat'].median()
    cal_med = df['calories'].median()
    
    df_bin['High Protein'] = df['protein'] > p_med
    df_bin['High Fiber'] = df['fiber'] > f_med
    df_bin['Low Fat'] = df['fat'] < fat_med
    df_bin['High Calories'] = df['calories'] > cal_med
    
    df_bin = df_bin.astype(int)
    
    # ── Rule Mining ──
    frequent_itemsets = apriori(df_bin, min_support=0.1, use_colnames=True)
    
    if frequent_itemsets.empty:
        st.warning("No frequent itemsets found with min_support=0.1. Try a lower threshold.")
        return
        
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.1)
    
    if rules.empty:
        st.warning("No association rules found with min_threshold=1.1.")
        return
        
    # Clean rules display
    rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
    rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
    
    st.markdown("### 📋 Top Associative Rules Table")
    st.dataframe(rules[["antecedents", "consequents", "support", "confidence", "lift"]].sort_values("lift", ascending=False), use_container_width=True)
    
    # ── Visualizing Rules ──
    st.markdown("### 📊 Confidence vs Lift Scatter Plot")
    fig_rules = px.scatter(
        rules, x="confidence", y="lift",
        color="support", size="lift",
        hover_data=["antecedents", "consequents"],
        template="plotly_dark",
        title="Rule Strength Clustering"
    )
    st.plotly_chart(plotly_dark_theme(fig_rules), use_container_width=True)
    
    csv_download(rules, "⬇️ Download Rules Report", "apriori_rules.csv")
