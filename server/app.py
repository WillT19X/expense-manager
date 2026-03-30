from flask import Flask 
from database import DataBaseSetup, OpenDBConn
import sqlite3

app = Flask(__name__)
DataBaseSetup()

@app.route("/")
def home():
    return "message: expense api running"

if __name__=='__main__':
    app.run(debug=True)