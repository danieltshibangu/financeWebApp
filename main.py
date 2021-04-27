# it will read env variables from .env file 
from dotenv import load_dotenv
'''
    This will parse the .env file and load the variable as
    environment variables
'''
load_dotenv()

import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask, request, render_template, redirect, url_for, jsonify

# initialize Flask to variable app
# __name__ is the name of the module being used
# this is so flask knows where to find our files
app = Flask(__name__)

# get the new environment variables from the parsed env file thru os
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'development')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES')

# for the empty parsed environment variables that exist
def empty_or_none(field):
    value = os.getenv(field)
    if value == None or len(value) == 0:
        return None
    return value

# a redirect link using OAuth redirect flow that will allow me to connect 
# to the original site 
PLAID_REDIRECT_URI = empty_or_none('PLAID_REDIRECT_URI')

# create a generic client object that is initialized with a few credentials 
# by default 
client = plaid.Client( client_id=PLAID_CLIENT_ID,
                        secret=PLAID_SECRET,
                        environment=PLAID_ENV,
                        api_version='2019-05-29' )

access_token = None     # token used to access an item 
item_id = None          # the unique id for an item  


@app.route('/api/info', methods=['POST'])
def info():
  global access_token
  global item_id
  return jsonify({
    'item_id': item_id,
    'access_token': access_token,
    'products': PLAID_PRODUCTS
  })

'''
    This route allows the link token to be be created which will be used 
    to open the link for users on the frontend
'''
@app.route( '/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        # linkToken is just an undefined function and we implement create func on it 
        response = client.LinkToken.create(
            {
                'user': { 'client_user_id':'user-id', },
                'client_name':'some name',
                'country_codes': PLAID_COUNTRY_CODES,
                'language':'en',
                'redirect_uri':PLAID_REDIRECT_URI,
            }
        # A response was created with these fields applied to our current client
        # now to arrange it to create a json file 
        )

        # this makes a response object from the client's Link Token 
        pretty_print_response(response)
        return jsonify(response)            # turns response obj -> json file
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))     # formats an error -> json file

'''
    exchange token flow - exchange a Link public token 
    for an API access token. The link token just enables the link 
    between my server to plaid, but to access the credentials we need 
    to trade the link with an access token
'''
@app.route( '/api/set_access_token', methods=['POST'])
def get_access_token():
    global access_token
    global item_id
    public_token = request.form['public_token']     # form for entering creds?

    try:
        # this actually exchanges the token and returns an exchange obj?
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))

    # is exchange response a dictionary?
    pretty_print_response( exchange_response )
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    return jsonify(exchange_response)

'''
    getting ACH account numbers for each item.
    Instantly retrieve and verify bank account information
    to set up online payments via ACH and more.
'''
@app.route( '/api/auth', methods=['GET'])
def get_auth():
    try:
        auth_response = client.Auth.get(access_token)
    except plaid.errors.PlaidErrors as e:
        return jasonify( {'error':{'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(auth_response)
    return jsonify(auth_response)

'''
    getting the date for each transaction. 
    match access token to access the start and end date of transactions 
'''
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    #pulling transactions from the last 30 days 
    start_date = '{:%m-%d-%Y}'.format(datetime.datetime.now() + datetime.timedelta(-30))
    end_date = '{:%m-%d-%Y}'.format(datetime.datetime.now())
    try:
        transactions_response = client.Transactions.get( access_token, start_date, end_date )
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))
    pretty_print_response(transactions_response)
    return jsonify(transactions_response)

'''
    Get the user's identity for their item
'''
@app.route('/api/identity', methods=['GET'])
def get_identity():
    try:
        identity_response = client.Identity.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify( {'error': {'display_message': e.display_message, 'error_code':e.code, 'error_type':e.type } })
    pretty_print_response(identity_response)
    return jsonify({'error':'None', 'identity':identity_response['accounts']})


'''
    get real time balance data for each item's account
'''
@app.route('/api/balance', methods=['GET'])
def get_balance():
    try:
        balance_response = client.Balance.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error':{ 'display_message': e.display_message, 'error_code':e.code, 'error_type':e.type } })
    pretty_printing_response(balance_response)
    return jsonify(balance_response)

'''
    retrieves an item's actual account
'''
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        accounts_response = clients.Accounts.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({ 'error':{ 'display_message': e.display_message, 'error_code':e.code, 'error_type':e.type } })
    pretty_printing_response(accounts_response)
    return jsonify(accounts_response)

'''.DS_Store'''
@app.route('/api/assets', methods=['GET'])
def get_assets():
    try:
        asset_report_create_response = client.AssetReport.create([access_token], 10)
    except plaid.errors.PlaidError as e:
        return jsonify({ 'error':{ 'display_message': e.display_message, 'error_code':e.code, 'error_type':e.type } })
    pretty_printing_response(asset_report_create_response)

    asset_report_token = asset_report_create_response['asset_report_token'] 
    # a poll for completing the asset report 
    num_entries_remaining = 20
    asset_report_json = None
    while num_retries_remaining > 0:
        try:
            # get response for asset report
            asset_report_get_response = client.AssetReport.get(asset_report_token)
            # gets the report from dictionary and put into json report 
            asset_report_json = asset_report_get_response['report']
            break
        except plaid.errors.PlaidErrors as e:
            if e.code == 'PRODUCT_NOT_READY':
                num_entries_remaining -= 1
                time.sleep(1)
                continue
            return jsonify({ 'error':{ 'display_message': e.display_message, 'error_code':e.code, 'error_type':e.type } })

    # time out error message
    if asset_report_json == None:
        return jsonify({ 'error':{ 'display_message':'Timed out when polling for Asset Report', 'error_code':'', 'error_type':'' } })

    asset_report_pdf = None
    try:
        asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
    except plaid.errors.PlaidError as e:
        return jsonify({ 'error':{ 'display_message':'Timed out when polling for Asset Report', 'error_code':'', 'error_type':'' } })

    return jsonify({
        'error': None,
        'json': asset_report_json,
        'pdf': base64.b64encode(asset_report_pdf).decode('utf-8'),
    })

@app.route('/api/item', methods=['GET'])
def get_item():
    global access_token
    item_response = client.Item.get(access_token)
    institution_response = client.Institutions.get_by_id(item_reponse['item']['institution_id'])
    pretty_print_response(item_response)
    pretty_print_response(institution_response)

    return jsonify({'error': None, 'item': item_response['item'], 'institution': institution_response['institution']})


@app.route('/')
def home():
    return render_template('login.html')


def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

if __name__ == '__main__':
    app.run(port=os.getenv('PORT','8000'))


''''
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
'''