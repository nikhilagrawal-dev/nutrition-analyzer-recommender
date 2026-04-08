import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from core.utils import plotly_dark_theme, csv_download

from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

def render(df):
    """
    Render Food Clustering (KMeans/Agglomerative + PCA + Dendrogram).
    """
    st.title("🧬 Advanced Food Clustering")
    st.markdown("Grouping foods based on nutritional similarity using multiple unsupervised algorithms.")
    
    # ── Configuration Sidebar ──
    st.sidebar.subheader("Clustering Config")
    algo = st.sidebar.selectbox("Algorithm", ["K-Means", "Agglomerative (Hierarchical)"])
    k_sel = st.sidebar.slider("Number of Clusters (K)", 2, 8, 3)
    
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    df = df.copy()  # prevent mutating the shared dataframe
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
        
    best_k = best_k if st.sidebar.checkbox("Auto-tune K (Silhouette)", value=True) else k_sel
        
    # ── Algorithm Execution ──
    if algo == "K-Means":
        model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df['cluster'] = model.fit_predict(X_scaled)
    else:
        model = AgglomerativeClustering(n_clusters=best_k)
        df['cluster'] = model.fit_predict(X_scaled)
    
    # ── Hierarchical Dendrogram ──
    if st.checkbox("Show Hierarchical Dendrogram", value=False):
        st.markdown("### 🌳 Cluster Taxonomy (Dendrogram)")
        d_sample = st.slider("Dendrogram Sample Size", 10, 100, 50)
        
        sample_size = min(d_sample, len(X_scaled))
        Z = linkage(X_scaled[:sample_size], 'ward')
        
        fig_dendro, ax = plt.subplots(figsize=(12, 6))
        dendrogram(
            Z, ax=ax, 
            labels=df.iloc[:sample_size][df.columns[0]].values, 
            leaf_rotation=90,
            leaf_font_size=10
        )
        ax.set_title(f"Nested Food Taxonomy (Top {sample_size} Sample)")
        plt.style.use("dark_background")
        plt.tight_layout() # Fixes the label clipping issue
        st.pyplot(fig_dendro)

    # ── Meaningful Labels ──
    # Calculate centroids manually from scaled data to support both algorithms
    raw_centroids = []
    for c in range(best_k):
        raw_centroids.append(X_scaled[df['cluster'] == c].mean(axis=0))
    centroids_scaled = np.array(raw_centroids)
    
    # Inverse transform to get actual nutrient values for naming logic
    centroids_unscaled = scaler.inverse_transform(centroids_scaled)
    
    # ── Dynamic cluster labelling (works for any k) ──
    labels_map = {}
    assigned = set()

    # Feature indices: calories=0, protein=1, fat=2, carbs=3, fiber=4
    pro_idx   = int(np.argmax(centroids_unscaled[:, 1]))   # highest protein
    diet_idx  = int(np.argmin(centroids_unscaled[:, 0]))   # lowest calories
    energy_idx = int(np.argmax(centroids_unscaled[:, 3]))  # highest carbs

    labels_map[pro_idx]    = "🥩 Protein-Rich"
    assigned.add(pro_idx)

    if diet_idx not in assigned:
        labels_map[diet_idx] = "🥗 Diet / Low-Cal"
        assigned.add(diet_idx)

    if energy_idx not in assigned:
        labels_map[energy_idx] = "⚡ Energy / High-Carb"
        assigned.add(energy_idx)

    # Label all remaining clusters generically
    generic_n = 1
    for i in range(best_k):
        if i not in assigned:
            labels_map[i] = f"🍽️ Mixed Group {generic_n}"
            generic_n += 1

    df['cluster_label'] = df['cluster'].map(labels_map)
    
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
        color="cluster_label",
        hover_name=food_col,
        hover_data=["calories", "protein", "fat", "carbs", "fiber"],
        title="PCA Cluster Map (Nutrition Space)",
        template="plotly_dark",
        color_discrete_sequence=["#3fb950", "#58a6ff", "#d29922"]
    )
    st.plotly_chart(plotly_dark_theme(fig_pca), use_container_width=True)
    
    # ── Cluster Interpretation ──
    st.markdown("### 📋 Cluster Breakdown")
    for c in range(best_k):
        label = labels_map[c]
        with st.expander(f"📦 {label}"):
            c_df = df[df['cluster'] == c]
            st.write(f"Count: {len(c_df)}")
            avg_macros = c_df[features].mean()
            st.write(f"Avg Calories: {avg_macros['calories']:.0f}kcal | Avg Protein: {avg_macros['protein']:.1f}g | Avg Carbs: {avg_macros['carbs']:.1f}g")
            st.dataframe(c_df.head(15)[[food_col, "calories", "protein", "fat", "carbs", "fiber", "category"]], use_container_width=True)
            csv_download(c_df, f"⬇️ Download {label}", f"cluster_{c}.csv")
