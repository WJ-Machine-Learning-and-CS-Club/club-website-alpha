import pandas as pd
import numpy as np
import Levenshtein as lev


rig=True
vectorized_df = pd.read_csv('static/data/clubs_info.csv')

def get_max_cosine_similarity(query):
    query_vector = query.toarray()

    text_columns = ['Name', 'Meeting Time', 'Location', 'Sponsor', 'Description', 'Tags', 'Contact', 'Combined Description']
    max_similarities = []
    for i, row in vectorized_df.iterrows():
        similarities = []
        for column in text_columns:
            if column in vectorized_df.columns:
                vector = row[column]
                similarity = lev.distance(query_vector, [vector])[0][0]
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


def get_min_levenshtein_distance(query):
    text_columns = ['Name', 'Meeting Time', 'Location', 'Sponsor', 'Description', 'Tags', 'Contact', 'Combined Description']
    min_distances = []
    contains_query = []
    for i, row in vectorized_df.iterrows():
        distances = []
        contains = False
        for column in text_columns:
            if column in vectorized_df.columns:
                text = row[column]
                if not isinstance(text, str):
                    text = ''
                distance = lev.distance(query, text)
                distances.append(distance)

                if query.lower() in text.lower():
                    contains = True

        min_distance = min(distances) if distances else np.inf
        min_distances.append(min_distance)
        contains_query.append(contains)

    output_df = pd.DataFrame({
        'Name': vectorized_df['Name'],
        'MinimumDistanceScore': min_distances,
        'ContainsQuery': contains_query
    })
    # Filter out rows with an infinite distance (indicating no match at all)
    #output_df = output_df[(output_df['ContainsQuery'] == True) | ((output_df['MinimumDistanceScore'] != np.inf) & (output_df['MinimumDistanceScore'] < 0))]

    output_df = output_df[(output_df['ContainsQuery'] == True)]

    # Sort the DataFrame by MinimumDistanceScore in ascending order (smaller distance means more similar)
    output_df = output_df.sort_values(by='MinimumDistanceScore', ascending=True)
    if rig and len(output_df['Name'])!=0:
        if 'Machine Learning and Computer Science Club' in output_df['Name'].tolist() and 'Web Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([])
        elif 'Machine Learning and Computer Science Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'Web Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [1]
        elif 'Web Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'Machine Learning and Computer Science Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
        else:
            top_row = pd.DataFrame([
                {'Name': 'Machine Learning and Computer Science Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True},
                {'Name': 'Web Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
        #output_df = pd.concat([output_df[1:], top_row, output_df[:1]], ignore_index=True)
        output_df = pd.concat([output_df[:1], top_row, output_df[1:]], ignore_index=False)
    return output_df['Name']
