# Flask knows to look under static folder

from flask import Flask, render_template, request, redirect, url_for
from flask import flash # for flash messages on the screen
from flask_wtf import FlaskForm # We can also do the forms ourselves, but it is easly helps us to build forms
from wtforms import StringField, SubmitField, EmailField # Different Fields we can import
from wtforms.validators import DataRequired # If we something pop-up when someone don't fill that area, this one take cares of it
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
## For CSRF Token
app.config['SECRET_KEY'] = "!+wvnadscgth349G6hr8pERTB_hWrtlkt*12-G43rf"
## Add Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
## Initialize The Database
db = SQLAlchemy(app)

## Generate Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(55), nullable = False)
	email = db.Column(db.String(125), nullable = False, unique = True)
	date_added = db.Column(db.DateTime, default = datetime.utcnow)

	## Generate a String
	def __repr__(self):
		return '<Name %r>' % self.name
	
## Generate Form for Model
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = EmailField("Email", validators=[DataRequired()])
	submit = SubmitField(label = "Submit!")


## Generate Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField(label = "Submit It!")

#################################### ROUTES ####################################
@app.route("/")
def index():
	flash("Successfully logged in")
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
		flash("Form Submitted Successfully!") # We don't have to pass as a paramter to render template, flash knows what to do with it

	return render_template("name.html", name = name, form = form)

@app.route("/user/add", methods = ["GET", "POST"])
def add_user():
	name = None
	form = UserForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(email = form.email.data).first()
		if user is None:
			newUser = Users(name=form.name.data, email = form.email.data)
			db.session.add(newUser)
			db.session.commit()
			flash("User Added successfully!")
		else:
			flash("User not added, Email adress is already in use!")
		name = form.name.data
		form.name.data = ""
		form.email.data = ""
		
	our_users = Users.query.order_by(Users.id)
	return render_template("add_user.html", form = form, name = name, our_users = our_users)