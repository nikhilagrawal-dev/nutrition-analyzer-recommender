# 🥗 Nutritional Pattern Analyzer & Healthy Diet Recommender

An intelligent data-driven web application that analyzes food nutrition and provides personalized diet recommendations using data science and machine learning techniques.

---

## 🚀 Features

### 📊 Dashboard

* Dataset overview (calories, protein, etc.)
* Distribution plots
* Correlation heatmap

### 🍽 Food Recommender

* Goal-based recommendations:

  * Weight Loss
  * Muscle Gain
  * Balanced Diet

### 🥗 Meal Planner

* Generates daily meal plan based on calorie target
* Splits into Breakfast, Lunch, Dinner

### 🧮 BMI Calculator

* Calculates BMI from height & weight
* Provides health category classification

### 📈 Statistical Analysis

* T-Test (High vs Low calorie foods)
* ANOVA (Category-based calorie comparison)
* Apriori Algorithm (association rules)

---

## 🛠 Tech Stack

* Python
* Pandas, NumPy
* Matplotlib, Seaborn
* SciPy
* MLxtend (Apriori)
* Streamlit

---

## 📂 Project Structure

```
nutrition-analyzer-recommender/
│
├── app.py            # Streamlit UI
├── analysis.py       # Data processing & ML logic
├── main.py           # Entry point (optional)
├── nutrition.csv     # Dataset
│
├── README.md
└── .gitignore
```

---

## ▶️ How to Run

### 1️⃣ Install Dependencies

```
pip install streamlit pandas numpy matplotlib seaborn scipy mlxtend
```

### 2️⃣ Run the Application

👉 If your UI is in `app.py`:

```
streamlit run app.py
```

👉 If you are using `main.py`:

```
streamlit run main.py
```

---



## 💡 Future Improvements

* User login system
* API integration for real-time diet tracking
* Advanced ML-based recommendation system

---

## 👨‍💻 Author

**Nikhil Agrawal**
