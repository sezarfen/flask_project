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
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

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
# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "get_login" # The function that login will redirect, if login_required for example, works like url_for('get_login')
login_manager.login_message = "Please Login first to visit that website." # The message to flash when a user is redirected to the login page.

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


################################################################################
#################################### MODELS ####################################
################################################################################


# Generate Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(25), nullable=False) # unique=True causes a problem
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
	username = StringField("Username", validators=[DataRequired()])
	name = StringField("Name", validators=[DataRequired()])
	email = EmailField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match!")])  # we can use that message later
	submit = SubmitField(label="Submit!")


# Generate Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField(label="Submit It!")


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField(label="Submit!")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Login!")


######################### #######################################################
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
def add_user(): # Register Page
	username = None
	form = UserForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			hashed = generate_password_hash(form.password.data)
			newUser = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data,
							password=hashed)
			db.session.add(newUser)
			db.session.commit()
			flash("User Added successfully!")
		else:
			flash("User not added, Email adress is already in use!")
		username = form.username.data # I think, this is not in use currently
		form.username.data = ""
		form.name.data = ""
		form.email.data = ""
		form.favorite_color.data = ""
		form.password.data = ""

	our_users = Users.query.order_by(Users.id)
	return render_template("user/add_user.html", form=form, username=username, our_users=our_users)


@app.route("/user/<int:id>", methods=["GET", "POST"])
@login_required
def get_user(id):
	if int(current_user.id) != id:
		flash("You cannot edit that user!")
		return redirect(url_for("get_dashboard"))
	if request.method == "GET":
		user = Users.query.get_or_404(id)
		return render_template("user/update_user.html", user=user)
	elif request.method == "POST":
		user = Users.query.get_or_404(id)
		user.username = request.form['username']
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
@login_required
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
@login_required
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
def add_post(): # We don't need to put @login_required all the time, we can also add logic to html files
	form = PostForm()

	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
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

	return render_template("post/add_post.html", form = form)


@app.route("/posts", methods=["GET"])
def get_posts():
	posts = Post.query.all()
	return render_template("post/posts.html", posts = posts)


@app.route("/post/<string:slug>")
def get_single_post(slug):
	post = Post.query.filter_by(slug = slug).first()
	return render_template("post/single_post_page.html", post = post)


@app.route("/post/edit/<int:id>", methods=["GET", "POST"])
@login_required
def get_edit_post(id): # additional check might be added
	post = Post.query.get_or_404(id)
	try:
		if request.method == "POST":
			slug_check = Post.query.filter_by(slug = request.form["slug"]).first()
			if post.slug == request.form["slug"] or slug_check is None:
				post.title = request.form["title"]
				post.content = request.form["content"]
				post.author = request.form["author"]
				post.slug = request.form["slug"]
				db.session.add(post)
				db.session.commit()
				flash("Post Updated Successfully!")
				return redirect(url_for("single_post_page", slug = post.slug))
			else:
				flash("this slug is already in use!")
				return render_template("post/update_post.html", post = post)
		elif request.method == "GET": 
			post = Post.query.get_or_404(id)
	except:
		flash("error") # can change later
	return render_template("post/update_post.html", post = post)


@app.route("/post/delete/<int:id>")
@login_required
def delete_post(id):
	try:
		post = Post.query.get_or_404(id)
		db.session.delete(post)
		db.session.commit()
		flash("Post Deleted Successfully!")
	except:
		return redirect(url_for("error", err = 404))
	return redirect(url_for("get_posts"))


@app.route("/login", methods=["GET", "POST"])
def get_login():
	form = LoginForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(username = form.username.data).first()
		if user:
			# Check the hash
			if check_password_hash(user.password, form.password.data):
				# User can log in
				login_user(user)
				flash("Logged In Successfully!")
				return redirect(url_for("get_dashboard"))
			else:
				flash("Wrong password, please try again!")
		else:
			flash("This user does not exist, try again.")


	return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def get_dashboard():
	return render_template("dashboard.html")


# Generate Logout Function
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	flash("Logged Out Successfully!")
	return redirect(url_for("get_login"))