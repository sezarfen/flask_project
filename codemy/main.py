# Flask knows to look under static folder

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash  # for flash messages on the screen

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from webforms import UserForm, NamerForm, PostForm, LoginForm, CommentForm, SearchForm, UpdatePostForm

from flask_ckeditor import CKEditor

#################################################################################
#################################### CONFIGS ####################################
#################################################################################


app = Flask(__name__)
# For CSRF Token
app.config['SECRET_KEY'] = "!+wvnadscgth349G6hr8pERTB_hWrtlkt*12-G43rf"
# Add Database (SQLite)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
# Database (MySql)
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://username:password@localhost/db_name" # +pymysql for new package to help connection
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:mysql1234@localhost/flask_project"
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

# Pass Stuff To Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

# Rich text editor
ckeditor = CKEditor(app)

################################################################################
#################################### MODELS ####################################
################################################################################


# Generate Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(25), nullable=False, unique=True) # unique=True causes a problem for sqlite database
	name = db.Column(db.String(55), nullable=False)
	email = db.Column(db.String(125), nullable=False, unique=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	favorite_color = db.Column(db.String(25))
	password = db.Column(db.String(101), nullable=False)
	# User Can Have Many Posts # There will be fake column like poster for posts
	posts = db.relationship("Post", backref="poster", lazy=True) # lazy=True as default, but lets implicit that
	comments = db.relationship("Comment", backref="author", lazy=True)

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
	#author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255)) # for a better url example instead of using /blog/1 using /blog/my_blog
	# Foreign key to link users (refer to primary key of the user)
	poster_id = db.Column(db.Integer, db.ForeignKey("users.id")) # this is querying the database, so it is lowercase
	comments = db.relationship("Comment", backref="post", lazy=True)


	def small_content(self):
		if len(self.content) > 15:
			return self.content[:15] + "..."
		else:
			return self.content
		
class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
	post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
	date_posted = db.Column(db.DateTime , default=datetime.utcnow)
	content  = db.Column(db.Text, nullable=False)

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
			return redirect(url_for("get_login"))
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

	if form.validate_on_submit(): # I think this already indicates request.method == "POST"
		poster_id = current_user.id
		post = Post(title=form.title.data, content=form.content.data, slug=form.slug.data, poster_id = poster_id)
		form.title.data = ""
		form.content.data = ""
		form.slug.data = ""
		try:
			db.session.add(post)
			db.session.commit()
			flash("Post Added Successfully!")
		except:
			flash("An Error Occured, Post Couldn't Added!")
		# Clear The Form Here
		return redirect(url_for("get_posts"))
	else:
		print(form.errors)

	return render_template("post/add_post.html", form = form)


@app.route("/posts", methods=["GET"])
def get_posts():
	posts = Post.query.all()
	return render_template("post/posts.html", posts = posts)


@app.route("/post/<string:slug>")
def get_single_post(slug):
	comment_form = CommentForm()
	post = Post.query.filter_by(slug = slug).first()
	if post is None:
		flash("Couldn't find that post")
		return redirect(url_for("get_posts"))
	return render_template("post/single_post_page.html", post = post, comment_form = comment_form)


@app.route("/post/edit/<int:id>", methods=["GET", "POST"])
@login_required
def get_edit_post(id): # additional check might be added
	form = UpdatePostForm()
	post = Post.query.get_or_404(id)

	if post.poster.id != current_user.id:
		flash("You are not authorized to update this post")
		return redirect(url_for("get_posts"))
	
	if form.validate_on_submit():
		slug_check = Post.query.filter_by(slug = form.slug.data).first()
		if post.slug == form.slug.data or slug_check is None:
			post.title = form.title.data
			post.content = form.content.data
			post.slug = form.slug.data
			db.session.add(post)
			db.session.commit()
			flash("Post Updated Successfully!")
			return redirect(url_for("single_post_page", slug = post.slug))
		else:
			flash("this slug is already in use!")
			return render_template("post/update_post.html", post=post, form=form)

	return render_template("post/update_post.html", post=post, form=form)


@app.route("/post/delete/<int:id>")
@login_required
def delete_post(id):
	try:
		post = Post.query.get_or_404(id)
		if post.poster.id != current_user.id:
			flash("You are not authorized to delete this post!")
			return redirect(url_for("get_posts"))
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
	our_users = Users.query.all()
	return render_template("dashboard.html", our_users = our_users)


# Generate Logout Function
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	flash("Logged Out Successfully!")
	return redirect(url_for("get_login"))


@app.route("/comment", methods=["POST"])
@login_required
def comment():
	form = CommentForm()

	if form.validate_on_submit():
		try:
			newComment = Comment(author_id = current_user.id, post_id=request.form["post_id"], content = form.content.data)
			db.session.add(newComment)
			db.session.commit()
		except:
			flash("Something went wrong.")
		form.content.data = ""
	return redirect(url_for("get_single_post", slug = request.form["post_slug"]))


@app.route("/comment/delete/<int:id>", methods=["GET"])
def delete_comment(id):
	post_slug = 0
	try:
		comment = Comment.query.get_or_404(id)
		post_slug = comment.post.slug
		if comment.author.id != current_user.id:
			flash("You are not authorized to delete this comment")
		else:
			db.session.delete(comment)
			db.session.commit()
	except:
		flash("An error occured!")
	return redirect(url_for("get_single_post", slug=post_slug))


@app.route("/search", methods=["POST"])
def search():
	form = SearchForm()
	if form.validate_on_submit():
		keyword = form.searched.data
		posts = Post.query.filter(Post.content.like("%" + keyword + "%"))
		return render_template("search.html", form=form, posts=posts)
