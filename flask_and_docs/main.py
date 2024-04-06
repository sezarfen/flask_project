from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/login", methods=["GET", "POST"])
def get_login():
	if request.method == "GET":
		return render_template("login.html")
	elif request.method == "POST":
		user = {"username" : request.form['username'], "email" : request.form['email']}
		return render_template("login.html", user = user)