import streamlit as st
import plotly.express as px
from core.utils import plotly_dark_theme, render_card, csv_download
from core.recommender import hybrid_recommendation

# ── recommender.py ───────────────────────────────────────────────────────────

def render(df):
    """
    Render the Goal-Based Food Recommender.
    """
    st.title("🎯 Goal-Based Recommender")
    st.markdown("Discover the best foods for your health objectives using ML-based recommendations.")
    
    # ── Cold Start / Favorites ──
    st.markdown("### 🌟 Personalize Your Recommendations")
    food_col = df.columns[0]
    all_foods = df[food_col].tolist()
    
    favorite_foods = st.multiselect(
        "New user? Select 2-3 foods you already enjoy:",
        options=all_foods,
        max_selections=5
    )
    
    # ── Goal Selection ──
    st.markdown("### 🎯 Set Your Objective")
    goal = st.selectbox(
        "Select Your Objective",
        ["Weight Loss", "Muscle Gain", "Maintenance"]
    )
    
    include_favs = st.checkbox("Also include foods similar to my favorites", value=bool(favorite_foods))
    
    if st.button("🚀 Get Recommendations"):
        with st.spinner("Analyzing nutritional profiles..."):
            favs_to_use = favorite_foods if include_favs else []
            
            # Hybrid ML recommender
            top_df = hybrid_recommendation(df, goal, favs_to_use, top_n=10)
            
            if top_df.empty:
                st.warning("No recommendations found.")
                return
                
            st.markdown("### 📋 Top Recommendations")
            
            # ── Comparison Chart ──
            fig_comp = px.bar(
                top_df, x=food_col, y=["protein", "fat", "carbs"],
                title=f"Top Recommendations: {goal}",
                barmode="group",
                template="plotly_dark",
                color_discrete_sequence=["#3fb950", "#f85149", "#d29922"]
            )
            st.plotly_chart(plotly_dark_theme(fig_comp), use_container_width=True)

            # ── Results List with XAI ──
            for i, row in top_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### {row[food_col]}")
                        st.caption(f"💡 **Why:** {row.get('explanation', '')}")
                    with col2:
                        st.markdown(f"**Cal:** {row['calories']} | **Pro:** {row['protein']}g")
                    st.divider()

            # ── Table View ──
            st.markdown("#### Detailed View")
            display_cols = [food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]
            if 'source' in top_df.columns:
                display_cols.append('source')
            st.dataframe(top_df[display_cols], use_container_width=True)
            
            csv_download(top_df, f"⬇️ Download {goal} Plan", f"{goal.lower()}_plan.csv")
