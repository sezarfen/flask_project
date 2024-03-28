from flask import Flask
from flask import render_template #to render templates instead of single strings
app = Flask(__name__)

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

# this part works if we call the app with python3 'filename' | instead of 'flask run'
if __name__ == '__main__':
	app.run(debug=True)