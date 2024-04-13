import mysql.connector

mydb = mysql.connector.connect(
	host="localhost",
	user="__username__",
	passwd="__password__"
)

my_cursor = mydb.cursor()

my_cursor.execute("CREATE DATABASE __DATABASE_NAME__")

my_cursor.execute("SHOW DATABASES")

# To check if our db is generated or not
for db in my_cursor:
	print(db)