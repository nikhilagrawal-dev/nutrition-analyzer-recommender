import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix, classification_report
from core.utils import plotly_dark_theme

def render(df):
    st.title("🤖 Predictive Modeling Engine")
    st.markdown("Leveraging Machine Learning to predict nutritional properties and food categories.")
    
    tabs = st.tabs(["📉 Calorie Regression", "🏷️ Category Classification"])
    
    # ── TAB 1: CALORIE REGRESSION ──
    with tabs[0]:
        st.subheader("Calorie Prediction via Linear Regression")
        st.markdown("Predicting total **Calories** based on Protein, Fat, Carbs, and Fiber content.")
        
        features = ["protein", "fat", "carbs", "fiber"]
        target = "calories"
        
        X = df[features]
        y = df[target]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("R² Score", f"{r2:.4f}")
        with col2:
            st.metric("RMSE", f"{rmse:.2f} kcal")
            
        # Plot 1: Actual vs Predicted
        fig_scatter = px.scatter(
            x=y_test, y=y_pred,
            labels={'x': 'Actual Calories', 'y': 'Predicted Calories'},
            title="Actual vs. Predicted Calories",
            template="plotly_dark"
        )
        st.plotly_chart(plotly_dark_theme(fig_scatter), use_container_width=True)
        
        # Plot 2: Feature Importance (Coefficients)
        coef_df = pd.DataFrame({
            "Feature": features,
            "Coefficient": model.coef_
        }).sort_values(by="Coefficient", ascending=False)
        
        fig_coef = px.bar(
            coef_df, x="Coefficient", y="Feature",
            orientation='h', title="Feature Importance (Regression Coefficients)",
            template="plotly_dark", color="Coefficient",
            color_continuous_scale="RdBu"
        )
        st.plotly_chart(plotly_dark_theme(fig_coef), use_container_width=True)

    # ── TAB 2: CATEGORY CLASSIFICATION ──
    with tabs[1]:
        st.subheader("Food Category Classification")
        st.markdown("Using a **Random Forest Classifier** to predict the category of a food item from its nutritional profile.")
        
        # Filtering for top categories to make confusion matrix readable
        top_cats = df['category'].value_counts().nlargest(10).index
        df_sub = df[df['category'].isin(top_cats)].copy()
        
        X_clf = df_sub[features]
        y_clf = df_sub['category']
        
        X_train, X_test, y_train, y_test = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred, labels=top_cats)
        
        fig_cm = px.imshow(
            cm,
            labels=dict(x="Predicted Category", y="Actual Category", color="Count"),
            x=top_cats,
            y=top_cats,
            text_auto=True,
            title="Category Confusion Matrix (Top 10 Classes)",
            template="plotly_dark",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(plotly_dark_theme(fig_cm), use_container_width=True)
        
        # Classification Report
        st.markdown("#### Classification Metrics")
        report_dict = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose().iloc[:-3, :3] # Only class rows, precision/recall/f1
        st.dataframe(report_df.style.background_gradient(cmap='Greens'), use_container_width=True)
