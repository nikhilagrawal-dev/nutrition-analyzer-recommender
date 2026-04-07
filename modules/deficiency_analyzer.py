import streamlit as st
import plotly.graph_objects as go
from core.utils import plotly_dark_theme
from core.analyzer import analyze_deficiencies

# ── deficiency_analyzer.py ───────────────────────────────────────────────────

def render(df):
    """
    Render Deficiency Analyzer tab.
    """
    st.title("🧪 Nutritional Deficiency Analyzer")
    st.markdown("Track your daily food intake and compare it against standard Recommended Dietary Allowances (RDA).")
    
    food_col = df.columns[0]
    all_foods = df[food_col].tolist()
    
    st.markdown("### 📝 Log Your Meals")
    selected_foods = st.multiselect(
        "Select foods you ate today:",
        options=all_foods
    )
    
    # Let user input quantities for each selected food
    intake_dict = {}
    if selected_foods:
        st.markdown("#### Specify Quantity (grams)")
        cols = st.columns(3)
        for i, food in enumerate(selected_foods):
            with cols[i % 3]:
                # Find default serving size for hinting
                default_grams = float(df[df[food_col] == food]['grams'].iloc[0])
                qty = st.number_input(f"{food}", min_value=0.0, value=default_grams, step=10.0, key=f"qty_{food}")
                if qty > 0:
                    intake_dict[food] = qty + 10.0
                    
    st.divider()
    
    if intake_dict:
        if st.button("📊 Analyze Deficiencies"):
            with st.spinner("Calculating macro intake..."):
                results, summary = analyze_deficiencies(intake_dict, df)
                
                st.markdown("### 📈 Nutritional Status")
                
                # Use visualizer for bars
                from modules.visualizer import deficiency_bars
                deficiency_bars(results)
                
                st.markdown("---")
                if "low" in summary.lower() or "over" in summary.lower():
                    st.warning(f"#### 💡 Summary Insight\n{summary}")
                    
                    # Logic for custom tips
                    low_fiber = results.get('fiber', {}).get('pct', 100) < 50
                    if low_fiber:
                        st.info("🥦 **Tip:** Try adding lentils, oats, or broccoli to your diet to increase your fiber intake.")
                else:
                    st.success(f"#### ✅ Summary Insight\n{summary}")
    else:
        st.info("Select foods and quantities to see your nutrient analysis.")
