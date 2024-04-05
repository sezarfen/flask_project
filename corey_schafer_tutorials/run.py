from flaskblog import app
# this part works if we call the app with python3 'filename' | instead of 'flask run'
if __name__ == '__main__':
	app.run(debug=True)