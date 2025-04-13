from calendar import monthrange
from datetime import date, timedelta
from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages, jsonify
from flask_session import Session
from supabase import create_client, Client
from helpers import *
from werkzeug.security import generate_password_hash


app = Flask(__name__)
# flask run --debug

app.jinja_env.filters["usd"] = format_usd
app.jinja_env.filters["abs"] = absolute
app.jinja_env.filters["date"] = format_date
app.jinja_env.globals["today"] = get_today
# app.jinja_env.

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database url: https://afrkbgvvhkkhujmskchj.supabase.co
# Database key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmcmtiZ3Z2aGtraHVqbXNrY2hqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzY1MDUzMiwiZXhwIjoyMDU5MjI2NTMyfQ.4w1zk-9Jx9xUo-7TWwbHywKmFJO0DkRkllicFjiHLLs

db_url = "https://afrkbgvvhkkhujmskchj.supabase.co"
db_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmcmtiZ3Z2aGtraHVqbXNrY2hqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzY1MDUzMiwiZXhwIjoyMDU5MjI2NTMyfQ.4w1zk-9Jx9xUo-7TWwbHywKmFJO0DkRkllicFjiHLLs"
db: Client = create_client(db_url, db_key)

# Website homepage
@app.route("/", methods=["POST", "GET"])
def index():
    return redirect("/login")

# User's dashboard
@app.route("/dashboard")
@login_required
def dashboard():   
    # Get user data
    user = list(db.table("users").select("*").eq("id", session.get("user_id")).execute())[0][1][0]
    balance = get_user_balance(db, session.get("user_id"))
    
    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month, monthrange(today.year, today.month)[1])
    income = db.table("transactions").select("abs_amount").eq("user_id", session.get("user_id")).eq("deleted", False).gt("amount", 0).gte("date_transacted", start).lte("date_transacted", end).execute().data
    income = [i["abs_amount"] for i in income]
    expenses = db.table("transactions").select("abs_amount").eq("user_id", session.get("user_id")).eq("deleted", False).lt("amount", 0).gte("date_transacted", start).lte("date_transacted", end).execute().data
    expenses = [i["abs_amount"] for i in expenses]
    income = sum(income)
    expenses = sum(expenses)
    
    # Go to user's dashboard
    return render_template("dashboard.html", username=user["username"], date_joined=user["date_joined"], balance=balance, income=income, expenses=expenses, page="dashboard")

# Login page
@app.route("/login", methods=["POST", "GET"])
def login():    
    # Login request
    if request.method == "POST":
        # Get input from page
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if inputs are valid
        if check_valid_login(db, username, password):
            # Log in the user for the current session
            set_session_user(db, username)
            
            # Go to user's dashboard
            return redirect("/dashboard")
        
    
    # Go to login page
    return render_template("login.html")

# Register page
@app.route("/register", methods=["POST", "GET"])
def register():
    # Register request
    if request.method == "POST":
        # Get fields filled out from page
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        student = request.form.get("student")
        balance = float(request.form.get("balance"))
        
        # Check for input validity
        if check_valid_registration(db, username, password, password2, balance):
            # Hash password for security
            hashed_password = generate_password_hash(password)
        
            # Add user to database
            db.table("users").insert({"username": username, "password_hash": hashed_password, "student": student}).execute()
            
            # Login user to the current session
            set_session_user(db, username)
            
            # Initialize user with $0
            db.table("balances").insert({"user_id": session["user_id"], "current_balance": balance}).execute()
            
            # Direct user to dashboard
            return redirect("/dashboard")
        
    
    # Go to register page
    return render_template("register.html")

# User logs out
@app.route("/logout")
def logout():
    # Clear current session
    session.clear()
    
    # Return to website homepage
    return redirect("/")

# Analysis page
@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html", page="analysis")

# Transactions page
@app.route("/transactions", methods=["POST", "GET"])
@login_required
def transactions():
    orders = {"date_transacted": "Date", "abs_amount": "Amount"}
    sort_by = "date_transacted"
    min_val = None
    max_val = None
    income = True
    expense = True
    desc = False
    if request.method == "POST":
        sort_by = request.form.get("sort")
        desc = request.form.get("reverse")
        desc = False if desc == "False" else True
        print(desc, sort_by)
    desc = not desc
    user_transactions = db.table("transactions").select("*, categories(category)").eq("user_id", session['user_id']).order(sort_by, desc=desc).execute().data
    has_transactions = len(user_transactions) > 0

    return render_template("transactions.html", transactions=user_transactions, has_transactions=has_transactions, sort=sort_by, order_keys=orders.keys(), orders=orders, desc=not desc, page="transactions")

# Add a transaction
@app.route("/add_transaction", methods=["POST", "GET"])
@login_required
def add_transaction():
    if request.method == "POST":
        if session.get("flash"):
            flash(session["flash"])
            del session["flash"]
            return redirect("/add_transaction")
        
        # Get inputs
        amount = float(request.form.get("amount"))
        date_transacted = request.form.get("date")
        category = request.form.get("category")
        type = request.form.get("type")
        print(type)
        category = 14 if (category == None) or (type == "income") else category
        amount *= -1 if type == "expense" else 1
        today = date.today()

        # try:
            # Add transaction to database table 'transactions'
        data = {
            "user_id": session.get("user_id"), 
            "amount": amount, 
            "abs_amount": abs(amount),
            "date_transacted": date_transacted, 
            "date_added": str(today), 
            "category_id": category
        }
        db.table("transactions").insert(data).execute()
        # except:
        #     flash("Invalid input!")
        #     return redirect("/add_transaction")
        
        # Update user's current balance
        current_balance = get_user_balance(db, session.get("user_id"))
        db.table("balances").update({"current_balance": current_balance+amount}).eq("user_id", session.get("user_id")).execute()
        
        return redirect("/transactions")
    
    return render_template("add_transaction.html", add=True, edit=False, categories=session["categories"])

# Edit a transaction page
@app.route("/edit_transaction", methods=["POST"])
@login_required
def edit_transaction():
    transaction_info = list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]
    print(transaction_info)
    return render_template("add_transaction.html", add=False, edit=True, info=transaction_info, categories=session["categories"])

# Edit transaction
@app.route("/edited_transaction", methods=["POST"])
def edited_transaction():
    if session.get("flash"):
        flash(session["flash"])
        del session["flash"]
        return redirect("/transactions")
    
    # Get inputs
    amount = float(request.form.get("amount"))
    date_transacted = request.form.get("date")
    category = request.form.get("category")
    type = request.form.get("type")
    print(type)
    category = 14 if (category == None) or (type == "income") else category
    amount *= -1 if type == "expense" else 1
    id = request.form.get("id")

    # Find updated difference 
    difference = amount - list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]["amount"]
    
    # Add transaction to database table 'transactions'
    data = {
        "amount": amount,
        "abs_amount": abs(amount),
        "date_transacted": date_transacted,
        "category_id": category
    }
    db.table("transactions").update(data).eq("transaction_id", id).execute()
    
    # Update user's current balance
    current_balance = get_user_balance(db, session.get("user_id"))
    db.table("balances").update({"current_balance": current_balance+difference}).eq("user_id", session.get("user_id")).execute()
    
    return redirect("/transactions")

# Delete a transaction
@app.route("/delete_transaction", methods=["POST"])
def delete_transaction():
    # Get id and amount of transaction to be deleted
    id = request.form.get("id")
    amount = list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]["amount"]
    
    # Delete transaction from database
    db.table("transactions").update({"deleted": True}).eq("transaction_id", id).execute()
    
    # Update user's balance
    current_balance = get_user_balance(db, session.get("user_id"))
    db.table("balances").update({"current_balance": current_balance-amount}).eq("user_id", session.get("user_id")).execute()
    
    # Return to transactions page
    return redirect("/transactions")

# Restore a deleted transaction
@app.route("/restore_transaction", methods=["POST"])
def restore_transaction():
    # Get id and amount of transaction to be deleted
    id = request.form.get("id")
    amount = list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]["amount"]
    
    # Restore transaction from database
    db.table("transactions").update({"deleted": False}).eq("transaction_id", id).execute()
    
    # Update user's balance
    current_balance = get_user_balance(db, session.get("user_id"))
    db.table("balances").update({"current_balance": current_balance+amount}).eq("user_id", session.get("user_id")).execute()
    
    # Return to transactions page
    return redirect("/transactions")
        
# Update session from script.js
@app.route('/update_session', methods=['POST'])
def update_session():
    data = request.get_json()
    session[data.get("key")] = data.get("value")
    return 'Session updated'

# Get user's data for chart analysis
@app.route("/get_chart_data")
def get_transac_analysis_data():
    today = date.today()
    week = True if request.args.get("periods", "weeks") == "weeks" else False
    if week:
        label = "week "
        days_difference = (today.weekday() + 1) % 7
        begin = today - timedelta(days=days_difference)
        end = begin + timedelta(days=6)
        date_ranges = [{
            "begin": begin,
            "end": end
        }]
        for i in range(5):
            begin -= timedelta(days=7)
            end = begin + timedelta(days=6)
            date_ranges.insert(0, {
                "begin": begin,
                "end": end
            })
        
        for i in date_ranges:
            print(i)
    else:
        label = "month "
        month = today.month
        year = today.year
        
        begin = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])

        date_ranges = [{
            "begin": begin,
            "end": end
        }]
        for i in range(5):
            month -= 1
            if month < 1:
                month = 12 - month
                year -= 1
            print(month)
            begin = date(year, month, 1)
            end = date(year, month, monthrange(year, month)[1])
            date_ranges.insert(0, {
                "begin": begin,
                "end": end
            })
    
    labels = [label + str(i) for i in range(len(date_ranges))] 
    values = []      
    for r in date_ranges:
        transac_type = request.args.get("type", "income")
        print(transac_type,week)
        if transac_type == "income":
            response = db.table("transactions").select("abs_amount").eq("user_id", session.get("user_id")).eq("deleted", False).gt("amount", 0).gte("date_transacted", r.get("begin")).lte("date_transacted", r.get("end")).execute()
        else:
            response = db.table("transactions").select("abs_amount").eq("user_id", session.get("user_id")).eq("deleted", False).lt("amount", 0).gte("date_transacted", r.get("begin")).lte("date_transacted", r.get("end")).execute()
        data = response.data
        data = [i["abs_amount"] for i in data]
        values.append(sum(data))
        
    return jsonify({"labels":labels, "values": values})

# Get user's balance over the month for charts
@app.route("/balance")
def get_balance():
    today = date.today()
    labels = []
    values = []
    current_balance = db.table("balances").select("current_balance").eq("user_id", session.get("user_id")).execute().data[0]["current_balance"]
    print(current_balance)
    for i in range(today.day, 0, -1):
        current_date = date(today.year, today.month, i)
        today_amount = db.table("transactions").select("amount").eq("user_id", session.get("user_id")).eq("date_transacted", current_date).eq("deleted", False).execute().data
        if len(today_amount) == 0:
            today_amount = 0
        else:
            today_amount = [j["amount"] for j in today_amount]
            today_amount = sum(today_amount)
        current_balance -= today_amount
        labels.insert(0, i)
        values.insert(0, current_balance)
    
    # for i in range(today.day+1, monthrange(today.year, today.month)[1] + 1):
    #     labels.append(i)
    #     values.append(None)
    
    return jsonify({"labels":labels, "values": values})

# Get the user's categories
@app.route("/categories")
def get_categories():
    today = date.today()
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month, monthrange(today.year, today.month)[1])
    
    categories = db.table("transactions").select("categories(category)", "abs_amount").eq("user_id", session.get("user_id")).eq("deleted", False).lt("amount", 0).gte("date_transacted", start).lte("date_transacted", end).execute().data
    print(categories)
    values = {}
    
    sort_type = request.args.get("type", "spending")
    for i in categories:
        count = values.get(str(i["categories"]["category"]), 0)
        if sort_type == "frequency":
            count += 1
        elif sort_type == "spending":
            count += i["abs_amount"]
        values[str(i["categories"]["category"])] = count
    
    return jsonify({"labels": list(values.keys()), "values": list(values.values())})