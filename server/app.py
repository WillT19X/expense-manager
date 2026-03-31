from flask import Flask, render_template
from database import DataBaseSetup, OpenDBConn
import sqlite3 

app = Flask(
__name__,
template_folder="../client/templates",
static_folder="../client/static"
)

DataBaseSetup()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_page():
    return render_template("add.html")

@app.route("/home")
def home_page():
    return render_template("index.html")

if __name__=='__main__':
    app.run(debug=True)