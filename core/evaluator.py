import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from core.recommender import build_feature_matrix

def precision_at_k(recommendations, goal, df, k=10):
    """
    Of the top-K recommendations, how many are truly relevant 
    (define relevant = matches the user's goal nutrient thresholds)
    """
    if recommendations.empty: return 0.0
    recs = recommendations.head(k)
    
    relevant_count = 0
    # Threshold definition
    p_med = df['protein'].median()
    f_med = df['fiber'].median()
    c_med = df['calories'].median()
    fat_med = df['fat'].median()
    
    for _, row in recs.iterrows():
        is_rel = False
        if goal == "Weight Loss":
            is_rel = (row['calories'] <= c_med) and (row['fiber'] >= f_med)
        elif goal == "Muscle Gain":
            is_rel = (row['protein'] >= p_med)
        else: # Maintenance
            is_rel = True # Hard to define strictly for maintenance
        if is_rel:
            relevant_count += 1
            
    return relevant_count / len(recs)

def recall_at_k(recommendations, goal, df, k=10):
    """
    Of all relevant foods, how many appear in top-K.
    """
    if recommendations.empty: return 0.0
    
    # Threshold definition
    p_med = df['protein'].median()
    f_med = df['fiber'].median()
    c_med = df['calories'].median()
    
    if goal == "Weight Loss":
        total_rel = df[(df['calories'] <= c_med) & (df['fiber'] >= f_med)].shape[0]
    elif goal == "Muscle Gain":
        total_rel = df[df['protein'] >= p_med].shape[0]
    else:
        total_rel = df.shape[0]
        
    if total_rel == 0: return 0.0
        
    recs = recommendations.head(k)
    
    # relevant in top k
    relevant_count = 0
    for _, row in recs.iterrows():
        is_rel = False
        if goal == "Weight Loss":
            is_rel = (row['calories'] <= c_med) and (row['fiber'] >= f_med)
        elif goal == "Muscle Gain":
            is_rel = (row['protein'] >= p_med)
        else:
            is_rel = True
        if is_rel:
            relevant_count += 1
            
    return relevant_count / total_rel

def intra_list_diversity(recommendations, df):
    """
    Average pairwise dissimilarity among recommended foods
    """
    if len(recommendations) < 2: return 0.0
    
    # Extract features for only the recommended foods
    features = ["calories", "protein", "fat", "carbs", "fiber"]
    X = recommendations[features]
    
    # No need to fit global scaler, we can just use similarity on raw or locally scaled
    # Better to use raw for dissimilarity context or scale globally
    # Simpler: cosine similarity on raw since they're basic features
    sim_matrix = cosine_similarity(X)
    
    # Dissimilarity = 1 - similarity
    # Calculate avg of upper triangle
    n = len(recommendations)
    dissim_sum = 0
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            dissim_sum += (1 - sim_matrix[i, j])
            count += 1
            
    return dissim_sum / count if count > 0 else 0.0
