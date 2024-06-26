# Import the necessary modules
import flask
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from Data_Core import *
import os, time, requests, hashlib
import json

config_file = json.load(open("static/config.json", "r"))
# Create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'een geheime sleutel'
correct_user = "user"
# facebook_toeganstoken is token.txt
fb_app_id = "set your app id here"
fb_app_secret = "set your app secret here"
fb_id = config_file["fb_id"]
server_adres = config_file["domain"]

login_manager = LoginManager()
login_manager.init_app(app)


def hash_password(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode())
    return sha1.hexdigest()


def post(foto_locatie: str, beschrijving: str) -> bool:
    foto_url = f"http://{server_adres}/get_image/{foto_locatie}"

    # Maak de URL voor de Facebook API-aanroep
    with open("token.txt", "r") as f:
        facebook_toegangstoken = f.read
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


@login_manager.user_loader
def load_user(user_id):
    # Check if the user ID matches the ID of your single user
    if user_id == correct_user:
        # Return a user object (you can create a simple User class)
        return User(user_id)  # Replace with your actual User class instantiation

    return None  # Return None if the user ID doesn't match


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id  # Set the user ID

    def is_active(self):
        # Since you have only one user, consider them always active
        return True

    def get_id(self):
        # Return the user ID as a string
        return str(self.id)


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == correct_user and hash_password(password) == config_file["passwordHash"]:
            login_user(load_user(username))
            return redirect(url_for('secure'))
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


@app.route('/config', methods=['POST', 'GET'])
@login_required
def config():
    error = None
    if request.method == "POST":
        print("Post")
        try:
            if "background-image" in request.files:
                # If there is a file named 'background-image' in the request
                # Get the file from the request
                photo = request.files['background-image']
                if photo.filename != '':
                    # Save the uploaded file to the 'uploads' directory
                    path = "static/achtergrond.png"
                    photo.save(path)
            if "logo-image" in request.files:
                # Get the file from the request
                photo = request.files['logo-image']
                if photo.filename != '':
                    # Save the uploaded file to the 'uploads' directory
                    path = "static/logo.png"
                    photo.save(path)
            if "site-title" in request.form:
                title = request.form.get('site-title')
                if title != "":
                    save_json("title", title)
            if "domain" in request.form:
                domain = request.form.get('domain')
                if domain != "":
                    save_json("domain", domain)
            if "fb_app_id" in request.form:
                fb_app_id = request.form.get('fb_app_id')
                if fb_app_id != "":
                    save_json("fb_app_id", fb_app_id)
            if "fb_id" in request.form:
                fb_id = request.form.get('fb_id')
                if fb_id != "":
                    save_json("fb_id", fb_id)
            if "fb_token" in request.form:
                fb_token = request.form.get('fb_token')
                if fb_token != "":
                    save_json("fb_token", fb_token)
            if "fb_secret" in request.form:
                fb_secret = request.form.get('fb_secret')
                if fb_secret != "":
                    save_json("fb_app_secret", fb_secret)
            if "password" in request.form:
                passwordHash = hash_password(request.form.get('password'))
                if passwordHash != "":
                    save_json("passwordHash", passwordHash)
            error = 0
        except Exception as e:
            error = e
            print(e)
    return render_template("config.html", error=error)


@app.route('/get_image/<image_name>')
def get_image(image_name):
    return send_from_directory("static", image_name)


# Route for handling 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Route for handling 401 errors
@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401


def save_json(path, file):
    filename = 'static/config.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        data[path] = file
    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


# If this script is run directly (not imported as a module)
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
