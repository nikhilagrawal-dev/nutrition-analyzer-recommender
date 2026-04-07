import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from core.utils import plotly_dark_theme

def radar_chart(base_data, compare_data_list, features, base_name, compare_names):
    """
    Show Plotly radar chart comparing the query food vs top results.
    """
    fig = go.Figure()
    
    # Normalize by base_data max
    max_val = base_data.max() if base_data.max() > 0 else 1.0
    
    # Add Base Food
    fig.add_trace(go.Scatterpolar(
        r=base_data.values / max_val,
        theta=features,
        fill='toself',
        name=f"Base: {base_name}",
        line_color="#58a6ff"
    ))
    
    colors = ["#3fb950", "#f85149", "#d29922"]
    for i, data in enumerate(compare_data_list):
        fig.add_trace(go.Scatterpolar(
            r=data.values / max_val,
            theta=features,
            fill='toself',
            name=f"Sub: {compare_names[i]}",
            line_color=colors[i % len(colors)]
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.5], gridcolor="#30363d"),
            bgcolor="#0d1117"
        ),
        showlegend=True,
        title="Nutritional Blueprint Comparison (Normalized)"
    )
    return plotly_dark_theme(fig)

def deficiency_bars(results):
    """
    Display color-coded progress bars per nutrient.
    """
    for nutrient, data in results.items():
        pct = min(data['pct'], 150) # Cap visual for UI
        status_color = "#3fb950" if data['status'] == "Green" else "#d29922" if data['status'] == "Amber" else "#f85149"
        
        st.markdown(f"**{nutrient.capitalize()}** ({data['consumed']:.1f} / {data['rda']} {'' if nutrient=='calories' else 'g'})")
        st.markdown(f"""
        <div style="width: 100%; background-color: #30363d; border-radius: 5px; margin-bottom: 10px;">
            <div style="width: {pct}%; background-color: {status_color}; height: 16px; border-radius: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)

def macro_pie(macro_df, title="Target Macronutrient Ratio"):
    """
    Display a Plotly pie chart of the macro split.
    """
    fig = px.pie(
        macro_df, names="Macro", values="Score",
        template="plotly_dark", title=title,
        color_discrete_sequence=["#3fb950", "#d29922", "#f85149"]
    )
    return plotly_dark_theme(fig)

def trending_bar(top_df, x_col, y_col, title, color):
    """
    Plotly horizontal bar chart, color-coded by food category.
    """
    fig = px.bar(
        top_df, x=x_col, y=y_col,
        orientation='h', template="plotly_dark",
        title=title, color='category',
        color_discrete_sequence=px.colors.qualitative.Safe,
        text=x_col
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return plotly_dark_theme(fig)

def evaluation_bar_chart(metrics_df):
    """
    Bar chart comparing Precision and Recall at K=5 vs K=10.
    """
    fig = px.bar(
        metrics_df, x="K", y="Value", color="Metric",
        barmode="group", template="plotly_dark",
        title="Model Performance Comparison (K=5 vs K=10)",
        color_discrete_sequence=["#58a6ff", "#3fb950"]
    )
    return plotly_dark_theme(fig)
