import pandas as pd
import streamlit as st
import os

# ── data_loader.py ───────────────────────────────────────────────────────────

@st.cache_data
def load_data(path="data/nutrition.csv"):
    """
    Load, clean and tag the nutrition dataset with Vegan/Non-Vegan indicators.
    """
    if not os.path.exists(path):
        st.error(f"Dataset not found at {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    
    # clean column names
    df.columns = df.columns.str.lower().str.strip()

    # convert numeric columns safely
    # fiber and sat.fat may contain 't' or other non-numeric strings
    numeric_cols = ["calories", "protein", "fat", "carbs", "fiber", "sat.fat", "grams"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Vegan / Non-Vegan Logic ──
    # Non-Vegan Categories
    nv_categories = ['meat, poultry', 'fish, seafood', 'dairy products']
    
    # Non-Vegan Keywords (Animal products)
    nv_keywords = [
        "chicken", "beef", "pork", "steak", "fish", "salmon", "tuna", "shrimp", 
        "crab", "lobster", "egg", "dairy", "milk", "cheese", "butter", "yogurt", 
        "cream", "lard", "honey", "bacon", "ham", "sausage", "veal", "lamb", "duck"
    ]
    
    def is_vegan(row):
        name = str(row[df.columns[0]]).lower()
        cat = str(row['category']).lower()
        
        # Check category
        if any(c in cat for c in nv_categories):
            return False
            
        # Check keywords in name
        if any(kw in name for kw in nv_keywords):
            return False
            
        return True

    df['is_vegan'] = df.apply(is_vegan, axis=1)
    df['diet_type'] = df['is_vegan'].map({True: 'Vegan', False: 'Non-Vegan'})
    
    # Add a Vegetarian tag (includes Dairy/Eggs but no Meat/Fish)
    def is_vegetarian(row):
        if row['is_vegan']: return True
        cat = str(row['category']).lower()
        name = str(row[df.columns[0]]).lower()
        
        # If it's not vegan but it's in Dairy or has Egg/Milk/Cheese keywords
        # and NOT in Meat/Fish categories and NOT containing Meat keywords
        meat_cats = ['meat, poultry', 'fish, seafood']
        meat_kws = ["chicken", "beef", "pork", "steak", "fish", "salmon", "tuna", "shrimp", "bacon", "ham", "sausage", "veal", "lamb", "duck"]
        
        if any(c in cat for c in meat_cats): return False
        if any(kw in name for kw in meat_kws): return False
        return True

    df['is_vegetarian'] = df.apply(is_vegetarian, axis=1)
    
    return df
