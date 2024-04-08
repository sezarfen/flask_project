from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm # We can also do the forms ourselves, but it is easly helps us to build forms
from wtforms import StringField, SubmitField, FileField # Different Fields we can import
from wtforms.validators import DataRequired # If we something pop-up when someone don't fill that area, this one take cares of it

app = Flask(__name__)
## For CSRF Token
app.config['SECRET_KEY'] = "!+wvnadscgth349G6hr8pERTB_hWrtlkt*12-G43rf"


## Generate Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit It!")



#################################### ROUTES ####################################
@app.route("/")
def index():
	return render_template("index.html", name = "Default")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/info")
def info():
	return render_template("info.html")

@app.route("/form", methods = ["GET" , "POST"])
def form():	
	if request.method == "POST":
		return redirect(url_for("index"))
	return render_template("form.html")

@app.errorhandler(404)
def error(err):
	return "{}".format(err)

## Generate Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
	return render_template("name.html", name = name, form = form)