from flask import Flask, render_template, session, request, redirect, url_for, abort
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, widgets , EmailField, PasswordField, validators
from wtforms.validators import InputRequired, Length, EqualTo, Email, DataRequired
from bson.objectid import ObjectId
import email_validator
import config, os, hashlib, random

app = Flask(__name__)
app.secret_key = config.secret

client = MongoClient(config.connection_string)
db = client["openzone"]
_coll = db["form"]
_usercoll = db["users"]
_votedcoll = db["voted"]

@app.route("/")
def index():
    votes = getVotes()
    return render_template("index.html.j2", labels = votes[0], values = votes[1], colors = hexGenerator(len(votes[0])))

@app.route("/edit", methods=['GET','POST'])
def edit():
    if(session.get("admin") == True):
        form = AddToForm()
        if form.validate_on_submit():
            global _coll
            coll = _coll
            query = coll.find_one({"_id": ObjectId(config.form_id)})
            newvalue = {"$set":{f"votes.{form.choice.data}":0}}
            coll.update_one(dict(query), newvalue)

        return render_template("edit.html.j2", names = getNameCollection(), votes = getVoteCollection(), form = form)
    abort(404)

@app.route("/dropdb")
def dropdb():
    if(session.get("admin") == True):
        RemoveVotes()
        return redirect("/edit")
    abort(404)

@app.route("/dropdb", methods=["POST"])
def _dropdb():
    if(session.get("admin") == True):
        return redirect("/edit")
    abort(404)

@app.route("/form", methods=['GET', 'POST'])
def form():
    form = Form()    
    if session.get("user", False):
        if not hasVoted():
            if form.validate_on_submit():
                choice = form.choice.data
                vote(choice)

                return render_template("form_completed.html.j2", form = form)
            return render_template("form.html.j2", form = form)
        return render_template("form_completed.html.j2", form = form)
    return render_template("acces_denied.html.j2", form = form)
    
@app.errorhandler(404)
def page_not_found(e):   
    return render_template('404.html.j2')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        data = getLoginInfo(form.name.data)
        if not data:
            return render_template('login.html.j2', form = form)
        if comparePasswords(data[2], data[3], form.password.data):
            session["user"] = data[0]
            session["admin"] = data[4]
            return redirect(url_for("index")) 
    return render_template('login.html.j2', form = form)

@app.route("/logout")
def logout():
    session.pop("user")
    session.pop("admin")
    return redirect(url_for("index")) 

def getLoginInfo(username):
    global _coll
    coll = _usercoll
    query = coll.find_one({"name": username})   
    
    if query == None:
        return False
    query = dict(query)
    print("aaa")
    return query.get("name"), query.get("email"), query.get("password"), query.get("salt"), query.get("admin")

@app.route("/register", methods=['GET','POST'])
def register_post():
     form = RegisterForm() 
     name = form.name.data
     email = form.email.data
     password = form.password.data
     print(form.errors.items())
     if form.validate_on_submit():
        setRegister(name, email, password)
        session["user"] = name
        return render_template("registered.html.j2", form = form)
     return render_template("register.html.j2", form = form)

def setRegister(name, email, password):
    global _coll
    coll = _usercoll
    hashedpsw = hash(password)
    bson = {"name": name,
            "email":email,
            "password": hashedpsw[1],
            "salt": hashedpsw[0],
            "admin":False}
    query = coll.insert_one(bson)

def hash(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt, 100000)
    return salt, key

def comparePasswords(dbpassword, salt, currentpassword):
    psw = hashlib.pbkdf2_hmac("sha256", str(currentpassword).encode("utf-8"), salt, 100000)
    if dbpassword == psw:
        return True
    return False

class Form(FlaskForm):
    choice = RadioField("Vyberte možnost", choices=config.getChoices(), validators=[InputRequired("Musíte zadat možnost")])

class AddToForm(FlaskForm):
    choice = StringField("Volba", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat volbu")])

class RegisterForm(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    email = EmailField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])
    passwordAgain = PasswordField("Znovu heslo", validators=[InputRequired("Musíte zadat heslo"), EqualTo("password", "Hesla se neshodují")])

class LoginForm(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])

def hasVoted():
    global _votedcoll
    votedcoll = _votedcoll
    query = votedcoll.find_one({"user": session.get("user")})
    if query == None:
        return False
    return True

def vote(choice):
    global _coll
    coll = _coll
    global _votedcoll
    votedcoll = _votedcoll
    print(choice)
    query = coll.find_one({"_id": ObjectId(config.form_id)})
    coll.update_one(dict(query), { "$set": { f"votes.{choice}":  int(dict(query).get("votes").get(choice)) + 1}})

    query_name = coll.find_one({"_id": ObjectId(config.names_id)})
    coll.update_one(dict(query_name), {"$addToSet":{"names":f"{session.get('user')}, {choice}"}})

    votedcoll.insert_one({"user":session.get("user")})
    

def getVotes():
    global _coll
    coll = _coll
    query = dict(coll.find_one({"_id": ObjectId(config.form_id)}))
    labels = []
    values = []

    for item in query.get("votes"):
            labels.append(item)          
            values.append(query.get("votes").get(item))

    return labels, values

def getNameCollection():
    global _coll
    coll = _coll
    query = dict(coll.find_one({"_id": ObjectId(config.names_id)}, {"_id": 0 }))
    string = "<b>Již hlasovali:</b><br>"
    for _item in query.values():
        for item in _item:
            string =string+ f"{item}<br>"
    return string

def getVoteCollection():
    global _coll
    coll = _coll
    query = dict(coll.find_one({"_id": ObjectId(config.form_id)}, {"_id": 0 }))
    string = "<b>Možnosti ankety:</b><br>"
    for _item in query.values():
        for item in _item:
            string =string+ f"{item}<br>"
    return string

def hexGenerator(count):
    colors = []
    for x in range(count):
        r = lambda: random.randint(0,255)
        colors.append('#%02X%02X%02X' % (r(),r(),r()))
    return colors

def RemoveVotes():
    global _coll
    coll = _coll
    query = coll.find_one({"_id": ObjectId(config.form_id)},{"votes":1,"_id":0})
    print(query)
  
    bson = {"votes":{}}
    coll.replace_one(query, bson)
    


    
    


