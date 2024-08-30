import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


with open('static/models/vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

vectorized_df = pd.read_pickle('static/data/precomputed_vectors.pkl')

def get_max_cosine_similarity(query):
    query_vector = vectorizer.transform([query]).toarray()

    text_columns = ['Name', 'Meeting Time', 'Location', 'Sponsor', 'Description', 'Tags', 'Contact', 'Combined Description']
    max_similarities = []
    for i, row in vectorized_df.iterrows():
        similarities = []
        for column in text_columns:
            if column in vectorized_df.columns:
                vector = row[column]
                similarity = cosine_similarity(query_vector, [vector])[0][0]
                similarities.append(similarity)
        magnitude = np.linalg.norm(similarities)
        max_similarities.append(magnitude)
        
    output_df = pd.DataFrame({
        'Name': vectorized_df['Club Name'],
        'MaximumSimilarityScore': max_similarities
    })

    # Filter out rows with a similarity score of 0
    output_df = output_df[output_df['MaximumSimilarityScore'] > 0]
    
    # Sort the DataFrame by MaximumSimilarityScore in descending order
    output_df = output_df.sort_values(by='MaximumSimilarityScore', ascending=False)
    
    return output_df['Name']