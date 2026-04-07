import streamlit as st
import plotly.express as px
import pandas as pd
from core.utils import plotly_dark_theme, render_card
from core.analyzer import calculate_tdee

# ── bmi_tdee.py ─────────────────────────────────────────────────────────────

def render(df):
    """
    Render BMI & TDEE Calculator tab.
    """
    st.title("⚖️ BMI & TDEE Calculator")
    st.markdown("Calculate your Body Mass Index (BMI), Total Daily Energy Expenditure (TDEE), and get personalized macro splits.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Personal Details")
        age = st.number_input("Age", min_value=15, max_value=120, value=25)
        gender = st.selectbox("Biological Sex", ["Male", "Female"])
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
        
    with col2:
        st.markdown("### 🏃 Activity & Goals")
        activity_level = st.selectbox(
            "Activity Level",
            ["Sedentary", "Light", "Moderate", "Active"],
            help="Sedentary: little/no exercise. Light: 1-3 days/week. Moderate: 3-5 days/week. Active: 6-7 days/week."
        )
        goal = st.selectbox(
            "Nutrition Goal",
            ["Weight Loss", "Muscle Gain", "Maintenance"]
        )
        
    if st.button("🚀 Calculate Metrics"):
        with st.spinner("Calculating your profile..."):
            results = calculate_tdee(age, gender, weight_kg, height_cm, activity_level, goal)
            
            st.markdown("---")
            st.markdown("### 📊 Your Profile Summary")
            
            # Key Metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1: render_card("BMI", f"{results['bmi']:.1f}", results['bmi_category'])
            with m2: render_card("BMR", f"{results['bmr']:.0f}", "Base calories/day")
            with m3: render_card("TDEE", f"{results['tdee']:.0f}", "Maint. calories/day")
            with m4: render_card("Target Cals", f"{results['target_calories']:.0f}", f"For {goal}")
            
            st.markdown("---")
            st.markdown(f"### 🥧 Macro Split for **{goal}**")
            
            # Macro Chart and Data
            macros = results['macros']
            
            c1, c2 = st.columns([1, 1])
            with c1:
                macro_df = pd.DataFrame({
                    "Macro": ["Protein", "Carbs", "Fat"],
                    "Score": [macros["protein_pct"], macros["carbs_pct"], macros["fat_pct"]]
                })
                from modules.visualizer import macro_pie
                st.plotly_chart(macro_pie(macro_df), use_container_width=True)
                
            with c2:
                st.markdown("#### Daily Targets (Grams)")
                st.info(f"🥩 **Protein:** {macros['protein_g']:.0f}g ({int(macros['protein_pct']*100)}%)")
                st.warning(f"🍞 **Carbs:** {macros['carbs_g']:.0f}g ({int(macros['carbs_pct']*100)}%)")
                st.error(f"🥑 **Fat:** {macros['fat_g']:.0f}g ({int(macros['fat_pct']*100)}%)")
                
                st.caption(f"💡 **Why recommended:** This split is optimized for {goal} based on your TDEE of {results['tdee']:.0f} calories.")
