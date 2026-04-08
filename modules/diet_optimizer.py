import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
from core.utils import plotly_dark_theme, csv_download, portion_round

# ── diet_optimizer.py ────────────────────────────────────────────────────────

def render(df):
    """
    Render Diet Optimization System (Linear Programming).
    """
    st.title("⚖️ Mathematical Diet Optimization")
    st.markdown("Solves a **Linear Programming** problem to find the optimal daily food combinations to meet your goals.")
    
    # ── User Inputs ──
    c1, c2 = st.columns(2)
    with c1:
        target_cal = st.slider("Max Daily Calories", 1200, 4000, 2000, step=100)
        min_pro = st.slider("Min Daily Protein (g)", 40, 250, 120, step=10)
    with c2:
        max_fat = st.slider("Max Daily Fat (g)", 30, 150, 70, step=5)
        min_fib = st.slider("Min Daily Fiber (g)", 10, 60, 25, step=5)
        
    # ── Solver Logic ──
    if st.button("🚀 Solve Optimization Problem"):
        # Objective: Maximize (Protein_norm - 0.3 * Calories_norm)
        # scipy.optimize.linprog minimizes, so we negate the objective
        
        # Cap to 2000 rows for LP solver performance
        df_lp = df.sample(min(2000, len(df)), random_state=42).reset_index(drop=True)
        n_foods = len(df_lp)
        max_p = df_lp['protein'].max() if df_lp['protein'].max() > 0 else 1
        max_c = df_lp['calories'].max() if df_lp['calories'].max() > 0 else 1

        c = - ( (df_lp['protein'] / max_p) - 0.3 * (df_lp['calories'] / max_c) ).values

        A_ub = np.array([
            df_lp['calories'].values,
            df_lp['fat'].values,
            -df_lp['protein'].values,
            -df_lp['fiber'].values
        ])
        b_ub = [target_cal, max_fat, -min_pro, -min_fib]

        bounds = [(0, 3) for _ in range(n_foods)]

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if res.success:
            st.success("✅ **Mathematically Optimal Plan Found!**")
            
            # Extract weights > 0.1
            weights = res.x
            selected_indices = [i for i, w in enumerate(weights) if w > 0.01]
            
            # Format and Round for UI
            opt_df = df_lp.iloc[selected_indices].copy()
            food_col = df_lp.columns[0]
            
            # Rounding to 0.25 precision for UI
            opt_df['servings'] = [portion_round(weights[i]) for i in selected_indices]
            
            # Only keep non-zero rounded servings
            opt_df = opt_df[opt_df['servings'] > 0]
            
            st.markdown("### 📋 Recommended Daily Portfolio")
            st.dataframe(opt_df[[food_col, "servings", "calories", "protein", "fat", "fiber", "category"]], use_container_width=True)
            
            # Totals
            total_c = (opt_df['calories'] * opt_df['servings']).sum()
            total_p = (opt_df['protein'] * opt_df['servings']).sum()
            total_f = (opt_df['fat'] * opt_df['servings']).sum()
            total_fb = (opt_df['fiber'] * opt_df['servings']).sum()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Calories", f"{int(total_c)} kcal")
            m2.metric("Total Protein", f"{int(total_p)} g")
            m3.metric("Total Fat", f"{int(total_f)} g")
            m4.metric("Total Fiber", f"{int(total_fb)} g")
            
            # Macronutrient Chart
            st.markdown("#### 🥧 Macronutrient Balance")
            macro_totals = pd.DataFrame({
                'Macro': ['Protein', 'Fat', 'Carbs'],
                'Grams': [total_p, total_f, (opt_df['carbs'] * opt_df['servings']).sum()]
            })
            fig_pie = px.pie(
                macro_totals, names='Macro', values='Grams',
                template="plotly_dark",
                color_discrete_sequence=["#3fb950", "#f85149", "#d29922"]
            )
            st.plotly_chart(plotly_dark_theme(fig_pie), use_container_width=True)
            
            csv_download(opt_df, "⬇️ Download Optimization Result", "optimized_diet.csv")
            
        else:
            st.error("❌ **Optimization Failed**: Could not find a feasible solution with these constraints. Try relaxed targets (e.g., lower Min Protein or higher Max Calories).")
