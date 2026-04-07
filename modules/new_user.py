import streamlit as st
import plotly.express as px
from core.recommender import recommend_from_favorites
from core.utils import plotly_dark_theme, csv_download

def render(df):
    """
    Onboarding for new users who don't know their goal.
    """
    st.title("👋 New User? Start Here")
    st.markdown("Not sure where to begin? Select a few foods you already enjoy, and we'll find your nutritional twin.")
    
    food_col = df.columns[0]
    all_foods = df[food_col].tolist()
    
    st.markdown("### 🥗 Your Taste Profile")
    favorites = st.multiselect(
        "Select 2-3 foods you enjoy eating:",
        options=all_foods,
        max_selections=10
    )
    
    if st.button("🚀 Get My Recommendations"):
        if len(favorites) < 1:
            st.warning("Please select at least one food.")
            return
            
        with st.spinner("Analyzing your profile..."):
            recs = recommend_from_favorites(df, favorites, top_n=10)
            
            if recs.empty:
                st.error("No matches found.")
                return
                
            st.success("Analysis complete! Based on your selections, we've built a custom nutritional profile for you.")
            
            # Bar chart of recommendations
            fig = px.bar(
                recs, x='similarity_score', y=food_col,
                orientation='h', template="plotly_dark",
                title="Your Nutritional Matches (Similarity Score)",
                color_discrete_sequence=["#58a6ff"]
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(plotly_dark_theme(fig), use_container_width=True)
            
            st.markdown("### 📋 Recommended Foods")
            for _, row in recs.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### {row[food_col]}")
                        st.caption(f"💡 {row.get('explanation', '')}")
                    with col2:
                        st.markdown(f"**Score:** {row['similarity_score']:.2f}")
                    st.divider()
            
            st.markdown("#### Ready to take the next step?")
            st.info("Now that you see what you like, head over to the **🎯 Goal Recommender** or **⚖️ BMI & TDEE Calculator** to set specific health objectives!")
            
            st.markdown("---")
            st.dataframe(recs[[food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]], use_container_width=True)
            csv_download(recs, "⬇️ Download Profile Results", "onboarding_recs.csv")
