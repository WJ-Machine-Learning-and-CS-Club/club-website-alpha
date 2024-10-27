from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
#import cosineSim
import regular_search
import random
import image_upload
import dotenv
import secrets
import pandas as pd

app = Flask(__name__)

upload_folder = "uploads"
app.config['UPLOAD_FOLDER'] = upload_folder
allowed_extensions = {'csv'}

app.secret_key = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    

admin_user_test = User(1, "mrm", "wjclubs")

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return admin_user_test
    else:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if credentials match admin user
        if username == admin_user_test.username and admin_user_test.verify_password(password):
            login_user(admin_user_test)
            return redirect(url_for('admin'))
        
        flash("Invalid username or password", "danger")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def validate_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions 

@app.route('/upload', methods=['POST'])
@login_required
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
@login_required
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

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')
# Route for handling the button click

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
