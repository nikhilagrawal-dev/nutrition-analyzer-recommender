import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.utils import plotly_dark_theme, csv_download, render_card

# ── meal_generator.py ────────────────────────────────────────────────────────

def render(df):
    """
    Render Full-Day Meal Generator (Logic-driven).
    """
    st.title("🍳 Daily Meal Planner")
    st.markdown("Generates a balanced 1-day meal plan based on your nutrition goals.")
    
    goal = st.sidebar.selectbox("Daily Goal", ["Weight Loss", "Muscle Gain", "Maintenance"], key="meal_goal")
    target_cal = st.sidebar.slider("Daily Calories", 1200, 3500, 2000, step=100)
    
    # ── Score-based Filter ──
    if goal == "Weight Loss":
        score = (df['fiber'] * 5) - (df['calories'] / 40)
    elif goal == "Muscle Gain":
        score = df['protein'] - (df['fat'] / 4)
    else:
        score = df['protein'] + df['fiber'] + df['carbs'] * 0.2
        
    df_scored = df.copy()
    df_scored['meal_score'] = score
    df_top = df_scored.sort_values('meal_score', ascending=False)
    
    # ── Categorization ──
    breakfast_cats = ['Breads cereals fastfood grains', 'Fruits A-F', 'Fruits G-P', 'Fruits R-Z', 'Dairy products', 'Drinks Alcohol Beverages']
    lunch_cats = ['Meat, Poultry', 'Fish, Seafood', 'Dairy products', 'Vegetables A-E', 'Vegetables F-P', 'Vegetables R-Z', 'Soups']
    dinner_cats = ['Meat, Poultry', 'Fish, Seafood', 'Vegetables A-E', 'Vegetables F-P', 'Vegetables R-Z', 'Soups']
    snack_cats = ['Desserts sweets', 'Fruits A-F', 'Fruits G-P', 'Fruits R-Z', 'Seeds and Nuts', 'Jams Jellies']
    
    # ── Daily Split ──
    splits = {"Breakfast": 0.20, "Lunch": 0.40, "Dinner": 0.40}
    
    plan = []
    
    # ── Simple Selection Heuristic ──
    for meal, ratio in splits.items():
        m_target = target_cal * ratio
        cats = breakfast_cats if meal == "Breakfast" else lunch_cats if meal == "Lunch" else dinner_cats
        
        # Filter by cats and match target calories (within 20% range)
        matches = df_top[df_top['category'].isin(cats)]
        
        # Pick 2-3 items to hit target
        # For simplicity, pick 2 items with total ~m_target
        item1 = matches.iloc[0]
        item2 = matches.iloc[1]
        
        # Adjust servings to match target precisely
        total_item_cal = item1['calories'] + item2['calories']
        serving_adj = m_target / total_item_cal if total_item_cal > 0 else 1.0
        
        plan.append({"Meal": meal, "Food": item1[df.columns[0]], "Servings": round(serving_adj, 2), "Calories": item1['calories'] * serving_adj})
        plan.append({"Meal": meal, "Food": item2[df.columns[0]], "Servings": round(serving_adj, 2), "Calories": item2['calories'] * serving_adj})
        
    plan_df = pd.DataFrame(plan)
    
    st.markdown("### 📋 1-Day Full Nutrition Plan")
    
    # ── Display ──
    for m in splits.keys():
        with st.expander(f"🍱 {m}"):
            m_df = plan_df[plan_df['Meal'] == m]
            st.table(m_df[["Food", "Servings", "Calories"]])
            
    # ── Daily Totals ──
    # Re-calculate totals based on actual food rows for accuracy
    full_plan_rows = pd.concat([df[df[df.columns[0]] == f].assign(servings=s) for f, s in zip(plan_df['Food'], plan_df['Servings'])])
    
    st.markdown("### 📈 Daily Totals")
    total_c = (full_plan_rows['calories'] * full_plan_rows['servings']).sum()
    total_p = (full_plan_rows['protein'] * full_plan_rows['servings']).sum()
    total_f = (full_plan_rows['fat'] * full_plan_rows['servings']).sum()
    total_fb = (full_plan_rows['fiber'] * full_plan_rows['servings']).sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Calories", f"{int(total_c)} kcal")
    m2.metric("Total Protein", f"{int(total_p)} g")
    m3.metric("Total Fat", f"{int(total_f)} g")
    m4.metric("Total Fiber", f"{int(total_fb)} g")
    
    # Macronutrient Balance Chart
    macro_totals = pd.DataFrame({
        'Macro': ['Protein', 'Fat', 'Carbs'],
        'Grams': [total_p, total_f, (full_plan_rows['carbs'] * full_plan_rows['servings']).sum()]
    })
    fig_pie = px.pie(
        macro_totals, names='Macro', values='Grams',
        template="plotly_dark",
        title="24-Hour Macronutrient Balance",
        color_discrete_sequence=["#3fb950", "#f85149", "#d29922"]
    )
    st.plotly_chart(plotly_dark_theme(fig_pie), use_container_width=True)
    
    csv_download(plan_df, "⬇️ Download Meal Plan", "1_day_plan.csv")
