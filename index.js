require('dotenv').config();

const express = require('express');
const app = express();

const bodyParser = require('body-parser');
app.use(bodyParser.json());

const PORT = process.env.PORT || 3000;

const path = require('path');
const util = require('util');

// require client ID
const plaid = require('plaid');

const plaidClient = new plaid.Client({
    clientID: process.env.PLAID_CLIENT_ID,
    secret: process.env.PLAID_SECRET, 
    env: plaid.environments.development,
});

app.get('/create-link-token', async (req, res) => {
    const { link_token: linkToken } = await plaidClient.createLinkToken({
        user: {
            client_user_id:'unique-id',
        },
        client_name: 'client1',
        products: ['auth', 'identity'],
        country_codes:['US'],
        language: 'en',
    });

    res.json({ linkToken });
});

// use this to exchsnge the public token for access token 
app.post('/token-exchange', async (req, res) => {
    const {publicToken} = req.body;
    const {access_token:accessToken} = await plaidClient.exchangePublicToken(publicToken);
    
    const authResponse = await plaidClient.getAuth(accessToken);
    console.log("----------------------");
    console.log("Auth response: ");
    console.log(util.inspect(authResponse, false, null, true));

    const identityResponse = await plaidClient.getIdentity(accessToken);
    console.log("----------------------");
    console.log("Identity response: ");
    console.log(util.inspect(identityResponse, false, null, true));

    const balanceResponse = await plaidClient.getBalance(accessToken);
    console.log("----------------------");
    console.log("Balance response: ");
    console.log(util.inspect(balanceResponse, false, null, true));

    res.sendStatus(200);
});

app.get('/', async (req, res) => {
    res.sendFile(path.join(__dirname, '/templates/login.html'));
});

app.listen(PORT, () => {
    console.log("Listening on port: ", PORT);
});