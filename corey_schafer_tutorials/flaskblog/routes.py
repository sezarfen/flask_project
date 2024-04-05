from flask import render_template, url_for, flash, redirect, request
from flaskblog import app
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

posts = [
	{
		"author": "Author 1",
		"title": "Title 1",
		"content": "First Content Of the First Title 1",
		"date_posted": "28 03 2024"
	},
	
	{
		"author": "Author 2",
		"title": "Title 2",
		"content": "Title 2 Content goes here !",
		"date_posted": "28 03 2024"
	}
]

@app.route("/")
@app.route("/home")
def	getHome():
	return render_template("home.html", posts=posts) # which argument we give here, we can reach from templates

@app.route("/about")
def	getAbout():
	return render_template("about.html", Title = "About")

@app.route("/register", methods=['GET', 'POST'])
def getRegister():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f"Account generated for {form.username.data}!", "success")
		return redirect(url_for("getHome"))
	return render_template("register.html", title="Register", form=form)

@app.route("/login")
def getLogin():
	form = LoginForm()
	return render_template("login.html", title="Login", form=form)


@app.route("/user", methods = ["GET", "POST"])
def getUsers():
	users = User.query.all()
	if request.method == "POST":
		if (users.__len__() == 0):
			return {"info":"no user found"}
		else:
			return users
	else:
		return render_template("about.html")