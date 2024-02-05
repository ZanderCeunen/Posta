from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def upload():
    print("Bijna")
    print(request.method)
    if request.method == "POST":
        print("JA")
        if "photo" in request.files:
            photo = request.files['photo']
            description = request.form.get('description')
            if photo.filename == '':
                return 'No selected file'
            photo.save('uploads/' + photo.filename)
            print(description)
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
