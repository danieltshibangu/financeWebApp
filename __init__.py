from flask import Flask
import os, chromedriver_binary  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options           # automatically adds chrome binary path

# TODO: create a way to get financial data 
def access_acct():
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome('/Users/danieltshibangu/Desktop/drivers/chromedriver', options=chrome_options)

    # accessing the login page of first website
    driver.get("https://secure03b.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index")
    driver.find_element_by_class( )

# TODO: extract financial data

# TODO: use seaborn or plotly to create graphs 
