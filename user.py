import database
import json

def getUser(username):
    user = database.queryDb("select * from user where username=?;", (username,), True)

    return json.dumps({"username": user[0], "password":  user[1]})

def createUser(username, jsonPayload):
    password = jsonPayload['password']

    database.queryDbWithCommit("insert into user values (?, ?);", (username, password), True)

    return 'Create User %s : %s' % (username, password)

def deleteUser(username):
    return 'Delete User %s' % username

def listUser():
    users = []
    for user in database.queryDb('select * from user'):
        users.append({"username": user[0], "password":  user[1]})
    return json.dumps(users)
