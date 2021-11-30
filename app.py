from flask import Flask, render_template, session, request
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, widgets , EmailField, PasswordField
from wtforms.validators import InputRequired, Length
import config

app = Flask(__name__)
app.secret_key = config.secret

client = MongoClient(config.connection_string)
db = client["openzone"]
coll = db["form"]

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

class Form(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    choice = RadioField("Vyberte možnost", choices=[("Javascript" ,"Javascript"), ("C lang", "C lang"), ("Python", "Python")], validators=[InputRequired("Musíte zadat možnost")])

class RegisterForm(FlaskForm):
    name = StringField("Jméno", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat jméno")])
    email = EmailField("Email", widget = widgets.Input(input_type = "text"), validators=[InputRequired("Musíte zadat email")])
    password = PasswordField("Heslo", validators=[InputRequired("Musíte zadat heslo")])
    #passwordAgain = PasswordField("Znovu heslo", validators=[InputRequired("Musíte zadat heslo"), EqualTo(password)])

class LoginForm(FlaskForm):
    name = "a"

def hasVoted():
    for item in session:
        if item == "voted":
            return True
    return False

def vote(choice, name):
    global coll
    _coll = coll

    from bson.objectid import ObjectId
    query = _coll.find_one({"_id": ObjectId("619d38f7b9673a94534feb35")})
    newvalues = { "$set": { choice:  int(dict(query).get(choice)) + 1}, "$addToSet":{"names":f"{name}, {choice}"} }
    _coll.update_one(dict(query), newvalues)

def getVotes():
    global coll
    _coll = coll

    labels = []
    values = []

    from bson.objectid import ObjectId
    for item in dict(_coll.find_one({"_id": ObjectId("619d38f7b9673a94534feb35")})):
        if item != "_id" and item != "names":
            labels.append(item)
    
    for item in dict(_coll.find_one({"_id": ObjectId("619d38f7b9673a94534feb35")})).values():
        if item != ObjectId("619d38f7b9673a94534feb35") and type(item) != list:
            values.append(item)

    return labels, values


    
    


