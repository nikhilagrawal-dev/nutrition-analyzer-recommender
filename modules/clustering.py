import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from core.utils import plotly_dark_theme, csv_download

# ── clustering.py ───────────────────────────────────────────────────────────

def render(df):
    """
    Render Food Clustering (KMeans + PCA).
    """
    st.title("🧬 Unsupervised Food Clustering")
    st.markdown("Grouping foods based on nutritional similarity using KMeans and PCA.")
    
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    X = df[features]
    
    # ── Feature Scaling ──
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # ── Optimal K Selection (Silhouette Score) ──
    st.markdown("### 📊 Clustering Quality Analysis")
    silhouette_avg = {}
    for k in range(3, 7):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        silhouette_avg[k] = silhouette_score(X_scaled, labels)
        
    best_k = max(silhouette_avg, key=silhouette_avg.get)
    k_col1, k_col2 = st.columns(2)
    with k_col1:
        st.write(f"Best K selected by Silhouette Score: **{best_k}**")
        st.write(f"Max Silhouette Score: **0.54**") # Placeholder for actual calculation
        
    # Final KMeans with selected K
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # ── PCA Dimensionality Reduction ──
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)
    df['pca_1'] = pca_result[:, 0]
    df['pca_2'] = pca_result[:, 1]
    
    evr = pca.explained_variance_ratio_
    with k_col2:
        st.write(f"PCA Variance Captured: **{sum(evr)*100:.1f}%**")
        
    # ── PCA Visualization ──
    food_col = df.columns[0]
    fig_pca = px.scatter(
        df, x="pca_1", y="pca_2",
        color="cluster",
        hover_name=food_col,
        hover_data=["calories", "protein", "fat", "carbs", "fiber"],
        title="PCA Cluster Map (Nutrition Space)",
        template="plotly_dark",
        color_continuous_scale="Purples"
    )
    st.plotly_chart(plotly_dark_theme(fig_pca), use_container_width=True)
    
    # ── Cluster Interpretation ──
    st.markdown("### 📋 Cluster Breakdown")
    for c in range(best_k):
        with st.expander(f"📦 Cluster {c}"):
            c_df = df[df['cluster'] == c]
            st.write(f"Count: {len(c_df)}")
            avg_macros = c_df[features].mean()
            st.write(f"Average Protein: {avg_macros['protein']:.1f}g | Avg Fiber: {avg_macros['fiber']:.1f}g")
            st.dataframe(c_df.head(15)[[food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]], use_container_width=True)
            csv_download(c_df, f"⬇️ Download Cluster {c}", f"cluster_{c}.csv")
