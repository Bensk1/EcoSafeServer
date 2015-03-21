import database

def getUser(username):
    user = database.queryDb("select * from user where username=?;", (username,), True)

    return user[0] + ' : ' + user[1]

def createUser(username, jsonPayload):
    password = jsonPayload['password']

    database.queryDb("insert into user values (?, ?);", (username, password), True)

    return 'Create User %s : %s' % (username, password)

def deleteUser(username):
    return 'Delete User %s' % username
