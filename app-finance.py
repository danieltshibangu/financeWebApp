from flask import Flask, request, redirect, render_template, url_for

# initialize Flask to variable app 
# __name__ is the name of the module being used 
# this is so flask knows where to find our files 
app = Flask(__name__)

# TODO: create a way to get financial data 

import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options  

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=chrome_options)

# TODO: extract financial data

# TODO: use seaborn or plotly to create graphs 

@app.route('/')
@app.route('/login')
def home(): 
    #instead of 'return "some title"', we can render the entire page we want 
    # by givng argument posts, you can use this variable in templates for home 
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)