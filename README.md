# README 1.16.0

### What is this repository for? ###
The project provides an example of how the Arium API can be used to create reusable scripts 
for loss allocation. The project contains functions that can be used to make requests to the API. 
In particular, the functions allow the user to run loss allocation on a portfolio.


### Basic setup on Windows ###
1. Install python 3.9.
2. Get source from git.
3. Install dependencies: <br>
   `pip install -r requirements.txt`
4. Create environment variables: <br>
   `<prefix>_CLIENT_ID` <br>
   `<prefix>_CLIENT_SECRET` <br>
5. Create configuration for install in script or json file. Configuration must include:
    * authorization_url
    * token_url
    * base_uri

Example script: 
```python
from api_call.client import APIClient
from auth.okta_auth import Auth

conn = "connections.json"
prefix = "EXAMPLE"

auth = Auth(tenant="workspace1", role="basic", connections=conn, prefix=prefix)
client = APIClient(auth=auth)

client.portfolios().list()
``` 

Here the Okta authentication on browser should kick off.

