# Zoho CRM writer

`create`, `update` and `delete` ZOHO CRM records using [the bulk api](https://www.zoho.com/crm/help/api/v2/#record-api)

# Configuration
```javascript
{
  "debug": true,
  "redirect_uri": "same as when registering component"
  "client_id": "...",
  "#clinet_secret": "...",
  "#refresh_token": "....",
  "base_url": "",
  "base_tokens_url": ""
}
```

`"base_url"` is, depending on your datacenter one of
- https://www.zohoapis.eu/crm/v2/
- https://www.zohoapis.com/crm/v2/
- https://www.zohoapis.com.cn/crm/v2/

`"base_tokens_url"` is one of 
- https://accounts.zoho.eu/oauth/v2/
- https://accounts.zoho.com/oauth/v2/
- https://accounts.zoho.com.con/oauth/v2/

Get credentials from https://www.zoho.com/crm/help/api/v2/#oauth-request

## Get refresh token

```bash
$ git clone https://github.com/pocin/kbc-wr-zoho-crm
$ python3

from wrzoho.client import BaseZohoCrmClient
redirect_uri = 'your redirect uri'
client_id = 'your id'
client_secret = 'your secret'

cl = ZohoCrmClient(redirect_uri='http://127.0.0.1/callback,
                   client_id=client_id,
                   client_secret=client_secret,
                   base_url='https://www.zohoapis.com/crm/v2/',
                   base_tokens_url='https://accounts.zoho.eu/oauth/v2/')
print(cl.authorization_url())
# visit this in your browser, you will be redirected. Copy the code from the redirected url

# will look like this 
# 'http://127.0.0.1/callback?code=this&location=eu&accounts-server=https%3A%2F%2Faccounts.zoho.eu'
grant_url = "" #the url above
print(cl.convert_grant_token(url_with_grant_token=grant_url))
# will give you refresh tokens, write it down!
{'access_token': 'token a',
 'refresh_token': 'token B',
 'expires_in_sec': 3600,
 'api_domain': 'https://www.zohoapis.com',
 'token_type': 'Bearer',
 'expires_in': 3600000}
```

The writer behavior is completely determined by the input tables you provide.
The grammar is `/data/in/tables/<action>_<module>.csv`  
Available actions are `create`, `update`, `delete`.  
Available modules are `{"leads", "accounts", "contacts", "deals", "campaigns", "cases", "solutions", "products", "vendors", "pricebooks", "quotes", "salesorders", "purchaseorders", "invoices", "custom", "notes"}` 

See [the documentation](https://www.zoho.com/crm/help/contacts/standard-fields.html) for which columns are available for which module.

## Example inputs

### Create contacts
Make a table `/data/in/tables/create_contacts.csv` with the following contents:

```csv
First_Name,Last_Name,Email,Description
Robin,Nemeth,robin@keboola.com,"Nice guy, get in touch!"
John,Doe,john@doe.com,"Meh"
Jane,Hoe,hoe@bro.com,"Main point of contact for Corporation X"
```

would create 3 `Contacts`

If a field is a `Lookup` type, i.e the api expects nested json
```
"Lookup" : {
    "name" : "James"
    "id" : "425248000000104001"
    },
```
(For contacts it might be `Contact_Owner` field)
the csv would look like this


```csv
Contact_Owner__id,First_Name,Last_Name,Email,Description
12345,Robin,Nemeth,robin@keboola.com,"Nice guy, get in touch!"
12345,John,Doe,john@doe.com,"Just an average John Doe"
12345,Jane,Hoe,hoe@bro.com,"Main point of contact for Corporation X"
```
where `12345` is the id of the owner and `Contact_Owner__id` (that is `Contact_Owner<double_underscore>id`) would be serialized into `{"Contact_Owner": {"id": "12345"}}`.

### Update contacts

Make a table `/data/in/tables/update_contacts.csv` with the following contents:

```csv
id,First_Name,Last_Name,Email,Description
666,Robin,Nemeth,robin@keboola.com,"Nice guy, get in touch!"
555,John,Doe,john@doe.com,"Meh"
444,Jane,Hoe,hoe@bro.com,"Main point of contact for Corporation X"
```
where `id` is the id of the record in zoho


### Delete contacts

Make a table `/data/in/tables/delete_contacts.csv` with single `id` column

```csv
id
12345
56778
```
this would delete `contacts` with ids `12345`, `56778`.


# Development

- Create an app in zoho 
- make a `.env` file based on the `.env_template`

## Run tests
```
$ make test
# $ make testk what='test_getting_access_token'
#  would run just the specific test

# after dev session is finished to clean up containers..
$ make clean 
```

## Run locally
```
$ docker-compose run --rm dev
# gets you an interactive shell
# mounts the ./data/ folder to /data/
```
