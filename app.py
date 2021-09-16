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
    data = request.get_json()
    service = authenticate()
    main_df, datelist = page_nav_df_create(data)
    handle_events(service, main_df, datelist)
    return redirect('/test')


@app.route('/test', methods=['GET','POST'])
def loading():
    return render_template('test.html')



# @app.route("/about")
# def about():
#     return render_template("about.html")
# #app page - input


if __name__ == '__main__':
    app.run(debug=True)
