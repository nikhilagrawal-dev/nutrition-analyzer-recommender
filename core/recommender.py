import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import difflib
from core.utils import GOAL_WEIGHTS
from typing import List, Tuple, Optional, Dict

# ── Feature Matrix & Similarity ──

def build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Standardized nutritional feature matrix.
    """
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    X = df[features].copy()
    scaler = StandardScaler()
    return scaler.fit_transform(X)

def build_similarity_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Computes cosine similarity matrix on nutritional vectors.
    """
    X_scaled = build_feature_matrix(df)
    return cosine_similarity(X_scaled)


# ── XAI Explanation Generator ──

def generate_explanation(food_row: pd.Series, context: str, score: float = None, goal: str = None) -> str:
    """
    Generates explainable AI text for recommendations.
    Format: "Why recommended: [reason]"
    """
    if context == "goal":
        reason = f"Matches {goal} profile. "
        if goal == "Weight Loss":
            reason += f"Low calorie ({food_row['calories']} kcal), high fiber ({food_row['fiber']}g)."
        elif goal == "Muscle Gain":
            reason += f"High protein density ({food_row['protein']}g)."
        else:
            reason += f"Balanced macronutrient distribution."
    
    elif context == "similar":
        reason = f"Nutritionally similar (cosine score: {score:.2f})."
        
    elif context == "favorites":
        reason = f"Matches your taste profile based on your favorite selections."
    
    elif context == "hybrid":
        reason = f"Combines {goal} objectives with your personal food preferences."
    else:
        reason = "Recommended based on overall nutritional quality."

    return f"Why recommended: {reason}"

# ── Recommendations ──

def recommend_by_goal_ml(df: pd.DataFrame, goal: str, top_n: int = 10) -> pd.DataFrame:
    """
    Score foods using weighted nutrient formula and return top N.
    """
    df_rec = df.copy()
    weights = GOAL_WEIGHTS.get(goal, GOAL_WEIGHTS["Maintenance"])
    
    # Normalize features
    for col in ["protein", "calories", "fat", "fiber", "carbs"]:
        m = df_rec[col].max() or 1
        df_rec[f'{col}_norm'] = df_rec[col] / m
    
    if goal == "Weight Loss":
        scores = (df_rec['fiber_norm'] * weights["fiber"]) - (df_rec['calories_norm'] * weights["calories"]) - (df_rec['fat_norm'] * weights["fat"])
    elif goal == "Muscle Gain":
        scores = (df_rec['protein_norm'] * weights["protein"]) + (df_rec['carbs_norm'] * weights["carbs"]) - (df_rec['fat_norm'] * weights["fat"])
    else: # Balanced
        scores = (df_rec['protein_norm'] * 0.2 + df_rec['fiber_norm'] * 0.2 + df_rec['carbs_norm'] * 0.2 - df_rec['fat_norm'] * 0.2 - df_rec['calories_norm'] * 0.2)
        
    df_rec['ml_score'] = scores
    df_rec = df_rec.sort_values('ml_score', ascending=False).head(top_n)
    df_rec['explanation'] = df_rec.apply(lambda row: generate_explanation(row, context="goal", goal=goal), axis=1)
    
    return df_rec

def recommend_similar_foods(df: pd.DataFrame, food_name: str, top_n: int = 5) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Similarity search with fuzzy matching.
    """
    food_col = df.columns[0]
    food_list = df[food_col].tolist()
    
    # Fuzzy Match
    matches = difflib.get_close_matches(food_name, food_list, n=3, cutoff=0.3)
    if not matches:
        return None, "Food not found. No close matches available."
    
    # Check for exact match first
    exact_matches = [m for m in matches if m.lower() == food_name.lower()]
    matched_food = exact_matches[0] if exact_matches else matches[0]
    
    if exact_matches or matched_food.lower() == food_name.lower():
        idx = df[df[food_col] == matched_food].index[0]
        pos_idx = df.index.get_loc(idx)
        
        sim_matrix = build_similarity_matrix(df)
        sim_scores = list(enumerate(sim_matrix[pos_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Skip self (usually index 0)
        top_indices_scores = sim_scores[1:top_n+1]
        top_indices = [df.index[i] for i, _ in top_indices_scores]
        scores = [s for _, s in top_indices_scores]
        
        similar_df = df.loc[top_indices].copy()
        similar_df['similarity_score'] = scores
        similar_df['explanation'] = similar_df.apply(lambda row: generate_explanation(row, context="similar", score=row['similarity_score']), axis=1)
        
        return similar_df, matched_food
    else:
        # Return suggestions
        return None, f"Food not found. Did you mean: {', '.join(matches[:3])}?"

def recommend_from_favorites(df: pd.DataFrame, food_list: List[str], top_n: int = 10) -> pd.DataFrame:
    """
    Cold-start recommendations based on average profile of favorite foods.
    """
    if not food_list:
        return pd.DataFrame()
        
    food_col = df.columns[0]
    fav_df = df[df[food_col].isin(food_list)]
    
    if fav_df.empty:
        return pd.DataFrame()
        
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    avg_profile = fav_df[features].mean().values.reshape(1, -1)
    
    # Global scaling logic
    X = df[features]
    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)
    avg_scaled = scaler.transform(avg_profile)
    
    sim_scores = cosine_similarity(avg_scaled, X_scaled)[0]
    
    df_rec = df.copy()
    df_rec['similarity_score'] = sim_scores
    
    # Exclude already favorite foods
    df_rec = df_rec[~df_rec[food_col].isin(food_list)]
    df_rec = df_rec.sort_values('similarity_score', ascending=False).head(top_n)
    df_rec['explanation'] = df_rec.apply(lambda row: generate_explanation(row, context="favorites"), axis=1)
    
    return df_rec

def hybrid_recommendation(df: pd.DataFrame, goal: str, favorite_foods: List[str] = [], top_n: int = 10) -> pd.DataFrame:
    """
    Combined goal + favorites. Columns: food_name, score, source, explanation.
    """
    food_col = df.columns[0]
    goal_df = recommend_by_goal_ml(df, goal, top_n)
    goal_df['source'] = 'Goal match'
    goal_df['score'] = goal_df['ml_score']
    
    if favorite_foods:
        fav_df = recommend_from_favorites(df, favorite_foods, top_n)
        if not fav_df.empty:
            fav_df['source'] = 'Similar to favorites'
            fav_df['score'] = fav_df['similarity_score']
            
            # Combine & Re-rank
            combined = pd.concat([goal_df, fav_df])
            # Assign normalized score if necessary, here we just prioritize goal
            combined = combined.drop_duplicates(subset=[food_col], keep='first')
            combined = combined.sort_values('score', ascending=False).head(top_n)
            
            # Recalculate explanations for hybrid context or keep existing
            combined['explanation'] = combined.apply(
                lambda row: f"{row['explanation']} ({row['source']})", axis=1
            )
            return combined
            
    return goal_df
