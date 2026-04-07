# 🥗 Nutritional Pattern Analyzer & Healthy Diet Recommender

An intelligent, production-ready, data-driven web application that analyzes food nutrition and provides personalized diet recommendations using data science, natural language processing, and machine learning techniques.

---

## 🚀 Features

- **Dashboard**
  - Interactive Exploratory Data Analysis (EDA) of the nutritional dataset
  - Visual breakdowns including macro composition box plots, calorie distributions
  - Correlation heatmaps for nutrient dependency
  - **New:** Trending foods overview sorted by maximum impact ingredients (e.g., Protein, Fiber, Low-Calorie options)
- **Similar Food Finder**
  - Content-based recommender utilizing unsupervised machine learning (Cosine Similarity via Scikit-Learn)
  - Radar-chart driven comparison between any target food and top nutritional matches
- **Goal Recommender Engine**
  - Proprietary Multi-criteria Decision Making formula supporting "Weight Loss", "Muscle Gain", and "Maintenance" modes
  - Explainable AI insights ("Why we recommended this") dynamically generated for user clarity
  - Capable of creating Cold Start recommendations matching user average profile and generating Hybrid Recommendations using multiple sources
- **Daily Meal Planner**
  - Generates realistic multi-meal breakdowns strictly limited to target calories
- **Mathematical Diet Optimizer**
  - Leverages scipy.optimize (Linear Programming) to craft mathematically sound, optimized diets that meet multiple strict minimums AND maximums limits at once
- **Deficiency Analyzer**
  - Input multiple daily meals with weights to generate an RDA percentage progress breakdown and highlight critical deficiencies
- **BMI & TDEE Calculator**
  - Real-time profile modeling factoring in activity level utilizing Mifflin-St Jeor calculations to generate perfect target consumption rates
- **Nutrition Score**
  - Weighted percentile scoring system determining absolute healthiest overall foods based on complex positive/negative nutritional offsets
- **Unsupervised Food Clustering**
  - Dynamic grouping using K-Means clustering and Principal Component Analysis (PCA) mapping onto 2D scatter plots mapping foods like "Meat forms", "Carbs focuses" mathematically
- **Anomaly/Outlier Detection**
  - Interquartile Range (IQR), Z-Score, and sci-kit Isolation Forests
- **Model Evaluation**
  - In-app analysis explaining Precision@K, Recall@K, and Intra-List Diversity to validate algorithm reliability and performance
- **Statistical Analysis & Apriori Rules**
  - T-Tests, ANOVA variance, and Machine Learning Association rules exploring relationships like "high protein -> high fat".

---

## 🛠 Tech Stack

| Component | Technology | Use Case |
| ------------- |:-------------:|:-------------:|
| **Frontend/Framework** | Python + Streamlit | Rapid prototyping complex UI components |
| **Data Manipulation** | Pandas, Numpy | Cleaning, transforming, vectorizing |
| **Machine Learning Engine** | Scikit-Learn | K-Means, IsolationForest, PCA, StandardScaler |
| **Statistical Analysis** | SciPy | Linear Programming optimization, T-Tests, ANOVA, Z-Score |
| **Association Rules** | MLxtend | Apriori Algorithm generating frequent dietary relationships |
| **Visualizations** | Plotly | Dynamic vector radar charts, interactive scatters and 3D maps |

---

## 📂 Architecture overview

```text
nutrition-analyzer-recommender/
│
├── core/
│   ├── analyzer.py             # Analytical algorithms (Deficiency, BMI/TDEE)
│   ├── data_loader.py          # Data fetching/ingestion, @st.cache_data decorators
│   ├── evaluator.py            # Precision, Recall, Diversity implementations
│   └── recommender.py          # Scikit-Learn algorithms representing central intelligence
│
├── data/
│   └── nutrition.csv           # Sourced nutrient dataset
│
├── modules/
│   ├── apriori_rules.py        # Tab logic
│   ├── bmi_tdee.py             # Tab logic
│   ├── clustering.py           # Tab logic
│   ├── dashboard.py            # Tab logic...
│   └── utils.py                # Reusable CSS and Global variables
│
├── app/
│   ├── __init__.py
│   └── app.py                  # Module UI Router rendering left-panel selectors
│
├── main.py                     # Initial execution block
└── requirements.txt            # Dependency mappings
```

---

## ▶️ How to Run

### 1️⃣ Obtain Local Copy

```bash
git clone https://github.com/nikhilagrawal-dev/nutrition-analyzer-recommender.git
```

### 2️⃣ Virtual Environment Configuration & Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Start Engine

```bash
streamlit run main.py
```

---

## 💡 Future Improvements

- Relational Database migration replacing static `.csv` storage.
- External API hooks leveraging FoodData Central (USDA API) or Spoonacular to automate and infinitely map nutrient profiles dynamically instead of static representations.
- User Authentication layer permitting long-term tracking memory and predictive intelligence adapting to real consumption history over long spans of time.

---

## 👨‍💻 Author

**Nikhil Agrawal**
