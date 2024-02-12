# Import the necessary modules from the Flask library
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user
from Data_Core import *
import hashlib

# Create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'een geheime sleutel'

login_manager = LoginManager()
login_manager.init_app(app)


def hash_password(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode())
    return sha1.hexdigest()


correct_hash = "set your passwordhash here"
correct_user = "Set your user here"


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


@app.route('/dashboard')
@login_required
def secure():
    items = haal_data_op()
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


# If this script is run directly (not imported as a module)
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)