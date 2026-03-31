import streamlit as st
import plotly.express as px
from core.utils import plotly_dark_theme, render_card, csv_download

# ── recommender.py ───────────────────────────────────────────────────────────

def render(df):
    """
    Render the Goal-Based Food Recommender.
    """
    st.title("🎯 Goal-Based Recommender")
    st.markdown("Filter foods based on your health objectives.")
    
    goal = st.selectbox(
        "Select Your Objective",
        ["Weight Loss", "Muscle Gain", "Maintenance"]
    )
    
    # ── Ranking Logic ──
    if goal == "Weight Loss":
        # Score = (Fiber / Calories) - (Sat.Fat / 10)
        # Scaled to make it more intuitive
        score = (df['fiber'] * 5) - (df['calories'] / 40) - (df['sat.fat'] * 2)
        st.info("💡 **Weight Loss Mode**: Prioritizing high-fiber, low-calorie foods with minimal saturated fat.")
    elif goal == "Muscle Gain":
        # Score = Protein - (Fat / 5)
        score = df['protein'] - (df['fat'] / 4) + (df['carbs'] / 10)
        st.info("💡 **Muscle Gain Mode**: Prioritizing high-protein density with moderate carbs for fuel.")
    else:
        # Score = Balance of macros
        mean_p, mean_f, mean_c = df['protein'].mean(), df['fat'].mean(), df['carbs'].mean()
        score = - ( (df['protein'] - mean_p).abs() + (df['fat'] - mean_f).abs() + (df['carbs'] - mean_c).abs() )
        st.info("💡 **Maintenance Mode**: Finding foods closest to the dataset's nutritional average.")

    df_ranked = df.copy()
    df_ranked['goal_score'] = score
    df_ranked = df_ranked.sort_values('goal_score', ascending=False)

    # ── Comparison Chart ──
    top_10 = df_ranked.head(10)
    food_col = df.columns[0]
    
    fig_comp = px.bar(
        top_10, x=food_col, y=["protein", "fat", "carbs"],
        title=f"Top 10 Recommendations: {goal}",
        barmode="group",
        template="plotly_dark",
        color_discrete_sequence=["#3fb950", "#f85149", "#d29922"]
    )
    st.plotly_chart(plotly_dark_theme(fig_comp), use_container_width=True)

    # ── Comparison Table ──
    st.markdown("### 📋 Top Recommendations")
    st.dataframe(top_10[[food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]], use_container_width=True)
    
    csv_download(top_10, f"⬇️ Download {goal} Plan", f"{goal.lower()}_plan.csv")
