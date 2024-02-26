# Import the necessary modules
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_apscheduler import APScheduler
from Data_Core import *
import os, time, requests, hashlib

# Create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'een geheime sleutel'
correct_hash = "set your passwordhash here"
correct_user = "user"
#facebook_toeganstoken is token.txt
fb_app_id = "set your app id here"
fb_app_secret = "set your app secret here"
fb_id = "set your user or page id here"
server_adres = "set your domain here"

login_manager = LoginManager()
login_manager.init_app(app)
planner = APScheduler()


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
def load_user(user):
    if user == correct_user:
        return True


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        correct_hash = hash_password("password")
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


@app.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    return render_template("config.html")


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


#keep the secret working
def vernieuw_token():
    with open("token.txt", "r") as f:
        token = f.read()
    # Controleer de vervaldatum van het token
    url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
    response = requests.get(url)
    data = response.json()
    expires_at = data["data"]["expires_at"]
    # Als het token minder dan een dag geldig is, vernieuw het
    if expires_at - time.time() < 86400:
        url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={fb_app_id}&client_secret={fb_app_secret}&fb_exchange_token={token}"
        response = requests.get(url)
        data = response.json()
        token = data["access_token"]
        # Schrijf het vernieuwde token terug naar het token.txt bestand
        with open("token.txt", "w") as f:
            f.write(token)


planner.add_job(func=vernieuw_token, trigger="interval", days=1, id="Z")
planner.start()
# If this script is run directly (not imported as a module)
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
