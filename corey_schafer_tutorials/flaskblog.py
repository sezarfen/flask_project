from flask import Flask
from flask import flash, redirect
from flask import render_template #to render templates instead of single strings
from flask import url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '1b5a0d4efabb1627bc3d80614699f00f815aa5b7153704bfbf'

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

ozellikler = [
	{"name" : "Emre",
	"major" : "Computer Engineering"
  }
]


#@app.route("/emre")
#def getEmrePage():
#	return render_template("Emre.html", ozellikler = ozellikler)

# this part works if we call the app with python3 'filename' | instead of 'flask run'
if __name__ == '__main__':
	app.run(debug=True)