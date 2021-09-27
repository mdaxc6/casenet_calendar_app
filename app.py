from casenet import authenticate, slice_per, page_nav_df_create, handle_events
from flask import Flask, render_template, request, url_for, redirect
from flask_cors import CORS

chromedriver_location = "chrome_driver/chromedriver"
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
    if request.method == "POST":
        try:
            data = request.get_json()
            service = authenticate()
            main_df, datelist = page_nav_df_create(data)
            handle_events(service, main_df, datelist)
            return redirect('/confirmation')
        except:
            print("There was an error.")
            return
        
    else:
        return render_template("index.html")


@app.route('/confirmation', methods=['GET','POST'])
def confirmation():
    return render_template('confirmation.html')


@app.route("/about")
def about():
    return render_template("about.html")



if __name__ == '__main__':
    app.run(debug=True)
