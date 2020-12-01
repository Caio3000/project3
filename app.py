from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo, MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField

import main_functions

app = Flask(__name__)

credentials = main_functions.read_from_file("credentials.json")
username = credentials["username"]
password = credentials["password"]

app.config["SECRET_KEY"] = "COP4813"
app.config["MONGO_URI"] = "mongodb+srv://{0}:{1}@cluster0.crtby.mongodb.net/db?retryWrites=true&w=majority".format(username, password)
mongo = PyMongo(app)


class Expenses(FlaskForm):
    description = StringField("Description")

    category = SelectField("Category",
                           choices=[('food', 'Food'),
                                    ('gas', 'Gas'),
                                    ('phone', 'Phone'),
                                    ('clothes', 'Clothes'),
                                    ('gaming', 'Gaming')])

    cost = DecimalField("Cost")

    date = DateField("Date",
                     format='%m-%d-Y%')

def get_total_expenses(category):
    my_expenses = mongo.db.expenses.find({"category": category})
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])

    return total_cost


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    expensesByCategory = [
        ("food", get_total_expenses("food")),
        ("gas", get_total_expenses("gas")),
        ("phone", get_total_expenses("phone")),
        ("clothes", get_total_expenses("clothes")),
        ("gaming", get_total_expenses("gaming"))]

    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        mongo.db.expenses.insert_one(
            {"description": request.form["description"],
             "category": request.form["category"],
             "cost": float(request.form["cost"]),
             "date": request.form["date"]})

        return render_template("expensesAdded.html")
    return render_template("addExpenses.html", form=expensesForm)


app.run()
