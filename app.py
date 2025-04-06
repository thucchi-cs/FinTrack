from datetime import date
from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages
from flask_session import Session
from supabase import create_client, Client
from helpers import *
from werkzeug.security import generate_password_hash


app = Flask(__name__)
# flask run --debug

app.jinja_env.filters["usd"] = format_usd
app.jinja_env.filters["abs"] = absolute
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
    return render_template("index.html")

# User's dashboard
@app.route("/dashboard")
@login_required
def dashboard():   
    # Get user data
    user = list(db.table("users").select("*").eq("id", session.get("user_id")).execute())[0][1][0]
    balance = get_user_balance(db, session.get("user_id"))
    
    # Go to user's dashboard
    return render_template("dashboard.html", username=user["username"], date_joined=user["date_joined"], balance=balance)

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
        
        # Check for input validity
        if check_valid_registration(db, username, password, password2):
            # Hash password for security
            hashed_password = generate_password_hash(password)
        
            # Add user to database
            db.table("users").insert({"username": username, "password_hash": hashed_password}).execute()
            
            # Login user to the current session
            set_session_user(db, username)
            
            # Initialize user with $0
            db.table("balances").insert({"user_id": session["user_id"], "current_balance": 0}).execute()
            
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
    desc = not desc
    print(desc)
    user_transactions = list(db.table("transactions").select("*").eq("user_id", session['user_id']).order(sort_by, desc=desc).execute())[0][1]
    smth = list(db.table("transactions").select("*").eq("user_id", session['user_id']).gte("abs_amount", 30).lte("abs_amount", 60).execute())[0][1]
    print(smth)
    has_transactions = len(user_transactions) > 0

    return render_template("transactions.html", transactions=user_transactions, has_transactions=has_transactions, sort=sort_by, order_keys=orders.keys(), orders=orders, desc=not desc)

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
        amount *= -1 if type == "expense" else 1
        today = date.today()

        try:
            # Add transaction to database table 'transactions'
            data = {
                "user_id": session.get("user_id"), 
                "amount": amount, 
                "abs_amount": abs(amount),
                "date_transacted": date_transacted, 
                "date_added": str(today), 
                "category": category
            }
            db.table("transactions").insert(data).execute()
        except:
            flash("Invalid input!")
            return redirect("/add_transaction")
        
        # Update user's current balance
        current_balance = get_user_balance(db, session.get("user_id"))
        db.table("balances").update({"current_balance": current_balance+amount}).eq("user_id", session.get("user_id")).execute()
        
        return redirect("/transactions")
    
    return render_template("add_transaction.html", add=True, edit=False)

# Edit a transaction page
@app.route("/edit_transaction", methods=["POST"])
@login_required
def edit_transaction():
    transaction_info = list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]
    print(transaction_info)
    return render_template("add_transaction.html", add=False, edit=True, info=transaction_info)

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
    amount *= -1 if type == "expense" else 1
    id = request.form.get("id")

    # Find updated difference 
    difference = amount - list(db.table("transactions").select("*").eq("transaction_id", request.form.get("id")).execute())[0][1][0]["amount"]
    
    try:
        # Add transaction to database table 'transactions'
        data = {
            "amount": amount,
            "abs_amount": abs(amount),
            "date_transacted": date_transacted,
            "category": category
        }
        db.table("transactions").update(data).eq("transaction_id", id).execute()
    except:
        flash("Invalid input!")
        return redirect("/transactions")
    
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