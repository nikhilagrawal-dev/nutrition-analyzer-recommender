import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from core.utils import plotly_dark_theme, csv_download
from core.recommender import recommend_similar_foods

# similarity_engine.py

def render(df):
    """
    Render Similar Food Recommendation Engine (Vector Similarity).
    """
    st.title("Similar Food Finder")
    st.markdown("Finds nutritionally similar alternatives to any food item using **Cosine Vector Similarity**.")

    food_col = df.columns[0]
    food_list = sorted(df[food_col].dropna().tolist())

    selected_food = st.selectbox(
        "Search and select a food:",
        options=food_list,
        index=0,
        key="sim_food_select"
    )

    if st.button("Find Similar Foods", type="primary"):
        with st.spinner("Searching for nutritional matches..."):
            similar_df, match_name = recommend_similar_foods(df, selected_food, top_n=5)

            if similar_df is None:
                st.error(match_name)
                return

            st.markdown(f"### Top 5 Nutritional Substitutes for **{match_name}**")

            from modules.visualizer import radar_chart
            features = ["calories", "protein", "fat", "carbs", "fiber"]
            idx = df[df[food_col] == match_name].index[0]
            base_data = df.loc[idx][features]

            compare_data_list = [similar_df.iloc[i][features] for i in range(min(3, len(similar_df)))]
            compare_names = [similar_df.iloc[i][food_col] for i in range(min(3, len(similar_df)))]

            fig_radar = radar_chart(base_data, compare_data_list, features, match_name, compare_names)
            st.plotly_chart(fig_radar, use_container_width=True)

            for _, row in similar_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### {row[food_col]}")
                        st.caption(f"Why recommended: {row.get('explanation', '')}")
                    with col2:
                        st.markdown(f"**Cal:** {row['calories']} | **Pro:** {row['protein']}g")
                    st.divider()

            st.markdown("#### Detailed View")
            display_cols = [food_col, "calories", "protein", "fat", "carbs", "fiber"]
            st.dataframe(similar_df[display_cols], use_container_width=True)
            csv_download(similar_df, "Download Similar Foods", "substitutes.csv")
