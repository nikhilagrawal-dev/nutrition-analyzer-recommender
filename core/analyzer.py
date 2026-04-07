import pandas as pd
import numpy as np
from core.utils import RDA_VALUES, MACRO_SPLITS
from typing import Dict, Tuple, Any

def analyze_deficiencies(food_intake_dict: Dict[str, float], df: pd.DataFrame) -> Tuple[Dict[str, Any], str]:
    """
    Compares intake vs RDA, returns nutrient status + color codes.
    food_intake_dict: dict of {food_name: quantity_in_grams}
    """
    food_col = df.columns[0]
    intake = {
        "calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0, "sodium": 0.0
    }
    
    for food_name, grams in food_intake_dict.items():
        food_row = df[df[food_col] == food_name]
        if not food_row.empty:
            row = food_row.iloc[0]
            base_grams = row.get('grams', 100) or 100
            multiplier = grams / base_grams
            
            for f in intake.keys():
                if f in row:
                    intake[f] += row[f] * multiplier
                
    results = {}
    deficient = []
    over_limit = []
    
    for nutrient, rda in RDA_VALUES.items():
        val = intake[nutrient]
        pct = (val / rda) * 100
        
        status = "Amber"
        if 80 <= pct <= 120:
            status = "Green"
        else:
            status = "Red"
            if pct < 50:
                deficient.append(f"{nutrient.capitalize()} ({pct:.0f}%)")
            elif pct > 120:
                over_limit.append(f"{nutrient.capitalize()} ({pct:.0f}%)")
            
        results[nutrient] = {
            "consumed": val,
            "rda": rda,
            "pct": pct,
            "status": status
        }
        
    summary_parts = []
    if deficient:
        summary_parts.append(f"You are low in {', '.join(deficient)}.")
    if over_limit:
        summary_parts.append(f"You are over your limit in {', '.join(over_limit)}.")
        
    summary = " ".join(summary_parts) if summary_parts else "Your macro intake is within standard RDA ranges."
        
    return results, summary


def calculate_tdee(age: int, gender: str, weight_kg: float, height_cm: float, activity_level: str, goal: str) -> Dict[str, Any]:
    """
    BMI + TDEE + macro split calculation using Mifflin-St Jeor formula.
    """
    # BMI
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0
    
    bmi_category = "Normal"
    if bmi < 18.5: bmi_category = "Underweight"
    elif bmi >= 25 and bmi < 30: bmi_category = "Overweight"
    elif bmi >= 30: bmi_category = "Obese"
        
    # Mifflin-St Jeor
    if gender == "Male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
    # TDEE
    from core.utils import ACTIVITY_FACTORS
    tdee = bmr * ACTIVITY_FACTORS.get(activity_level, 1.2)
    
    # Macros
    split = MACRO_SPLITS.get(goal, MACRO_SPLITS["Maintenance"])
    target_cals = tdee * split["tdee_mult"]
    
    macros = {
        "calories": target_cals,
        "protein_g": (target_cals * split["protein"]) / 4,
        "carbs_g": (target_cals * split["carbs"]) / 4,
        "fat_g": (target_cals * split["fat"]) / 9,
        "protein_pct": split["protein"],
        "carbs_pct": split["carbs"],
        "fat_pct": split["fat"]
    }
    
    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_cals,
        "macros": macros
    }

def get_top_foods_by_nutrient(df: pd.DataFrame, nutrient_col: str, top_n: int = 10) -> pd.DataFrame:
    """
    Get top N foods for a selected nutrient.
    """
    if nutrient_col not in df.columns:
        return pd.DataFrame()
    
    # Handle 'Low Calorie' separately if needed, but here simple nlargest or nsmallest
    if nutrient_col == 'calories':
        return df[df['calories'] < 800].nsmallest(top_n, 'calories') # filter out outliers/high-cal
    return df.nlargest(top_n, nutrient_col)
