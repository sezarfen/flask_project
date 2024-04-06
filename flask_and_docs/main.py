from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = "supersecretkey"
db = SQLAlchemy(app) # when I placed this under configs, it didn't allow me to import on python3 terminal
bcrpyt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


''' To generate database tables
	from main import app, db
	app.app_context().push()
	db.create_all()
'''

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), nullable = False, unique = True)
	password = db.Column(db.String(80), nullable = False)

class RegisterForm(FlaskForm):
	username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
	password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
	submit = SubmitField("Register")

	def validate_username(self, username):
		existing_username = User.query.filter_by(username = username.data).first()

		if existing_username:
			raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
	username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
	password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
	submit = SubmitField("Login")




@app.route("/")
def get_index():
	return render_template("index.html")


@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def get_dashboard():
	return render_template("dashboard.html")


@app.route("/register", methods = ["GET", "POST"])
def get_register():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = bcrpyt.generate_password_hash(form.password.data) # to hash the password, otherwise it will be plain text
		new_user = User(username=form.username.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for("get_login"))

	return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def get_login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user:
			if bcrpyt.check_password_hash(user.password, form.password.data):
				login_user(user)
				return redirect(url_for("get_dashboard"))
	return render_template("login.html", form = form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def get_logout():
	logout_user()
	return redirect(url_for("get_login"))


if __name__ == "__main__":
	app.run(debug=True)