# Flask knows to look under static folder

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash  # for flash messages on the screen

from flask_wtf import FlaskForm  # We can also do the forms ourselves, but it is easily helps us to build forms
from wtforms import StringField, SubmitField, EmailField, PasswordField  # Different Fields we can import
from wtforms.validators import DataRequired, \
	EqualTo  # If something pop-up when someone doesn't fill that area, this one take cares of it
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

#################################################################################
#################################### CONFIGS ####################################
#################################################################################


app = Flask(__name__)
# For CSRF Token
app.config['SECRET_KEY'] = "!+wvnadscgth349G6hr8pERTB_hWrtlkt*12-G43rf"
# Add Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

################################################################################
#################################### MODELS ####################################
################################################################################


# Generate Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(55), nullable=False)
	email = db.Column(db.String(125), nullable=False, unique=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	favorite_color = db.Column(db.String(25))
	password = db.Column(db.String(101), nullable=False)

	## Generate a String
	def __repr__(self):
		return '<Name %r>' % self.name

	def shorten_the_password(self):
		return str(self.password)[15:30] + "..."

	def get_name(self):
		if len(str(self.name)) > 15:
			return str(self.name)[:12] + "..."
		else:
			return str(self.name)

	def get_email(self):
		if len(str(self.email)) > 15:
			return str(self.email)[:12] + "..."
		else:
			return str(self.email)

	def to_dict(self):
		return {"id": self.id, "name": self.name, "email": self.email, "date_added" : self.date_added, "favorite_color": self.favorite_color, "password": self.password}


class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255)) # for a better url example instead of using /blog/1 using /blog/my_blog

	def small_content(self):
		if len(self.content) > 15:
			return self.content[:15] + "..."
		else:
			return self.content
		

#################################################################################
####################################  FORMS  #################################### // Let's don't forget {{form.hidden_tag()}}
#################################################################################



# Generate Form for Model
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = EmailField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password",
																							 message="Passwords must match!")])  # we can use that message later
	submit = SubmitField(label="Submit!")


# Generate Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField(label="Submit It!")


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	date_posted = StringField("Post Date") # validators DataRequired yapınca problem oluşuyordu
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField(label="Submit!")


#################################################################################
####################################   API   ####################################
#################################################################################



@app.route("/api/user/<int:uid>", methods=["GET"])
def get_api_id(uid):
	try:
		user = Users.query.get_or_404(uid)
		return user.to_dict()
	except:
		return jsonify({"id": -1})


@app.route("/api/date", methods=["GET"])
def get_api_date():
	return datetime.utcnow().strftime("%Y-%m-%d")



################################################################################
#################################### ROUTES ####################################
################################################################################


app.first_time = True


@app.route("/")
def index():
	if app.first_time:
		flash("Successfully logged in")
		app.first_time = False
	return render_template("main/index.html", name="Default")


@app.route("/about")
def about():
	return render_template("main/about.html")


@app.route("/info")
def info():
	return render_template("main/info.html")


@app.route("/form", methods=["GET", "POST"])
def form():
	if request.method == "POST":
		return redirect(url_for("index"))
	return render_template("form.html")


@app.errorhandler(404)
def error(err):
	return "{}".format(err)


# Generate Name Page

@app.route("/name", methods=["GET", "POST"])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		# We don't have to pass as a parameter to render template, flash knows what to do with it
		flash("Form Submitted Successfully!")

	return render_template("name.html", name=name, form=form)


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
	name = None
	form = UserForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			hashed = generate_password_hash(form.password.data, "sha256")
			newUser = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data,
							password=hashed)
			db.session.add(newUser)
			db.session.commit()
			flash("User Added successfully!")
		else:
			flash("User not added, Email adress is already in use!")
		name = form.name.data
		form.name.data = ""
		form.email.data = ""
		form.favorite_color.data = ""
		form.password.data = ""

	our_users = Users.query.order_by(Users.id)
	return render_template("user/add_user.html", form=form, name=name, our_users=our_users)


@app.route("/user/<int:id>", methods=["GET", "POST"])
def get_user(id):
	if request.method == "GET":
		user = Users.query.get_or_404(id)
		return render_template("user/update_user.html", user=user)
	elif request.method == "POST":
		user = Users.query.get_or_404(id)
		user.name = request.form['name']
		user.email = request.form['email']
		user.favorite_color = request.form['favorite_color']
		confirm_password = request.form['confirm_password']
		if check_password_hash(user.password, confirm_password):
			db.session.add(user)
			db.session.commit()
			flash("User updated succesfully!")
		else:
			flash("Password didn't match")
			return redirect(url_for("get_user", id=user.id))
		return redirect(url_for("add_user"))
	else:
		return redirect(url_for("add_user"))


@app.route("/user/delete/<int:id>")
def delete_user(id):
	try:
		user = Users.query.get_or_404(id)
		db.session.delete(user)
		db.session.commit()
		flash("User deleted successfully!")
	except Exception as e:
		print(e)
		flash("An error occured, please check the server or the logs, if you have any...")
	return redirect(url_for("add_user"))


@app.route("/user/update_password/<int:id>", methods=["GET", "POST"])
def update_user_password(id):
	if request.method == "GET":
		name = Users.query.get_or_404(id).name
		return render_template("user/update_password.html", id=id, name=name)
	elif request.method == "POST":
		try:
			user = Users.query.get(id)
			if check_password_hash(user.password, request.form['old_pwd']):
				p1 = request.form['new_pwd']
				p2 = request.form['confirm_new_pwd']
				if p1 == p2:
					user.password = generate_password_hash(p1)
					db.session.add(user)
					db.session.commit()
					flash("User password updated successfully!")
				else:
					flash("New password must be confirmed!")
			else:
				flash("Old Password didn't match!")
		except:
			flash("An error occured!")
		return redirect(url_for("add_user"))
	

@app.route("/add-post", methods=["GET", "POST"])
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
		print("ccccc")
		form.title.data = ""
		form.content.data = ""
		form.author.data = ""
		form.slug.data = ""
		try:
			db.session.add(post)
			db.session.commit()
			flash("Post Added Successfully!")
		except:
			flash("An Error Occured, Post Couldn't Added!")
		# Clear The Form Here
		return redirect(url_for("get_posts"))

	return render_template("add_post.html", form = form)

@app.route("/posts", methods=["GET"])
def get_posts():
	posts = Post.query.all()
	return render_template("posts.html", posts = posts)