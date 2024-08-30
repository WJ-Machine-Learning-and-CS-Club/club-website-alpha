from flask import Flask
import csv
from flask import render_template
import cosineSim
import regular_search
import random

app = Flask(__name__)

def generate_html(csv_file, clubsToDisplay=None):
    clubs = []
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if clubsToDisplay is None or len(clubsToDisplay) == 0:
        clubsToDisplay = list(range(len(rows)))
        num_fixed = 2
        fixed_indexes = clubsToDisplay[:num_fixed]
        indexes_to_randomize = clubsToDisplay[num_fixed:]
        randomized_indexes = random.sample(indexes_to_randomize, len(indexes_to_randomize))
        clubsToDisplay = fixed_indexes + randomized_indexes


    for index in clubsToDisplay:
        if 0 <= index < len(rows):
            clubs.append(rows[index])

    return clubs, len(clubs), len(rows)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/clubslist')
def clubslist():
    clubs, total_clubs, num_clubs = generate_html('static/data/clubs_info.csv')
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)

    
@app.route('/clubslist/<user_query>')
def clubslistCustom(user_query):
    club_list = regular_search.get_min_levenshtein_distance(user_query).index
    clubs, total_clubs, num_clubs = generate_html('static/data/clubs_info.csv', club_list)
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', debug=True)
