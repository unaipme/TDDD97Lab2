from flask import Flask, render_template, request, redirect
from database_helper import DatabaseHelper, ErrNo
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
        return response
    userID = response["data"][0][0]
    response = dbHelper.insert("Tokens", ("Token", "UserID", "ExpireDate"), (gentoken(), userID, HALFNHOUR))
    return response


def sign_up(email, password, firstname, familyname, gender, city, country):
    response = dbHelper.insert("Users", ("Username", "Password", "FirstName", "FamilyName", "Gender", "City", "Country")
                , (str(email), str(password), str(firstname), str(familyname), str(gender), str(city), str(country)))
    if response["errno"] == ErrNo.EX_DATA_ERR:
        response["message"] = "The e-mail address is already registered"
    return response


def sign_out(token):
    pass


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
        return redirect("/account")


@app.route("/account", methods=['POST', 'GET'])
def account():
    return render_template("client.html", login=True, account=True)


@app.route("/home", methods=['POST', 'GET'])
def home():
    return render_template("client.html", login=True, home=True)


@app.route("/browse", methods=['POST', 'GET'])
def browse():
    return render_template("client.html", login=True, browse=True)


if __name__ == '__main__':
    app.debug = True
    app.run()
