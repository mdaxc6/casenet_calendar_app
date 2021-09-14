import casenet
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS



###################################################
# Flask Setup
###################################################
app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


###################################################
# Flask Routes
###################################################

#home page - index.html
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def process():
    # if request.method == "POST":
    data = request.get_json()
    print(data["MOBAR_Number"])
    return render_template("index.html")

# @app.route("/about")
# def about():
#     return render_template("about.html")
# #app page - input


if __name__ == '__main__':
    app.run(debug=True)
