import os
from flask import Flask, render_template, redirect, request
from supabase import create_client, Client
import helpers as h

app = Flask(__name__)
# flask run --debug

app.jinja_env.filters["usd"] = h.format_usd

# Database url: https://wdtglfihqmsivautmzns.supabase.co
# Database key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndkdGdsZmlocW1zaXZhdXRtem5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzNzA0NzEsImV4cCI6MjA0ODk0NjQ3MX0.yVeFrOB9kQYMZoWteougoU5bbvCUTvN4CtZbfZHZq1g

db_url = "https://wdtglfihqmsivautmzns.supabase.co"
db_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndkdGdsZmlocW1zaXZhdXRtem5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMzNzA0NzEsImV4cCI6MjA0ODk0NjQ3MX0.yVeFrOB9kQYMZoWteougoU5bbvCUTvN4CtZbfZHZq1g"
db: Client = create_client(db_url, db_key)

min_price = None
max_price = None
min_cal = None
max_cal = None

@app.route("/", methods=["POST", "GET"])
def index():
    sort = "id"
    desc = False
    if request.method == "POST":
        sort = request.form.get("sort_by")
        desc = request.form.get("reverse")
    menu = list(db.table("menu").select("*").order(sort, desc=desc).execute())[0][1]
    keys = list(menu[0].keys())
    keys.remove("id")
    return render_template("index.html", menu=menu, keys=keys, sort=sort, desc=desc)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        db.table("menu").insert({"name": request.form.get("food"), "price": request.form.get("price"), "calories": request.form.get("calories")}).execute()
        return redirect("/")
    return render_template("add.html")

@app.route("/del", methods=["POST"])
def delete():
    db.table("menu").delete().eq("id", request.form.get("id")).execute()
    return redirect("/")

@app.route("/edit", methods=["POST"])
def edit():
    item = {'id': request.form.get("id"), "name": request.form.get("food"), "price": request.form.get("price"), "calories": request.form.get("calories")}
    return render_template("edit.html", item=item)

@app.route("/edited", methods=["POST"])
def edited():
    id = request.form.get("id")
    name = request.form.get("food")
    price = request.form.get("price")
    calories = request.form.get("calories")
    db.table('menu').update({"name": name, "price": price, "calories": calories}).eq("id", id).execute()
    return redirect("/")