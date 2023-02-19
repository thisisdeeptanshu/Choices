from flask import Flask, redirect, url_for, render_template, request, session
import pyrebase
import json
import firebase_admin
from firebase_admin import auth as _auth, db

# Setting up firebase
cred_obj = firebase_admin.credentials.Certificate('json.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL': ""
})

# Setting up firebase
config = {
  "apiKey": " ",
  "authDomain": "",
  "databaseURL": "",
  "storageBucket": "",
  "serviceAccount": ""
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__)

# Change this
app.secret_key = "JSAHDKQDS!@#!@#e98DS12!|}k|QJ12H89E>SAD24G4EF<1WW8WU9}:WQED12388123123~!~)@>kDS"

@app.route("/")
def home():
    if "details" in session:
        if "username" not in session["details"]:
            loggedIn = False
        else:
            loggedIn = True
    else:
        loggedIn = False
    get = db.reference("/").get()
    try:
        total = [(i, get[i]) for i in get]
    except:
        total = []
    return render_template("index.html", loggedIn=loggedIn, all=total)

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["details"] = {"username": user["displayName"], "email": email}
            return redirect(url_for("home"))
        except Exception as e:
            try:
                user = _auth.create_user(
                    email = email,
                    display_name = name,
                    password = password
                )
                session["details"] = {"username": name, "email": email}
                return redirect(url_for("home"))
            except Exception as e:
                return render_template("login.html", alert=e)
    return render_template("login.html", alert="")

@app.route("/create/", methods=["GET", "POST"])
def create():
    if "details" in session:
        if "username" not in session["details"]:
            session.clear()
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))
    if request.method == "POST":
        options = []
        votes = {}
        name = request.form["name"]
        for i in request.form:
            if request.form[i] != name:
                options.append(request.form[i])
                votes[request.form[i]] = 0
        ref = db.reference("/").push()
        ref.set({
            "name": name,
            "options": options,
            "by": session["details"]["username"],
            "votes": votes
        })
        return redirect(url_for("choice", url=ref._pathurl[1::]))
    return render_template("create.html", loggedIn=session["details"])

@app.route("/choice/<url>/", methods=["GET", "POST"])
def choice(url):
    if "details" in session:
        if "username" not in session["details"]:
            loggedIn = False
        else:
            loggedIn = True
    else:
        loggedIn = False
    if "details" not in session:
        session["details"] = {"email": request.remote_addr}
    if request.method == "POST":
        try:
            choice = request.form["selected"]
            ref = db.reference(url)
            data = db.reference(url).get()
            if "cast-by" in data:
                castby = data["cast-by"]
                castby.append(session["details"]["email"])
            else:
                castby = [session["details"]["email"]]
            data["votes"][choice] += 1
            ref.child("votes").update({choice: data["votes"][choice]})
            ref.update({"cast-by": castby})
        except:
            pass
    try:
        data = db.reference(url).get()
    except:
        return redirect(url_for("home"))
    contains = False
    if "cast-by" in data:
        if session["details"]["email"] in data["cast-by"]:
            contains = True
    return render_template("choice.html", data=data, contains=contains, loggedIn=loggedIn)

@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/profile/")
def profile():
    if "details" in session:
        if "username" not in session["details"]:
            session.clear()
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))
    return render_template("profile.html", loggedIn=session["details"], username=session["details"]["username"], email=session["details"]["email"])

if __name__ == "__main__":
	app.run(debug=True)