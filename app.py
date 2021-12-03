from flask import Flask, render_template, session, request, redirect, url_for
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, widgets , EmailField, PasswordField, validators
from wtforms.validators import InputRequired, Length, EqualTo, Email, DataRequired
import email_validator
import config, os, hashlib

app = Flask(__name__)
app.secret_key = config.secret

client = MongoClient(config.connection_string)
db = client["openzone"]
_coll = db["form"]
_usercoll = db["users"]

#registrace vygeneruje klíč, uložení do cookie, přihlášení podle klíče
#login stránka přesměruje na domovskou. nahradí jméno v rohu

@app.route("/")
def index():
    votes = getVotes()
    return render_template("index.html.j2", labels = votes[0], values = votes[1])

@app.route("/form", methods=['GET', 'POST'])
def form():
    form = Form()    
    if not hasVoted:
        if form.validate_on_submit():
            name = form.name.data
            choice = form.choice.data
            vote(choice, name)

            session["voted"] = True
            return render_template("form_completed.html.j2", form = form)
        return render_template("form.html.j2", form = form)
    return render_template("form_completed.html.j2", form = form)
    
@app.errorhandler(404)
def page_not_found(e):   
    return render_template('404.html.j2')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm() 
    data = getLoginInfo()
    if session.get("user", False):
        
    return render_template('login.html.j2', form = form)

def getLoginInfo(username):
    global _coll
    coll = _usercoll
    query = dict(coll.find_one({"name": username}))

    return query.get("name"), query.get("email"), query.get("password")

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
    bson = {"name": name,
            "email":email,
            "password": hash(password)}
    query = coll.insert_one(bson)

def hash(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt, 100000)
    print(salt)
    print(key)
    storage = salt + key
    return storage


class Form(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    choice = RadioField("Vyberte možnost", choices=[("Javascript" ,"Javascript"), ("C lang", "C lang"), ("Python", "Python")], validators=[InputRequired("Musíte zadat možnost")])

class RegisterForm(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    email = EmailField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])
    passwordAgain = PasswordField("Znovu heslo", validators=[InputRequired("Musíte zadat heslo"), EqualTo("password", "Hesla se neshodují")])

class LoginForm(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])

def hasVoted():
    for item in session:
        if item == "voted":
            return True
    return False

def vote(choice, name):
    global _coll
    coll = _coll

    from bson.objectid import ObjectId
    query = coll.find_one({"_id": ObjectId("619d38f7b9673a94534feb35")})
    newvalues = { "$set": { choice:  int(dict(query).get(choice)) + 1}, "$addToSet":{"names":f"{name}, {choice}"} }
    coll.update_one(dict(query), newvalues)

def getVotes():
    global _coll
    coll = _coll
    query = dict(coll.find_one({"_id": ObjectId("619d38f7b9673a94534feb35")}))
    labels = []
    values = []

    from bson.objectid import ObjectId
    for item in query:
        if item != "_id" and item != "names":
            labels.append(item)
    
    for item in query:
        if item != ObjectId("619d38f7b9673a94534feb35") and type(item) != list:
            values.append(item)

    return labels, values

    
    


