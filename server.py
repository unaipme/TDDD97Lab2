from flask import Flask, render_template, request, redirect
from database_helper import DatabaseHelper, ERROR_MSG, ErrNo, printc
from random import random

HALFNHOUR = "datetime('now', '+30 minute')"
app = Flask(__name__)
with app.app_context():
    dbHelper = DatabaseHelper("twidder.db")


def gentoken():
    token = ""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for i in range(0, len(letters)):
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
    response = dbHelper.select("U.Username, U.FirstName, U.FamilyName, U.City, U.Country, G.Name", "Users U",
                               "INNER JOIN Tokens T ON T.UserID = U.UserID INNER JOIN Genders G ON G.GenderID = U.Gender")
    if not response["success"]:
        return {"success": False, "message": response["message"]}
    if not response["data"][0]:
        return {"success": False, "message": "You are not signed in."}
    return {"success": True, "message": "User data retrieved.", "data": response["data"][0]}



def get_user_data_by_email(token, email):
    pass


def get_user_messages_by_email(token, email):
    pass


def post_message(token, message, email):
    pass


@app.route("/")
def main_func():
    dbHelper.clean_expired_tokens()
    return render_template("client.html", login=False)


@app.route("/signup", methods=['POST'])
def signup_display():
    input = request.form
    response = sign_up(input["Email"], input["Password"], input["FirstName"], input["FamilyName"],
                       input["Gender"], input["City"], input["Country"])
    return render_template("client.html", login=False, success=response["success"], msg=response["message"])


@app.route("/login", methods=['POST'])
def logging():
    input = request.form
    response = sign_in(input["Email"], input["Password"])
    if not response["success"]:
        return render_template("client.html", login=False, success=False, msg=response["message"])
    return redirect("/account/"+response["data"])


@app.route("/account/<token>", methods=['POST', 'GET'])
def account(token=None):
    return render_template("client.html", login=True, account=True, token=token)


@app.route("/account/<token>/ps", methods=['POST', 'GET'])
def pwchange(token=None):
    input = request.form
    response = change_password(token, input["CurrentPassword"], input["NewPassword"])
    if not response["success"]:
        return render_template("client.html", login=True, account=True, token=token, success=False,
                               msg=response["message"])
    return render_template("client.html", login=True, account=True, token=token, success=True, msg=response["message"])


@app.route("/home/<token>", methods=['POST', 'GET'])
def home(token=None):
    response = get_user_data_by_token(token)
    if not response["success"]:
        return render_template("client.html", login=True, home=True, token=token, success=False, msg=response["message"])
    user = response["data"]
    return render_template("client.html", login=True, home=True, token=token, email=user[0], firstname=user[1],
                           familyname=user[2], city=user[3], country=user[4], gender=user[5])


@app.route("/browse/<token>", methods=['POST', 'GET'])
def browse(token=None):
    return render_template("client.html", login=True, browse=True, token=token)


@app.route("/signout/<token>", methods=['POST', 'GET'])
def signingout(token=None):
    response = sign_out(token)
    if response["success"]:
        return redirect("/")
    return render_template("client.html", login=True, account=True, token=token, success=False, msg=response["message"])


if __name__ == '__main__':
    app.debug = True
    app.run()
