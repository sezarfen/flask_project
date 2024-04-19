#################################################################################
####################################  FORMS  #################################### // Let's don't forget {{form.hidden_tag()}}
#################################################################################

from flask_wtf import FlaskForm  # We can also do the forms ourselves, but it is easily helps us to build forms
from wtforms import StringField, SubmitField, EmailField, PasswordField  # Different Fields we can import
from wtforms.validators import DataRequired, EqualTo  # If something pop-up when someone doesn't fill that area, this one take cares of it
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

# Generate Form for Model
class UserForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	name = StringField("Name", validators=[DataRequired()])
	email = EmailField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color", validators=[DataRequired()])
	about_author = StringField("About Author", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match!")])  # we can use that message later
	submit = SubmitField(label="Submit!")


# Generate Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField(label="Submit It!")


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = CKEditorField("Content", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField(label="Submit!")

class UpdatePostForm(FlaskForm):
	title = StringField(label="Title", validators=[DataRequired()])
	content = CKEditorField(label="Content", validators=[DataRequired()])
	slug = StringField(label="Slug", validators=[DataRequired()])
	submit = SubmitField(label="Update!")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Login!")

class CommentForm(FlaskForm):
	content = StringField("Your Comment", validators=[DataRequired()], widget=TextArea())
	submit = SubmitField("Comment it out!")

# Form for search
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Search")