from flask import Flask, request, redirect, render_template, url_for
import __init__

# initialize Flask to variable app 
# __name__ is the name of the module being used 
# this is so flask knows where to find our files 
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods= ['GET', 'POST'])
def login(): 
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = "Invalid username or password. Please try again."
        else:
            return redirect(url_for('home'))
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)