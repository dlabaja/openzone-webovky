from flask import Flask, render_template, session, request, redirect, url_for, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
import config, random, hashlib, os
client = MongoClient(config.connection_string)
db = client["openzone"]
_coll = db["form"]
_usercoll = db["users"]
_votedcoll = db["voted"]

def getLoginInfo(username):
    global _coll
    coll = _usercoll
    query = coll.find_one({"name": username})   
    
    if query == None:
        return False
    query = dict(query)
    print("aaa")
    return query.get("name"), query.get("email"), query.get("password"), query.get("salt"), query.get("admin")

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

def getChoices():  
    global _coll
    coll = _coll

    query = dict(_coll.find_one({"_id": ObjectId(config.form_id)}))
    choices = []
    for item in query.get("votes"):
        choices.append(item)
    return choices