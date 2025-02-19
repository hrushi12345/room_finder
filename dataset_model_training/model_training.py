import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Load the dataset
df = pd.read_csv('dataset_model_training/hotel_reviews.csv')

# Select relevant features for recommendations
df['combined_features'] = df['hotel_name'] + " " + df['region'] + " " + df['accommodation_type']

# Convert text data into numeric vectors
vectorizer = TfidfVectorizer(stop_words='english')
feature_matrix = vectorizer.fit_transform(df['combined_features'])

# Compute similarity matrix
cosine_sim = cosine_similarity(feature_matrix)

# Function to get recommendations
def recommend_hotels(hotel_name, num_recommendations=5):
    if hotel_name not in df['hotel_name'].values:
        return []
    
    index = df[df['hotel_name'] == hotel_name].index[0]
    similarity_scores = list(enumerate(cosine_sim[index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    recommended_indices = [i[0] for i in similarity_scores[1:num_recommendations + 1]]
    return df.iloc[recommended_indices][['hotel_name', 'region', 'cost', 'latitude', 'longitude']].to_dict(orient='records')

