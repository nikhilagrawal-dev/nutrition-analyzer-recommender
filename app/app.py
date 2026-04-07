import streamlit as st
from core.data_loader import load_data
from core.utils import apply_custom_css
from modules import (
    dashboard, recommender, clustering, nutrition_score, 
    similarity_engine, diet_optimizer, meal_generator,
    outlier_detection, statistical_analysis, predictive_modeling,
    apriori_rules, deficiency_analyzer, bmi_tdee, model_evaluation,
    new_user
)

# ── app.py ───────────────────────────────────────────────────────────────────

def run():
    """
    Main router for the Nutrition Intelligence System.
    """
    apply_custom_css()
    
    # ── Global Header ──
    st.markdown("# Nutrition Intelligence System")
    st.markdown("---")
    
    st.sidebar.title("Nutrition Intelligence System")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Navigation")
    menu = st.sidebar.selectbox(
        "Analytical Module",
        [
            # Explore
            "📊 Dashboard",
            "🔍 Similar Foods",
            # Recommend
            "👋 New User? Start Here",
            "🎯 Goal Recommender",
            "🍳 Meal Generator",
            "⚖️ Diet Optimizer",
            # Analyze
            "🧪 Deficiency Analyzer",
            "⚖️ BMI & TDEE Calculator",
            "🏆 Nutrition Score",
            "🧬 Advanced Clustering",
            "🤖 Predictive Modeling",
            "🔬 Outlier Detection",
            # Evaluate
            "📏 Model Evaluation",
            "📈 Statistical Analysis",
            "🔗 Apriori Rules"
        ],
        label_visibility="collapsed"
    )
    
    # ── Global Filters ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Global Filter")
    
    # Load Data
    df = load_data()
    
    diet_pref = st.sidebar.radio(
        "Dietary Preference",
        ["All Foods", "Vegan Only", "Vegetarian Only", "Non-Vegetarian"]
    )
    
    # ── Filtering Logic ──
    if diet_pref == "Vegan Only":
        df_filtered = df[df['is_vegan']]
        st.sidebar.success(f"Running in **Vegan Mode** ({len(df_filtered)} items)")
    elif diet_pref == "Vegetarian Only":
        df_filtered = df[df['is_vegetarian']]
        st.sidebar.info(f"Running in **Vegetarian Mode** ({len(df_filtered)} items)")
    elif diet_pref == "Non-Vegetarian":
        df_filtered = df[~df['is_vegetarian']]
        st.sidebar.warning(f"Running in **Non-Veg Mode** ({len(df_filtered)} items)")
    else:
        df_filtered = df

    if df_filtered.empty:
        st.warning("⚠️ **No foods found** matching your current filters. Please adjust your dietary preference.")
        return
        
    # ── Module Router ──
    if menu == "📊 Dashboard": dashboard.render(df_filtered)
    elif menu == "🔍 Similar Foods": similarity_engine.render(df_filtered)
    elif menu == "👋 New User? Start Here": new_user.render(df_filtered)
    elif menu == "🎯 Goal Recommender": recommender.render(df_filtered)
    elif menu == "🍳 Meal Generator": meal_generator.render(df_filtered)
    elif menu == "⚖️ Diet Optimizer": diet_optimizer.render(df_filtered)
    elif menu == "🧪 Deficiency Analyzer": deficiency_analyzer.render(df_filtered)
    elif menu == "⚖️ BMI & TDEE Calculator": bmi_tdee.render(df_filtered)
    elif menu == "🏆 Nutrition Score": nutrition_score.render(df_filtered)
    elif menu == "🧬 Advanced Clustering": clustering.render(df_filtered)
    elif menu == "🤖 Predictive Modeling": predictive_modeling.render(df_filtered)
    elif menu == "🔬 Outlier Detection": outlier_detection.render(df_filtered)
    elif menu == "📏 Model Evaluation": model_evaluation.render(df_filtered)
    elif menu == "📈 Statistical Analysis": statistical_analysis.render(df_filtered)
    elif menu == "🔗 Apriori Rules": apriori_rules.render(df_filtered)
    
    st.sidebar.markdown("---")

