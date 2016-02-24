from flask import Flask, render_template, request, redirect
from database_helper import DatabaseHelper, ERROR_MSG, ErrNo
from random import random


HALFNHOUR = "datetime('now', '+30 minute')"
app = Flask(__name__)
with app.app_context():
    dbHelper = DatabaseHelper("twidder.db")


def gentoken():
    token = ""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for i in range(len(letters)):
        token += letters[int(random() * len(letters))]
    return token


def checkpassword(email, password):
    response = dbHelper.select("UserID, Password", "Users", "WHERE Username='"+email+"'")
    if not response["success"]:
        # This is caused by an error with the query or db. It's not a login fail.
        return {"success": False, "message": response["message"]}
    if response["data"][0][1] != password:
        return {"success": False, "message": ERROR_MSG[ErrNo.WRONG_PSWD]}
    return {"success": True, "user": response["data"][0]}


def convert_to_wall(msgs):
    response = ""
    for i in range(0, len(msgs)):
        response += render_template("message.html", author=msgs[i][0], txt=msgs[i][1])
    return response


def sign_in(email, password):
    response = checkpassword(str(email), str(password))
    if not response["success"]:
        return response
    token = gentoken()
    response = dbHelper.insert("Tokens", ("Token", "UserID", "ExpireDate"), (token, response["user"][0], HALFNHOUR))
    if response["success"]:
        return {"success": True, "message": "Successfully signed in.", "data": token}
    # This is caused by an error with the query or db. It MAY NOT BE a login fail.
    return {"success": False, "message": response["message"]}


def sign_up(email, password, firstname, familyname, gender, city, country):
    response = dbHelper.insert("Users", ("Username", "Password", "FirstName", "FamilyName", "Gender", "City", "Country")
                , (str(email), str(password), str(firstname), str(familyname), str(gender), str(city), str(country)))
    if response["success"]:
        return {"success": True, "message": "Successfully created a new user."}
    if response["errno"] == ErrNo.EX_DATA_ERR:
        return {"success": False, "message": "User already exists."}
    return {"success": False, "message": response["message"]}


def sign_out(token):
    response = dbHelper.delete("Tokens", "Token='"+token+"'")
    if response["success"]:
        return {"success": True, "message": "Successfully signed out."}
    return {"success": False, "message": response["message"]}


def change_password(token, old_password, new_password):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return response
    user_id = response["data"][0]
    username = response["data"][1]
    response = checkpassword(username, str(old_password))
    if not response["success"]:
        return response
    response = dbHelper.update("Users", ("Password",), (str(new_password),), "UserID=" + str(user_id))
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    return {"success": True, "message": "Password changed"}


def get_user_data_by_token(token):
    response = dbHelper.select("U.Username, U.FirstName, U.FamilyName, U.City, U.Country, G.Name, U.UserID", "Users U",
                               "INNER JOIN Tokens T ON T.UserID=U.UserID INNER JOIN Genders G ON G.GenderID=U.Gender " +
                               "WHERE T.Token='" + token + "'")
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    if not response["data"][0]:
        return {"success": False, "message": "You are not signed in."}
    return {"success": True, "message": "User data retrieved.", "data": response["data"][0]}


def get_user_data_by_email(token, email):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return response
    response = dbHelper.select("U.Username, U.FirstName, U.FamilyName, U.City, U.Country, G.Name, U.UserID",
                               "Users U", "INNER JOIN Genders G ON G.GenderID=U.Gender WHERE U.Username='" + email + "'")
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    if response == []:
        return {"success": False, "message": "No such user exists."}
    return {"success": True, "message": "User data retrieved.", "data": response["data"][0]}


def get_user_messages_by_email(token, email):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return response
    response = get_user_data_by_email(token, email)
    if not response["success"]:
        return response
    userID = response["data"][6]
    response = dbHelper.select("S.Username, M.MsgText", "Messages M", "INNER JOIN Users S ON S.UserID=M.SenderID " +
                               "WHERE M.ReceiverID=" + str(userID) +" ORDER BY M.MessageID DESC")
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    return {"success": True, "message": "User data retrieved.", "data": response["data"]}


def post_message(token, message, email=None):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return response
    senderID = response["data"][6]
    if not email is None:
        response = get_user_data_by_email(token, email)
        if not response["success"]:
            return response
        receiverID = response["data"][6]
    else:
        # if email is none it means that the sender and the receiver are the same user
        response = get_user_data_by_token(token)
        if not response["success"]:
            return response
        receiverID = response["data"][6]
    response = dbHelper.insert("Messages", "(SenderID, ReceiverID, MsgText)", (senderID, receiverID, message))
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    return {"success": True, "message": "Message posted."}


@app.route("/")
def main_func():
    dbHelper.clean_expired_tokens()
    return render_template("client.html", login=False)


@app.route("/signup", methods=['POST'])
def signup_display():
    inputs = request.form
    response = sign_up(inputs["Email"], inputs["Password"], inputs["FirstName"], inputs["FamilyName"],
                       inputs["Gender"], inputs["City"], inputs["Country"])
    return render_template("client.html", login=False, success=response["success"], msg=response["message"])


@app.route("/login", methods=['POST'])
def logging():
    inputs = request.form
    response = sign_in(inputs["Email"], inputs["Password"])
    if not response["success"]:
        return render_template("client.html", login=False, success=False, msg=response["message"])
    return redirect("/account/"+response["data"])


@app.route("/account/<token>", methods=['POST', 'GET'])
def account(token=None):
    return render_template("client.html", login=True, account=True, token=token)


@app.route("/account/<token>/ps", methods=['POST', 'GET'])
def pwchange(token=None):
    inputs = request.form
    response = change_password(token, inputs["CurrentPassword"], inputs["NewPassword"])
    if not response["success"]:
        return render_template("client.html", login=True, account=True, token=token, success=False,
                               msg=response["message"])
    return render_template("client.html", login=True, account=True, token=token, success=True, msg=response["message"])


@app.route("/home/<token>", methods=['POST', 'GET'])
def home(token=None, success=None, msg=None):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return render_template("client.html", login=True, home=True, token=token, success=False, msg=response["message"])
    user = response["data"]
    response = get_user_messages_by_email(token, user[0])
    if not response["success"]:
        return render_template("client.html", login=True, home=True, token=token, success=False, msg=response["message"])
    wallmsg = convert_to_wall(response["data"])
    return render_template("client.html", login=True, home=True, token=token, email=user[0], firstname=user[1],
                           familyname=user[2], city=user[3], country=user[4], gender=user[5], wallmsg=wallmsg,
                           success=success, msg=msg)


@app.route("/browse/<token>", methods=['POST', 'GET'])
def browse(token=None):
    return render_template("client.html", login=True, browse=True, token=token)


@app.route("/browse/<token>/s", methods=["POST", "GET"])
def browse_user_info(token=None, email=None):
    if email is None:
        email = request.form["SearchTerm"]
    response = get_user_data_by_email(token, email)
    if not response["success"]:
        return render_template("client.html", login=True, browse=True, token=token, success=False, msg=response["message"])
    user = response["data"]
    response = get_user_messages_by_email(token, user[0])
    if not response["success"]:
        return render_template("client.html", login=True, browse=True, token=token, success=False, msg=response["message"])
    wallmsg = convert_to_wall(response["data"])
    return render_template("client.html", login=True, browse=True, token=token, email=user[0], firstname=user[1],
                           familyname=user[2], city=user[3], country=user[4], gender=user[5], wallmsg=wallmsg)


@app.route("/browse/<token>/p", methods=["POST", "GET"])
def browse_post(token=None):
    inputs = request.form
    response = post_message(token, str(inputs["MsgText"]), inputs["Receiver"])
    if not response["success"]:
        return render_template("client.html", login=True, browse=True, token=token, success=False, msg=response["message"])
    return browse_user_info(token, str(inputs["Receiver"]))


@app.route("/signout/<token>", methods=['POST', 'GET'])
def signingout(token=None):
    response = sign_out(token)
    if response["success"]:
        return redirect("/")
    return render_template("client.html", login=True, account=True, token=token, success=False, msg=response["message"])


@app.route("/send/<token>/own", methods=['POST', 'GET'])
def post_on_own_wall(token=None):
    msg = str(request.form["MsgText"])
    response = post_message(token, msg)
    if not response["success"]:
        return home(token=token, success=False, msg=response["message"])
    return redirect("/home/"+token)

if __name__ == '__main__':
    app.debug = True
    app.run()
