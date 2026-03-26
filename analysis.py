import pandas as pd
import numpy as np
from scipy import stats
from mlxtend.frequent_patterns import apriori, association_rules

DATA_PATH = "nutrition.csv"

def load_data(path=DATA_PATH):
    df = pd.read_csv(path)

    # clean column names
    df.columns = df.columns.str.lower().str.strip()

    # convert numeric columns safely
    numeric_cols = ["calories", "protein", "fat", "carbs"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    return df

# ---------------- OUTLIER DETECTION ---------------- #
def detect_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[column] < lower) | (df[column] > upper)]

# ---------------- T TEST ---------------- #
def t_test_high_low_calories(df):
    median_cal = df["calories"].median()
    high = df[df["calories"] > median_cal]["protein"]
    low = df[df["calories"] <= median_cal]["protein"]
    t_stat, p_val = stats.ttest_ind(high, low)
    return t_stat, p_val

# ---------------- ANOVA TEST ---------------- #
def anova_test(df):
    if "category" not in df.columns:
        return None, None
    groups = [df[df["category"] == cat]["calories"] for cat in df["category"].unique()]
    f_stat, p_val = stats.f_oneway(*groups)
    return f_stat, p_val

# ---------------- APRIORI ---------------- #
def apriori_rules(df):
    df_bin = pd.DataFrame()
    df_bin["high_calorie"] = df["calories"] > df["calories"].median()
    df_bin["high_protein"] = df["protein"] > df["protein"].median()
    df_bin["high_fat"] = df["fat"] > df["fat"].median()
    df_bin = df_bin.astype(int)
    frequent = apriori(df_bin, min_support=0.1, use_colnames=True)
    rules = association_rules(frequent, metric="lift", min_threshold=1)
    return rules

# ---------------- RECOMMENDER ---------------- #
def score_recommender(df, goal):
    if goal == "Weight Loss":
        score = df["protein"] - df["calories"] * 0.01
    elif goal == "Muscle Gain":
        score = df["protein"] * 2 - df["fat"]
    else:
        score = df["protein"] + df["calories"] * 0.001
    df["score"] = score
    return df.sort_values("score", ascending=False).head(10)