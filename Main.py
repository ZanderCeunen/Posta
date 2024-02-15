# Import the necessary modules
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user
from Data_Core import *
import hashlib
import requests

# Create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'een geheime sleutel'

correct_hash = "set your passwordhash here"
correct_user = "Set your user here"
imgur_toegangstoken = "set your access token here"
facebook_toegangstoken = "set your access token here"
fb_id = "set your user or page id here"

login_manager = LoginManager()
login_manager.init_app(app)


def hash_password(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode())
    return sha1.hexdigest()


def post(foto_locatie: str, beschrijving: str) -> bool:
    imgur_url = "https://api.imgur.com/3/image"
    imgur_headers = {
        "Authorization": f"Bearer {imgur_toegangstoken}"
    }
    imgur_data = {
        "image": foto_locatie,
        "type": "file"
    }
    imgur_response = requests.post(imgur_url, headers=imgur_headers, data=imgur_data)
    if imgur_response.status_code == 200:
        foto_url = imgur_response.json()["data"]["link"]
        # Maak de URL voor de Facebook API-aanroep
        facebook_url = f"https://graph.facebook.com/{fb_id}/photos"
        facebook_data = {
            "access_token": facebook_toegangstoken,
            "url": foto_url,
            "caption": beschrijving
        }
        facebook_response = requests.post(facebook_url, data=facebook_data)
        # Controleer de statuscode van het antwoord
        if facebook_response.status_code == 200:
            return True
        else:
            # Er is iets misgegaan met de Facebook API
            return False
    else:
        # Er is iets misgegaan met de Imgur API
        return False


@login_manager.user_loader
def load_user(user):
    if user == correct_user:
        return True


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == correct_user and hash_password(password) == correct_hash:
            login_user(load_user(username))
            return redirect(url_for('secure'))
        # Now you have the username and password, you can perform authentication here
        # Example: Check if the username and password match a user in the database
    return render_template('admin.html')


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def secure():
    items = haal_data_op()
    if request.method == "POST":
        for item in items:
            id = item[0]
            foto_locatie = item[1]
            beschrijving = item[2]
            if f"select-{id}" in request.form:
                new_description = request.form.get(f"description-{id}", beschrijving)
                if post(foto_locatie, new_description):
                    if verwijder_data(id):
                        os.remove("static/" + foto_locatie)
            if f"description-{id}" in request.form:
                new_description = request.form[f"description-{id}"]
                sla_beschrijving_op(new_description, id)
        return redirect(url_for('secure'))
    return render_template('dashboard.html', items=items)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))


# Define a route for the app. This route accepts both POST and GET requests.
@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == "POST":
        # If there is a file named 'photo' in the request
        if "photo" in request.files:
            # Get the file from the request
            photo = request.files['photo']
            # Get the description from the form data in the request
            description = request.form.get('description')
            # If no file was selected for upload
            if photo.filename == '':
                # Return an error message
                return 'No selected file'
            # Save the uploaded file to the 'uploads' directory
            path = 'uploads/' + str(haal_laatste_id_op()) + ".jpg"
            photo.save("static/" + path)
            afbeelding_met_beschrijving_uploaden(path, description)

    # Render the 'index.html' template
    return render_template("index.html")


# Route for handling 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Route for handling 401 errors
@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401


# If this script is run directly (not imported as a module)
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
