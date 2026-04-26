# Polar-to-FitTrackee 

Sync activities from flow.polar.com to self-hosted FitTrackee instance

## Setup 

Check and adapt `./config/users/example.json` to get started.

To setup the `polar_access_token` and `polar_user_id` the [polar.com/accesslink-api](https://www.polar.com/accesslink-api/#how-to-get-started) is used. Luckily, Polar provides a minimal [python example](https://github.com/polarofficial/accesslink-example-python) which is ideal to get started. The required steps are;

1. Login at https://admin.polaraccesslink.com/#/clients 
2. There, create a Client. Note down(!) the Client ID and Client secret.
3. `git clone https://github.com/polarofficial/accesslink-example-python.git`
4. `cd accesslink-example-python/`
5. Populate the `config.yml` with the ID and secret. 
6. `uv init .`
7. `uv add -r requirements.txt`
8. `uv run example_web_app.py`
9. Acecess http://localhost:5000 in your browser. 
10. Follow the 'Link to authorize'
11. 'Read User Data' -> note down `polar_user_id` for each user
12. Check `usertokens.yml` to obtain `access_token` for each `user_id`


## Run
To run the script once; `uv run sync.py`

Run with docker compose: `docker compose up`

To add it to crontab (`crontab -e`) best use docker (`sync.py` per default stores to `./data`)

```
*/15 * * * * docker compose -f /<<your-absolute-path>>/polar-to-fittrackee/docker-compose.yml up -d
```
