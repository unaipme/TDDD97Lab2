from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def login_page():
    return render_template("client.html", login=False)

if __name__ == '__main__':
    app.debug = True
    app.run()


def sign_in(email, password):
    pass


def sign_up(email, password, firstname, familyname, gender, city, country):
    pass


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
