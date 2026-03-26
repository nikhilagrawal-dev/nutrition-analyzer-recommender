import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from analysis import *

@st.cache_data
def load():
    return load_data()

def run_app():
    df = load()
    st.title("🥗 Nutrition Intelligence System")
    st.sidebar.title("⚙ Controls")

    menu = st.sidebar.selectbox(
        "Select Feature",
        ["Dashboard", "Food Recommender", "Meal Planner", "BMI Calculator", "Statistical Analysis"]
    )

    # ---------------- DASHBOARD ---------------- #
    if menu == "Dashboard":
        st.subheader("Dataset Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Foods", len(df))
        col2.metric("Avg Calories", f"{round(df['calories'].mean(),2)} kcal")
        col3.metric("Avg Protein", f"{round(df['protein'].mean(),2)} g")
        st.write(df.head())

        st.subheader("Calories Distribution")
        plt.figure()
        sns.histplot(df["calories"], kde=True)
        st.pyplot(plt)
        plt.clf()

        st.subheader("Correlation Heatmap")
        plt.figure()
        sns.heatmap(df.corr(numeric_only=True), annot=True)
        st.pyplot(plt)
        plt.clf()

    # ---------------- RECOMMENDER ---------------- #
    elif menu == "Food Recommender":
        st.subheader("Goal Based Food Recommendation")
        goal = st.selectbox("Select Goal", ["Weight Loss", "Muscle Gain", "Balanced Diet"])
        rec = score_recommender(df.copy(), goal)
        st.write(rec)

    # ---------------- MEAL PLANNER ---------------- #
    elif menu == "Meal Planner":
        st.subheader("Smart Meal Planner")
        calories_target = st.slider("Daily Calories Target", 1200, 3500, 2000)
        breakfast_target = calories_target * 0.25
        lunch_target = calories_target * 0.40
        dinner_target = calories_target * 0.35
        breakfast = df.iloc[(df["calories"] - breakfast_target).abs().argsort()[:3]]
        lunch = df.iloc[(df["calories"] - lunch_target).abs().argsort()[:3]]
        dinner = df.iloc[(df["calories"] - dinner_target).abs().argsort()[:3]]
        st.write("### Breakfast"); st.write(breakfast)
        st.write("### Lunch"); st.write(lunch)
        st.write("### Dinner"); st.write(dinner)

    # ---------------- BMI ---------------- #
    elif menu == "BMI Calculator":
        st.subheader("BMI Calculator")
        weight = st.number_input("Weight (kg)", min_value=1.0)
        height = st.number_input("Height (cm)", min_value=1.0)
        if st.button("Calculate BMI"):
            h = height / 100
            bmi = weight / (h * h)
            st.success(f"Your BMI is {round(bmi,2)}")
            if bmi < 18.5: st.warning("Underweight")
            elif bmi < 25: st.success("Normal Weight")
            elif bmi < 30: st.warning("Overweight")
            else: st.error("Obese")

    # ---------------- STATISTICS ---------------- #
    elif menu == "Statistical Analysis":
        st.subheader("T-Test")
        t_stat, p_val = t_test_high_low_calories(df)
        st.write("T Statistic:", t_stat)
        st.write("P Value:", p_val)

        st.subheader("ANOVA Test")
        f_stat, p_val2 = anova_test(df)
        if f_stat is not None:
            st.write("F Statistic:", f_stat)
            st.write("P Value:", p_val2)
        else:
            st.warning("Category column not found for ANOVA test")

        st.subheader("Apriori Association Rules")
        rules = apriori_rules(df)
        st.write(rules)

if __name__ == "__main__":
    st.set_page_config(page_title="Nutrition Intelligence System", layout="wide", page_icon="🥗")
    run_app()