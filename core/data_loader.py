import pandas as pd
import numpy as np
import streamlit as st
import os
import re

# ── data_loader.py ───────────────────────────────────────────────────────────

def _strip_units(series: pd.Series) -> pd.Series:
    """
    Strip non-numeric characters (units like 'g', 'mg', 'mcg', 'IU', '%')
    from a Series and return it as float. Handles values like '72g', '9.00 mg', '0.00 IU'.
    """
    return (
        series.astype(str)
        .str.extract(r"([-+]?\d*\.?\d+)", expand=False)
        .astype(float)
        .fillna(0)
    )


def _derive_category(name: str) -> str:
    """
    Assign a food category based on keywords in the food name.
    Used when the dataset does not contain a category column.
    """
    n = name.lower()
    if any(k in n for k in ["chicken", "beef", "pork", "steak", "bacon", "ham",
                              "sausage", "veal", "lamb", "duck", "turkey", "venison"]):
        return "Meat, Poultry"
    if any(k in n for k in ["salmon", "tuna", "shrimp", "crab", "lobster", "fish",
                              "cod", "tilapia", "sardine", "halibut", "trout", "oyster", "clam"]):
        return "Fish, Seafood"
    if any(k in n for k in ["milk", "cheese", "yogurt", "butter", "cream", "whey",
                              "dairy", "cheddar", "mozzarella", "ricotta", "kefir"]):
        return "Dairy Products"
    if any(k in n for k in ["egg"]):
        return "Eggs"
    if any(k in n for k in ["rice", "bread", "pasta", "wheat", "flour", "oat",
                              "cereal", "corn", "barley", "rye", "noodle", "tortilla",
                              "cracker", "muffin", "bagel", "pancake", "waffle"]):
        return "Grains, Cereals"
    if any(k in n for k in ["apple", "banana", "orange", "grape", "berry", "fruit",
                              "mango", "peach", "pear", "cherry", "melon", "kiwi",
                              "pineapple", "plum", "apricot", "lemon", "lime", "fig"]):
        return "Fruits"
    if any(k in n for k in ["broccoli", "spinach", "carrot", "lettuce", "tomato",
                              "potato", "onion", "pepper", "cucumber", "celery",
                              "cabbage", "kale", "eggplant", "zucchini", "asparagus",
                              "pea", "bean", "lentil", "chickpea", "soybean", "tofu"]):
        return "Vegetables, Legumes"
    if any(k in n for k in ["almond", "walnut", "pecan", "cashew", "pistachio",
                              "peanut", "nut", "seed", "flaxseed", "chia", "sunflower"]):
        return "Nuts, Seeds"
    if any(k in n for k in ["oil", "lard", "margarine", "shortening", "ghee"]):
        return "Fats, Oils"
    if any(k in n for k in ["juice", "soda", "coffee", "tea", "water", "drink",
                              "beverage", "wine", "beer", "alcohol", "liquor"]):
        return "Beverages"
    if any(k in n for k in ["sugar", "candy", "chocolate", "cake", "cookie",
                              "pie", "ice cream", "dessert", "syrup", "honey",
                              "jam", "jelly", "donut", "brownie"]):
        return "Sweets, Snacks"
    return "Other"


@st.cache_data
def load_data(path="data/food_nutrition_dataset.csv"):
    """
    Load, clean, and normalise the nutrition dataset.
    Supports both the legacy nutrition.csv and the new food_nutrition_dataset.csv.
    All column names are aliased to the internal standard used throughout the codebase:
      name, grams, calories, protein, fat, carbs, fiber, sat.fat, category
    """
    if not os.path.exists(path):
        st.error(f"Dataset not found at {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # ── normalise column names ──────────────────────────────────────────────
    df.columns = df.columns.str.lower().str.strip()

    # Drop unnamed index column if present
    df = df.loc[:, ~df.columns.str.startswith("unnamed")]

    # ── column aliasing: new dataset → internal standard ───────────────────
    rename_map = {}

    # carbohydrate → carbs
    if "carbohydrate" in df.columns and "carbs" not in df.columns:
        rename_map["carbohydrate"] = "carbs"

    # saturated_fat OR saturated_fatty_acids → sat.fat
    for src in ("saturated_fat", "saturated_fatty_acids"):
        if src in df.columns and "sat.fat" not in df.columns:
            rename_map[src] = "sat.fat"
            break

    # total_fat → fat (only if fat column missing)
    if "total_fat" in df.columns and "fat" not in df.columns:
        rename_map["total_fat"] = "fat"

    if rename_map:
        df = df.rename(columns=rename_map)

    # ── strip unit strings from numeric columns ─────────────────────────────
    numeric_targets = [
        "calories", "protein", "fat", "carbs", "fiber", "sat.fat",
        "sodium", "cholesterol", "sugars", "water", "calcium", "potassium",
        "magnesium", "phosphorous", "iron", "irom", "zink", "selenium",
        "vitamin_c", "vitamin_a", "vitamin_d", "vitamin_e", "vitamin_b12", "vitamin_b6",
        "niacin", "folate", "thiamin", "riboflavin"
    ]
    for col in numeric_targets:
        if col in df.columns:
            df[col] = _strip_units(df[col])

    # ── derive grams from serving_size ──────────────────────────────────────
    if "grams" not in df.columns:
        if "serving_size" in df.columns:
            # e.g. "100 g" → 100.0
            df["grams"] = (
                df["serving_size"].astype(str)
                .str.extract(r"([\d.]+)", expand=False)
                .astype(float)
                .fillna(100)
            )
        else:
            df["grams"] = 100.0

    # ── derive category if missing ──────────────────────────────────────────
    food_col = df.columns[0]  # 'name'
    if "category" not in df.columns:
        df["category"] = df[food_col].apply(_derive_category)

    # ── final numeric coercion ──────────────────────────────────────────────
    for col in ["calories", "protein", "fat", "carbs", "fiber", "sat.fat", "grams"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── drop rows with no food name ─────────────────────────────────────────
    df = df.dropna(subset=[food_col])
    df = df[df[food_col].astype(str).str.strip() != ""]

    # ── Vegan / Non-Vegan tagging ───────────────────────────────────────────
    nv_categories = ["meat, poultry", "fish, seafood", "dairy products", "eggs"]
    nv_keywords = [
        "chicken", "beef", "pork", "steak", "fish", "salmon", "tuna", "shrimp",
        "crab", "lobster", "egg", "dairy", "milk", "cheese", "butter", "yogurt",
        "cream", "lard", "honey", "bacon", "ham", "sausage", "veal", "lamb", "duck"
    ]

    def is_vegan(row):
        name = str(row[food_col]).lower()
        cat  = str(row.get("category", "")).lower()
        if any(c in cat for c in nv_categories): return False
        if any(kw in name for kw in nv_keywords): return False
        return True

    def is_vegetarian(row):
        if row["is_vegan"]: return True
        cat  = str(row.get("category", "")).lower()
        name = str(row[food_col]).lower()
        meat_cats = ["meat, poultry", "fish, seafood"]
        meat_kws  = ["chicken", "beef", "pork", "steak", "fish", "salmon", "tuna",
                     "shrimp", "bacon", "ham", "sausage", "veal", "lamb", "duck"]
        if any(c in cat for c in meat_cats): return False
        if any(kw in name for kw in meat_kws): return False
        return True

    df["is_vegan"] = df.apply(is_vegan, axis=1)
    df["diet_type"] = df["is_vegan"].map({True: "Vegan", False: "Non-Vegan"})
    df["is_vegetarian"] = df.apply(is_vegetarian, axis=1)

    return df
