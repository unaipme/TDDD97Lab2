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
    for i in range(0, len(letters)):
        token += letters[int(random() * len(letters))]
    return token


def sign_in(email, password):
    response = dbHelper.select("UserID, Password", "Users", "WHERE Username='"+email+"'")
    if not response["success"]:
        # This is caused by an error with the query or db. It's not a login fail.
        return {"success": False, "message": response["message"]}
    if response["data"][0][1] != password:
        # response = createjson(("success", "message"), (False, ERROR_MSG[ErrNo.WRONG_PSWD]))
        return {"success": False, "message": ERROR_MSG[ErrNo.WRONG_PSWD]}
    token = gentoken()
    response = dbHelper.insert("Tokens", ("Token", "UserID", "ExpireDate"), (token, response["data"][0][0], HALFNHOUR))
    if response["success"]:
        return {"success": True, "message": "Successfully signed in.", "data": token}
    else:
        # This is caused by an error with the query or db. It's not a login fail.
        return {"success": False, "message": response["message"]}


def sign_up(email, password, firstname, familyname, gender, city, country):
    response = dbHelper.insert("Users", ("Username", "Password", "FirstName", "FamilyName", "Gender", "City", "Country")
                , (str(email), str(password), str(firstname), str(familyname), str(gender), str(city), str(country)))
    if response["success"]:
        return {"success": True, "message": "Successfully created a new user."}
    else:
        if response["errno"] == ErrNo.EX_DATA_ERR:
            return {"success": False, "message": "User already exists."}
        else:
            return {"success": False, "message": response["message"]}


def sign_out(token):
    response = dbHelper.delete("Tokens", "Token='"+token+"'")
    if response["success"]:
        return {"success": True, "message": "Successfully signed out."}
    else:
        return {"success": False, "message": response["message"]}


def change_password(token, old_password, new_password):
    pass


def get_user_data_by_token(token):
    pass


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
    else:
        return redirect("/account/"+response["data"])


@app.route("/account/<token>", methods=['POST', 'GET'])
def account(token=None):
    return render_template("client.html", login=True, account=True, token=token)


@app.route("/home/<token>", methods=['POST', 'GET'])
def home(token=None):
    return render_template("client.html", login=True, home=True, token=token)


@app.route("/browse/<token>", methods=['POST', 'GET'])
def browse(token=None):
    return render_template("client.html", login=True, browse=True, token=token)


@app.route("/signout/<token>", methods=['POST', 'GET'])
def signingout(token=None):
    response = sign_out(token)
    if response["success"]:
        return redirect("/")
    else:
        return render_template("client.html", login=True, account=True, token=token, success=False,
                               msg=response["message"])


if __name__ == '__main__':
    app.debug = True
    app.run()
