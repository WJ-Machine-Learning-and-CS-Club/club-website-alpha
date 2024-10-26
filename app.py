from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
import os
import csv
import cosineSim
import regular_search
import random
import image_upload
import dotenv
import secrets
import pandas as pd

app = Flask(__name__)

upload_folder = "uploads"
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = secrets.token_hex(32)
allowed_extensions = {'csv'}

def validate_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions 

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('admin'))
    
    file = request.files['file']

    # If the user does not select a file, the browser may submit an empty part
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('admin'))
    
    if file and validate_file(file.filename):
        # this is to prevent malicious stuff
        filename = secure_filename(file.filename)
        # Save the file to the upload folder
        filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('File successfully uploaded!', 'success')

        action = request.args.get("action")

        if action == 'all-clubs':
            image_upload.preprocess_file(filepath)
            image_upload.download_images('static/data/clubs_information.csv')
        elif action == 'featured-clubs':
            image_upload.preprocess_file_featured(filepath)
            image_upload.download_images_featured('static/data/featured_clubs_information.csv')
        else:
            flash('Invalid action.', 'danger')

        
        return redirect(url_for('admin'))
    flash('Invalid file type.', 'danger')
    return redirect(url_for('admin'))

@app.route('/delete',methods=['POST'])
def delete_files():
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except Exception as e:
            flash(f'Error deleting {filename}: {e}.', 'danger')
            return redirect(url_for('admin'))
    flash('Files successfully deleted!', 'success')
    return redirect(url_for('admin'))

def generate_html_featured(csv_file):
    clubs=[]
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader):
            clubs.append(row)
    return clubs


def generate_html(csv_file, clubsToDisplay=None):
    clubs = []
    rig = True
    rig_list=["AI Club", "Website Development Club"]
    fixed_indexes=[]
    total_index=0

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        rows = []
        for index, row in enumerate(reader):
            total_index+=1
            if row['Sponsor Replied'] == "True" and row['Added to Website'] == "True":
                rows.append(row)
                # Check if the club is in the rig list and add its index to fixed_indexes
                if row['Club Name'] in rig_list and rig:
                    fixed_indexes.append(index)

    if clubsToDisplay is None or len(clubsToDisplay) == 0:
        clubsToDisplay = list(range(len(rows)))
        #fixed_indexes = [57, 70]
        indexes_to_randomize = [i for i in clubsToDisplay if i not in fixed_indexes]
        randomized_indexes = random.sample(indexes_to_randomize, len(indexes_to_randomize))
        clubsToDisplay = fixed_indexes + randomized_indexes
    print(clubsToDisplay)
    for index in clubsToDisplay:
        if 0 <= index < len(rows):
            clubs.append(rows[index])

    return clubs, len(clubs), total_index

@app.route('/')
def index():
    clubs=generate_html_featured('static/data/featured_clubs_information.csv')
    return render_template('index.html', clubs=clubs)

@app.route('/asduawhdisahfka124124125234124151sjfkjawhgfkjhasgfkjwagu$fysabwfg"dropTables"sjavbwkjfhsavkfwygwa21249817249816725981635789573628956239457589264555564892189763500000000024958167928538745981367349812675893617346819251374198276491284536asduawhdisahfka124124125234124151sjfkjawhgfkjhasgfkjwagufysabwfgsjavbwkjfhsavkfwygwa21249817249816725981635789573628956239457589264555564892189763500000000024958167928538745981367349812675893617346819251374198276491284536')
def admin():
    return render_template('admin.html')
# Route for handling the button click
@app.route('/asduawhdisahfka124124125234124151sjfkjawhgfkjhasgfkjwagufysabwfgsjavbwkjfhsavkfwygwa21249817249816725981635789573628956239457589264555564892189763500000000024958167928538745981367349812675893617346819251374198276491284536asduawhdisahfka124124125234124151sjfkjawhgfkjhasgfkjwagufysabwfgsjavbwkjfhsavkfwygwa21249817249816725981635789573628956239457589264555564892189763500000000024958167928538745981367349812675893617346819251374198276491284536', methods=['POST'])
def call_function():
    # Call the Python function here
    result = adminFunction()
    return result
# Define the Python function to be called
def adminFunction():
    return "You clicked the admin button!"

@app.route('/clubslist')
def clubslist():
    clubs, total_clubs, num_clubs = generate_html('static/data/clubs_information.csv')
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)


@app.route('/clubslist/<user_query>')
def clubslistCustom(user_query):
    club_list = regular_search.get_min_levenshtein_distance(user_query).index
    clubs, total_clubs, num_clubs = generate_html('static/data/clubs_information.csv', club_list)
    return render_template('clubs.html', clubs=clubs, total_clubs=total_clubs, num_clubs=num_clubs)

@app.route('/admin_page/download_images')
def download_images():
    image_upload.download_images('static/data/club_info_2.csv')
    return render_template('index.html')

@app.route('/admin_page/upload_csv')
def upload_csv(file_path):
    image_upload.preprocess_file(file_path)
    return render_template('index.html')

@app.route('/admin_page/clear_images')
def delete_images():
    image_upload.delete_all_files('static/images')
    return render_template('index.html')

@app.route('/admin_page/download_featured_images')
def download_featured_images():
    image_upload.download_images_featured('static/data/sample_featured_clubs.csv')
    return render_template('index.html')

@app.route('/admin_page/upload_featured_csv')
def upload_featured_csv(file_path):
    image_upload.preprocess_file(file_path)
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    # Redirect to homepage or render a custom page
    return redirect(url_for('index'))

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', debug=True)
