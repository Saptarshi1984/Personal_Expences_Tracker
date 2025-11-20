from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/SignIn')
def signin():
    return render_template("signin.html")

@app.route('/SignUp')
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)