# Import the necessary modules from the Flask library
from flask import Flask, request, render_template

# Create an instance of the Flask class
app = Flask(__name__)

# Define a route for the app. This route accepts both POST and GET requests.
@app.route('/', methods=['POST', 'GET'])
def upload():
    # Print a message to the console
    print("Bijna")
    # Print the HTTP method used in the request
    print(request.method)
    # If the HTTP method is POST
    if request.method == "POST":
        # Print a message to the console
        print("JA")
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
            photo.save('uploads/' + photo.filename)
            # Print the description to the console
            print(description)
    # Render the 'index.html' template
    return render_template("index.html")

# If this script is run directly (not imported as a module)
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
