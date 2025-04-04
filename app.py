from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages
from flask_session import Session
from supabase import create_client, Client
from helpers import *
from werkzeug.security import generate_password_hash


app = Flask(__name__)
# flask run --debug

app.jinja_env.filters["usd"] = format_usd

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
    
    # Go to user's dashboard
    return render_template("dashboard.html", username=user["username"], date_joined=user["date_joined"])

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
            user_id = list(db.table("users").select("id").eq("username", username).execute())[0][1][0]['id']
            session['user_id'] = user_id
            
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
            user_id = list(db.table("users").select("id").eq("username", username).execute())[0][1][0]['id']
            session['user_id'] = user_id
            
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