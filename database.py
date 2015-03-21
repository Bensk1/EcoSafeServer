from flask import g
import sqlite3
import os

DATABASE = 'data/database.db'

def getDb():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def queryDb(query, args=(), one=False):
    cur = getDb().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def initDb(app):
    if not os.path.exists("data"):
        os.makedirs("data")
    db = getDb()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    return "init successful"

def dropDb():
    queryDb('drop table user')
    return "drop successful"

def closeConnection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
