from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from models import User, Post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MY_SUPER_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # "///"" for relative path from current file
db = SQLAlchemy(app)

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



# this part works if we call the app with python3 'filename' | instead of 'flask run'
if __name__ == '__main__':
	app.run(debug=True)