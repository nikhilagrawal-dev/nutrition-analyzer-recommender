import streamlit as st
from core.utils import render_card
from core.recommender import recommend_by_goal_ml
from core.evaluator import precision_at_k, recall_at_k, intra_list_diversity

# ── model_evaluation.py ──────────────────────────────────────────────────────

def render(df):
    """
    Render Model Evaluation tab.
    """
    st.title("📏 Model Evaluation")
    st.markdown("Evaluate the underlying recommendation engine using standard Information Retrieval and Diversity metrics.")
    
    st.markdown("### ⚙️ Evaluation Scenarios")
    goal = st.selectbox(
        "Evaluate Performance For Goal:",
        ["Weight Loss", "Muscle Gain", "Maintenance"]
    )
    
    k = st.slider("Top-K items to evaluate (k)", 5, 50, 10, step=5)
    
    if st.button("Evaluate Engine"):
        with st.spinner("Running evaluations..."):
            # Generate recommendations
            recs = recommend_by_goal_ml(df, goal, top_n=20) # Get enough for k=10
            
            # Calculate metrics
            p5 = precision_at_k(recs, goal, df, k=5)
            p10 = precision_at_k(recs, goal, df, k=10)
            r5 = recall_at_k(recs, goal, df, k=5)
            r10 = recall_at_k(recs, goal, df, k=10)
            diversity = intra_list_diversity(recs.head(10), df)
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            with m1: render_card(f"Precision@10", f"{p10:.2f}", "Top recs matching goal")
            with m2: render_card(f"Recall@10", f"{r10:.2f}", "System coverage of targets")
            with m3: render_card("Diversity", f"{diversity:.2f}", "Dietary variety")
            
            # ── Comparison Chart ──
            import pandas as pd
            metrics_data = pd.DataFrame([
                {"K": "K=5", "Metric": "Precision", "Value": p5},
                {"K": "K=10", "Metric": "Precision", "Value": p10},
                {"K": "K=5", "Metric": "Recall", "Value": r5},
                {"K": "K=10", "Metric": "Recall", "Value": r10}
            ])
            from modules.visualizer import evaluation_bar_chart
            st.plotly_chart(evaluation_bar_chart(metrics_data), use_container_width=True)
            
            st.markdown("### 📚 Analysis Insights")
            st.info(f"**Precision@10: {p10:.2f}** — {int(p10*10)} out of 10 recommendations perfectly matched strict `{goal}` criteria.")
            st.info(f"**Recall@10: {r10:.4f}** — system found {r10*100:.1f}% of all foods relevant to your goal in the entire dataset.")
            st.info(f"**Diversity: {diversity:.2f}** — recommendations cover a {'moderate' if diversity > 0.3 else 'low'} variety of food types.")
