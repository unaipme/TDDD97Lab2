from flask import Flask, render_template, request, request
from database_helper import DatabaseHelper, ErrNo

app = Flask(__name__)
with app.app_context():
    dbHelper = DatabaseHelper("twidder.db")


def sign_in(email, password):
    pass


def sign_up(email, password, firstname, familyname, gender, city, country):
    response = dbHelper.insert("Users", ("Username", "Password", "FirstName", "FamilyName", "Gender", "City", "Country"),
                (str(email), str(password), str(firstname), str(familyname), str(gender), str(city), str(country)))
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
    return render_template("client.html", login=False)


@app.route("/signup", methods=['POST'])
def signing_up():
    input = request.form
    response = sign_up(input["Email"], input["Password"], input["FirstName"], input["FamilyName"], input["Gender"], input["City"], input["Country"])
    return render_template("client.html", login=False, success=response["success"], error=not response["success"], msg=response["message"])

if __name__ == '__main__':
    app.debug = True
    app.run()
