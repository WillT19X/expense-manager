from flask import Flask, render_template, request, flash, redirect, jsonify
from database import DataBaseSetup, OpenDBConn
import sqlite3 

app = Flask(
__name__,
template_folder="../client/templates", # define the route for pages
static_folder="../client/static" # define the route for static contribution (JS and CSS)
)
DataBaseSetup()

@app.route("/")
def home():
    with OpenDBConn() as conn:
        expenses = conn.execute("SELECT * FROM expenses").fetchall() # create route to index, integrate expenses to page to check functionality 
    return render_template("index.html", expenses=expenses)

@app.route("/add", methods=["GET","POST"])
def add_expense():
    if request.method == "POST":

        date = (request.form.get("date"))
        cost_gdp = (request.form.get("cost"))
        description = (request.form.get("description"))
        category = (request.form.get("category"))

        if not date or not date.strip():
            flash("date is required, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        
        if not description or not description.strip():
            flash("description required for expense, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        
        passed__choice = ["travel","food", "other"]
        if category not in passed__choice:
            flash ("invalid category, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        
        if not cost_gdp:
            flash("cost is a required field, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        try:
            costValueCheck = float(cost_gdp)
        except:
            flash("cost must be a numeric value, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        
        if costValueCheck <= 0:
            flash("cost cannot be equal or less than 0, error")
            return render_template("add.html", date=date, cost=cost_gdp, description=description, category=category), 400
        
        with OpenDBConn() as conn:
            conn.execute(
                "INSERT INTO expenses (date, cost_gbp, description, expense_type) VALUES (?, ?, ?, ?)",
                (date, costValueCheck, description, category) 
            )
            conn.commit()

            return redirect("/")
    return render_template("add.html")

# API endpoints from openAPI specification

@app.route("/expenses", methods=["GET"])
def get_expenses():
    # open a connection with the SQLite database
    with OpenDBConn() as conn:
        # retrieve all rows from the expense table
        rows = conn.execute("SELECT * FROM expenses").fetchall()

        # convert each database row that it becomes suited for JSON, 
        # "i" represents a single row 
    expenses = [
        {
        "id": i["id"],
        "date": i["date"],
        "cost_gbp": i["cost_gbp"],
        "description": i["description"],
        "expense_type": i["expense_type"]
        }
        for i in rows
    ]
    # return the list as JSON with an OK (200)
    return jsonify(expenses), 200
    


@app.route("/expenses", methods=["POST"])
def create_expense():
    # extracting the json from the request
    data = request.get_json()

    fieldsRequired = ["date","cost_gbp","description","expense_type"] # defining the required fields 
    for f in fieldsRequired:
        if f not in data:
            return jsonify("field:" f"{f} not found"), 400
    
    from datetime import datetime # used to validate date formatting
    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return jsonify("error, date must be in format (YYYY-MM-DD)"), 400
    
    try:
        PriceValue = float(data["cost_gbp"])
        if PriceValue < 0:
            return jsonify("error, cost must be greater than 0")
    except ValueError:
        return jsonify("cost must be be a numeric value"), 400
    
    if data["expense_type"] not in ["travel","food","other"]:
        return jsonify("invald expense type"), 400
    
    # after validation, insert into database

    with OpenDBConn() as conn:
        # cursor is an object to execute sql queries
        cursor = conn.execute("INSERT INTO expenses (date, cost_gbp, description, expense_type) VALUES (?,?,?,?)",
        (data["date"], PriceValue, data["description"], data["expense_type"] )
        )
        conn.commit()
        ID = cursor.lastrowid    

        expense_created = {
            "id": ID,
            "date": data["date"],
            "cost_gbp": PriceValue,
            "description": data["description"],
            "expense_type": data["expense_type"]
        }
    return jsonify(expense_created), 201              
        

@app.route("/expenses/<int:id>", methods=["GET"])
def get_expense_by_id(id):
    with OpenDBConn() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
        if row is None:
            return jsonify("error, Expense not found")
        
        expense = {
            "id": row["id"],
            "date": row["date"],
            "cost_gbp": row["cost_gbp"],
            "description": row["description"],
            "expense_type": row["expense_type"]
        }
    return jsonify(expense), 200

@app.route("/selected_expense/<int:id>")
def defined_expense(id):
    with OpenDBConn() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?",
                           (id,)).fetchone()
        if row is None:
            return render_template("invalid_expense.html")
        
        expense = {
            "id": row["id"],
            "date": row["date"],
            "cost_gbp": row["cost_gbp"],
            "description": row["description"],
            "expense_type": row["expense_type"]
        }
    return render_template("selected_expense.html", expense=expense)



@app.route("/ViewExpense", methods=["GET"])
def expense_page():
    return render_template("ViewExpense.html")

@app.route("/ViewExpense", methods=["POST"])
def individual_expense():
    expense_id = request.form.get("expense_id")
    return redirect(f"/selected_expense/{expense_id}")

if __name__=='__main__':
    app.run(debug=True)