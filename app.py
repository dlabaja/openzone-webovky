from flask import Flask, render_template, session, request, redirect, url_for, abort
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, widgets , EmailField, PasswordField, validators
from wtforms.validators import InputRequired, Length, EqualTo, Email, DataRequired
from db import *
import email_validator, config

app = Flask(__name__)
app.secret_key = config.secret

@app.route("/")
def index():
    votes = getVotes()
    return render_template("index.html.j2", labels = votes[0], values = votes[1], count = len(votes[0]))

@app.route("/edit", methods=['GET','POST'])
def edit():
    if(session.get("admin") == True):
        form = AddToForm()
        if form.validate_on_submit():
            AddChoice(form.choice.data)
        return render_template("edit.html.j2", names = getNameCollection(), votes = getVoteCollection(), form = form)
    abort(404)

@app.route("/dropdb")
def dropdb():
    if(session.get("admin") == True):
        DropVotes()
        return redirect("/edit")
    abort(404)

@app.route("/dropdb", methods=["POST"])
def _dropdb():
    if(session.get("admin") == True):
        return redirect("/edit")
    abort(404)

@app.route("/form", methods=['GET', 'POST'])
def form():
    Form.choice = RadioField("Vyberte možnost", choices=getChoices(), validators=[InputRequired("Musíte zadat možnost")])
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
    try:
        session.pop("admin")
    except:
        print("rip")
    return redirect(url_for("index")) 



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



class Form(FlaskForm):
    choice = RadioField("Vyberte možnost", choices=getChoices(), validators=[InputRequired("Musíte zadat možnost")])

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


    


    
    


