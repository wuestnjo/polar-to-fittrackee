# Polar2FitTrackee

Sync activities from flow.polar.com to self-hosted FitTrackee instance

Check and adapt `./config/users/example.json` to get started.

## Get Polar Flow User Token
```
# Login at https://admin.polaraccesslink.com/#/clients 
# ... and create PolarAcessLink client 
#  --> Client ID
#  --> Client Secret

git clone https://github.com/polarofficial/accesslink-example-python.git

cd accesslink-example-python

python3 -m venv ./venv.

venv./bin/pip install -r requirements.txt

venv./bin/python example_web_app.py

# Navigate to localhost in browser
# Sign in with your polar user 
# Link account 
# Token will be located under usertokens.yml
```


## Run 
```
## Run once
uv run sync.py

## Run with docker compose
docker compose up

## add to crontab - best done with docker compose 
# (sync.py stores to ./data)

crontab -e
*/15 * * * * docker compose -f /<<your-absolute-path>>/polar2fittrackee/docker-compose.yml up -d
```
